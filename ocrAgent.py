import streamlit as st
import json
import os
from datetime import datetime
import time
from PIL import Image
import io
import base64
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 初始化session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# 設定檔案路徑
USERS_FILE = 'users.json'
CUSTOM_FIELDS_FILE = 'custom_fields.json'

# OpenAI設定
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    st.error("請在.env檔案中設定OPENAI_API_KEY")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# 初始化資料檔案
def init_data_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({
                'admin': {
                    'password': 'admin',
                    'created_at': str(datetime.now())
                }
            }, f)
    
    if not os.path.exists(CUSTOM_FIELDS_FILE):
        with open(CUSTOM_FIELDS_FILE, 'w') as f:
            json.dump({}, f)

# 讀取使用者資料
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

# 讀取自訂欄位資料
def load_custom_fields():
    with open(CUSTOM_FIELDS_FILE, 'r') as f:
        return json.load(f)

# 儲存自訂欄位資料
def save_custom_fields(custom_fields):
    with open(CUSTOM_FIELDS_FILE, 'w') as f:
        json.dump(custom_fields, f)

# 使用GPT-4 Vision處理圖片
def process_with_gpt4_vision(image_bytes, custom_fields):
    try:
        # 將圖片轉換為base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # 準備提示詞
        fields_str = ", ".join(custom_fields) if custom_fields else "所有文字內容"
        prompt = f"請幫我從這張圖片中識別以下資訊：{fields_str}。請以結構化的方式列出結果，並標明對應的欄位。如果找不到某些欄位的資訊，請標示為「未找到」。"

        # 呼叫GPT-4 Vision API
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        # 解析回應
        result = response.choices[0].message.content
        return result

    except Exception as e:
        st.error(f"圖片處理錯誤: {str(e)}")
        return None

# 登入頁面
def login_page():
    st.title("文件辨識系統")
    username = st.text_input("使用者名稱")
    password = st.text_input("密碼", type="password")
    
    if st.button("登入"):
        users = load_users()
        if username in users and users[username]['password'] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success("登入成功！")
            st.experimental_rerun()
        else:
            st.error("使用者名稱或密碼錯誤！")

# 主應用程式
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    st.title("文件辨識系統")
    st.write(f"目前使用者: {st.session_state.current_user}")

    if st.button("登出"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.experimental_rerun()

    # 載入使用者的自訂欄位
    custom_fields = load_custom_fields()
    user_fields = custom_fields.get(st.session_state.current_user, [])

    # 自訂欄位管理
    with st.expander("自訂欄位管理"):
        new_field = st.text_input("新增欄位關鍵字")
        if st.button("新增欄位"):
            if new_field and new_field not in user_fields:
                user_fields.append(new_field)
                custom_fields[st.session_state.current_user] = user_fields
                save_custom_fields(custom_fields)
                st.success("欄位新增成功！")

        if user_fields:
            st.write("目前的自訂欄位：")
            for field in user_fields:
                col1, col2 = st.columns([3, 1])
                col1.write(field)
                if col2.button("刪除", key=f"del_{field}"):
                    user_fields.remove(field)
                    custom_fields[st.session_state.current_user] = user_fields
                    save_custom_fields(custom_fields)
                    st.experimental_rerun()

    # 檔案上傳和處理
    uploaded_file = st.file_uploader("上傳文件", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # 顯示上傳的圖片
        image = Image.open(uploaded_file)
        st.image(image, caption="上傳的文件", use_column_width=True)

        # GPT-4 Vision處理
        if st.button("執行辨識"):
            with st.spinner("處理中..."):
                result = process_with_gpt4_vision(uploaded_file.getvalue(), user_fields)
                
                if result:
                    st.subheader("辨識結果")
                    st.write(result)

if __name__ == "__main__":
    init_data_files()
    main()
