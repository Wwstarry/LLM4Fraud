from flask import jsonify, Blueprint, request
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


chatbot = Blueprint('chatbot', __name__)

MODEL_NAME = "gpt-4o-mini"

KEY = ""
BASE = ""


@chatbot.route('/catalogue', methods=['POST'])
def sent_msg():
    data = request.get_json()
    message = data.get('message')
    answer = get_answer(message, MODEL_NAME)
    print(answer)
    return jsonify({'answer': answer})


def get_answer(text, used_model):
    # 加入 system prompt：使用 ChatOpenAI 构造时传入 system message
    llm = ChatOpenAI(
        model=used_model,
        api_key=KEY,
        base_url=BASE,
        temperature=0.95
    ).bind(system_message="""
        [ROLE] 
        You are a software static analyst, engaged in the identification and supervision of fraud 
        and Android applications. You have profound professional knowledge and are invited to answer related professional 
        questions. 
        [TASK] 
        Answer questions related to the analysis of the Android fraud APP, and should also refuse to 
        answer any questions in other fields.
        [OTHER INSTRUCTIONS]
        When asking questions other than professional, you should apologize and ask for questions.
        All the questions must be answered in Chinese.
    """)

    api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
    tool = WikipediaQueryRun(api_wrapper=api_wrapper)

    # 不再传 messages_modifier
    ChatAgent = create_react_agent(llm, [tool])

    prompt = {
        "messages": [
            ("user", f"{text}"),
            ("user", "Please check and confirm that this question is related to the analysis of the Android fraud crime."),
        ]
    }

    result = ChatAgent.invoke(prompt)["messages"][-1].content
    return result
