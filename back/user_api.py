import re
import sqlite3
import requests
from flask import Blueprint, request, jsonify, make_response

user_api = Blueprint('user_api', __name__)

# 连接数据库的函数
def connect_db():
    conn = sqlite3.connect('database.sqlite')
    return conn

# 注册接口
@user_api.route('/register', methods=['POST'])
def register():
    conn = connect_db()
    cursor = conn.cursor()
    print(request.json)

    uname = request.json.get('uname')
    pwd = request.json.get('pwd')
    uemail = request.json.get('uemail')

    # 检查用户名是否为空
    if not uname:
        return jsonify({'msg': '用户名不能为空'})

    # 查询用户名是否已经存在
    cursor.execute("SELECT * FROM User WHERE Uname=?", (uname,))
    user = cursor.fetchone()

    if user:
        return jsonify({'msg': '用户名已存在'}), 400  # 返回 400 Bad Request 状态码

    # 插入新用户
    cursor.execute("INSERT INTO User (Uname, Upassword, Uemail) VALUES (?, ?, ?)", (uname, pwd, uemail))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'msg': '注册成功'}), 200  # 返回 200 OK 状态码


# 登录接口
@user_api.route('/login', methods=['POST'])
def login():
    conn = connect_db()
    cursor = conn.cursor()
    print(request.json)

    uname = request.json.get('uname')
    pwd = request.json.get('pwd')

    # 查询用户
    cursor.execute("SELECT * FROM User WHERE Uname=? AND Upassword=?", (uname, pwd))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        response = make_response(jsonify({'msg': '登录成功'}), 200)
        response.set_cookie('uname', uname)
        return response
    else:
        return jsonify({'msg': '用户名或密码错误'}), 400

# 重置密码发送邮箱接口
@user_api.route('/find', methods=['POST'])
def find():
    # 获取邮箱
    uemail = request.json.get('uemail')
    if not uemail:
        return jsonify({'msg': '邮箱不能为空'}), 400

    # 验证邮箱格式
    if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', uemail):
        return jsonify({'msg': '邮箱格式错误'}), 400

    # 发送邮件
    # 这里应该调用发送邮件的函数，这里只是模拟发送邮件
    # send_email(uemail)

    return jsonify({'msg': '邮箱发送成功'}), 200