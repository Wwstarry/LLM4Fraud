import os
import csv
import hashlib
import io
import pandas as pd
from loguru import logger
from androguard.core.apk import APK
from tqdm import tqdm
from PIL import Image


# 移除所有现有的日志处理器
logger.remove()

# 定义存储Logo的目录
logo_dir = "./logo"
os.makedirs(logo_dir, exist_ok=True)

# 定义标签文件目录
label_dir = "./batch"
label_files = ["sex.xlsx", "black.xlsx", "gamble.xlsx", "scam.xlsx", "white.xlsx"]

# 定义解析结果输出文件
output_csv = "apk_info.csv"

# 解析单个APK文件
def parse_apk(apk_path):
    try:
        a = APK(apk_path)
        app_name = a.get_app_name()
        package_name = a.get_package()
        main_activity = a.get_main_activity()
        activities = a.get_activities()
        services = a.get_services()
        receivers = a.get_receivers()
        permissions = a.get_permissions()

        # 获取第一个证书信息
        cert = a.get_certificates()[0]
        cert_info = {
            'Cert_SHA1': cert.sha1.hex(),
            'Cert_SHA256': cert.sha256.hex(),
            'Cert_Issuer': cert.issuer.human_friendly,
            'Cert_Subject': cert.subject.human_friendly,
            'Cert_Hash_Algo': cert.hash_algo,
            'Cert_Signature_Algo': cert.signature_algo,
            'Cert_Serial_Number': cert.serial_number
        }

        # 计算APK文件的MD5
        md5_digest = hashlib.md5(open(apk_path, 'rb').read()).hexdigest()

        # 提取并保存Logo
        logo_path = os.path.join(logo_dir, f"{md5_digest}.png")
        icon_path = a.get_app_icon()
        if icon_path:
            try:
                icon_data = a.get_file(icon_path)
                if icon_data:
                    if icon_path.endswith('.xml'):
                        try:
                            with open(logo_path, 'wb') as f:
                                f.write(icon_data)
                        except Exception as e:
                            logo_path = ""
                            logger.error(f"Failed to parse XML: {e}")
                    else:
                        image = Image.open(io.BytesIO(icon_data))
                        image.save(logo_path)
                else:
                    logger.error(f"Icon data not found for APK: {apk_path}")
                    logo_path = ""
            except Exception as e:
                logger.error(f"Failed to save logo for APK: {apk_path}, Error: {e}")
                logo_path = ""

        apk_info = {
            'App Name': app_name,
            'Package Name': package_name,
            'Main Activity': main_activity,
            'Activities': activities,
            'Services': services,
            'Receivers': receivers,
            'Permissions': permissions,
            'MD5': md5_digest,
            'Logo Path': logo_path,
            'Cert_SHA1': cert_info['Cert_SHA1'],
            'Cert_SHA256': cert_info['Cert_SHA256'],
            'Cert_Issuer': cert_info['Cert_Issuer'],
            'Cert_Subject': cert_info['Cert_Subject'],
            'Cert_Hash_Algo': cert_info['Cert_Hash_Algo'],
            'Cert_Signature_Algo': cert_info['Cert_Signature_Algo'],
            'Cert_Serial_Number': cert_info['Cert_Serial_Number']
        }

        return apk_info
    except Exception as e:
        logger.error(f"Failed to analyze APK: {apk_path}, Error: {e}")
        return None

# 匹配标签
def match_labels(md5_digest, apk_dir):
    # 只为batch目录中的APK文件匹配标签
    if apk_dir == "./batch":
        for label_file in label_files:
            df = pd.read_excel(os.path.join(label_dir, label_file))
            if md5_digest in df['md5'].values:
                return df[df['md5'] == md5_digest]['result'].values[0]
    return os.path.basename(apk_dir)  # 返回目录名称作为默认标签

# 解析并保存所有APK信息
def main():
    dirs_to_search = ["./batch", "./sex", "./black", "./gamble", "./scam"]
    apk_files = []

    # 搜集所有目录中的APK文件
    for dir in dirs_to_search:
        apk_files.extend([(os.path.join(dir, f), dir) for f in os.listdir(dir) if f.endswith('.apk')])

    # 仅解析前五个APK文件
    # apk_files = apk_files[-5:]

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        # 获取所有可能的字段名
        fieldnames = ['App Name', 'Package Name', 'Main Activity', 'Activities', 'Services', 'Receivers',
                      'Permissions', 'MD5', 'Logo Path', 'Cert_SHA1', 'Cert_SHA256', 'Cert_Issuer',
                      'Cert_Subject', 'Cert_Hash_Algo', 'Cert_Signature_Algo', 'Cert_Serial_Number', 'Label']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # 添加进度条
        for apk_file, apk_dir in tqdm(apk_files, desc="Processing APK files"):
            apk_info = parse_apk(apk_file)
            if apk_info is not None:
                label = match_labels(apk_info['MD5'], apk_dir)
                apk_info['Label'] = label
                writer.writerow(apk_info)
                # 打印解析结果
                # print(json.dumps(apk_info, indent=4))

def get_file_name(md5):
    dirs_to_search = ["./batch", "./sex", "./black", "./gamble", "./scam"]
    apk_files = []

    # 搜集所有目录中的APK文件
    for dir in dirs_to_search:
        apk_files.extend([(os.path.join(dir, f), dir) for f in os.listdir(dir) if f.endswith('.apk')])

    for apk_file, apk_dir in tqdm(apk_files, desc="Processing APK files"):
        apk_info = parse_apk(apk_file)
        if apk_info is not None:
            if apk_info['MD5'] == md5:
                print("file name:", apk_file)
                break

if __name__ == "__main__":
    main()
    # get_file_name("873f94c2c3f5a9fa1bfc476b2f3ad3ae")
