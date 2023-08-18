from datetime import datetime
import pandas as pd
import streamlit as st
from utils import *


# Settings
st.set_page_config(layout="wide")
today = datetime.today().date()
formatted_date = today.strftime("%Y-%m-%d")
targets = {"Protain": 158, "Fat": 46, "Carbohydrate": 263}

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
d = st.date_input("いつのデータを見ますか？", today)
# st.write(d, type(today), type(d))
plt, achieve_P, achieve_F, achieve_C = calc_diet(
    diet_db, targets=targets, date=d)
diet_cols = st.columns([2, 1])
diet_cols[0].pyplot(plt)

diet_cols[1].markdown("## タンパク質")
diet_cols[1].write(
    f"現在{round(achieve_P,1)}%、あと{round(targets['Protain']*(1-achieve_P/100), 1)}g！")
diet_cols[1].markdown("## 脂質")
diet_cols[1].write(
    f"現在{round(achieve_F, 1)}%、あと{round(targets['Fat']*(1-achieve_F/100), 1)}g！")
diet_cols[1].markdown("## 炭水化物")
diet_cols[1].write(
    f"現在{round(achieve_C, 1)}%、あと{round(targets['Carbohydrate']*(1-achieve_C/100), 1)}g！")
st.dataframe(diet_db[diet_db["date"].dt.date == d],
             use_container_width=True, hide_index=True)


st.markdown("## 体重の推移")
# スプレッドシートから取得したデータを加工して線図を表示
weight_fig = visualize_weight_and_body_fat(weight_db, "2023-08-01", "2023-09-30", 73, 69)
st.pyplot(weight_fig)

# TODO
# 食事の入力:: Done
# 体重の入力:: Done
# 食事・体重DBのEdit機能（更新・削除）:: Done
# サイドバーに「設定」:: Done
# ユーザー選択
# 設定（目標体重、開始日、目標日、代謝）記入 → スプレッドシート書き込み → 目標値（PFC）算出
# 目標体重推移を計算、DBに作成（設定の更新ボタントリガー）:: Done
# 体重推移をグラフ化:: Done
# 実体重の推移を1週間の平均で見せる:: Done

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
    input_diet = [formatted_date, input_protein,
                  input_fat, input_carbo, selected_item]
    if st.button("食事データを追加"):
        ws_diet.append_row(input_diet)
        st.success('データが追加されました！', icon="✅")

    st.markdown("### 体重")
    input_weight = st.number_input("体重")
    input_bodyfat = st.number_input("体脂肪率")
    input_data = [formatted_date, input_weight, input_bodyfat]
    if st.button("体重データ追加"):
        ws_weight.append_row(input_data)
        st.success('データが追加されました！', icon="✅")
