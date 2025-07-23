import pandas as pd
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset as TorchDataset
from sklearn.preprocessing import LabelEncoder
import os
from tqdm import tqdm
os.environ['CUDA_VISIBLE_DEVICES'] = '2'

# 读取标签文件
train_labels = pd.read_csv('./train_labels.csv')
test_labels = pd.read_csv('./test_labels.csv')

train_labels = train_labels[train_labels['Label'] != 'batch'].reset_index(drop=True)
test_labels = test_labels[test_labels['Label'] != 'batch'].reset_index(drop=True)

# 添加图像路径
train_labels['Filename'] = './logo/train/' + train_labels['Filename']
test_labels['Filename'] = './logo/test/' + test_labels['Filename']

# 转换字符串标签为数值标签
label_encoder = LabelEncoder()
train_labels['Label'] = label_encoder.fit_transform(train_labels['Label'])
test_labels['Label'] = label_encoder.transform(test_labels['Label'])


# 定义自定义Dataset类
class CustomDataset(TorchDataset):
    def __init__(self, df, feature_extractor):
        self.df = df
        self.feature_extractor = feature_extractor

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_path = self.df.iloc[idx]['Filename']
        label = self.df.iloc[idx]['Label']
        image = Image.open(img_path).convert("RGB")
        inputs = self.feature_extractor(images=image, return_tensors="pt")
        inputs = {k: v.squeeze() for k, v in inputs.items()}
        inputs['labels'] = torch.tensor(label, dtype=torch.long)
        return inputs

# 加载预训练的DeiT模型和特征提取器
# model_name = "facebook/deit-base-distilled-patch16-224"
model_name = "./pretrain_weight"
feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name, num_labels=5, ignore_mismatched_sizes=True)

# 创建自定义Dataset实例
train_dataset = CustomDataset(train_labels, feature_extractor)
test_dataset = CustomDataset(test_labels, feature_extractor)

# 创建DataLoader
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)
model.to(device)

# 定义优化器和损失函数
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=0.01)
criterion = torch.nn.CrossEntropyLoss()

# 训练函数
def train(epoch, model, train_loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    correct = 0
    for batch in tqdm(train_loader, desc=f"Training Epoch {epoch}"):
        inputs = {k: v.to(device) for k, v in batch.items()}
        labels = inputs.pop('labels').to(device)  # 确保标签也被转移到GPU上
        optimizer.zero_grad()
        outputs = model(**inputs)
        logits = outputs.logits
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        preds = logits.argmax(dim=1)
        correct += (preds == labels).sum().item()
    accuracy = correct / len(train_loader.dataset)
    avg_loss = total_loss / len(train_loader)
    return avg_loss, accuracy

# 验证函数
def validate(epoch, model, test_loader, criterion, device):
    model.eval()
    total_loss = 0
    correct = 0
    with torch.no_grad():
        for batch in tqdm(test_loader, desc=f"Validation Epoch {epoch}"):
            inputs = {k: v.to(device) for k, v in batch.items()}
            labels = inputs.pop('labels').to(device)  # 确保标签也被转移到GPU上
            outputs = model(**inputs)
            logits = outputs.logits
            loss = criterion(logits, labels)
            total_loss += loss.item()
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
    accuracy = correct / len(test_loader.dataset)
    avg_loss = total_loss / len(test_loader)
    return avg_loss, accuracy

# 训练和验证循环
num_epochs = 4
for epoch in range(1, num_epochs + 1):
    train_loss, train_accuracy = train(epoch, model, train_loader, optimizer, criterion, device)
    val_loss, val_accuracy = validate(epoch, model, test_loader, criterion, device)
    print(f"Epoch {epoch}:")
    print(f"  Train Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy:.4f}")
    print(f"  Validation Loss: {val_loss:.4f}, Validation Accuracy: {val_accuracy:.4f}")

# 保存模型权重
model_save_path = "./saved_model"
os.makedirs(model_save_path, exist_ok=True)
model.save_pretrained(model_save_path)
feature_extractor.save_pretrained(model_save_path)

# # 测试推理函数
# model_path = "./saved_model"
# test_image_path = "./logo/test/0062b5de62847c652f406c40e65a7a5e.png"  # 替换为你的测试图像路径
# probs = load_model_and_predict(model_path, test_image_path)
# print(probs)
