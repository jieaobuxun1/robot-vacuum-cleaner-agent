"""
在你的项目里，只要拿到这个 logger，你就能同时把日志“打印到屏幕上”和“保存到硬盘文件里”，而且格式统一、目录自动建、不会重复打印。
先确定了存放目录和文件夹建立以及日志的输出格式
函数1:get_logger()建立屏幕输出器和文件输出器 并且连接到日志上 一运行就能在屏幕输出并且在文件中保存
"""

from datetime import datetime
import logging,os
from .path_tool import get_abs_path

# 生成日志的存放目录
LOG_ROOT = get_abs_path("logs")
# 确认是否存在目录 不存在就创建
os.makedirs(LOG_ROOT,exist_ok=True)
# 日志的输出格式
DEFAULT_LOG_FORMAT = logging.Formatter(
    # 时间          函数定义的名字  级别名           文件名        行号         日志内容
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

def get_logger(
        name = 'agent',
        console_level = logging.INFO,
        file_level = logging.DEBUG,
        log_file = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # 防重复 防止同一个日志在屏幕上多次打印
    if logger.handlers:
        return logger

    # 屏幕输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    # 把组装好的输出器连接到日志器上
    logger.addHandler(console_handler)

    # 造一个文件输出器
    if not log_file:
        log_file = os.path.join(LOG_ROOT,f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file,encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger

logger = get_logger()