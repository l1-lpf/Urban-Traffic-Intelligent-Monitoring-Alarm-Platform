import cv2
import numpy as np
import onnxruntime as ort


class TrafficDetector:
    def __init__(self, model_path="models/best.onnx"):
        self.session = ort.InferenceSession(
            model_path, providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        self.classes = [
            "pedestrian",
            "people",
            "bicycle",
            "car",
            "van",
            "truck",
            "tricycle",
            "awning-tricycle",
            "bus",
            "motor",
        ]

    def detect(self, img, conf_thres=0.25):
        # 1. 预处理 (保持你之前的逻辑)
        h, w = img.shape[:2]
        img_resized = cv2.resize(img, (640, 640))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_chw = img_rgb.transpose(2, 0, 1).astype(np.float32) / 255.0
        input_tensor = np.expand_dims(img_chw, axis=0)

        # 2. 推理
        outputs = self.session.run(None, {self.input_name: input_tensor})

        # 3. 后处理 (简单提取检测到的类别和坐标)
        predictions = np.squeeze(outputs[0]).T
        boxes, scores, class_ids = [], [], []

        for pred in predictions:
            class_scores = pred[4:]
            class_id = np.argmax(class_scores)
            confidence = class_scores[class_id]

            if confidence > conf_thres:
                cx, cy, bw, bh = pred[:4]
                x = int((cx - bw / 2) * w / 640)
                y = int((cy - bh / 2) * h / 640)
                boxes.append([x, y, int(bw * w / 640), int(bh * h / 640)])
                scores.append(float(confidence))
                class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, scores, conf_thres, 0.45)
        results = []
        if len(indices) > 0:
            for i in indices.flatten():
                results.append(
                    {
                        "box": boxes[i],
                        "class_name": self.classes[class_ids[i]],
                        "score": scores[i],
                    }
                )
        return results
