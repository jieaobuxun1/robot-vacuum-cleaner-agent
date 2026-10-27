import time
import streamlit as st
from prompts.agent.react_agent import ReactAgent
from rag.vector_store import VectorStoreService

@st.cache_resource
def get_vector_store() -> VectorStoreService:
    return VectorStoreService()

# 绘制标题
st.title("智扫通扫地机器人智能客服")
# 标题分割线
st.divider()

# 知识库为空时，检索结果必然为空，提前提示用户先建库
if get_vector_store().count_documents() == 0:
    st.warning("知识库为空，请先在项目根目录运行 `python -m rag.build_index` 构建知识库。")

# 侧边栏选择所在城市，供 get_user_location 工具读取
st.sidebar.selectbox("你所在的城市", ["潍坊", "青岛", "滨州"], key="user_location")


#持久化对象

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()
if "message" not in st.session_state:
    st.session_state["message"] = [{"role":"assistant","content":"你好，有什么可以帮助你？"}]
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 底部聊天输入框
prompt = st.chat_input()

if prompt:

    # 立即显示并保存用户信息
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})
    response_messages = [] # 空列表 接住完整回答
    with st.spinner("智能客服思考中。。。"): # 等待/生成期间加载显示动画
        res_stream = st.session_state["agent"].execute_stream(
            prompt, st.session_state.get("user_location", "未知")
        )

        def capture(generator,cache_list):

            full_text = "" # 用于拼接完整的回答

            for chunk in generator:
                full_text += chunk
                for char in chunk: # 逐字符yield
                    time.sleep(0.01)
                    yield char
            cache_list.append(full_text) # 生成结束后把完整内容存入外部列表

            # 把 capture 产出的字符边产边显示，形成流式打字效果。
        st.chat_message("assistant").write_stream(capture(res_stream,response_messages))
        st.session_state["message"].append({"role":"assistant","content":response_messages[-1]})# 把完整回答存入历史
        st.rerun() # 重构干净的界面