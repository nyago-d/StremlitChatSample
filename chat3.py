from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessageChunk
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

def main():

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
            if "tool" in message:
                with st.expander("tool use proccess"):
                    st.markdown(message["tool"])
            st.markdown(message["content"])

    # チャットボットとの対話
    if prompt := st.chat_input("What is up?"):

        # ユーザーのメッセージを表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # チャットボットの応答
        # see https://langchain-ai.github.io/langgraph/concepts/streaming/
        with st.chat_message("assistant"):

            expander = st.expander("tool use proccess")
            message_placeholder = st.empty()
            contents = ""
            tool_output = ""

            stream = graph.stream({"messages": st.session_state.messages}, stream_mode=["updates", "messages"])
            for token in stream:
                # メッセージでかつツールからの回答ではない場合に表示
                if token[0] == "messages" and isinstance(token[1][0], AIMessageChunk) and token[1][0].content != "":
                    contents += token[1][0].content
                    message_placeholder.markdown(contents)
                # ツールからの回答の場合に表示
                elif token[0] == "updates":
                    if "tools" in token[1]:
                        tmp = f"#### Using the tool ： {token[1]['tools']['messages'][0].name}  \nOutput ： {token[1]['tools']['messages'][0].content}"
                        tool_output += tmp
                        expander.markdown(tmp)

            st.session_state.messages.append({"role": "assistant", "content": contents, "tool": tool_output})

if __name__ == "__main__":
    main()