from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# 環境変数読み込み
load_dotenv()

# タイトルの設定
st.title("Simple Chat App")

# モデルの読み込み
client = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash"
)

# メッセージの初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# メッセージの表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# チャットボットとの対話
if prompt := st.chat_input("What is up?"):

    # ユーザーのメッセージを表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # チャットボットの応答
    with st.chat_message("assistant"):
        message = client.invoke(st.session_state.messages)
        response = message.content
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})