import sqlite3
import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from matplotlib import rcParams

def updateGraph():
    # 连接到SQLite数据库
    conn = sqlite3.connect('./database.sqlite')
    cursor = conn.cursor()

    # 从Apk表中读出App_Name、Permissions和MD5三个字段
    cursor.execute("SELECT App_Name, Permissions, MD5, Label FROM Apk")
    rows = cursor.fetchall()

    # 读取已存储的图，如果不存在则初始化空图
    try:
        with open('./relatedGraph/graph.json', 'r') as f:
            data = json.load(f)
            G = json_graph.node_link_graph(data)
    except FileNotFoundError:
        G = nx.Graph()

    # 将数据库中的数据添加到图中
    apps = {}
    for row in rows:
        app_name = row[0]
        permissions = set(eval(row[1]))
        md5 = row[2]
        lable = row[3]
        apps[app_name] = (permissions, md5, lable)
        if app_name not in G:
            G.add_node(app_name, md5=md5, lable=lable)

    # 现有节点集合
    existing_nodes = set(G.nodes())

    # 需要更新的节点集合
    current_nodes = set(apps.keys())

    # 删除不存在的节点
    for node in existing_nodes - current_nodes:
        G.remove_node(node)

    # 添加或更新边
    for app1 in apps:
        for app2 in apps:
            if app1 != app2:
                permissions1 = apps[app1][0]
                permissions2 = apps[app2][0]
                jaccard_sim = len(permissions1 & permissions2) / len(permissions1 | permissions2)
                jaccard_sim = round(jaccard_sim, 4)  # 保留四位小数
                if jaccard_sim > 0:
                    G.add_edge(app1, app2, weight=jaccard_sim)
                elif G.has_edge(app1, app2):
                    G.remove_edge(app1, app2)

    # 将更新后的图保存为JSON文件，格式化为结构化的多行JSON
    data = json_graph.node_link_data(G)
    with open('./relatedGraph/graph.json', 'w') as f:
        json.dump(data, f, indent=4)

    # visualizeGraph(G)
    # 关闭数据库连接
    conn.close()


def visualizeGraph(G):
    # 设置matplotlib中文字体
    rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

    # 绘制图
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)  # 选择一种布局方式
    nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=10, font_weight="bold")
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("App Permissions Graph")
    plt.show()


def getGraphData():
    # 读取图数据
    try:
        with open('./relatedGraph/graph.json', 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {"message": "Graph data not found"}


def getSubGraph(md5):
    # 读取图数据
    try:
        with open('./relatedGraph/graph.json', 'r') as f:
            data = json.load(f)
            G = json_graph.node_link_graph(data)
    except FileNotFoundError:
        return {"message": "Graph data not found"}

    # 找到与指定MD5对应的节点
    target_node = None
    for node, attrs in G.nodes(data=True):
        if attrs.get('md5') == md5:
            target_node = node
            break

    if not target_node:
        return {"message": "MD5 not found in graph"}

    # 找到与目标节点相连的一阶子图
    subgraph = {}
    for neighbor in G.neighbors(target_node):
        neighbor_md5 = G.nodes[neighbor]['md5']
        subgraph[neighbor_md5] = (G[target_node][neighbor]['weight'], G.nodes[neighbor]['lable'], neighbor)

    return subgraph


# # 示例用法
# if __name__ == "__main__":
#     md5 = '3dacdd95621ce98e27a4a495752de86e'  # 示例MD5值
#     subgraph = getSubGraph(md5)
#     print(subgraph)
