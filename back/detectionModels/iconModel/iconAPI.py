from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch

# icon推理函数，返回概率['black' 'gamble' 'scam' 'sex' 'white']
def icon_predict(image_path, model_path="./"):
    # 加载模型和处理器
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_path)
    model = AutoModelForImageClassification.from_pretrained(model_path)
    # 读取图像并进行预处理
    image = Image.open(image_path).convert("RGB")
    inputs = feature_extractor(images=image, return_tensors="pt")
    # 将模型设置为评估模式
    model.eval()
    # 推理
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = logits.softmax(dim=1)  # 计算概率
    return probs[0].tolist()
