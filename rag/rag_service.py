"""
实现“问答/总结”服务
函数1：print_prompt()展示下提问AI的提示词
类1:RagSummarizeService
内部方法1:__init__()初始化工具 连接向量库 检索器 读prmopt模板然后转化为Langchain模板
内部方法2:_init_chain()基础链 把提示词大模型
内部方法3:retriever_docs()把用户的问题给检索器，然后返回k组相关文档
内部方法4:rag_summarize()先从检索器拿到用户的问题 然后把这个问题和检索器返回的k个文档一起打包填模板 再给大模型
"""


from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt

class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain

    def retriever_docs(self,query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self,query: str) -> str:

        context_docs = self.retriever_docs(query)

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"[参考资料{counter}]:内容:{doc.page_content} | 参考元数据:{doc.metadata}\n"

        return self.chain.invoke(
            {
                "input":query,
                "context":context,
            }
        )