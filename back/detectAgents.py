from flask import Blueprint, request, jsonify

from relatedGraph.graphConstruction import updateGraph

detectAgents = Blueprint('detectAgents', __name__)
import os

os.environ["OPENAI_API_KEY"] = "sk-INXANUofc0XdCz4Q88C47aB7Aa6541AfAbE294673e1fE71d"
os.environ["OPENAI_API_BASE"] = "https://api.b3n.fun/v1"


# os.environ["OPENAI_API_KEY"] = ""
# os.environ["OPENAI_API_BASE"] = ""

# os.environ["OPENAI_API_KEY"] = ""
# os.environ["OPENAI_API_BASE"] = ""



from agent.detect_prompts import *
from agent.detect_tools import *

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

import functools
import operator
from typing import Sequence, TypedDict

from langgraph.graph import END, StateGraph

from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# MODEL_NAME = "gpt-4o-mini-2024-07-18"

MODEL_NAME = "gpt-4o-2024-08-06"

def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}

def create_workflow(md5):
    # 设置初始状态，包括用户提示词
    user_prompt = """
    Please analyze the APK with the following details:
    - MD5: {md5}
    Identify as much as possible which category of the APK belongs to the following:
    ['black' 'gamble' 'scam' 'sex' 'white']
    """.format(md5=md5)
    initial_state = {
        "messages": [HumanMessage(content=user_prompt, name="user")],
        "next": "supervisor"
    }

    members = ["APP_Package_Tracer", "Sensitive_Info_Analizer", 'Certificate_Inspector', "Relationship_Analizer",
               'Icon_Analizer', 'Content_Analizer']
    # members = ["APP_Package_Tracer"]
    # Our team supervisor is an LLM node. It just picks the next agent to process
    # and decides when the work is completed
    options = ["Decision"] + members
    # Using openai function calling can make output parsing easier for us
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                }
            },
            "required": ["next"],
        },
    }

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", supervisor_system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), members=", ".join(members))

    llm = ChatOpenAI(model=MODEL_NAME, temperature=0.95)

    supervisor_chain = (
            prompt
            | llm.bind_functions(functions=[function_def], function_call="route")
            | JsonOutputFunctionsParser()
    )

    # The agent state is the input to each node in the graph
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]

        black: float
        gamble: float
        scam: float
        sex: float
        white: float
        label: str
        next: str

    APP_Package_Tracer = create_agent(llm, [get_package_name, get_name, get_activaties], APP_Package_Tracer_system_prompt)
    APP_Package_Tracer_node = functools.partial(agent_node, agent=APP_Package_Tracer, name="APP_Package_Tracer")

    # NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION. PROCEED WITH CAUTION
    Sensitive_Info_Analizer = create_agent(llm, [get_activaties, get_service_reciver, get_permissions], Sensitive_Info_Analizer_system_prompt)
    Sensitive_Info_Analizer_node = functools.partial(agent_node, agent=Sensitive_Info_Analizer,
                                                     name="Sensitive_Info_Analizer")

    Certificate_Inspector = create_agent(llm, [get_certificate], Certificate_Inspector_system_prompt)
    Certificate_Inspector_node = functools.partial(agent_node, agent=Certificate_Inspector,
                                                     name="Certificate_Inspector")

    Icon_Analizer = create_agent(llm, [get_icon_prob], Icon_Analizer_system_prompt)
    Icon_Analizer_node = functools.partial(agent_node, agent=Icon_Analizer,
                                                     name="Icon_Analizer")

    Content_Analizer = create_agent(llm, [get_content_prob], Content_Analizer_system_prompt)
    Content_Analizer_node = functools.partial(agent_node, agent=Content_Analizer,
                                                     name="Content_Analizer")

    Relationship_Analizer = create_agent(llm, [get_relation, get_permissions], Relationship_Analizer_system_prompt)
    Relationship_Analizer_node = functools.partial(agent_node, agent=Relationship_Analizer,
                                                     name="Relationship_Analizer")


    json_schema = {
        "title": "Classifier",
        "description": "Classify the apk into 5 classes.",
        "type": "object",
        "properties": {
            "label": {
                "type": "string",
                "description": "The final judgment of the app, tag with the largest probability of use.",
            },
            "black": {
                "type": "number",
                "description": "The probability of the app belongs to Class 'black.",
            },
            "gamble": {
                "type": "number",
                "description": "The probability of the app belongs to Class 'gamble.",
            },
            "scam": {
                "type": "number",
                "description": "The probability of the app belongs to Class 'scam.",
            },
            "sex": {
                "type": "number",
                "description": "The probability of the app belongs to Class 'sex.",
            },
            "white": {
                "type": "number",
                "description": "The probability of the app belongs to Class 'white.",
            },
        },
        "required": ["label", "black", "gamble", "scam", "sex", "white"],
    }

    model = ChatOpenAI(model=MODEL_NAME, temperature=0)

    Decision_Maker = ChatPromptTemplate.from_messages(
        [
            ("system", Decision_Maker_system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ('user', "You should combine the output results of Vision model, Text model and your evaluation of the APP "
                     "information to give a comprehensive probability, rather than just outputting the probability of "
                     "one model."),
            ('user', "You must control each probability between 0 and 1, and the sum of the probabilities of all is 1"),
        ]
    ) | model.bind_functions(functions=[json_schema], function_call="Classifier") | JsonOutputFunctionsParser()



    print("构建workflow")
    workflow = StateGraph(AgentState)
    workflow.add_node("APP_Package_Tracer", APP_Package_Tracer_node)
    workflow.add_node("Sensitive_Info_Analizer", Sensitive_Info_Analizer_node)
    workflow.add_node("Certificate_Inspector", Certificate_Inspector_node)
    workflow.add_node("Icon_Analizer", Icon_Analizer_node)
    workflow.add_node("Content_Analizer", Content_Analizer_node)
    workflow.add_node("supervisor", supervisor_chain)
    workflow.add_node("Decision_Maker", Decision_Maker)
    workflow.add_node("Relationship_Analizer", Relationship_Analizer_node)

    for member in members:
        # We want our workers to ALWAYS "report back" to the supervisor when done
        workflow.add_edge(member, "supervisor")
    # The supervisor populates the "next" field in the graph state
    # which routes to a node or finishes
    conditional_map = {k: k for k in members}
    conditional_map["Decision"] = "Decision_Maker"
    workflow.add_edge("Decision_Maker", END)
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    # Finally, add entrypoint
    workflow.set_entry_point("supervisor")


    print("编译工作流")
    graph = workflow.compile()
    work_res = {}
    chat_log=[]
    print("调用agent")
    for s in graph.stream(initial_state):
        if "__end__" not in s:
            try:
                print(s)
                print("----")
                work_res = s
                chat_log.append(s)
            except:
                work_res = s
                chat_log.append(s)


    work_res = work_res['Decision_Maker']
    result_dic={
        "black": work_res["black"],
        "gamble": work_res["gamble"],
        "scam": work_res["scam"],
        "sex": work_res["sex"],
        "white": work_res["white"],
        "label": work_res["label"],
    }

    print(result_dic)
    return result_dic, chat_log


@detectAgents.route('/detect', methods=['POST'])
def detect():
    data = request.get_json()
    if 'md5' not in data:
        return jsonify({'message': 'Missing MD5 in request body'}), 400

    md5 = data['md5']
    result, chat_log = create_workflow(md5)
    conversation_dict = extract_and_map_conversation(chat_log)
    conversation_dict['MD5'] = md5

    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()

    # 将非基本数据类型转换为字符串
    for key, value in result.items():
        if isinstance(value, (list, dict, set, tuple)):
            result[key] = str(value)

    # 准备更新Apk表的SQL语句
    set_clause = ', '.join([f"{key} = ?" for key in result.keys()])
    sql = f"UPDATE Apk SET {set_clause} WHERE MD5 = ?"
    # 执行更新操作
    cursor.execute(sql, list(result.values()) + [md5])
    # 提交事务
    conn.commit()

    # 准备更新Result表的SQL语句
    sql = "UPDATE Result SET prob=?, res=?  WHERE MD5 = ?"
    # 执行更新操作
    cursor.execute(sql, [1 - result['white'], 0 if result['label'] == "white" else 1, md5])
    # 提交事务并关闭连接
    conn.commit()

    sql = "UPDATE Apk SET Label=?  WHERE MD5 = ?"
    cursor.execute(sql, [result['label'], md5])
    conn.commit()

    placeholders = ', '.join(['?'] * len(conversation_dict))
    columns = ', '.join(conversation_dict.keys())
    updates = ', '.join([f"{col} = EXCLUDED.{col}" for col in conversation_dict.keys()])

    sql = f"""
    INSERT INTO ChatHistory ({columns}) 
    VALUES ({placeholders}) 
    ON CONFLICT(MD5) DO UPDATE 
    SET {updates}
    """

    cursor.execute(sql, list(conversation_dict.values()))
    conn.commit()

    cursor.close()
    conn.close()
    updateGraph()

    return jsonify({'message': 'Detection completed successfully'}), 200


def extract_and_map_conversation(history):
    key_mapping = {
        'Sensitive_Info_Analizer': 'SensitiveInfoAnalizer',
        'Icon_Analizer': 'IconAnalizer',
        'Content_Analizer': 'ContentAnalizer',
        'Certificate_Inspector': 'CertificateInspector',
        'APP_Package_Tracer': 'PackageTracer',
        'Relationship_Analizer': 'RelationshipAnalizer'
    }
    result = {}
    for item in history:
        for key, value in item.items():
            if key not in ['supervisor', 'Decision']:
                new_key = key_mapping.get(key, key)
                messages = value.get('messages', "")
                for message in messages:
                    if new_key not in result:
                        result[new_key] = ""
                    result[new_key] += (message.content)
    return result




def query_chat_history(md5):
    conn = sqlite3.connect('database.sqlite')
    cur = conn.cursor()
    cur.execute('''
    SELECT SensitiveInfoAnalizer, IconAnalizer, ContentAnalizer, CertificateInspector, PackageTracer, RelationshipAnalizer
    FROM ChatHistory
    WHERE md5 = ?
    ''', (md5,))
    row = cur.fetchone()
    conn.close()
    return row


@detectAgents.route('/api/chat-messages', methods=['GET'])
def get_chat_messages():
    md5 = request.args.get('md5')
    if not md5:
        return jsonify({'error': 'md5 parameter is required'}), 400

    row = query_chat_history(md5)
    if row:
        response = {
            'leftChats': [
                row[4] if row[4] is not None else '',
                row[0] if row[0] is not None else '',
                row[3] if row[3] is not None else ''
            ],
            'rightChats': [
                row[1] if row[1] is not None else '',
                row[2] if row[2] is not None else '',
                row[5] if row[5] is not None else ''
            ]
        }
        return jsonify(response)
    else:
        return jsonify({'error': 'No chat history found for the provided md5'}), 404

# if __name__ == '__main__':
    # history = [{'supervisor': {'next': 'APP_Package_Tracer'}}, {'APP_Package_Tracer': {'messages': [HumanMessage(content='Based on the provided details and the retrieved information about the APK, here is the analysis:\n\n1. **Package Name**: `com.hebu.hbcar`\n2. **App Name**: `i智行`\n3. **Main Activity**: `com.hebu.hbcar.activitys.SplashActivity`\n4. **Activities**: Various activities related to car functionalities, navigation, settings, user login, and device management.\n\n### Analysis:\n- The package name `com.hebu.hbcar` suggests a focus on car-related functionalities.\n- The app name `i智行` translates to "i Smart Navigation" or "i Smart Travel".\n- The activities within the app include functionalities for navigation, car settings, user login, device management, location-based services, and statistics.\n\nGiven these details, the APK appears to be associated with intelligent car navigation or a smart car management system.\n\n### Conclusion:\nThe category of this APK is likely to be **\'white\'** as it seems to be a legitimate application related to smart car navigation and management. There are no obvious indicators that suggest it falls into categories such as \'black\', \'gamble\', \'scam\', or \'sex\'.', name='APP_Package_Tracer')]}}, {'supervisor': {'next': 'Sensitive_Info_Analizer'}}, {'Sensitive_Info_Analizer': {'messages': [HumanMessage(content="Based on the obtained details, here is the comprehensive analysis of the APK:\n\n### Main Activity and Activities:\n- **Main Activity**: `com.hebu.hbcar.activitys.SplashActivity`\n- **Activities**: \n  - `com.hebu.hbcar.activitys.LocusActivity`\n  - `com.hebu.hbcar.activitys.OTAToolsActivity`\n  - `com.hebu.hbcar.activitys.LampActivity`\n  - `com.hebu.hbcar.activitys.MainActivity`\n  - `com.hebu.hbcar.activitys.GuideLoginActivity`\n  - `com.hebu.hbcar.activitys.LoginActivity`\n  - `com.hebu.hbcar.activitys.SettingActivity`\n  - `com.hebu.hbcar.activitys.RegisterActivity`\n  - `com.hebu.hbcar.activitys.MainActivityTest`\n  - `com.amap.api.navi.AmapRouteActivity`\n  - `com.hebu.hbcar.activitys.CyclingStatisticsActivity`\n  - `com.hebu.hbcar.activitys.NaviActivity`\n  - `com.hebu.hbcar.activitys.BaseNaviActivity`\n  - `com.hebu.hbcar.activitys.SplashActivity`\n  - `com.hebu.hbcar.activitys.DeviceMsgActivity`\n  - `com.hebu.hbcar.activitys.PickProofSettingActivity`\n  - `com.hebu.hbcar.activitys.ElectronicFenceActivity`\n  - `com.hebu.hbcar.activitys.AddFenceActivity`\n  - `com.hebu.hbcar.activitys.ItineraryReportActivity`\n  - `com.hebu.hbcar.activitys.ItineraryDetailsActivity`\n  - `com.hebu.hbcar.activitys.BindingDeviceActivity`\n  - `com.hebu.hbcar.activitys.SafeAreaActivity`\n  - `com.hebu.hbcar.activitys.AddSafeAreaActivity`\n  - `com.hebu.hbcar.activitys.ShowMarkActivity`\n  - `com.hebu.hbcar.activitys.PermissActivity`\n  - `com.hebu.hbcar.activitys.LogoActivity`\n  - `com.hebu.hbcar.activitys.AddCarActivity`\n  - `com.hebu.hbcar.activitys.BtSetActivity`\n  - `com.hebu.hbcar.activitys.CarSetActivity`\n  - `com.hebu.hbcar.activitys.BindHiniActivity`\n  - `com.hebu.hbcar.activitys.WebViewActivity`\n  - `cn.jpush.android.ui.PopWinActivity`\n  - `cn.jpush.android.ui.PushActivity`\n  - `cn.jpush.android.service.JNotifyActivity`\n  - `cn.android.service.JTransitActivity`\n  - `com.huawei.hms.support.api.push.TransActivity`\n  - `com.huawei.hms.activity.BridgeActivity`\n  - `com.huawei.hms.activity.EnableServiceActivity`\n\n### Services and Receivers:\n- **Services**:\n  - `com.hebu.hbcar.jgpush.JGServer`\n  - `com.hebu.hbcar.jgpush.JGReceiver`\n  - `com.hebu.hbcar.service.BleService`\n  - `com.amap.api.location.APSService`\n  - `com.hebu.unistepnet.main.LinkService`\n  - `com.hebu.hbcar.service.UpdateService`\n  - `com.hebu.hbcar.service.DisPlayService`\n  - `cn.jpush.android.service.PushService`\n  - `com.huawei.hms.support.api.push.service.HmsMsgService`\n  - `com.huawei.agconnect.core.ServiceDiscovery`\n  - `cn.jpush.android.service.PluginHuaweiPlatformsService`\n\n- **Receivers**:\n  - `cn.jpush.android.service.PushReceiver`\n  - `cn.jpush.android.service.AlarmReceiver`\n  - `cn.jpush.android.service.SchedulerReceiver`\n  - `cn.jpush.android.asus.AsusPushMessageReceiver`\n  - `com.huawei.hms.support.api.push.PushMsgReceiver`\n  - `com.huawei.hms.support.api.push.PushReceiver`\n\n### Permissions:\n- Permissions related to Bluetooth, location, internet, notifications, and storage, among other typical app functionalities.\n\n### Analysis:\n1. **Activities**: The wide range of activities shows functionalities related to:\n   - Navigation\n   - User login and registration\n   - Device management\n   - Settings configuration\n   - Location services\n   - Statistics and reporting\n\n2. **Services and Receivers**: The app leverages push notifications through services like JPush and Huawei Push. There are also services for Bluetooth, updates, and location tracking.\n\n3. **Permissions**: The permissions requested align with the functionalities observed:\n   - Location permissions for navigation and tracking.\n   - Bluetooth permissions for connectivity.\n   - Storage permissions for reading and writing data.\n   - Internet permissions for network activities.\n   - Notification permissions for sending push notifications.\n\n### Conclusion:\nBased on the examination of the activities, services, receivers, and permissions:\nThe APK falls into the **'white'** category. Its functionalities and permissions suggest it is a legitimate application related to smart car navigation and management. There are no indicators of fraudulent or criminal activities typically associated with 'black', 'gamble', 'scam', or 'sex' categories.", name='Sensitive_Info_Analizer')]}}, {'supervisor': {'next': 'Certificate_Inspector'}}, {'Certificate_Inspector': {'messages': [HumanMessage(content='### Certificate Information\n- **SHA1**: 24aea229d24adb8554d330aaf0694de4c2810921\n- **SHA256**: c9c71ed75972f83940101ac1c026bf96d916afc4d82133d21d752df3d705e75e\n- **Issuer**: \n  - Common Name: unistep_hebu\n  - Locality: shenzhen\n  - State/Province: shenzhen\n  - Country: 86\n- **Subject**: \n  - Common Name: unistep_hebu\n  - Locality: shenzhen\n  - State/Province: shenzhen\n  - Country: 86\n- **Hash Algorithm**: sha256\n- **Signature Algorithm**: rsassa_pkcs1v15\n- **Serial Number**: 1718444542\n\n### Analysis\nThe certificate information is provided by an issuer and subject identified as "unistep_hebu" located in Shenzhen, China. Here are the key points to analyze:\n\n1. **Issuer and Subject**: Both issuer and subject details are the same, indicating a self-signed certificate, which is common for app developers. The entity "unistep_hebu" appears to be legitimate and associated with Shenzhen, a major tech hub in China.\n\n2. **Organization Details**: The certificate lacks specific organizational details which might initially raise a flag, but it is not uncommon in many developer or smaller organization scenarios.\n\n3. **Certificate Algorithms**: The use of `sha256` for hashing and `rsassa_pkcs1v15` for signature indicate standard and secure algorithms.\n\n### Conclusion\nGiven the certificate details and the earlier provided app functionalities, this APK falls into the **\'white\'** category. The certificate does not present any obvious indicators of malfeasance, and combined with the application\'s likely functionalities, it appears to be a legitimate application. There are no signals pointing towards \'black\', \'gamble\', \'scam\', or \'sex\' categories.', name='Certificate_Inspector')]}}, {'supervisor': {'next': 'Icon_Analizer'}}, {'Icon_Analizer': {'messages': [HumanMessage(content="### Icon Analysis Results:\nThe icon analysis returned the following probabilities for each category:\n- **Black**: 0.0015903620515018702\n- **Gamble**: 0.00026620717835612595\n- **Scam**: 0.0006473638350144029\n- **Sex**: 0.0010244605364277959\n- **White**: 0.996471643447876\n\n### Summary:\nThe icon analysis strongly indicates that the APK belongs to the **'white'** category with a high probability of 99.65%. This further reinforces the conclusion that the application is legitimate and does not fall into the 'black', 'gamble', 'scam', or 'sex' categories.\n\n### Conclusion:\nBased on the details from the app package, permissions, certificate information, and the icon analysis:\n- The APK is classified under the **'white'** category.", name='Icon_Analizer')]}}, {'supervisor': {'next': 'Content_Analizer'}}, {'Content_Analizer': {'messages': [HumanMessage(content="### Comprehensive Analysis of the APK (MD5: 3dacdd95621ce98e27a4a495752de86e)\n\n#### Category Probabilities:\n- **Black**: 2.69%\n- **Gamble**: 1.59%\n- **Scam**: 0.52%\n- **Sex**: 19.46%\n- **White**: 75.73%\n\n#### Summary:\nThe model indicates the following probabilities for the APK in various categories with the highest probability in the **'white'** category (75.73%). \n\n### Key Points:\n1. **High Probability of Legitimate Content**: The highest probability (75.73%) is for the 'white' category, suggesting the APK is most likely legitimate.\n2. **Notable but Lower Probabilities**:\n   - The 'sex' category has a notable probability of 19.46%, which although significant, is not the highest.\n   - Other categories such as 'black', 'gamble', and 'scam' have probabilities significantly lower than 3%.\n\n### Conclusion:\nGiven the high probability of the APK being legitimate and the supporting evidence from the icon analysis, package details, and certificate information, the APK is classified as **'white'**. The slightly higher probability in the 'sex' category indicates a minor presence but is not substantial enough to override the overall conclusion. The APK appears to be a legitimate application with a primary focus on smart car navigation and management.", name='Content_Analizer')]}}, {'supervisor': {'next': 'Decision'}}, {'Decision_Maker': {'black': 0.005, 'gamble': 0.003, 'scam': 0.002, 'sex': 0.04, 'white': 0.95, 'label': 'white', 'next': None}}]
    # conversation_dict = extract_and_map_conversation(history)
    # conversation_dict['MD5'] = "3dacdd95621ce98e27a4a495752de86e"
    # import pprint
    # pprint.pprint(conversation_dict)
    # conn = sqlite3.connect('database.sqlite')
    # cursor = conn.cursor()
    # placeholders = ', '.join(['?'] * len(conversation_dict))
    # columns = ', '.join(conversation_dict.keys())
    # sql = f"INSERT INTO ChatHistory ({columns}) VALUES ({placeholders})"
    #
    # cursor.execute(sql, list(conversation_dict.values()))
    # conn.commit()
    # cursor.close()
    # conn.close()
    # print("插入成功")
    # msg = "你的知识截止到什么时候"
    # model = ChatOpenAI(model=MODEL_NAME, temperature=0.9)
    # print(model.invoke(msg))
