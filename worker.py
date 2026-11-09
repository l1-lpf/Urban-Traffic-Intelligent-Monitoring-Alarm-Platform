import time
import cv2
import numpy as np
import os
from datetime import datetime
from backend.database import SessionLocal, redis_binary_client as redis_client
from backend.models.models import AlertRecord
from core.detector import TrafficDetector

# 初始化检测器
detector = TrafficDetector("models/best.onnx")
QUEUE_NAME = "video_frames_queue"

print("🤖 Worker 已启动，正在监听 Redis 队列...")

# ================= 核心防抖机制（终极双重防抖） =================
TIME_COOLDOWN = 4.0  # 🌟 1. 物理时间：两次报警至少间隔 4 秒
FRAME_COOLDOWN = 120  # 🌟 2. 逻辑帧：两次报警至少间隔 120 帧（30fps视频也是4秒）
MAX_QUEUE_SIZE = 1000000  # 🌟 3. 队列阈值：积压超过 X 帧则丢弃旧帧保新帧

frame_counter = 0  # 记录当前批次处理的总帧数
last_alert_frame = -999  # 记录上一次报警时的帧数
last_alert_time = 0.0  # 记录上一次报警时的物理时间


def process_frame():
    global frame_counter, last_alert_frame, last_alert_time
    db = SessionLocal()
    try:
        # 丢帧保新策略
        queue_len = redis_client.llen(QUEUE_NAME)
        if queue_len > MAX_QUEUE_SIZE:
            # print(f"⚠️ 队列积压，正在执行丢帧保新策略...")
            redis_client.ltrim(QUEUE_NAME, 0, MAX_QUEUE_SIZE - 1)

        # 从 Redis 获取数据
        queue_data = redis_client.brpop(QUEUE_NAME, timeout=1)
        if not queue_data:
            return

        _, frame_bytes = queue_data

        # 拦截结束标记
        if frame_bytes == b"EOF":
            print("\n" + "=" * 60)
            print("🎉 本次推流批次已处理完毕！Worker 重新进入待命状态...")
            print("=" * 60 + "\n")
            # 重置状态
            frame_counter = 0
            last_alert_frame = -999
            last_alert_time = 0.0
            return

        frame_counter += 1

        # 解析图片
        img_array = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # 1. 执行推理
        results = detector.detect(frame)
        if not results:
            return

        # 2. 业务规则引擎
        vehicle_classes = [
            "car",
            "van",
            "truck",
            "bus",
            "tricycle",
            "awning-tricycle",
            "motor",
        ]
        car_count = sum(1 for res in results if res["class_name"] in vehicle_classes)

        if car_count > 25:
            current_time = time.time()

            # 🌟 双重防抖判断：
            # 必须满足：物理时间过了 5 秒 且 视频帧数过了 150 帧
            time_passed = (current_time - last_alert_time) >= TIME_COOLDOWN
            frames_passed = (frame_counter - last_alert_frame) >= FRAME_COOLDOWN

            if time_passed and frames_passed:
                # 更新最后报警状态
                last_alert_time = current_time
                last_alert_frame = frame_counter

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                img_name = f"alert_{timestamp}.jpg"
                save_dir = "static/alerts"
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, img_name)

                for res in results:
                    x, y, w, h = res["box"]
                    if res["class_name"] in vehicle_classes:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

                cv2.imwrite(save_path, frame)

                new_alert = AlertRecord(
                    camera_id=1,
                    alert_type="traffic_jam",
                    snapshot_path=save_path,
                    confidence=results[0]["score"],
                )
                db.add(new_alert)
                db.commit()
                print(
                    f"🚨 拥堵报警！检测到 {car_count} 辆车（第 {frame_counter} 帧），生成截图：{img_name}"
                )

    except Exception as e:
        print(f"❌ 处理帧失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 🌟 新增：每次启动前，先清空 Redis 队列，防止旧数据干扰测试
    redis_client.delete(QUEUE_NAME)
    print("🧹 Worker 启动前已清空 Redis 旧队列")

    while True:
        process_frame()
