import asyncio
import re
import socket
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import requests
from androguard.misc import AnalyzeAPK
from flask import Blueprint, request, jsonify
from loguru import logger
import aiohttp
logger.remove()

ip_api = Blueprint('ip_api', __name__)

# 连接数据库的函数
def connect_db():
    conn = sqlite3.connect('database.sqlite')
    return conn

def extract_ips_and_urls(apk_path):
    print("start")
    # 加载并分析 APK 文件
    apk, _, dx = AnalyzeAPK(apk_path)

    # 定义正则表达式
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    ip_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    urls = set()
    ips = set()

    print("遍历")
    # 遍历 APK 中的字符串
    for string in dx.get_strings():
        string_value = string.get_value() if hasattr(string, 'get_value') else str(string)

        # 使用 finditer 迭代匹配所有 URL
        for match in url_pattern.finditer(string_value):
            urls.add(match.group())

        # 使用 finditer 迭代匹配所有 IP 地址
        for match in ip_pattern.finditer(string_value):
            ips.add(match.group())

    print(urls, ips)
    return urls, ips


async def get_location(ip):
    proxy = "http://127.0.0.1:7890"
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://ipinfo.io/{ip}/json?token=f4902a3bdecd54', proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                return (data.get('city'), data.get('region'), data.get('country'), data.get('loc'))
            return None, None, None, None


def extract_domain_from_url(url):
    # 匹配 http:// 或 https:// 开头，然后提取域名部分
    domain_pattern = re.compile(r'^https?://([^/]+)')

    # 使用正则表达式进行匹配
    match = domain_pattern.match(url)
    if match:
        return match.group(1)  # 返回匹配到的域名部分（不包含 http:// 或 https://）
    else:
        return None  # 如果没有匹配到，则返回 None

async def update_ips_with_urls(urls, ips):
    updated_urls = []
    updated_ips = []

    # 使用asyncio.gather来并行处理所有URL
    tasks = [async_get_ip_from_domain(extract_domain_from_url(url)) for url in urls]
    results = await asyncio.gather(*tasks)

    for url, ip in zip(urls, results):
        if ip:
            updated_urls.append(url)
            updated_ips.append(ip)
        else:
            updated_urls.append(url)
            updated_ips.append(None)

    for ip in ips:
        if ip not in updated_ips:
            updated_urls.append(None)
            updated_ips.append(ip)

    return updated_urls, updated_ips


def get_ip_from_domain(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror as e:
        print(f"获取域名 {domain} 的 IP 地址时出错: {e}")
        return None
    except Exception as ex:
        print(f"获取域名 {domain} 的 IP 地址时出现未知错误: {ex}")
        return None

async def async_get_ip_from_domain(domain):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        ip = await loop.run_in_executor(pool, get_ip_from_domain, domain)
        return ip


# 查询 IP 表的函数
def query_ip_table(md5):
    conn = connect_db()
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("SELECT * FROM IP WHERE MD5=?", (md5,))
    ip_info = cursor.fetchone()  # 假设只返回一条结果
    # print(ip_info)

    cursor.close()
    conn.close()

    return ip_info


@ip_api.route('/get_location', methods=['GET'])
def get_location_api():
    md5 = request.args.get('md5', '')
    if not md5:
        return jsonify({'error': 'md5 parameter is required'})

    # 假设这里是从数据库中查询到的结果
    ip_info = query_ip_table(md5)
    if not ip_info:
        return jsonify({'error': 'No data found for the given md5'})

    # 解析 loc 字段
    try:
        formatted_string = f'[{ip_info[5]}]'
        loc_list = list(eval(formatted_string))
    except:
        print("空")
        return jsonify([{
            'ip': 'None',
            'city': 'None',
            'region': 'None',
            'country': 'None',
            'lat': 'None',
            'lng': 'None',
            'domain': 'None'
        }])

    results = []
    for i in range(len(loc_list)):
        ip = ip_info[1].split(',')[i].strip().strip("'") if i < len(ip_info[1].split(',')) else ip_info[
            1].strip().strip("'")
        city = ip_info[2].split(',')[i].strip().strip("'") if i < len(ip_info[2].split(',')) else ip_info[
            2].strip().strip("'")
        region = ip_info[4].split(',')[i].strip().strip("'") if i < len(ip_info[4].split(',')) else ip_info[
            4].strip().strip("'")
        country = ip_info[3].split(',')[i].strip().strip("'") if i < len(ip_info[3].split(',')) else ip_info[
            3].strip().strip("'")
        domain = ip_info[6].split(',')[i].strip().strip("'") if i < len(ip_info[6].split(',')) else ip_info[
            6].strip().strip("'")
        lat_lng = loc_list[i].split(',')
        print(lat_lng)

        # 检查是否有有效的经纬度数据
        if not lat_lng[0].strip() or (len(lat_lng) < 2 or not lat_lng[1].strip()):
            continue

        lat = float(lat_lng[0].strip())
        lng = float(lat_lng[1].strip())

        data = {
            'ip': ip,
            'city': city,
            'region': region,
            'country': country,
            'lat': lat,
            'lng': lng,
            'domain': domain
        }
        results.append(data)

    return jsonify(results)

@ip_api.route('/get_location_new', methods=['GET'])
async def get_location_api_new():
    md5 = request.args.get('md5', '')
    if not md5:
        return jsonify({'error': 'md5 parameter is required'})

    ip_info = query_ip_table(md5)
    if not ip_info:
        return jsonify({'error': 'No data found for the given md5'})

    try:
        formatted_string = f'[{ip_info[5]}]'
        loc_list = list(eval(formatted_string))
    except:
        return jsonify([{
            'ip': 'None',
            'city': 'None',
            'region': 'None',
            'country': 'None',
            'lat': 'None',
            'lng': 'None',
            'domain': 'None'
        }])

    results = []
    for i in range(len(loc_list)):
        ip = ip_info[1].split(',')[i].strip().strip("'") if i < len(ip_info[1].split(',')) else ip_info[
            1].strip().strip("'")
        city = ip_info[2].split(',')[i].strip().strip("'") if i < len(ip_info[2].split(',')) else ip_info[
            2].strip().strip("'")
        region = ip_info[4].split(',')[i].strip().strip("'") if i < len(ip_info[4].split(',')) else ip_info[
            4].strip().strip("'")
        country = ip_info[3].split(',')[i].strip().strip("'") if i < len(ip_info[3].split(',')) else ip_info[
            3].strip().strip("'")
        domain = ip_info[6].split(',')[i].strip().strip("'") if i < len(ip_info[6].split(',')) else ip_info[
            6].strip().strip("'")
        lat_lng = loc_list[i].split(',')

        if not lat_lng[0].strip() or (len(lat_lng) < 2 or not lat_lng[1].strip()):
            continue

        lat = float(lat_lng[0].strip())
        lng = float(lat_lng[1].strip())

        data = {
            'ip': ip,
            'city': city,
            'region': region,
            'country': country,
            'lat': lat,
            'lng': lng,
            'domain': domain
        }
        results.append(data)

    current_location = await get_current_location()
    if not current_location:
        return jsonify({'error': 'Could not determine current location'})

    routes = []
    for location in results:
        routes.append({
            'start': current_location,
            'end': location
        })

    return jsonify({'locations': results, 'routes': routes})


async def get_external_ip():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://httpbin.org/ip') as response:
            if response.status == 200:
                data = await response.json()
                return data['origin']
            return None


async def get_current_location():
    ip = await get_external_ip()
    if not ip:
        return None

    city, region, country, loc = await get_location(ip)
    if loc:
        lat, lng = map(float, loc.split(','))
        return {
            'ip': ip,
            'city': city,
            'region': region,
            'country': country,
            'lat': lat,
            'lng': lng,
            'domain': ''
        }
    return None


if __name__ == "__main__":
    ip = '104.234.0.191'  # 你可以替换为任何有效的 IP 地址
    loop = asyncio.get_event_loop()  # 获取当前事件循环
    location = loop.run_until_complete(get_location(ip))  # 运行异步函数并获取结果
    print(location)  # 输出结果

    # print(requests.get(f'http://ipinfo.io/{ip}/json?token=f4902a3bdecd54').json())