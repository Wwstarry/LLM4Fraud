from langchain_core.tools import tool
from typing import Annotated, List, Dict, Optional, Any
import sqlite3

# ip分析
@tool
def ip_analize(
    md5: Annotated[str, "md5 code of an apk."],
) -> list[dict[str, float | Any]]:
    """
    Get the ip adress that the app related to.
    :param md5:
    :return: ip, city, region, country, latitude, lng
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()
    # 查询具体的 md5 对应的记录
    cursor.execute("SELECT * FROM IP WHERE MD5=?", (md5,))
    ip_info = cursor.fetchone()  # 假设只返回一条结果
    cursor.close()
    conn.close()

    try:
        formatted_string = f'[{ip_info[5]}]'
        loc_list = list(eval(formatted_string))
    except:
        return [{
            'ip': 'None',
            'city': 'None',
            'region': 'None',
            'country': 'None',
            'lat': 'None',
            'lng': 'None',
            'domain': 'None'
        }]

    # 获取每个 IP 的经纬度
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
            'lng': lng
        }
        results.append(data)
    return results

# 异常权限行为分析
@tool
def permission_analize(
    md5: Annotated[str, "md5 code of an apk."],
)-> str:
    """
    Obtaining the authority list of the app request according to the MD5 code.
    :param md5:
    :return: the authority list of the app request
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("SELECT Permissions FROM Apk WHERE MD5=?", (md5,))
    info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()
    conn.close()

    return info[0]

# 异常活动分析
@tool
def activity_analize(
    md5: Annotated[str, "md5 code of an apk."],
)-> str:
    """
    Obtain the main activity and  app activities according to the MD5 code.
    :param md5:
    :return: main activity and  app activities
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("SELECT Main_Activity, Activities FROM Apk WHERE MD5=?", (md5,))
    info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()
    conn.close()

    return f"Main_Activity: {info[0]}, Activities: {info[1]}"

# 证书分析
@tool
def certificate_analize(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
    """
    Obtain the certificate information according to the MD5 code.
    :param md5:
    :return: certificate information
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("""
        SELECT
            Cert_SHA1,
            Cert_SHA256,
            Cert_Issuer,
            Cert_Subject,
            Cert_Hash_Algo,
            Cert_Signature_Algo,
            Cert_Serial_Number
        FROM Apk
        WHERE MD5=?
    """, (md5,))
    cert_info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()
    conn.close()

    # 合并查询结果为一个字符串返回
    if cert_info:
        result = f"""
        Cert_SHA1: {cert_info[0]},
        Cert_SHA256: {cert_info[1]},
        Cert_Issuer: {cert_info[2]},
        Cert_Subject: {cert_info[3]},
        Cert_Hash_Algo: {cert_info[4]},
        Cert_Signature_Algo: {cert_info[5]},
        Cert_Serial_Number: {cert_info[6]}
        """
        return result.strip()
    else:
        return "No certificate information found for the given MD5."

# 获取muti-agent的分析结果
@tool
def model_result_analize(
    md5: Annotated[str, "md5 code of an apk."],
)-> str:
    """
    Get the probobility of each class that the detection model perform.
    :param md5: probobility of black, gamble, scam, sex, white,and the predicted Label.
    :return:
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("""
        SELECT
            black,
            gamble,
            scam,
            sex,
            white,
            Label
        FROM Apk
        WHERE MD5=?
    """, (md5,))
    cert_info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()
    conn.close()

    # 合并查询结果为一个字符串返回
    if cert_info:
        result = f"""
        black: {cert_info[0]},
        gamble: {cert_info[1]},
        scam: {cert_info[2]},
        sex: {cert_info[3]},
        white: {cert_info[4]},
        Label: {cert_info[5]},
        """
        return result.strip()
    else:
        return "No certificate information found for the given MD5."



