import asyncio
import json
import os
import sqlite3
from collections import Counter

from flask import Blueprint, request, jsonify, abort, send_file

from permissionAgents import query_permission
from relatedGraph.graphConstruction import updateGraph, getGraphData

report_api = Blueprint('report_api', __name__)

# 将连接数据库的函数提取出来
def get_db_connection():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# 给出接口，根据前端的md5返回Apk表的所有信息
@report_api.route('/report/info', methods=['GET'])
def get_apk_info():
    md5 = request.args.get('md5')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM Apk WHERE MD5=?', (md5,))
        apk_data = cursor.fetchone()
        if apk_data is None:
            return jsonify({'message': 'MD5 not found'}), 404

        cursor.execute('SELECT * FROM Result WHERE MD5=?', (md5,))
        result_data = cursor.fetchone()
        if result_data is None:
            return jsonify({'message': 'Result not found'}), 404

        cursor.execute('SELECT * FROM IP WHERE MD5=?', (md5,))
        ip_data = cursor.fetchone()
        if ip_data is None:
            return jsonify({'message': 'IP not found'}), 404

        cursor.execute('SELECT black, gamble, sex, scam, white FROM Apk WHERE MD5 = ?', (md5,))
        row = cursor.fetchone()

        if row:
            # 构建权限概率数据
            probability = [
                {'name': 'black', 'value': row['black']},
                {'name': 'gamble', 'value': row['gamble']},
                {'name': 'sex', 'value': row['sex']},
                {'name': 'scam', 'value': row['scam']},
                {'name': 'white', 'value': row['white']},
            ]
            result = {
                'apk_data': dict(apk_data),
                'result_data': dict(result_data),
                'ip_data': dict(ip_data),
                'probability': probability
            }
            return jsonify(result), 200

    except Exception as e:
        print(str(e))
        return jsonify({'message': 'Failed to retrieve apk info'}), 500
    finally:
        conn.close()

# 定义接口路由，接收MD5参数
@report_api.route('/get_permissions', methods=['GET'])
def get_permissions():
    md5_value = request.args.get('md5')  # 获取前端传递的MD5值参数

    if not md5_value:
        pack = request.args.get('pack')
        if pack:
            # 连接数据库
            conn = get_db_connection()
            cursor = conn.cursor()
            # 查询Apk表中指定MD5值的权限列表
            cursor.execute('SELECT MD5 FROM Apk WHERE Package_Name = ?;', (pack,))
            row = cursor.fetchone()
            if row:
                md5_value = row['MD5']
            else:
                return jsonify({'error': 'Package not found.'}), 404
            conn.close()
        else:
            return jsonify({'error': 'MD5 value is required.'}), 400

    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询Apk表中指定MD5值的权限列表
        cursor.execute('SELECT Permissions FROM Apk WHERE MD5 = ?;', (md5_value,))
        row = cursor.fetchone()

        if row and row['Permissions']:
            try:
                permissions_str = row['Permissions']
                permissions_list = eval(permissions_str)  # 解析为Python列表

                # 查询Permission表中每个权限的详细信息
                detailed_permissions = []
                risk_counter = Counter()
                risk_counter[2] = 0
                risk_counter[1] = 0
                risk_counter[0] = 0

                missing = []
                for permission in permissions_list:
                    cursor.execute('''
                        SELECT permission, risk, name, detail FROM Permission WHERE permission = ?;
                    ''', (permission,))
                    perm_row = cursor.fetchone()
                    if perm_row:
                        perm_dict = {
                            'permission': perm_row['permission'],
                            'risk': perm_row['risk'],
                            'name': perm_row['name'],
                            'detail': perm_row['detail'],
                        }
                        detailed_permissions.append(perm_dict)
                        risk_counter[perm_row['risk']] += 1
                    else:
                        missing.append(permission)

                if missing:
                    index = asyncio.run(get_missing(missing))  # 调用异步函数
                    for i, permission in enumerate(missing):
                        if index[i]:
                            cursor.execute('''
                                SELECT permission, risk, name, detail FROM Permission WHERE permission = ?;
                            ''', (permission,))
                            perm_row = cursor.fetchone()
                            if perm_row:
                                perm_dict = {
                                    'permission': perm_row['permission'],
                                    'risk': perm_row['risk'],
                                    'name': perm_row['name'],
                                    'detail': perm_row['detail'],
                                }
                                detailed_permissions.append(perm_dict)
                                risk_counter[perm_row['risk']] += 1

                # 将计数器转换为字典格式
                risk_counts = dict(risk_counter)
                # 关闭数据库连接
                conn.close()
                # 格式化为JSON并返回给前端
                return jsonify({
                    'detailed_permissions': detailed_permissions,
                    'risk_counts': risk_counts
                })

            except Exception as e:
                # 关闭数据库连接
                conn.close()
                return jsonify({'error': 'Failed to decode JSON data.'}), 500

        else:
            conn.close()
            return jsonify({'error': f'No permissions found for MD5: {md5_value}'}), 404

    except sqlite3.Error as e:
        return jsonify({'error': f'SQLite error: {str(e)}'}), 500



async def get_missing(missing):
    tasks = [
        query_permission(permission) for permission in missing
    ]
    results = await asyncio.gather(*tasks)
    return results

# 访问图片资源的接口
@report_api.route('/icon/<path:img_path>', methods=['GET'])
def get_image(img_path):
    # 拼接图片存储的基本路径，确保安全性
    base_path = './icon'  # 替换成实际的图片存储路径
    full_path = os.path.join(base_path, img_path)
    # 验证路径是否存在，不存在则返回404
    if not os.path.exists(full_path):
        abort(404)
    try:
        # 使用send_file直接发送文件，不需要手动处理内容和响应头
        return send_file(full_path, mimetype='image/png')
    except Exception as e:
        # 发生错误时返回适当的错误信息
        return str(e), 500


# 定义接口路由，根据md5值返回source或target等于该md5下的名字下的所有边
@report_api.route('/report/get_edges', methods=['GET'])
def get_edges():
    md5_value = request.args.get('md5')
    if md5_value is None:
        return jsonify({'error': 'MD5 value is required.'}), 400
    # else:
    #     conn = get_db_connection()
    #     cursor = conn.cursor()
    #     # 根据md5查App_Name
    #     cursor.execute('SELECT App_Name FROM Apk WHERE MD5 = ?;', (md5_value,))
    #     row = cursor.fetchone()
    #     if row is None:
    #         return jsonify({'error': 'MD5 value not found.'}), 404
    #     app_name = row['App_Name']
    #     # 关闭数据库连接
    #     conn.close()
    #     # 从图数据中查找所有边
    #     edges = []
    #     for edge in graph_data['links']:
    #         if edge['source'] == app_name or edge['target'] == app_name:
    #             edges.append(edge)
    #     return jsonify(edges), 200
    else:
        graph_data = getGraphData()
        return jsonify({
            'graphData': graph_data,
        }), 200


