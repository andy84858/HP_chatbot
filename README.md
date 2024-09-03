# HP_chatbot

## 1.項目說明
這是一個基於OpenAI ChatGPT-4o-mini模型的雙語聊天機器人，專門用於回答與哈利波特系列小說（範圍：1-7集）的相關問題。
此模型可以理解並回答繁體中文和英文的問題，並能記憶先前的對話內容，提供連貫的對話體驗。

### 主要特點
* 使用 OpenAI GPT-4o-mini 模型進行自然語言處理和生成
* 採用 OpenAI 的 text-embedding-3-small 模型進行文本嵌入
* 運用 RAG（檢索增強生成）技術，結合預訓練的語言模型和特定領域知識庫
* 支持中英文雙語問答，自動檢測輸入語言並做出相應回應
* 基於 Streamlit 構建直觀的用戶界面，易於使用和部署

本專案以 NLP 技術應用於特定領域的智能對話系統。如果您想重現或自行訓練一個類似的中英文模型來完成特定任務，可以參考以下訓練步驟。

## 2.訓練步驟
訓練過程分為中文和英文兩個部分，分別使用不同的訓練腳本於Google Colab進行訓練。

### (1)中文版小說訓練(HP_CN_RAG.ipynb)
1. 資料加載：使用 TextLoader 加載中文版小說文件(中文小說txt檔請見____)。
2. 文本分割：採用 RecursiveCharacterTextSplitter 將文本分割成適當大小的chunk。
3. 向量化：使用 OpenAIEmbeddings(model="text-embedding-3-small") 模型進行文本embedding。
4. 資料庫創建：使用 Chroma 創建向量資料庫，用於高效檢索(資料庫請見___）。
5. 問答模型：結合 ChatOpenAI 模型和自定義提示模板，生成回答。

### (2)英文版小說訓練(HP_EN_RAG.ipynb)
1. 資料處理：使用 TextLoader 加載英文版小說文件(英文小說txt檔請見____)。
2. 文本分割：採用 RecursiveCharacterTextSplitter 將文本分割成適當大小的chunk。
3. 向量化：同樣使用 OpenAIEmbeddings(model="text-embedding-3-small") 進行文本embedding。
4. 資料庫創建：使用 Chroma 創建向量資料庫，用於高效檢索(資料庫請見___）。
5. 問答模型：結合 ChatOpenAI 模型和自定義提示模板，生成回答。

#### 備註說明
根據目前查到的資料，各家模型在繁體中文的embedding表現力如以是否開源進行篩選，以微軟 multilingual-e5-small表現最優，我同時挑選了OpenAI的text-embedding-3-small模型進行對照。
之所以選擇OpenAI的text-embedding-3-small模型進行對照，在於其embedding的vector的長度（共1536個）可以與英文版吻合（微軟的模型vector長度為384個），因而不用特別調整。
我同時以網路上蒐集的哈利波特問答集進行測試，發現text-embedding-3-small較能準確回答問題，最終以text-embedding-3-small作為embedding的模型。

## 3. Streamlit部署
1. 初始化 ChatOpenAI 模型，使用 "gpt-4o-mini" 作為基礎模型。
2. 使用 langid 庫來檢測用戶輸入的語言（中文或英文）。
3. 根據檢測到的語言，使用不同的提示模板。
4. 將對話歷史轉換為str格式，納入上下文考慮。
5. 使用 ChatOpenAI 模型生成對用戶查詢的回應。

## 4. Licence
本項目採用 MIT 許可證。詳情請見 LICENSE 文件。
