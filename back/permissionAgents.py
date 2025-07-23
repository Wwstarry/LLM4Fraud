import sqlite3

from langchain_core.pydantic_v1 import BaseModel, Field
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

MODEL_NAME = "gpt-4o-mini"
# KEY = ""
# BASE = ""
KEY = ""
BASE = ""


async def query_permission(name):
    model = ChatOpenAI(model=MODEL_NAME, api_key=KEY, base_url=BASE, temperature=0.95)
    system_prompt = "I will give you the name of an Android APP permission, please tell me its Chinese name and " \
                    "description, and evaluate its risk level, where 0 is no risk, 1 is low risk, and 2 is high risk."

    class APPPermission(BaseModel):
        permission: str = Field(description="The code for the permission that the app is requesting.")
        risk: int = Field(description="The risk level of this permission.")
        name: str = Field(description="The Chinese name of the permission")
        detail: str = Field(description="The detail description of the permission")

    parser = JsonOutputParser(pydantic_object=APPPermission)
    prompt = PromptTemplate(
        template=system_prompt + "\n {format_instructions}\n Permission:{name}\n",
        input_variables=["name"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser
    try:
        print(f"调用链{name}")
        perm_dict = await chain.ainvoke({"name": name})
        print(perm_dict)
        insert_into_permission(perm_dict['permission'], perm_dict['risk'], perm_dict['name'], perm_dict['detail'])
        print("插入新权限成功")
        return True
    except Exception as e:
        return False




def insert_into_permission(permission, risk, name, detail):
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    print("start insert permission")

    sql = "INSERT INTO Permission (permission, risk, name, detail) VALUES (?, ?, ?, ?)"
    cursor.execute(sql, (permission, risk, name, detail))

    conn.commit()
    conn.close()



