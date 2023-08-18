import datetime
import pandas as pd
import streamlit as st
from utils import *


# Settings
st.set_page_config(layout="wide")

# Database
ws_diet = get_worksheet("食事")
diet_db = get_db(ws_diet)
diet_db["date"] = pd.to_datetime(diet_db["date"])

st.title("食事データの編集")
st.dataframe(diet_db, use_container_width=True)

operation = st.radio("操作を選択してください", ("入力", "更新", "削除"), horizontal=True)

if operation == "入力":
    st.write("新しいデータの追加")
    input_date = st.date_input("日付")
    input_item = st.text_input('食品アイテムを入力', value='')
    input_protein = st.number_input("タンパク質（g）")
    input_fat = st.number_input("脂質（g）")
    input_carbo = st.number_input("炭水化物（g）")
    if st.button("追加"):
        input_date_str = input_date.strftime("%Y-%m-%d")
        new_data_list = [input_date_str, input_protein, input_fat, input_carbo, input_item]
        ws_diet.append_row(new_data_list)
        st.success("データが追加されました！")

elif operation == "更新":
    st.write("既存データの更新")
    row_to_update = st.number_input("更新する行番号を入力してください", min_value=0, value=0)
    selected_row_data = ws_diet.row_values(row_to_update + 2)
    edit_date = datetime.strptime(selected_row_data[0], "%Y-%m-%d").date()
    updated_date = st.date_input("日付", value=edit_date)
    updated_item = st.text_input('食品アイテムを入力', value=selected_row_data[4])
    updated_protein = st.number_input("タンパク質（g）", value=float(selected_row_data[1]))
    updated_fat = st.number_input("脂質（g）", value=float(selected_row_data[2]))
    updated_carbo = st.number_input("炭水化物（g）", value=float(selected_row_data[3]))
    if st.button("更新"):
        updated_data_list = [updated_date, updated_protein, updated_fat, updated_carbo, updated_item]
        ws_diet.update("A" + str(row_to_update), updated_data_list)
        st.success("データが更新されました！")

elif operation == "削除":
    st.write("データ削除")
    delete_row = st.number_input("削除する行番号を入力してください", min_value=0, value=0)
    if st.button("削除"):
        ws_diet.delete_rows(delete_row + 2)
        st.success("データが削除されました！")