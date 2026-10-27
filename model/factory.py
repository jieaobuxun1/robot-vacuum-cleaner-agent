"""
模型工厂 为RAG检索提供要用的大模型 并且实例化
函数1：BaseModelFactory()规定继承的子类必须实现generator() 返回向量模型或者对话模型 否则不许实例化 
函数2：ChatModelFactory()提供创建对话模型的方法
函数3：EmbeddingsFactory()提供创建向量模型的方法
"""

from abc import ABC,abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from utils.config_handler import rag_config
from .model_data import OPENAI_API_KEY,OPENAI_BASE_URL

class BaseModelFactory(ABC):
    # 建立契约
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
            return ChatOpenAI(model=rag_config["chat_model_name"],api_key=OPENAI_API_KEY,base_url=OPENAI_BASE_URL)

class EmbeddingsFactory(BaseModelFactory):

     def generator(self) -> Optional[Embeddings | BaseChatModel]:
          return OpenAIEmbeddings(model=rag_config["embedding_model_name"],api_key=OPENAI_API_KEY,
                                  base_url=OPENAI_BASE_URL,check_embedding_ctx_length=False,
                                  chunk_size=rag_config["embedding_batch_size"])

chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()