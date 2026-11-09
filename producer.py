import cv2
import time
from backend.database import redis_binary_client as redis_client

QUEUE_NAME = "video_frames_queue"

# ==========================================
# 🌟 切换模式：把这里改成 "image" 或 "video"
# ==========================================
MODE = "video"  # 测试视频用 "video"，测试单图用 "image"

IMG_PATH = "test.jpg"  # 单图模式下的图片路径
VIDEO_PATH = "test.mp4"  # 视频模式下的视频路径
# ==========================================


def push_image():
    """模式1：单张图片，推流后发送结束标记"""
    print(f"🎥 [单图模式] 正在读取图片: {IMG_PATH}...")
    img = cv2.imread(IMG_PATH)
    if img is None:
        print(f"❌ 找不到图片 {IMG_PATH}")
        return

    _, buffer = cv2.imencode(".jpg", img)
    # 推入图片
    redis_client.lpush(QUEUE_NAME, buffer.tobytes())
    # 推入结束标记
    redis_client.lpush(QUEUE_NAME, b"EOF")

    print("📤 图片推送完毕，并已发送结束标记！程序退出。")


def push_video():
    """模式2：读取真实的视频文件，按帧率推流，结束后发送标记"""
    print(f"🎥 [视频模式] 正在打开视频: {VIDEO_PATH}...")
    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"❌ 无法打开视频文件 {VIDEO_PATH}，请检查路径或格式！")
        return

    # 获取视频真实帧率（FPS）
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps > 60:
        fps = 30  # 兜底处理
    sleep_time = 1.0 / fps

    count = 0
    print(f"📤 视频打开成功，帧率: {fps} FPS，开始推流...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 视频播完了，退出循环

        _, buffer = cv2.imencode(".jpg", frame)
        redis_client.lpush(QUEUE_NAME, buffer.tobytes())

        count += 1
        if count % 300 == 0:  # 每 300 帧打印一次，防刷屏
            print(f"📤 已推送 {count} 帧...")

        # 控制推送速度，模拟真实视频
        time.sleep(sleep_time)

    cap.release()

    # 🌟 核心：视频推流结束后，往队列推入一个特殊暗号 b"EOF"
    redis_client.lpush(QUEUE_NAME, b"EOF")
    print(f"✅ 视频读取完毕，总计推送 {count} 帧。已发送结束标记！")


if __name__ == "__main__":
    # 启动前自动清空队列，防止旧数据干扰
    redis_client.delete(QUEUE_NAME)
    print("🧹 已自动清空 Redis 旧队列")

    if MODE == "image":
        push_image()
    elif MODE == "video":
        push_video()
    else:
        print("❌ 模式错误，请设置 MODE = 'image' 或 'video'")
