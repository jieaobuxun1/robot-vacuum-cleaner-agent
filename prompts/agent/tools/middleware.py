"""
中间件拦截器 一般在大模型搜索工具后执行
函数1：monitor_tool只要大模型用了(搜索到了)agent_tools里的某个工具，就会被调用 
      返回消息或者命令 输出日志 如果调用了fill_content_for_report就会把关键词设为True(全局变量)
函数2：log_before_model模型执行完一轮要进行下一轮前必须要执行的 输入日志查看模型发送了多少条消息(识别卡死的情况) 然后返回最后一条消息 主要是给程序员看模型是否在正常运作
函数3：report_prompt_switch决定模型是用专业知识回答还说普通知识回答(如果要生成报告->关键词为true) 根据关键词的T/F 返回report/system的prompts
"""

from langchain.agents.middleware import AgentState,wrap_tool_call,Runtime,before_model,dynamic_prompt,ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from typing import Callable
from utils.prompt_loader import load_report_prompts,load_system_prompts
from utils.logger_handler import logger

@wrap_tool_call
def monitor_tool(

    request:ToolCallRequest,
    handler:Callable[[ToolCallRequest],ToolCallRequest | Command]
) -> ToolMessage | Command:

    logger.info(f"[tool monitor]执行参数:{request.tool_call['name']}")
    logger.info(f"[tool monitor]传入参数:{request.tool_call['args']}")
    try:
        result = handler(request)
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")

        if request.tool_call['name'] == "fill_content_for_report":
            request.runtime.context["report"] = True

        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}调用失败，原因:{str(e)}")
        raise e


@before_model
def log_before_model(
    state : AgentState,
    runtime : Runtime
):
    logger.info(f"[log_before_model]即将调用模型,带有{len(state['messages'])}条信息.")
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")
    return None

@dynamic_prompt
def report_prompt_switch(request: ModelRequest):
    is_report = request.runtime.context.get("report",False)
    if is_report:
        request.runtime.context["report"] = False
        return load_report_prompts()

    return load_system_prompts()