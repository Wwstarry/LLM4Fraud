from flask import Flask
import subprocess
from flask_cors import CORS

from offline import offline
from dynamicAnalize import dynamic
from ip_api import ip_api
from user_api import user_api
from detectAgents import detectAgents  # 导入接口Blueprint
from reportAgents import reportAgents
from uploadFiles import uploadFiles  # 导入上传文件Blueprint
from apkList import apk
from whiteSetting_api import whiteSetting_api
from report_api import report_api
from count_api import count_api
from chatbotAgents import chatbot

ADB = "adb/adb.exe"


app = Flask(__name__)
CORS(app)

# 注册接口Blueprint
app.register_blueprint(detectAgents)
app.register_blueprint(uploadFiles)
app.register_blueprint(apk)
app.register_blueprint(ip_api)
app.register_blueprint(user_api)
app.register_blueprint(reportAgents)
app.register_blueprint(count_api)
app.register_blueprint(whiteSetting_api)
app.register_blueprint(report_api)
app.register_blueprint(chatbot)
app.register_blueprint(dynamic)
app.register_blueprint(offline)

subprocess.run([ADB, 'kill-server'], check=True)
subprocess.run([ADB, 'start-server'], check=True)
subprocess.run([ADB, 'connect', '127.0.0.1:62001'], check=True)

if __name__ == '__main__':
    app.run(debug=False)
