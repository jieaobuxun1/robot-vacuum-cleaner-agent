"""
类:ReactAgent:打包模型、收集用户问题并且流式输出
函数1：__init__打包生成agent 包括模型、初始提示词、所有的工具和中间件 这样每次Agent思考都会在初始提示词的基础上 用模型+工具+中间件解决问题
函数2：execute_stream先把用户的问题填入模板 然后流式输出最后一条回答(最新的一条回答) 
"""

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from prompts.agent.tools.agent_tools import (rag_summarize,get_weather,get_user_location,
                                             get_user_id,get_current_month,fetch_external_data,fill_content_for_report,
                                             AgentContext)
from prompts.agent.tools.middleware import monitor_tool,log_before_model,report_prompt_switch

class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize,get_weather,get_user_id,get_user_location,get_current_month,fetch_external_data,fill_content_for_report],
            middleware=[monitor_tool,log_before_model,report_prompt_switch],
            context_schema=AgentContext,
        )

    def execute_stream(self,query:str,user_location:str = "未知"):
        input_dict = {
            "messages" : [
                {"role":"user","content":query},
            ]
        }

        for chunk in self.agent.stream(
            input_dict,
            stream_mode = "values",
            context = {"report":False,"user_location":user_location},
        ):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                if isinstance(latest_message, AIMessage) and latest_message.content:
                    # yield就是流水线输出里的return 可以一点点输出结果
                    yield latest_message.content.strip() + "\n"