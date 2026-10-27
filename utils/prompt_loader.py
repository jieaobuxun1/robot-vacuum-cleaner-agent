"""
分别对应prompts里的三个txt文件 进行加载和管理大模型的提示词
函数1：_load_prompt_file() 第一个try找文件的路径  第二个try把文件内的文本读出并且返回
函数2：load_system_prompts() 对应系统提示词
函数3：load_rag_prompts() 对应RAG总结提示词
函数4：load_report_prompts()  对应报告提示词
"""

from .config_handler import prompts_config
from .path_tool import get_abs_path
from .logger_handler import logger

# 前面加了_ 表示私有函数 只在这个文件内用
def _load_prompt_file(config_key: str,prompt_name: str):
    try:
        prompt_path = get_abs_path(prompts_config[config_key])
    except KeyError as e:
        logger.error(f"[读取提示词]在yml配置项中没有{config_key}配置项")
        raise e

    try:
        with open(prompt_path,'r',encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"[读取提示词]解析{prompt_name}出错:{str(e)}")
        raise e

def load_system_prompts():
    return _load_prompt_file("main_prompt_path","系统提示词")

def load_rag_prompts():
    return _load_prompt_file("rag_summarize_prompt_path","RAG总结提示词")

def load_report_prompts():
    return _load_prompt_file("report_prompt_path","报告提示词")