"""
传入内容转化为向量并且持久化存储，构造知识库
函数1：__init__()初始化创建要用的工具 1.Chroma(AI原生向量数据库)提供表名、把文本转变为向量的模型、持久化存储的磁盘目录 
                                  2.RecursiveCharacterTextSplitter文本分割器 把传入的文本按照下面的规矩进行分割 每段最长长度、相邻两段允许最大重复字符数、常见分隔符、分割方法
函数2：get_retriever()把Chroma中定义的向量数据库包装成一个检索器，根据提问的问题，返回和问题最有关的k段文档
主函数1：load_document()把知识入库
内部函数1：check_md5_hex()检查有没有放md5字符串的地方，没有的话创建一个 如果有，就拿这次的md5字符串和文件里面的逐行比较，查看是否存储过
内部函数2：save_md5_hex()追加一行(append)写入md5_for_check(这一次的md5字符串)
内部函数3:get_file_documents()根据传入的文件，通过对应的文件解析器返回解析到的文件内容
主函数2:后面：先获取文件夹内所有能被解析后缀的文件路径,然后调用get_file_md5_hex获取字符串，再调用check_md5_hex看看存过没
       对于没有存过的，通过get_file_documents获取文件内容并用self.spliter进行分割，
       调用add_documents（先调用Embedding模型，再把这一段的所有东西打包写入磁盘数据库）
       此时说明这段文字是正确存进去了，再save_md5_hex把这个正确存入的向量文本记录 不能颠倒顺序
"""

from langchain_chroma import Chroma
from utils.config_handler import chroma_config
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from utils.path_tool import get_abs_path
from utils.file_handler import txt_loader,pdf_loader,listdir_with_allowed_type,get_file_md5_hex
from utils.logger_handler import logger
from langchain_core.documents import Document

class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_config["persist_directory"],
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size = chroma_config["chunk_size"],
            chunk_overlap = chroma_config["chunk_overlap"],
            separators = chroma_config["separators"],
            length_function = len
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})

    def count_documents(self) -> int:
        return self.vector_store._collection.count()

    def load_document(self):

        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(get_abs_path(chroma_config["md5_hex_store"])):
                open(get_abs_path(chroma_config["md5_hex_store"]),'w',encoding="utf-8").close()
                return False

            with open(get_abs_path(chroma_config["md5_hex_store"]),'r',encoding="utf-8") as f:
                for line in f.readlines():
                    Line = line.strip()
                    if Line == md5_for_check:
                        return True

                return False

        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_config["md5_hex_store"]),'a',encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(now_read_path: str) -> list[Document]:
            if now_read_path.endswith("txt"):
                return txt_loader(now_read_path)

            if now_read_path.endswith("pdf"):
                return pdf_loader(now_read_path)

            return [] # 如果不是上述两种文件，为了保证返回的格式相同，返回个空列表

        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(chroma_config["data_path"]),
            tuple(chroma_config["allow_knowledge_file_type"])
        )

        for path in allowed_files_path:

            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在于知识库内，跳过")
                continue

            try:
                documents: list[Document] = get_file_documents(path)
                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue

                split_document: list[Document] = self.spliter.split_documents(documents)
                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没有有效文本，跳过")
                    continue

                self.vector_store.add_documents(split_document)
                save_md5_hex(md5_hex)
                logger.info(f"[加载数据库]{path}内容加载成功")
            except Exception as e:
                logger.error(f"[加载数据库]{path}加载失败,{str(e)}",exc_info=True) 
                                    #在日志里不仅打印错误信息，还要把完整的“错误堆栈（Traceback）”一起打印出来。
