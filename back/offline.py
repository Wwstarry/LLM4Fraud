from flask import Blueprint, request, jsonify, abort
import sqlite3


offline = Blueprint('offline', __name__)


def get_db_connection():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

@offline.route('/off_data', methods=['GET'])
def get_apk_data():
    md5 = request.args.get('md5')

    if not md5:
        abort(400, description="MD5 parameter is required")

    conn = get_db_connection()
    apk_data = conn.execute('SELECT App_Name, MD5, Package_Name, Label FROM Apk WHERE MD5 = ?', (md5,)).fetchone()
    result_data = conn.execute('SELECT MD5, prob, res, model FROM Result WHERE MD5 = ?', (md5,)).fetchone()
    conn.close()

    if apk_data is None:
        abort(404, description="No data found for the given MD5")

    apk_dict = dict(apk_data)
    if result_data:
        apk_dict.update({
            'prob': round(result_data['prob'], 4),
            'res': result_data['res'],
            'model': result_data['model']
        })
    else:
        apk_dict.update({'prob': 0, 'res': -1, 'model': '未检测'})

    return jsonify({
        'data': [apk_dict],
        'page': 1,
        'per_page': 1,
        'total': 1,
        'total_pages': 1
    })