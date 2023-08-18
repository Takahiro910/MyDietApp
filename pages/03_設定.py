import pandas as pd
import streamlit as st
from utils import *


# Settings
st.set_page_config(layout="wide")

# Database
ws_users = get_worksheet("ユーザー")
user_db = get_db(ws_users)

st.title("ユーザーデータ")
userid = "uwasanoaitsu910@gmail.com"
st.write(userid.split("@")[0])
user_data = user_db[user_db["id"]==userid].iloc[0]
st.write(f"性別：{user_data['sex']}")
age = calc_age(int(user_data["birth_y"]), int(user_data["birth_m"]), int(user_data["birth_d"]))
st.write(f"年齢：{age}歳")
st.write(f"概算消費カロリー：{int(user_data['TDEE'])} kcal/day")
st.markdown("## 目標設定")
st.markdown(f"目標体重：**{round(float(user_data['target_weight']),1)}kg**")
st.write(f"減量期間：{user_data['start_date']}～{user_data['goal_date']}")


st.markdown("---")
st.write("以下は変更可能です。")
updated_height = st.number_input("身長", value=int(user_data["height"]))
updated_weight = st.number_input("減量開始時の体重", value=int(user_data["weight"]))
updated_BMR = st.number_input("基礎代謝", value=int(user_data["BMR"]))
activity_level = st.selectbox("活動レベルを選択してください", [
    "ほとんど運動しない (Sedentary)",
    "軽い運動をする (Lightly Active)",
    "運動をする (Moderately Active)",
    "激しい運動をする (Very Active)",
    "超激しい運動をする (Extra Active)"
], index=int(user_data["activity"]))
estimated_calories = calculate_calories(updated_BMR, activity_level)
if st.button("プロファイルを更新"):
    updated_values = [
        ("height", updated_height),
        ("weight", updated_weight),
        ("BMR", updated_BMR),
        ("activity", activity_level),
        ("TDEE", estimated_calories)
    ]
    
    for field, value in updated_values:
        user_db.loc[user_db["id"] == userid, field] = value
    data_values = user_db.values.tolist()
    ws_users.update("A2", data_values, raw=False)
    st.success("プロファイルが更新されました！")