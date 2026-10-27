# 智扫通扫地机器人智能客服 (RAG-Agent)

基于 LangChain + Streamlit + Chroma 构建的扫地机器人智能客服。

## 功能特性
- 支持多轮对话与流式输出（打字机效果）
- RAG 检索增强生成，精准回答保养、故障排查等问题
- ReAct Agent 架构，支持工具调用

## 快速开始
1. 克隆项目：`git clone https://github.com/...`
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量：复制 `.env.example` 为 `.env`，填入你的 `OPENAI_API_KEY`
4. 启动应用：`streamlit run app.py`