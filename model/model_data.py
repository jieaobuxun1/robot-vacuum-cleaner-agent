# 得到调用大模型的Key和Url(放在了.env环境变量中 而且用.gitignore忽略) 

import os
from dotenv import load_dotenv
from utils.path_tool import get_abs_path

# 找到我配置环境变量的文件位置
# load_dotenv 拿这个路径去打开文件、解析内容，把里面的配置加载到"环境变量"里。
load_dotenv(get_abs_path(".env"))

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")   # 按"键"取出对应的"值"
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  
