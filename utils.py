from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
import gspread
import matplotlib.pyplot as plt
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd
import streamlit as st


# --- SETTINGS --- #
load_dotenv(verbose=True, dotenv_path='.env')
JSON_FILE_PATH = os.environ.get("JSON_FILE_PATH")
SHEET_KEY = os.environ.get("SHEET_KEY")

# --- Worksheet Editting --- #
def get_worksheet(title):
    """
    Return worksheet '体重' and '食事'
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # For Streamlit Share
    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)

    # For local
    # credentials = ServiceAccountCredentials.from_json_keyfile_name(
    #     JSON_FILE_PATH, scope)

    gs = gspread.authorize(credentials)
    spreadsheet_key = SHEET_KEY
    wb = gs.open_by_key(spreadsheet_key)
    ws = wb.worksheet(title)
    return ws


def get_db(WorkSheet):
    worksheet = WorkSheet
    db = worksheet.get_all_records()
    df = pd.DataFrame(db)
    return df


# --- Visualize --- #
def calc_diet(data, targets, date):
    data = data
    filtered_data = data[data["date"].dt.date == date]
    total_P = filtered_data["Protein"].sum()
    total_F = filtered_data["Fat"].sum()
    total_C = filtered_data["Carbohydrate"].sum()
    target_P = targets["Protein"]
    target_F = targets["Fat"]
    target_C = targets["Carbohydrate"]
    achieve_P = total_P / target_P * 100
    achieve_F = total_F / target_F * 100
    achieve_C = total_C / target_C * 100

    categories = ["Protein", "Fat", "Carbo"]
    values = [achieve_P, achieve_F, achieve_C]
    plt.bar(categories, values, color=['red', 'green', 'orange'])
    plt.ylabel("Intake (%)", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    return plt, achieve_P, achieve_F, achieve_C


def weekly_weight_and_body_fat(dataframe, start_date, end_date, start_weight, target_weight):
    # DataFrameから必要なデータを取得
    dataframe = dataframe.replace("", np.nan)
    dataframe = dataframe.dropna(subset=["weight", "fat"])
    weight_data = dataframe['weight'].astype(float)
    body_fat_data = dataframe['fat'].astype(float)
    dates = dataframe["date"]

    # 1週間ごとにデータをリサンプリングして平均値を計算
    weekly_data = pd.DataFrame({
        "Date": dates,
        "Weight": weight_data,
        "Body Fat": body_fat_data
    })
    weekly_data.set_index("Date", inplace=True)
    weekly_data = weekly_data.resample("D").mean().rolling(window=7).mean()

    # チャートを作成
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(weekly_data.index,
             weekly_data['Weight'], marker='o', color='tab:blue', label="Weight")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Weight", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.plot(weekly_data.index, weekly_data['Body Fat'],
             marker='o', color='tab:orange', label="Body Fat")
    ax2.set_ylabel("Fat Percentage", color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')
    ax2.set_ylim(5, 20)

    # 開始日と目標体重をプロット
    ax1.plot([pd.to_datetime(start_date), pd.to_datetime(end_date)], [
             start_weight, target_weight], linestyle='--', color='tab:blue', label="Weight Target")

    plt.title("Weight and Fat Percentage Over Time")
    plt.xticks(rotation=45)
    plt.gca().get_xticklabels()[0].set_verticalalignment("bottom")

    # 凡例を1つに統合
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.tight_layout()
    return fig


def daily_weight_and_body_fat(dataframe, start_date, end_date, start_weight, target_weight):
    # DataFrameから必要なデータを取得
    dataframe = dataframe.replace("", np.nan)
    dataframe = dataframe.dropna(subset=["weight", "fat"])
    weight_data = dataframe['weight'].astype(float)
    body_fat_data = dataframe['fat'].astype(float)
    dates = dataframe["date"]

    daily_data = pd.DataFrame({
        "Date": dates,
        "Weight": weight_data,
        "Body Fat": body_fat_data
    })
    daily_data.set_index("Date", inplace=True)

    # チャートを作成
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(daily_data.index,
             daily_data['Weight'], marker='o', color='tab:blue', label="Weight")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Weight", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.plot(daily_data.index, daily_data['Body Fat'],
             marker='o', color='tab:orange', label="Body Fat")
    ax2.set_ylabel("Fat Percentage", color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')
    ax2.set_ylim(5, 20)

    # 開始日と目標体重をプロット
    ax1.plot([pd.to_datetime(start_date), pd.to_datetime(end_date)], [
             start_weight, target_weight], linestyle='--', color='tab:blue', label="Weight Target")

    plt.title("Weight and Fat Percentage Over Time")
    plt.xticks(rotation=45)
    plt.gca().get_xticklabels()[0].set_verticalalignment("bottom")

    # 凡例を1つに統合
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.tight_layout()
    return fig

# --- Others --- #
def calc_age(birth_year, birth_month, birth_day):
    current_date = datetime.now()
    birth_date = datetime(birth_year, birth_month, birth_day)
    age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    return age


def calculate_calories(bmr, activity_level):
    activity_multipliers = {
        "ほとんど運動しない (Sedentary)": 1.2,
        "軽い運動をする (Lightly Active)": 1.375,
        "運動をする (Moderately Active)": 1.55,
        "激しい運動をする (Very Active)": 1.725,
        "超激しい運動をする (Extra Active)": 1.9
    }
    activity_multiplier = activity_multipliers[activity_level]
    estimated_calories = bmr * activity_multiplier
    return estimated_calories
