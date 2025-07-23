import requests
import cv2
from pyzbar.pyzbar import decode  # 使用 pyzbar 库解码二维码
from tqdm import tqdm  # 导入 tqdm


# 1. 解析二维码图片获取链接或文件路径
def decode_qr_code(image_path):
    image = cv2.imread(image_path)  # 读取二维码图片
    print("二维码存储路径：", image_path)
    barcodes = decode(image)  # 解码二维码
    if barcodes:
        qr_data = barcodes[0].data.decode('utf-8')  # 解码结果为 bytes，转换为字符串
        return qr_data
    else:
        return None

# 2. 下载文件
def download_file(url, save_path):
    response = requests.get(url, stream=True)  # 使用 stream=True 开启流式下载
    total_size = int(response.headers.get('content-length', 0))  # 获取文件总大小
    if response.status_code == 200:
        # with open(save_path, 'wb') as f:
        #     f.write(response.content)
        # print(f"文件下载成功: {save_path}")
        with open(save_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=save_path.split('/')[-1]) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    f.write(data)
                    pbar.update(len(data))  # 更新进度条
    else:
        print(f"文件下载失败: {response.status_code}")



# 示例用法
if __name__ == "__main__":
    qr_image_path = 'uploads/qr_douyin.png'  # 替换为你的二维码图片路径
    file_save_path = f"./tmp/{qr_image_path.strip().split('.')[-2].split('/')[-1]}.apk"  # 替换为你希望保存的文件路径

    # 解析二维码图片获取链接
    qr_url = decode_qr_code(qr_image_path)
    if qr_url:
        print(f"解析到的二维码链接: {qr_url}")
        # 下载文件
        download_file(qr_url, file_save_path)
    else:
        print("未能解析到有效的二维码内容")
