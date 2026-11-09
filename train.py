from ultralytics import YOLO

if __name__ == "__main__":
    # 加载 YOLOv11s 预训练模型
    model = YOLO("yolo11s.pt")

    # 开始训练
    results = model.train(
        data="VisDrone_YOLO/data.yaml",  # 指向你刚生成的那个 yaml
        epochs=50,  # 跑 50 轮（VisDrone 很大，50 轮足够出好效果）
        imgsz=640,  # 图片尺寸
        batch=4,  # 【极其重要】你的 3050 只有 4G 显存，VisDrone 图里小目标极多，千万别用 8 或 16，必爆显存！用 4 最稳。
        device=0,  # 使用你的 3050 显卡
        name="visdrone_v11s",  # 保存文件夹名字
        workers=4,  # Windows 下如果卡死或报错，改成 0
        patience=15,  # 早停机制：连续15轮精度不升就提前结束
    )
