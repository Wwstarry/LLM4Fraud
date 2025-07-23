from transformers import T5Tokenizer, T5ForSequenceClassification
import torch

# text推理接口['black' 'gamble' 'scam' 'sex' 'white']
# 输入特征
"""
# 合并文本特征
data['combined_text'] = data['Package Name'] + " " + data['Main Activity'] + " " + \
                        data['Activities'].astype(str) + " " + data['Services'].astype(str) + " " + \
                        data['Receivers'].astype(str) + " " + data['Permissions'].astype(str)
"""
def text_predict(text, model_path="./"):
    model = T5ForSequenceClassification.from_pretrained(model_path)
    tokenizer = T5Tokenizer.from_pretrained(model_path, legacy=False)
    encoding = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=512,
        return_tensors='pt'
    )
    input_ids = encoding['input_ids']
    attention_mask = encoding['attention_mask']
    outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    # 计算每个类别的概率
    probs = torch.softmax(outputs.logits, dim=1).detach().cpu().numpy()[0]

    # 返回每个类别的概率向量
    return probs
