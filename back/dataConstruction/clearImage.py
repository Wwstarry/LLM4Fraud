import os
from PIL import Image
import pandas as pd
from sklearn.model_selection import train_test_split
import shutil

# 第一步：清洗无法读取的png
def clean_images(directory):
    unusable_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            file_path = os.path.join(directory, filename)
            try:
                img = Image.open(file_path)
                img.verify()  # 验证图像文件是否完整
            except (IOError, SyntaxError) as e:
                print(f"标记无法读取的文件: {file_path}")
                unusable_files.append(filename)
    return unusable_files

# 第二步：读取 CSV 文件并获取图片标签
def get_image_labels(csv_file):
    df = pd.read_csv(csv_file)
    md5_to_label = dict(zip(df['MD5'], df['Label']))
    return md5_to_label

# 第三步：拆分训练集和测试集
def split_data(image_dir, md5_to_label, unusable_files):
    image_files = []
    labels = []

    for filename in os.listdir(image_dir):
        if filename.endswith('.png') and filename not in unusable_files:
            md5 = filename.split('.')[0]
            if md5 in md5_to_label and md5_to_label[md5] != 'batch':
                image_files.append(os.path.join(image_dir, filename))
                labels.append(md5_to_label[md5])

    # 使用 train_test_split 将数据集拆分为训练集和测试集
    train_files, test_files, train_labels, test_labels = train_test_split(
        image_files, labels, test_size=0.2, stratify=labels, random_state=42
    )

    # 将文件移动到训练和测试文件夹中
    train_dir = os.path.join(image_dir, 'train')
    test_dir = os.path.join(image_dir, 'test')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    for file in train_files:
        shutil.move(file, train_dir)

    for file in test_files:
        shutil.move(file, test_dir)

    # 生成训练集标签文件
    train_files_basename = [os.path.basename(file) for file in train_files]
    train_labels_df = pd.DataFrame({'Filename': train_files_basename, 'Label': train_labels})
    train_labels_df.to_csv('train_labels.csv', index=False)

    # 生成测试集标签文件
    test_files_basename = [os.path.basename(file) for file in test_files]
    test_labels_df = pd.DataFrame({'Filename': test_files_basename, 'Label': test_labels})
    test_labels_df.to_csv('test_labels.csv', index=False)

    return train_dir, test_dir, unusable_files

# 执行清洗和拆分数据集
logo_directory = './logo'
apk_info_csv = './apk_info.csv'

unusable_files = clean_images(logo_directory)
md5_to_label = get_image_labels(apk_info_csv)
train_directory, test_directory, unusable_files = split_data(logo_directory, md5_to_label, unusable_files)

print(f"训练集目录: {train_directory}")
print(f"测试集目录: {test_directory}")
print(f"无法读取的文件: {unusable_files}")

# 读取 apk_info.csv 文件并创建 MD5 到 App Name 的映射
apk_info_df = pd.read_csv(apk_info_csv)
md5_to_app_name = dict(zip(apk_info_df['MD5'], apk_info_df['App Name']))

# 读取训练集标签文件
train_labels_df = pd.read_csv('train_labels.csv')
# 添加 App Name 列
train_labels_df['App_Name'] = train_labels_df['Filename'].apply(lambda x: md5_to_app_name.get(x.split('.')[0], ''))
# 保存修改后的训练集标签文件
train_labels_df.to_csv('train_labels.csv', index=False)

# 读取测试集标签文件
test_labels_df = pd.read_csv('test_labels.csv')
# 添加 App Name 列
test_labels_df['App_Name'] = test_labels_df['Filename'].apply(lambda x: md5_to_app_name.get(x.split('.')[0], ''))
# 保存修改后的测试集标签文件
test_labels_df.to_csv('test_labels.csv', index=False)
