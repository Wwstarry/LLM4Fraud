import asyncio

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import sqlite3
import os
import hashlib
import io
from loguru import logger
from androguard.core.apk import APK
from pyaxmlparser import APK as APPK
from PIL import Image

# 移除所有现有的日志处理器
from ip_api import extract_ips_and_urls, get_location, update_ips_with_urls
from qrcode_api import decode_qr_code, download_file

logger.remove()

# 定义存储Logo的目录
logo_dir = "icon"
os.makedirs(logo_dir, exist_ok=True)

uploadFiles = Blueprint('uploadFiles', __name__)
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def insert_into_apk(apk_info, model):
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()

    # Convert non-primitive data types to string
    for key, value in apk_info.items():
        if isinstance(value, (list, dict, set, tuple)):  # Add other data types if needed
            apk_info[key] = str(value)

    placeholders = ', '.join(['?'] * len(apk_info))
    columns = ', '.join(apk_info.keys())
    sql = f"INSERT INTO Apk ({columns}) VALUES ({placeholders})"

    cursor.execute(sql, list(str(_) for _ in apk_info.values()))
    conn.commit()
    md5 = apk_info['MD5']
    columns = 'MD5, model'
    placeholders = '?, ?'
    sql = f"INSERT INTO Result ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, [md5, model])
    conn.commit()
    conn.close()

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
                            apk = APPK(apk_path)
                            image = Image.open(io.BytesIO(apk.icon_data))
                            image.save(logo_path)
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
            'App_Name': app_name,
            'Package_Name': package_name,
            'Main_Activity': main_activity,
            'Activities': activities,
            'Services': services,
            'Receivers': receivers,
            'Permissions': permissions,
            'MD5': md5_digest,
            'Logo_Path': logo_path,
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


# 获取文件大小
def get_file_size_mb(file_path):
    size_in_bytes = os.path.getsize(file_path)
    size_in_mb = size_in_bytes / (1024 * 1024)
    return str(round(size_in_mb, 2)) + ' MB'


def update_apk_size(md5, file_path):
    try:
        conn = sqlite3.connect('database.sqlite')
        cursor = conn.cursor()

        # Get file size in MB
        size_mb = get_file_size_mb(file_path)

        # Update size in database
        sql = "UPDATE Apk SET size = ? WHERE MD5 = ?"
        cursor.execute(sql, (size_mb, md5))
        conn.commit()

        conn.close()
        print(f"Size updated successfully for MD5: {md5}")

    except Exception as e:
        print(f"Error updating size for MD5 {md5}: {e}")


# 连接数据库的函数
def connect_db():
    conn = sqlite3.connect('database.sqlite')
    return conn


# 将域名和IP地址存入数据库的函数
async def store_ips_and_urls(md5, apk_path):
    conn = connect_db()
    cursor = conn.cursor()

    urls, ips = extract_ips_and_urls(apk_path)
    urls = list(urls)
    ips = list(ips)
    print(urls, ips)
    urls, ips = await update_ips_with_urls(urls, ips)
    # 使用 asyncio.gather 并行处理所有IP的地理位置查询
    location_data = await asyncio.gather(*(get_location(ip) for ip in ips if ip is not None))


    cities, regions, countries, locs = zip(*location_data) if location_data else ([], [], [], [])

    print(len(urls), len(ips), len(cities), len(regions), len(countries), len(locs))
    # 将数据转换成适合存储的格式
    urls_str = ', '.join(f"'{url}'" for url in urls)
    ips_str = ', '.join(f"'{ip}'" for ip in ips)
    cities_str = ', '.join(f"'{city}'" for city in cities)
    regions_str = ', '.join(f"'{region}'" for region in regions)
    countries_str = ', '.join(f"'{country}'" for country in countries)
    locs_str = ', '.join(f"'{loc}'" for loc in locs)

    # 构造 SQL 语句
    sql = f'INSERT INTO IP (MD5, domain, ip, city, country, region, loc) VALUES' \
          f' ("{md5}", "{urls_str}", "{ips_str}", "{cities_str}", "{regions_str}", "{countries_str}", "{locs_str}")'
    # print(sql)

    try:
        # 执行 SQL 语句
        cursor.execute(sql)
        conn.commit()
        print(f"数据成功插入数据库: {md5}")
    except sqlite3.Error as e:
        print(f"插入数据时出现错误: {e}")
    finally:
        # 关闭连接
        conn.close()

@uploadFiles.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and file.filename.endswith('.apk'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        apk_info = parse_apk(file_path)
        # print(request.form['model'])
        # print(apk_info)
        insert_into_apk(apk_info, request.form['model'])
        md5_digest = apk_info['MD5']
        update_apk_size(md5_digest, file_path)
        asyncio.run(store_ips_and_urls(md5_digest, file_path))

        # Delete the uploaded file
        # os.remove(file_path)

        # 重命名文件为MD5值
        os.rename(file_path, f"{UPLOAD_FOLDER}/{md5_digest}.apk")

        return jsonify({
            'message': 'File uploaded and processed successfully',
            'md5': md5_digest,
        }), 200
    else:
        return 'Invalid file type', 400


@uploadFiles.route('/upload/qr', methods=['POST'])
def upload_qr():
    # 接收前端返回的图片
    if 'image' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['image']
    # print(file.filename)

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the uploaded file to a designated folder
    if file:
        file.save(UPLOAD_FOLDER + '/' + file.filename)
        qr_image_path = UPLOAD_FOLDER + '/' + file.filename  # 替换为你的二维码图片路径
        file_save_path = f"{UPLOAD_FOLDER}/{qr_image_path.strip().split('.')[-2].split('/')[-1]}.apk"  # 替换为你希望保存的文件路径
        # 解析二维码图片获取链接
        qr_url = decode_qr_code(qr_image_path)
        if qr_url:
            print(f"解析到的二维码链接: {qr_url}")
            # 下载文件
            download_file(qr_url, file_save_path)

            # 解析文件
            apk_info = parse_apk(file_save_path)
            insert_into_apk(apk_info, request.form['model'])
            md5_digest = apk_info['MD5']
            update_apk_size(md5_digest, file_save_path)
            asyncio.run(store_ips_and_urls(md5_digest, file_save_path))

            # Delete the uploaded file
            os.remove(qr_image_path)
            # os.remove(file_save_path)

            # 重命名文件为MD5值
            os.rename(file_save_path, f"{UPLOAD_FOLDER}/{md5_digest}.apk")

        else:
            print("未能解析到有效的二维码内容")
            return jsonify({'error': '二维码无效'}), 500
        return jsonify({'message': 'File successfully uploaded', 'filename': file.filename,
                        'md5': md5_digest}), 200

    return jsonify({'error': 'Upload failed'}), 500


@uploadFiles.route('/upload/url', methods=['POST'])
def upload_url():
    # 示例快手URL：https://js.a.kspkg.com/kos/nlav10814/kwai-android-generic-gifmakerrelease-10.10.30.28545_x32_1f14b3.apk
    url = request.form['url']
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    file_save_path = f"{UPLOAD_FOLDER}/{url.strip().split('.')[-2].split('/')[-1]}.apk"
    if url:
        print(f"URL链接: {url}")
        # 下载文件
        download_file(url, file_save_path)

        # 解析文件
        apk_info = parse_apk(file_save_path)
        insert_into_apk(apk_info, request.form['model'])
        md5_digest = apk_info['MD5']
        update_apk_size(md5_digest, file_save_path)
        asyncio.run(store_ips_and_urls(md5_digest, file_save_path))

        # Delete the uploaded file
        # os.remove(file_save_path)
        # 重命名文件为MD5值
        os.rename(file_save_path, f"{UPLOAD_FOLDER}/{md5_digest}.apk")
        return jsonify({'message': 'File successfully uploaded',
                        'md5': md5_digest}), 200
    else:
        print("无效的URL链接")
        return jsonify({'error': 'URL无效'}), 500


# if __name__ == '__main__':
#     asyncio.run(store_ips_and_urls("873f94c2c3f5a9fa1bfc476b2f3ad3ae", "./APKunzip/67.apk"))