import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# 初始化session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# 資料檔案路徑
USERS_FILE = 'users.json'
GROUPS_FILE = 'groups.json'

# 初始化資料檔案
def init_data_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({
                'admin': {
                    'password': 'admin',
                    'group': 'admin',
                    'created_at': str(datetime.now())
                }
            }, f)
    
    if not os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'w') as f:
            json.dump({
                'admin': {
                    'permissions': ['create', 'read', 'update', 'delete'],
                    'created_at': str(datetime.now())
                }
            }, f)

# 讀取資料
def load_data():
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    with open(GROUPS_FILE, 'r') as f:
        groups = json.load(f)
    return users, groups

# 儲存資料
def save_data(users, groups):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)
    with open(GROUPS_FILE, 'w') as f:
        json.dump(groups, f)

# 登入頁面
def login_page():
    st.title("系統登入")
    username = st.text_input("使用者名稱")
    password = st.text_input("密碼", type="password")
    
    if st.button("登入"):
        users, _ = load_data()
        if username in users and users[username]['password'] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success("登入成功！")
            st.experimental_rerun()
        else:
            st.error("使用者名稱或密碼錯誤！")

# 使用者管理頁面
def user_management():
    st.header("使用者管理")
    users, groups = load_data()
    
    # 新增使用者
    with st.expander("新增使用者"):
        new_username = st.text_input("使用者名稱")
        new_password = st.text_input("密碼", type="password")
        new_group = st.selectbox("使用者群組", list(groups.keys()))
        
        if st.button("新增使用者"):
            if new_username and new_password:
                if new_username not in users:
                    users[new_username] = {
                        'password': new_password,
                        'group': new_group,
                        'created_at': str(datetime.now())
                    }
                    save_data(users, groups)
                    st.success("使用者新增成功！")
                else:
                    st.error("使用者名稱已存在！")
    
    # 顯示使用者列表
    st.subheader("使用者列表")
    user_data = []
    for username, data in users.items():
        user_data.append({
            '使用者名稱': username,
            '使用者群組': data['group'],
            '建立時間': data['created_at']
        })
    st.table(pd.DataFrame(user_data))

# 群組管理頁面
def group_management():
    st.header("群組管理")
    users, groups = load_data()
    
    # 新增群組
    with st.expander("新增群組"):
        new_group = st.text_input("群組名稱")
        permissions = st.multiselect(
            "權限",
            ['create', 'read', 'update', 'delete'],
            default=['read']
        )
        
        if st.button("新增群組"):
            if new_group:
                if new_group not in groups:
                    groups[new_group] = {
                        'permissions': permissions,
                        'created_at': str(datetime.now())
                    }
                    save_data(users, groups)
                    st.success("群組新增成功！")
                else:
                    st.error("群組已存在！")
    
    # 顯示群組列表
    st.subheader("群組列表")
    group_data = []
    for group_name, data in groups.items():
        group_data.append({
            '群組名稱': group_name,
            '權限': ', '.join(data['permissions']),
            '建立時間': data['created_at']
        })
    st.table(pd.DataFrame(group_data))

# 主應用程式
def main():
    init_data_files()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        st.title("權限管理系統")
        st.write(f"目前使用者: {st.session_state.current_user}")
        
        if st.button("登出"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.experimental_rerun()
        
        # 側邊欄選單
        menu = st.sidebar.selectbox(
            "功能選單",
            ["使用者管理", "群組管理"]
        )
        
        if menu == "使用者管理":
            user_management()
        elif menu == "群組管理":
            group_management()

if __name__ == "__main__":
    main()
    
