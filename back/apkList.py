from flask import Blueprint, request, jsonify, abort
import sqlite3


apk = Blueprint('apk', __name__)


def get_db_connection():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# apk列表中的数据
@apk.route('/apk_data', methods=['GET'])
def get_apk_data():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    conn = get_db_connection()
    apk_data = conn.execute('SELECT App_Name, MD5, Package_Name, Label FROM Apk').fetchall()
    result_data = conn.execute('SELECT MD5, prob, res, model FROM Result').fetchall()
    conn.close()
    result_data = [
        {
            'MD5': row['MD5'],
            'prob': round(row['prob'], 4),
            'res': row['res'],
            'model': row['model']
        }
        for row in result_data
    ]

    # Merge data from both tables
    combined_data = []
    for apk in apk_data:
        apk_dict = dict(apk)
        for result in result_data:
            if result['MD5'] == apk['MD5']:
                apk_dict.update(result)
                break
        else:
            # If no matching result found, set default values
            apk_dict.update({'prob': 0, 'res': -1, 'model': '未检测'})
        combined_data.append(apk_dict)

    # Pagination logic
    total = len(combined_data)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = combined_data[start:end]

    return jsonify({
        'data': paginated_data,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total // per_page) + (1 if total % per_page > 0 else 0)
    })


@apk.route('/delete_apk', methods=['POST'])
def delete_apk():
    data = request.get_json()
    if 'md5' not in data:
        return jsonify({'message': 'Missing MD5 in request body'}), 400

    md5 = data['md5']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM Apk WHERE MD5 = ?', (md5,))
        cursor.execute('DELETE FROM IP WHERE MD5 = ?', (md5,))
        cursor.execute('DELETE FROM Result WHERE MD5 = ?', (md5,))
        conn.commit()
        return jsonify({'message': f'APK record with MD5 {md5} deleted successfully'}), 200
    except Exception as e:
        print(str(e))
        conn.rollback()
        return jsonify({'message': 'Failed to delete APK record'}), 500
    finally:
        conn.close()


