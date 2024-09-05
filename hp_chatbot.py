__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import boto3
import os
import tarfile
import langid
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import openai

# 設置 OpenAI API 密鑰

# client = OpenAI(
#     api_key=st.secrets["OPENAI_API_KEY"]
# )
# os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
# client = OpenAI(api_key=st.secrets["openai_api_key"])
openai.api_key = st.secrets.get("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai.api_key

# 設置 AWS 認證
aws_access_key_id = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")

if not aws_access_key_id or not aws_secret_access_key:
    st.error("AWS credentials not found in secrets. Please add them to your Streamlit secrets.")
    st.stop()

# 創建 S3 客戶端
try:
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    # 測試 S3 連接
    s3.list_buckets()
    st.success("Successfully connected to AWS S3")
except Exception as e:
    st.error(f"Error connecting to AWS S3: {str(e)}")
    st.stop()

@st.cache_resource
def load_db_from_s3(lang):
    bucket_name = st.secrets["S3_BUCKET_NAME"]
    file_name = f'hp_{lang}_database.tar.gz'
    local_file = f'/tmp/hp_{lang}_database.tar.gz'
    local_dir = f'/tmp/hp_{lang}_database'

    try:
        # Download files from S3 bucket
        s3.download_file(bucket_name, file_name, local_file)

        # Unzip files
        with tarfile.open(local_file, 'r:gz') as tar:
            tar.extractall(path='/tmp')

        # Laod Chroma dataset
        embedding_function = OpenAIEmbeddings()
        db = Chroma(persist_directory=local_dir, embedding_function=embedding_function)

        st.success(f"Successfully loaded {lang.upper()} database")
        return db
    except Exception as e:
        st.error(f"Error loading {lang.upper()} database: {str(e)}")
        return None

# 加载中英文数据库Load CN/EN database
@st.cache_resource
def load_databases():
    cn_db = load_db_from_s3('cn')
    en_db = load_db_from_s3('en')
    return cn_db, en_db

cn_db, en_db = load_databases()


# 創建聊天模型
chat_model = ChatOpenAI(model_name="gpt-4o-mini")

def detect_language(text):
    lang, _ = langid.classify(text)
    return 'zh' if lang == 'zh' else 'en'

def generate_response(query, language, chat_history):
    db = cn_db if language == 'zh' else en_db
    if db is None:
        return "I'm sorry, but the required database is not available at the moment. Please try again later."

    results = db.similarity_search_with_relevance_scores(query, k=5)
    context = "\n".join([doc.page_content for doc, _ in results])
    # 將聊天歷史轉換為str格式
    history_str = "\n".join([f"Human: {msg['content']}" if msg['role'] == 'user' else f"AI: {msg['content']}" for msg in chat_history])

    if language == 'zh':
        prompt_template = ChatPromptTemplate.from_template(
            "你是一個專門回答關於哈利波特問題的AI助手。請考慮以下對話歷史，並以台灣翻譯的繁體中文版小說的角色、地名、物品名稱回答最新的問題：\n\n"
            "如果上下文中並未提到具體訊息，請依你對哈利波特小說繁體中文版的理解進行回答"
            "對話歷史：\n{history}\n\n"
            "上下文：\n{context}\n\n"
            "Human: {query}\n"
            "AI: "
        )
    else:
        prompt_template = ChatPromptTemplate.from_template(
            "You are an AI assistant specializing in answering questions about Harry Potter. "
            "Please consider the following conversation history and answer the latest question in English:\n\n"
            "If context contains no specific content, please answer the question based on your understanding to the Harry Potter novels"
            "Conversation history:\n{history}\n\n"
            "Context:\n{context}\n\n"
            "Human: {query}\n"
            "AI: "
        )

    prompt = prompt_template.format(history=history_str, context=context, query=query)
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
