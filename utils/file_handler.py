"""
处理各种文件
函数1：get_file_md5_hex() 验证文件存在/是不是 从路径读取文件 把一次性读取的内容转化为16进制
函数2：listdir_with_allowed_type() 返回目标后缀的文件路径
函数3：pdf_loader() 解析PDF文件的内容
函数4：txt_loader() 解析TXT文件的内容
"""

import os,hashlib
from .logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,TextLoader

# 得到MD5文件的十六制字符串
def get_file_md5_hex(filepath):

    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]文件{filepath}不是文件")
        return
    # 初始化md5文件对象
    md5_obj = hashlib.md5()
    # 一次性读取的最大文件大小
    chunk_size = 4096
    try:
        with open(filepath,'rb') as f:
            while chunk := f.read(chunk_size):
                # 把读取的数据一点点更新进去    
                md5_obj.update(chunk)
        # 记录读取的数据的十六进制字符串
        md5_hex = md5_obj.hexdigest()
        return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败，{str(e)}")
        return None

def listdir_with_allowed_type(path: str,allowed_types: tuple[str]):

    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return ()  

    for f in os.listdir(path):
        if f.lower().endswith(allowed_types):
            files.append(os.path.join(path,f))

    return tuple(files)

def pdf_loader(filepath: str,passwd = None) -> list[Document]:

    return PyPDFLoader(filepath,passwd).load()

def txt_loader(filepath: str) -> list[Document]:
    return TextLoader(filepath,encoding="utf-8").load()