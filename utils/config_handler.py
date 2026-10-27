# 设置处理器 处理一些基础设置 打基础 解析yml的内容 并以字典形式返回(yaml都是k:v形式)  然后创建实例化对象
# 函数1：load_rag_config() 解析rag.yml 大模型使用选择
# 函数2：load_chroma_config() 解析chroma.yml 向量转换 md5文件 文本切割
# 函数3：load_prompts_config() 解析prompts.yml 获取行动指令 该怎么做
# 函数4：load_agent_config() 解析agent.yml 获取记录csv

import yaml
from .path_tool import get_abs_path

def load_rag_config(config_path = None,encoding = "utf-8"):
    if config_path == None:
        config_path = get_abs_path("config/rag.yml")
    with open(config_path,'r',encoding=encoding) as f: # 打开文件
        return yaml.safe_load(f) # 解析YAML，返回字典

def load_chroma_config(config_path = None,encoding = "utf-8"):
    if config_path == None:
        config_path = get_abs_path("config/chroma.yml")
    with open(config_path,'r',encoding=encoding) as f:
        return yaml.safe_load(f)

def load_prompts_config(config_path = None,encoding = "utf-8"):
    if config_path == None:
        config_path = get_abs_path("config/prompts.yml")
    with open(config_path,'r',encoding=encoding) as f:
        return yaml.safe_load(f)

def load_agent_config(config_path = None,encoding = "utf-8"):
    if config_path == None:
        config_path = get_abs_path("config/agent.yml")
    with open(config_path,'r',encoding=encoding) as f:
        return yaml.safe_load(f)

rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompts_config()
agent_config = load_agent_config()
