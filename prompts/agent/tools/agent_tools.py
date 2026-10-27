"""
为大模型检索提供工具
函数1：rag_summarize()把之前写好的RAG服务（检索向量数据库并生成答案）包装成了一个工具。
函数2：get_weather()获取城市对应的真实的天气
函数3：get_user_location()获取用户的城市(写死)
函数4：get_user_id()随机获取用户id(假数据)
函数5：get_current_month()随机获取当前年月(假数据)
函数6：generator_external_data()把本地的一个CSV数据文件，读取并转换成一个Python里的“嵌套字典”，存在内存里方便后面快速查询，
                                先获取路径验证是否存在，然后对应csv中的表头一项项列出写死格式
函数7：fetch_external_data()按照user_id和current_month让大模型去查数据，查到就返回字符串，否则返回空字符串
函数8：fill_content_for_report()信号触发器，辅助大模型拼凑逻辑 唤醒某个中间件 启动报告模式 只要提问和报告有关的问题 就会触发
"""



from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from typing import TypedDict
from rag.rag_service import RagSummarizeService
import random,os,requests,json
from utils.config_handler import agent_config
from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from dotenv import load_dotenv

load_dotenv(get_abs_path(".env"))
AMAP_KEY = os.getenv("AMAP_KEY")


class AgentContext(TypedDict):
    report: bool
    user_location: str

rag = RagSummarizeService()

user_ids = ["1001","1002","1003","1004","1005","1006","1007","1008","1009"]
month_arr = ["2025-01","2025-02","2025-03","2025-04","2025-05","2025-06",
             "2025-07","2025-08","2025-09","2025-10","2025-11","2025-12"]

external_data = {}

@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)

@tool(description="获取指定城市的实时天气，以消息字符串形式返回")
def get_weather(city: str) -> str:

    try:
        geo_resp = requests.get(
            "https://restapi.amap.com/v3/geocode/geo",
            params={"address": city, "key": AMAP_KEY},
            timeout=5,
        )
        geocodes = geo_resp.json().get("geocodes") or []
        if not geocodes:
            return f"未能识别城市{city}，请提供标准城市名称"

        # 先由城市名换算出 adcode，天气接口只认 adcode
        adcode = geocodes[0]["adcode"]
        weather_resp = requests.get(
            "https://restapi.amap.com/v3/weather/weatherInfo",
            params={"city": adcode, "key": AMAP_KEY},
            timeout=5,
        )
        data = weather_resp.json()
    except requests.RequestException as e:
        logger.warning(f"[get_weather]调用高德接口失败:{str(e)}")
        return f"获取{city}天气失败，请稍后再试"

    if data.get("status") != "1" or not data.get("lives"):
        return f"未能获取{city}的天气"
    live = data["lives"][0]
    return (f"城市{live['city']}天气为{live['weather']}，气温{live['temperature']}摄氏度，"
            f"空气湿度{live['humidity']}%，{live['winddirection']}风{live['windpower']}级")


@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location(runtime: ToolRuntime[AgentContext]) -> str:
    return runtime.context.get("user_location", "未知")

@tool(description="获取用户的ID,以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_ids)

@tool(description="获取当前月份,以纯字符串形式返回")
def get_current_month() -> str:
    return random.choice(month_arr)

def generator_external_data():

    if not external_data:
        external_data_path = get_abs_path(agent_config["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")

        with open(external_data_path,'r',encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")

                user_id: str = arr[0].replace('"',"")
                feature: str = arr[1].replace('"',"")
                efficiency: str = arr[2].replace('"',"")
                consumables: str = arr[3].replace('"',"")
                comparision: str = arr[4].replace('"',"")
                time: str = arr[5].replace('"',"")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征" : feature,
                    "效率" : efficiency,
                    "耗材" : consumables,
                    "对比" : comparision                    
                }

@tool(description="从外部系统中获取用户的使用记录，以纯字符串形式返回，如果未检索到,返回空字符串")
def fetch_external_data(user_id: str,month: str) -> str:
    generator_external_data()

    try:
        record = external_data[user_id][month]
        return json.dumps(record,ensure_ascii=False)
    except KeyError:
        logger.warning(f"[generator_external_data]未能检索到用户{user_id}在{month}的使用记录数据")
        return ""

@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的动态场景注入上下文信息，为后续提示词切换提供上下文信息")
def fill_content_for_report():
    return "fill_content_for_report已调用"