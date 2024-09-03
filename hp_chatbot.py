import streamlit as st
import os
import langid
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 設置 OpenAI API 密鑰
os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'

# 創建聊天模型
chat_model = ChatOpenAI(model_name="gpt-4o-mini")

def detect_language(text):
    lang, _ = langid.classify(text)
    return 'zh' if lang == 'zh' else 'en'

def generate_response(query, language, chat_history):
    # 將聊天歷史轉換為字符串格式
    history_str = "\n".join([f"Human: {msg['content']}" if msg['role'] == 'user' else f"AI: {msg['content']}" for msg in chat_history])

    if language == 'zh':
        prompt_template = ChatPromptTemplate.from_template(
            "你是一個專門回答關於哈利波特問題的AI助手。請考慮以下對話歷史，並以繁體中文版小說的翻譯名稱回答最新的問題：\n\n"
            "對話歷史：\n{history}\n\n"
            "Human: {query}\n"
            "AI: "
        )
    else:
        prompt_template = ChatPromptTemplate.from_template(
            "You are an AI assistant specializing in answering questions about Harry Potter. "
            "Please consider the following conversation history and answer the latest question in English:\n\n"
            "Conversation history:\n{history}\n\n"
            "Human: {query}\n"
            "AI: "
        )

    prompt = prompt_template.format(history=history_str, query=query)
    response = chat_model.invoke(prompt)

    return response.content

def main():
    st.title("⚡🧹Harry Potter Chatbot ⚡🧹")

    # 初始化聊天歷史
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # 顯示聊天歷史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 接受用戶輸入
    if prompt := st.chat_input("What would you like to know about Harry Potter?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 檢測語言並生成回應
        language = detect_language(prompt)
        response = generate_response(prompt, language, st.session_state.messages)

        # 顯示助手回應
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 添加側邊欄說明
    st.sidebar.title("About")
    st.sidebar.info(
        "This chatbot can answer questions about Harry Potter novels in both English and Traditional Chinese. "
        "Simply type your question in either language, and the bot will respond accordingly."
    )
    st.sidebar.info(
        "這個聊天機器人可以用繁體中文和英文回答關於哈利波特的問題。"
        "只需用任何一種語言輸入您的問題，機器人就會相應地回答。"
    )
    
    # 添加免責聲明
    st.sidebar.warning(
        "Disclaimer: The answers generated by this model might contain errors. Please evaluate the responses with caution."
    )
    st.sidebar.warning(
        "免責聲明：模型生成的回答可能有誤，請謹慎評估回覆內容。"
    )

if __name__ == "__main__":
    main()
