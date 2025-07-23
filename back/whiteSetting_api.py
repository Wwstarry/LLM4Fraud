from flask import Blueprint, jsonify, request
import sqlite3

whiteSetting_api = Blueprint('whiteSetting_api', __name__)

def get_db_connection():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

@whiteSetting_api.route('/get_blackList', methods=['GET'])
def get_blackList():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT MD5, App_Name, Package_Name, size, Label, blackList FROM Apk')
        apk_data = cursor.fetchall()

        cursor.execute('SELECT MD5, prob FROM Result')
        result_data = cursor.fetchall()

        blackList = []
        for apk in apk_data:
            apk_dict = dict(apk)
            for result in result_data:
                if result['MD5'] == apk['MD5']:
                    apk_dict['prob'] = round(result['prob'], 4)
                    break
            else:
                # If no matching result found, set default prob value
                apk_dict['prob'] = '未检测'

            blackList.append(apk_dict)

        return jsonify(blackList), 200

    except Exception as e:
        print(str(e))
        return jsonify({'message': 'Failed to retrieve blackList data'}), 500
    finally:
        conn.close()


# 增加接口更新对应MD5的blackList的值
@whiteSetting_api.route('/update_blackList', methods=['POST'])
def update_blackList():
    data = request.get_json()
    if 'md5' not in data or 'blackList' not in data:
        return jsonify({'message': 'Missing MD5 or blackList in request body'}), 400

    md5 = data['md5']
    blackList = data['blackList']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE Apk SET blackList = ? WHERE MD5 = ?', (blackList, md5))
        conn.commit()
        return jsonify({'message': f'blackList updated successfully for MD5: {md5}'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'message': f'Failed to update blackList for MD5: {md5}'}), 500
    finally:
        conn.close()


# 增加接口增加记录到Apk表
# 前端返回的数据格式为：
#     md5: set_md5.value,
#     name: set_name.value,
#     pack: set_pack.value,
#     cate: set_cate.value,
#     size: set_size.value,
#     blackList: 1,
@whiteSetting_api.route('/addBlack', methods=['POST'])
def add_black():
    data = request.get_json()
    if 'md5' not in data or 'name' not in data or 'pack' not in data or 'cate' not in data or 'size' not in data:
        return jsonify({'message': 'Missing required fields in request body'}), 400

    md5 = data['md5']
    name = data['name']
    pack = data['pack']
    cate = data['cate']
    size = data['size']
    blackList = data['blackList']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO Apk (MD5, App_Name, Package_Name, Label, size, blackList) VALUES (?, ?, ?, ?, ?, ?)',
                       (md5, name, pack, cate, size, blackList))
        conn.commit()
        return jsonify({'message': f'APK record with MD5 {md5} added successfully'}), 200
    except Exception as e:
        print(str(e))
        conn.rollback()
        return jsonify({'message': 'Failed to add APK record'}), 500
    finally:
        conn.close()