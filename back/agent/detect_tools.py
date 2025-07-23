import json

from langchain_core.tools import tool
from typing import Annotated, List, Dict, Optional
import sqlite3
import sys

from networkx.readwrite import json_graph

from detectionModels.iconModel.iconAPI import icon_predict
from detectionModels.textModel.textAPI import text_predict
import os

@tool
def get_package_name(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
    """
    Obtain the app package name according to the MD5 code.
    :param md5:
    :return: package name
    """
    current_working_directory = os.getcwd()
    print(f"Current working directory: {current_working_directory}")
    conn = sqlite3.connect('./database.sqlite')
    print("Database connection established successfully.")
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("SELECT Package_Name FROM Apk WHERE MD5=?", (md5,))
    info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()
    conn.close()

    return info[0]

@tool
def get_name(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
    """
    Obtain the app name according to the MD5 code.
    :param md5:
    :return: app name
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("SELECT App_Name FROM Apk WHERE MD5=?", (md5,))
    info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()
    conn.close()

    return info[0]

@tool
def get_activaties(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
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

@tool
def get_service_reciver(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
    """
    Obtain the services and recivers that the app requests according to the MD5 code.
    :param md5:
    :return: services and recivers
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("SELECT Services, Receivers FROM Apk WHERE MD5=?", (md5,))
    info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()
    conn.close()

    return f"Services: {info[0]}, Receivers: {info[1]}"

@tool
def get_permissions(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
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

@tool
def get_certificate(
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

@tool
def get_icon_prob(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
    """
    Obtain the APP icon corresponding to the MD5 belongs to the following five types of probability ['black' 'gamble' 'scam' 'sex' 'white'].
    :param md5:
    :return: probability
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()
    sys.path.append('../')
    # 查询具体的 md5 对应的记录
    cursor.execute("SELECT Logo_Path FROM Apk WHERE MD5=?", (md5,))
    info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()

    if info:
        # 处理路径，确保路径格式正确
        logo_path = info[0]
        logo_path = os.path.abspath(logo_path)  # 将相对路径转换为绝对路径
        result = icon_predict(logo_path, "./detectionModels/iconModel")
        cursor = conn.cursor()
        cursor.execute(f"UPDATE Result SET icon_black={result[0]}, icon_gamble={result[1]}, icon_scam={result[2]}, \
                        icon_sex={result[3]},icon_white={result[4]} WHERE MD5=?", (md5,))
        conn.commit()
        cursor.close()
        conn.close()
        return str(result)
    else:
        conn.close()
        return "No logo path found for the given MD5."


@tool
def get_content_prob(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
    """
    Obtain the APP content corresponding to the MD5 belongs to the following five types of probability ['black' 'gamble' 'scam' 'sex' 'white'].
    :param md5:
    :return: probability
    """
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    # 查询具体的 md5 对应的记录
    cursor.execute("""
        SELECT 
            Package_Name, 
            Main_Activity, 
            Activities, 
            Services, 
            Receivers, 
            Permissions 
        FROM Apk 
        WHERE MD5=?
    """, (md5,))
    info = cursor.fetchone()  # 假设只返回一条结果

    cursor.close()


    if info:
        # 构建 combined_text 字段
        combined_text = f"{info[0]} {info[1]} {info[2]} {info[3]} {info[4]} {info[5]}"

        # 调用文本预测函数
        result = text_predict(combined_text, "./detectionModels/textModel")
        cursor = conn.cursor()
        cursor.execute(f"UPDATE Result SET content_black={result[0]}, content_gamble={result[1]}, content_scam={result[2]}, \
                                content_sex={result[3]},content_white={result[4]} WHERE MD5=?", (md5,))
        conn.commit()
        cursor.close()
        conn.close()
        return str(result)
    else:
        conn.close()
        return "No data found for the given MD5."

@tool
def get_relation(
    md5: Annotated[str, "md5 code of an apk."],
) -> str:
    """
    Get the Top-3 MD5 code and similarity and app name of the apps related to this app.
    :param md5:
    :return: MD5 code and similarity and app name
    """
    # 读取图数据
    try:
        with open('./relatedGraph/graph.json', 'r') as f:
            data = json.load(f)
            G = json_graph.node_link_graph(data)
    except FileNotFoundError:
        return "Graph data not found"

    # 找到与指定MD5对应的节点
    target_node = None
    for node, attrs in G.nodes(data=True):
        if attrs.get('md5') == md5:
            target_node = node
            break

    if not target_node:
        return "MD5 not found in graph"

    # 找到与目标节点相连的一阶子图
    neighbors = [(neighbor, G[target_node][neighbor]['weight']) for neighbor in G.neighbors(target_node)]
    # 按相似度权重排序，取前三个
    top_neighbors = sorted(neighbors, key=lambda x: x[1], reverse=True)[:3]

    subgraph = {}
    for neighbor, weight in top_neighbors:
        neighbor_md5 = G.nodes[neighbor]['md5']
        subgraph[neighbor_md5] = (weight, G.nodes[neighbor]['lable'], neighbor)

    return str(subgraph)


