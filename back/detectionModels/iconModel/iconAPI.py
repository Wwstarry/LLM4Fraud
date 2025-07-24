from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch


def icon_predict(image_path, model_path="./"):
 
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_path)
    model = AutoModelForImageClassification.from_pretrained(model_path)
  
    image = Image.open(image_path).convert("RGB")
    inputs = feature_extractor(images=image, return_tensors="pt")
   
    model.eval()
  
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = logits.softmax(dim=1)  
    return probs[0].tolist()
