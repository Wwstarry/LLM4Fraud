from flask import Blueprint, request
import os
import asyncio

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agent.report_tools import *
from agent.report_prompts import *

reportAgents = Blueprint('reportAgents', __name__)

MODEL_NAME = "gpt-4o-mini"

# 初始化通用 LLM
model = ChatOpenAI(model=MODEL_NAME, api_key=KEY, base_url=BASE, temperature=0.95)

# 绑定每个 Agent 对应的系统提示
model_ip = model.bind(system_message=ipAnalizeAgent_prompt)
model_permission = model.bind(system_message=permissionAnalizeAgent_prompt)
model_activity = model.bind(system_message=activityAnalizeAgent_prompt)
model_certificate = model.bind(system_message=certificateAnalizeAgent_prompt)
model_summary = model.bind(system_message=SummaryAgent_prompt)
model_limitation = model.bind(system_message=LimitationAgent_prompt)

# 构造每个分析 Agent（无 messages_modifier 参数）
ipAnalizeAgent = create_react_agent(model_ip, [ip_analize])
permissionAnalizeAgent = create_react_agent(model_permission, [permission_analize])
activityAnalizeAgent = create_react_agent(model_activity, [activity_analize])
certificateAnalizeAgent = create_react_agent(model_certificate, [certificate_analize])
SummaryAgent = create_react_agent(model_summary, [model_result_analize])
LimitationAgent = create_react_agent(model_limitation, [model_result_analize])


async def analyze_with_agent(agent, user_prompt, md5):
    work_res = await agent.ainvoke({
        "messages": [
            ("user", user_prompt),
            ("user", f"MD5:{md5}"),
            ("system",
             "最终的内容请使用中文回答. The target users of the report are the personnel of the App Security Inspection Bureau. The content of the report should be as detailed as possible and not too concise.")
        ]
    })
    return work_res["messages"][-1].content


async def summary_with_agent(agent, user_prompt, results):
    work_res = await agent.ainvoke({
        "messages": [
            ("user", user_prompt),
            ("user",
             f'"ip_analysis": {results[0]}, "permission_analysis": {results[1]}, "activity_analysis": {results[2]} ,"certificate_analysis": {results[3]}'),
            ("system",
             "最终的内容请使用中文回答. The target users of the report are the personnel of the App Security Inspection Bureau. The content of the report should be as detailed as possible and not too concise.")
        ]
    })
    return work_res["messages"][-1].content


async def get_report(md5):
    tasks = [
        analyze_with_agent(ipAnalizeAgent, ipAnalizeAgent_user_prompt, md5),
        analyze_with_agent(permissionAnalizeAgent, permissionAnalizeAgent_user_prompt, md5),
        analyze_with_agent(activityAnalizeAgent, activityAnalizeAgent_user_prompt, md5),
        analyze_with_agent(certificateAnalizeAgent, certificateAnalizeAgent_user_prompt, md5),
    ]
    results = await asyncio.gather(*tasks)

    summary_tasks = [
        summary_with_agent(SummaryAgent, SummaryAgent_user_prompt, results),
        summary_with_agent(LimitationAgent, LimitationAgent_user_prompt, results)
    ]

    summary_results = await asyncio.gather(*summary_tasks)

    result_dict = {
        "ip_analysis": results[0],
        "permission_analysis": results[1],
        "activity_analysis": results[2],
        "certificate_analysis": results[3],
        "summary": summary_results[0],
        "limitations": summary_results[1]
    }

    print(result_dict)
    print(
        result_dict["ip_analysis"] +
        result_dict['permission_analysis'] +
        result_dict['activity_analysis'] +
        result_dict['certificate_analysis'] +
        result_dict['summary'] +
        result_dict['limitations']
    )
    return result_dict


@reportAgents.route('/report/agent', methods=['GET'])
def analize_report_generation():
    md5 = request.args.get('md5')
    print("Report Generation Start!")
    try:
        result_dic = asyncio.run(get_report(md5))
        return result_dic, 200
    except Exception as e:
        print(f"Exception occurred: {e}")
        return {"error": "Report generation failed."}, 500
