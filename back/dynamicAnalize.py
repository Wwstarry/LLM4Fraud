import sqlite3

from flask import jsonify
import subprocess
import base64

from flask import Blueprint, request

dynamic = Blueprint('dynamic', __name__)
ADB = "adb/adb.exe"


# Route for executing ADB commands
@dynamic.route('/execute-command', methods=['POST'])
def execute_command():
    command = request.json.get('cmd')
    try:
        # 打印执行的命令
        print(f"Executing command: adb shell {command}")
        result = subprocess.run([ADB, 'shell'] + command.split(), check=True, capture_output=True, text=True)
        return jsonify({'output': result.stdout})
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500


@dynamic.route('/getScreen', methods=['POST'])
def capture_screen():
    try:
        # 执行截图命令，将截图保存到设备存储
        subprocess.run([ADB, 'shell', 'screencap', '/sdcard/screen.png'], check=True)
        # 将截图从设备存储拉取到服务器
        subprocess.run([ADB, 'pull', '/sdcard/screen.png', 'adb/screen.png'], check=True)
        # 读取截图文件
        with open('adb/screen.png', 'rb') as image_file:
            frame = image_file.read()
            encoded_frame = base64.b64encode(frame).decode('utf-8')
            return jsonify({'frame': encoded_frame})
    except subprocess.CalledProcessError as e:
        subprocess.run([ADB, 'connect', '127.0.0.1:62001'], check=True)
        print(f"CalledProcessError: {e.stderr.decode('utf-8')}")
    except Exception as e:
        subprocess.run([ADB, 'connect', '127.0.0.1:62001'], check=True)
        print(f"Exception: {e}")


@dynamic.route('/click', methods=['POST'])
def handle_click():
    data = request.get_json()
    x = data['x']
    y = data['y']
    try:
        subprocess.run([ADB, 'shell', 'input', 'tap', str(x), str(y)], check=True)
        return jsonify({'status': 'success'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to execute click: {e}'}), 500

@dynamic.route('/install', methods=['POST'])
def handle_install():
    data = request.get_json()
    md5 = data['md5']
    try:
        app_path = f'uploads/{md5}.apk'
        subprocess.run([ADB, 'install', app_path], check=True)
        return jsonify({'status': 'success'})

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to install app: {e}'}), 500

@dynamic.route('/input-text', methods=['POST'])
def handle_input_text():
    data = request.get_json()
    text = data['text']
    try:
        subprocess.run([ADB, 'shell', 'input', 'text', text], check=True)
        return jsonify({'status': 'success'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to input text: {e}'}), 500

@dynamic.route('/keyevent', methods=['POST'])
def handle_keyevent():
    data = request.get_json()
    keycode = data['keycode']
    try:
        subprocess.run([ADB, 'shell', 'input', 'keyevent', str(keycode)], check=True)
        return jsonify({'status': 'success'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to execute keyevent: {e}'}), 500

@dynamic.route('/apps', methods=['GET'])
def get_apps():
    try:
        conn = sqlite3.connect('database.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT App_Name, MD5 FROM Apk")
        apps = cursor.fetchall()
        conn.close()
        return jsonify(apps)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic.route('/systemlogs', methods=['GET'])
def get_logs():
    try:
        result = subprocess.run([ADB, 'logcat', '-d'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', check=True)
        logs = result.stdout
        return jsonify({'logs': logs})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to get logs: {e}'}), 500
    except UnicodeDecodeError as e:
        return jsonify({'error': f'UnicodeDecodeError: {e}'}), 500


@dynamic.route('/permissions/<package_name>', methods=['GET'])
def get_permissions(package_name):
    try:
        result = subprocess.run([ADB, 'shell', 'dumpsys', 'package', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', check=True)
        permissions = result.stdout
        return jsonify({'permissions': permissions})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to get permissions for package {package_name}: {e}'}), 500
    except UnicodeDecodeError as e:
        return jsonify({'error': f'UnicodeDecodeError: {e}'}), 500


