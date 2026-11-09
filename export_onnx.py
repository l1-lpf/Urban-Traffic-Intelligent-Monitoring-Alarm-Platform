from ultralytics import YOLO
import shutil
import os

if __name__ == "__main__":
    model_path = "runs/detect/visdrone_v11s/weights/best.pt"
    model = YOLO(model_path)
    export_path = model.export(format="onnx", opset=12, simplify=True)

    os.makedirs("models", exist_ok=True)
    shutil.copy(export_path, "models/best.onnx")
    shutil.copy(model_path, "models/best.pt")
    print("✅ 模型导出成功！")
