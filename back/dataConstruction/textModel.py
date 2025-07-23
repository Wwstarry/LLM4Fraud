import pandas as pd
from sklearn.preprocessing import LabelEncoder
from transformers import T5Tokenizer, T5ForSequenceClassification, Trainer, TrainingArguments, EvalPrediction
from torch.utils.data import Dataset
import torch
from sklearn.model_selection import train_test_split
import os
import numpy as np
import evaluate

os.environ['CUDA_VISIBLE_DEVICES'] = '2'

# 加载数据
data = pd.read_csv('./apk_info.csv')

# 剔除标签为batch的数据
data = data[data['Label'] != 'batch'].reset_index(drop=True)

# 合并文本特征
data['combined_text'] = data['Package Name'] + " " + data['Main Activity'] + " " + \
                        data['Activities'].astype(str) + " " + data['Services'].astype(str) + " " + \
                        data['Receivers'].astype(str) + " " + data['Permissions'].astype(str)

# 对标签进行编码
label_encoder = LabelEncoder()
data['encoded_label'] = label_encoder.fit_transform(data['Label'])

# 划分训练集和测试集
train_texts, test_texts, train_labels, test_labels = train_test_split(
    data['combined_text'].tolist(), data['encoded_label'].tolist(), test_size=0.2, random_state=42
)

# 定义自定义数据集类
class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_len,
            return_tensors='pt'
        )
        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': torch.tensor(label, dtype=torch.long)
        }

cache_dir = "./pretrain_weight/T5"
# 初始化tokenizer和模型
tokenizer = T5Tokenizer.from_pretrained(cache_dir, legacy=False)
model = T5ForSequenceClassification.from_pretrained(cache_dir, num_labels=len(label_encoder.classes_))

# 准备数据加载器
train_dataset = TextDataset(train_texts, train_labels, tokenizer, max_len=512)
test_dataset = TextDataset(test_texts, test_labels, tokenizer, max_len=512)

metric = evaluate.load("accuracy")
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    if isinstance(logits, tuple):  # 检查 logits 是否为元组
        logits = logits[0]  # 提取 logits 的第一部分
    print("Logits shape:", np.array(logits).shape)  # 打印logits的形状
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# 定义训练参数
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    evaluation_strategy="epoch",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
)

# 定义Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# 训练模型
trainer.train()

# 保存模型权重
model.save_pretrained('./saved_model')
tokenizer.save_pretrained('./saved_model')

# 评估模型
eval_result = trainer.evaluate()
print(f"Evaluation results: {eval_result}")

# 获取预测结果
predictions = trainer.predict(test_dataset)
logits = predictions.predictions
if isinstance(logits, tuple):
    logits = logits[0]
preds = np.argmax(logits, axis=-1)

# 反编码预测标签
pred_labels = label_encoder.inverse_transform(preds)
true_labels = label_encoder.inverse_transform(test_labels)


