import sqlite3

import numpy as np
from flask import Blueprint, jsonify, request
import json
from relatedGraph.graphConstruction import updateGraph, getGraphData

count_api = Blueprint('count_api', __name__)

def connect_db():
    conn = sqlite3.connect('database.sqlite')
    return conn

def clean_coordinates(coordinates):
    cleaned_coords = []
    for coord in coordinates:
        cleaned_coord = coord.strip("'")
        if cleaned_coord != 'None':
            cleaned_coords.append(cleaned_coord)
    return cleaned_coords

def fetch_data():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 'high_risk_count' AS label, COUNT(*) AS count FROM Result WHERE prob > 0.75
    UNION ALL
    SELECT 'hei_hui_chan_count' AS label, COUNT(*) AS count FROM Result WHERE res = 1
    UNION ALL
    SELECT 'label_other_count' AS label, COUNT(*) AS count FROM Apk WHERE Label = 'black'
    UNION ALL
    SELECT 'label_sex_count' AS label, COUNT(*) AS count FROM Apk WHERE Label = 'sex'
    UNION ALL
    SELECT 'label_gamble_count' AS label, COUNT(*) AS count FROM Apk WHERE Label = 'gamble'
    UNION ALL
    SELECT 'label_scam_count' AS label, COUNT(*) AS count FROM Apk WHERE Label = 'scam'
    """)

    results = cursor.fetchall()
    counts = {row[0]: row[1] for row in results}

    high_risk_count = counts.get('high_risk_count', 0)
    hei_hui_chan_count = counts.get('hei_hui_chan_count', 0)
    label_minus_one_count = counts.get('label_other_count', 0)
    label_sex_count = counts.get('label_sex_count', 0)
    label_gamble_count = counts.get('label_gamble_count', 0)
    label_scam_count = counts.get('label_scam_count', 0)

    query = """
    SELECT Apk.App_Name, Result.prob, Result.MD5 
    FROM Apk 
    INNER JOIN Result 
    ON Apk.MD5 = Result.MD5
    """
    cursor.execute(query)
    app_results = cursor.fetchall()
    app_data = [{"Pname": row[0], "Pdanger": row[1], "MD5": row[2]} for row in app_results]

    cursor.execute("""
    SELECT IP.loc 
    FROM IP 
    JOIN Result ON IP.MD5 = Result.MD5 
    WHERE Result.res = '1'
    """)

    ip_addresses = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return high_risk_count, hei_hui_chan_count, label_minus_one_count, label_sex_count, label_gamble_count, label_scam_count, app_data, ip_addresses

def fetch_white_industry_percentage():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM Apk WHERE Label IN ('sex', 'white', 'black', 'scam', 'gamble')
    """)
    total_count = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM Apk WHERE Label = 'white'
    """)
    white_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    white_percentage = round((white_count / total_count) * 100, 1) if total_count > 0 else 0

    return white_percentage


@count_api.route('/home/index', methods=['GET'])
def get_data():
    updateGraph()
    try:
        high_risk_count, hei_hui_chan_count, label_minus_one_count, label_sex_count, label_gamble_count, label_scam_count, app_data, ip_addresses = fetch_data()
        white_industry_percentage = fetch_white_industry_percentage()
        graph_data = getGraphData()

        coordinates = []
        for ip_list in ip_addresses:
            ip_list_split = ip_list.split(', ')
            for ip in ip_list_split:
                coordinates.append(ip)

        coordinates_modified = clean_coordinates(coordinates)

        data = {
            'monthFixCount': high_risk_count,
            'monthFixIncreasePercentage': 5,
            'monthVulCount': hei_hui_chan_count,
            'monthVulIncreasePercentage': 3,
            'otherCount': label_minus_one_count,
            'sexCount': label_sex_count,
            'gambleCount': label_gamble_count,
            'scamCount': label_scam_count,
            'highRisk': [{'date': '2024-06-01', 'total_vul': high_risk_count, 'total_fix': hei_hui_chan_count - high_risk_count}],
            'userProjects': app_data,
            'coordinates': coordinates_modified,
            'whiteIndustryPercentage': white_industry_percentage,
            'graphData': graph_data
        }

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@count_api.route('/home/density', methods=['GET'])
def get_density_data():
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT blackList, size FROM APK')
    data = cursor.fetchall()
    conn.close()

    size_list = [int(float(row[1].split(' ')[0])) for row in data]
    black_list = [int(row[0]) for row in data]

    max_size = max(size_list)
    bin_edges = np.linspace(0, max_size, num=20)

    density_data = {
        'bin_edges': bin_edges.tolist(),
        'total_count': len(size_list),
        'density': {
            'all_apps': np.histogram(size_list, bins=bin_edges)[0].tolist(),
            'blacklisted_apps': np.histogram([size_list[i] for i in range(len(size_list)) if black_list[i] == 1], bins=bin_edges)[0].tolist()
        }
    }

    return jsonify(density_data)


@count_api.route('/home/revenue', methods=['GET'])
def get_revenue_data():
    # 获取前端传递的 md5 参数
    md5 = request.args.get('md5')

    # 连接数据库
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    try:
        if md5:
            # 如果前端传递了 md5 参数，则查询指定 md5 的数据
            cursor.execute("""
                    SELECT r.md5,
                           r.icon_sex, r.icon_gamble, r.icon_black, r.icon_scam, r.icon_white,
                           r.content_sex, r.content_gamble, r.content_black, r.content_scam, r.content_white,
                           a.black, a.gamble, a.scam, a.sex, a.white
                    FROM Result r
                    INNER JOIN APK a ON r.md5 = a.md5
                    WHERE r.md5 = ?
                """, (md5,))
        else:
            # 如果前端未传递 md5 参数，则查询所有数据
            cursor.execute("""
                    SELECT r.md5,
                           r.icon_sex, r.icon_gamble, r.icon_black, r.icon_scam, r.icon_white,
                           r.content_sex, r.content_gamble, r.content_black, r.content_scam, r.content_white,
                           a.black, a.gamble, a.scam, a.sex, a.white
                    FROM Result r
                    INNER JOIN APK a ON r.md5 = a.md5
                """)

        # 提取查询结果
        results = cursor.fetchall()

        if results:
            # 构造返回的 JSON 数据
            response_data = []
            for result in results:
                data = {
                    'md5': result[0],
                    'icon_sex': result[1],
                    'icon_gamble': result[2],
                    'icon_black': result[3],
                    'icon_scam': result[4],
                    'icon_white': result[5],
                    'content_sex': result[6],
                    'content_gamble': result[7],
                    'content_black': result[8],
                    'content_scam': result[9],
                    'content_white': result[10],
                    'black': result[11],
                    'gamble': result[12],
                    'scam': result[13],
                    'sex': result[14],
                    'white': result[15]
                }
                response_data.append(data)

            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'No data found'}), 404

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500

    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()


@count_api.route('/home/sum_count', methods=['GET'])
def get_sum_count():
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    try:
        # 查询prob不为0的数量
        cursor.execute("SELECT COUNT(*) FROM Result WHERE prob != 0")
        count_prob_not_zero = cursor.fetchone()[0]

        # 查询res为1的数量
        cursor.execute("SELECT COUNT(*) FROM Result WHERE res = 1")
        count_res_one = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "prob_not_zero_count": count_prob_not_zero,
            "res_one_count": count_res_one
        }), 200
    except Exception as e:
        print(e)

    return jsonify({"error": "An error occurred"}), 500



