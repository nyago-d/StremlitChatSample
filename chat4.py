import asyncio
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# 環境変数読み込み
load_dotenv()

@tool
def get_now():
    """Useful for when you need to cuttent datetime."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def main():

    # ツールの設定
    tools = [get_now, DuckDuckGoSearchRun(), WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())]

    # タイトルの設定
    st.title("Agent Chat App")

    # モデルの読み込み
    client = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        stream=True
    )

    # graphの構築
    graph = create_react_agent(client, tools=tools)

    # メッセージの初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # メッセージの表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "tools" in message:
                with st.expander("tool use proccess"):
                    for tool_output in message["tools"]:
                        st.markdown(tool_output)
            st.markdown(message["content"])

    # チャットボットとの対話
    if prompt := st.chat_input("What is up?"):

        # ユーザーのメッセージを表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # チャットボットの応答
        with st.chat_message("assistant"):

            expander = st.expander("tool use proccess")
            message_placeholder = st.empty()
            contents = ""
            tool_outputs = []

            async for event in graph.astream_events({"messages": st.session_state.messages}, version="v1"):
                # メッセージの表示
                if event["event"] == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        contents += content
                        message_placeholder.markdown(contents)
                # ツール利用の開始
                elif event["event"] == "on_tool_start":
                    tmp = f"#### Start using the tool ： {event['name']}  \nInputs: {event['data'].get('input')}"
                    tool_outputs.append(tmp)
                    expander.markdown(tmp)
                # ツール利用の終了
                elif event["event"] == "on_tool_end":
                    tmp = f"#### Finish using the tool ： {event['name']}  \nOutput ： {event['data'].get('output')}"
                    tool_outputs.append(tmp)
                    expander.markdown(tmp)
            
            st.session_state.messages.append({"role": "assistant", "content": contents, "tools": tool_outputs})

if __name__ == "__main__":
    asyncio.run(main())