from datetime import datetime
import pandas as pd
import pytz
import streamlit as st
import time
from utils import *


# Settings
st.set_page_config(
    layout="centered",
    page_title="MyDietApp",
    page_icon=":weight_lifter:",
    initial_sidebar_state="expanded"
    )
today = datetime.today().date()
japan_timezone = pytz.timezone('Asia/Tokyo')
current_time_japan = datetime.now(japan_timezone)
formatted_date = current_time_japan.date()
formatted_date_str = formatted_date.strftime("%Y-%m-%d")
targets = {"Protein": 158, "Fat": 46, "Carbohydrate": 263}

# Database
ws_weight = get_worksheet("体重")
ws_diet = get_worksheet("食事")
weight_db = get_db(ws_weight)
weight_db["date"] = pd.to_datetime(weight_db["date"])
diet_db = get_db(ws_diet)
diet_db["date"] = pd.to_datetime(diet_db["date"])

# Page Start
st.title("My Diet App!")
# st.write("一日の摂取PFCを管理し、体重の推移を見守ろう！")
# st.markdown("目標体重：69.0kg")
# st.markdown(f"現在の体重：*{}kg*")

st.markdown("## PFCの摂取状況")
# 目標に対して何%食べているかをグラフ表示
# 今日摂りたいPFCの残量を表示
d = st.date_input("いつのデータを見ますか？", formatted_date)
plt, achieve_P, achieve_F, achieve_C = calc_diet(
    diet_db, targets=targets, date=d)
diet_cols = st.columns([2, 1])
diet_cols[0].pyplot(plt)

diet_cols[1].markdown(f"## 目標値")
diet_cols[1].markdown(f"**タンパク質:{targets['Protein']}g**")
if achieve_P >= 100:
    diet_cols[1].write(f"目標を達成しました！({round(achieve_P * targets['Protein'] / 100, 1)}g)")
else:
    diet_cols[1].write(
    f"現在{round(achieve_P,1)}%、あと**{round(targets['Protein']*(1-achieve_P/100), 1)}g**！")
diet_cols[1].markdown(f"**脂質:{targets['Fat']}g**")
if achieve_F >= 100:
    diet_cols[1].write(f"目標を達成しました！({round(achieve_F * targets['Fat'] / 100, 1)}g)")
else:
    diet_cols[1].write(
    f"現在{round(achieve_F, 1)}%、あと**{round(targets['Fat']*(1-achieve_F/100), 1)}g**！")
diet_cols[1].markdown(f"**炭水化物:{targets['Carbohydrate']}g**")
if achieve_C >= 100:
    diet_cols[1].write(f"目標を達成しました！({round(achieve_C * targets['Carbohydrate'] / 100, 1)}g)")
else:
    diet_cols[1].write(
    f"現在{round(achieve_C, 1)}%、あと**{round(targets['Carbohydrate']*(1-achieve_C/100), 1)}g**！")
diet_cols[1].markdown("**総摂取カロリー：2098kcal以下**")
calorie = round(achieve_P * targets["Protein"] * 0.04 + achieve_F * targets["Fat"] * 0.09 + achieve_C * targets["Carbohydrate"] * 0.04, 1)
diet_cols[1].write(f"**{calorie}kcal**")

st.dataframe(diet_db[diet_db["date"].dt.date == d],
             use_container_width=True, hide_index=True)


st.markdown("## 体重の推移")
# スプレッドシートから取得したデータを加工して線図を表示
weekly = st.radio("グラフ表示選択", ("Weekly", "Daily"), horizontal=True)
if weekly == "Weekly":
    weight_fig = weekly_weight_and_body_fat(weight_db, "2023-08-01", "2023-09-30", 73, 69)
else:
    weight_fig = daily_weight_and_body_fat(weight_db, "2023-08-01", "2023-09-30", 73, 69)
st.pyplot(weight_fig)


with st.sidebar:
    st.markdown("## データ入力")
    st.markdown("### 食事")
    data_option = st.radio('選択肢', ['過去のデータを参照する', '新たに入力する'])
    if data_option == '過去のデータを参照する':
        # 過去のデータを参照する場合
        unique_items = diet_db['Item'].unique()
        selected_item = st.selectbox('食品アイテムを選択', unique_items)
        selected_row = diet_db[diet_db['Item'] == selected_item].iloc[0]
        initial_protein = selected_row['Protein']
        initial_fat = selected_row['Fat']
        initial_carbohydrate = selected_row['Carbohydrate']
    else:
        # 新たに入力する場合
        selected_item = st.text_input('食品アイテムを入力', value='')
        initial_protein = 0.0
        initial_fat = 0.0
        initial_carbohydrate = 0.0

    # 栄養素の入力欄を作成
    input_protein = st.number_input("タンパク質（g）", value=initial_protein)
    input_fat = st.number_input("脂質（g）", value=initial_fat)
    input_carbo = st.number_input("炭水化物（g）", value=initial_carbohydrate)
    input_diet = [formatted_date_str, input_protein, input_fat, input_carbo, None]
    input_diet.append(selected_item)
    if st.button("食事データを追加"):
        row_num = len(ws_diet.col_values(1)) + 1
        ws_diet.insert_rows(values=input_diet, row=row_num)
        st.success('データが追加されました！', icon="✅")

    st.markdown("### 体重")
    input_weight = st.number_input("体重")
    input_bodyfat = st.number_input("体脂肪率")
    input_data = [formatted_date_str, input_weight, input_bodyfat]
    if st.button("体重データ追加"):
        ws_weight.append_row(input_data)
        st.success('データが追加されました！', icon="✅")
        time.sleep(2)
        st.experimental_rerun()
