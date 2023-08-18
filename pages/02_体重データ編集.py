import datetime
import pandas as pd
import streamlit as st
from utils import *


# Settings
st.set_page_config(layout="wide")

# Database
ws_weight = get_worksheet("体重")
weight_db = get_db(ws_weight)
weight_db["date"] = pd.to_datetime(weight_db["date"])

st.title("体重データの編集")
st.dataframe(weight_db, use_container_width=True)

operation = st.radio("操作を選択してください", ("入力", "更新", "削除"), horizontal=True)

if operation == "入力":
    st.write("新しいデータの追加")
    input_date = st.date_input("日付")
    input_weight = st.number_input("体重")
    input_bodyfat = st.number_input("体脂肪率")
    if st.button("追加"):
        input_date_str = input_date.strftime("%Y-%m-%d")
        new_data_list = [input_date_str, input_weight, input_bodyfat]
        ws_weight.append_row(new_data_list)
        st.success("データが追加されました！")

elif operation == "更新":
    st.write("既存データの更新")
    row_to_update = st.number_input("更新する行番号を入力してください", min_value=0, value=0)
    selected_row_data = ws_weight.row_values(row_to_update + 2)
    edit_date = datetime.datetime.strptime(selected_row_data[0], "%Y-%m-%d").date()
    updated_date = st.date_input("日付", value=edit_date)
    updated_weight = st.number_input("体重", value=float(selected_row_data[1]))
    updated_bodyfat = st.number_input("体脂肪率", value=float(selected_row_data[2]))
    if st.button("更新"):
        updated_data_list = [updated_date, updated_weight, updated_bodyfat]
        ws_weight.update("A" + str(row_to_update), updated_data_list)
        st.success("データが更新されました！")

elif operation == "削除":
    st.write("データ削除")
    delete_row = st.number_input("削除する行番号を入力してください", min_value=0, value=0)
    if st.button("削除"):
        ws_weight.delete_rows(delete_row + 2)
        st.success("データが削除されました！")