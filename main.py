import streamlit as st
import requests
import pandas as pd

API_KEY = "$2a$10$wkVzPCcsW64wR96r26OsI.HDd3ijLveJn6sxJoSjfzByIRyODPCHq"
BIN_ID = "6926b417ae596e708f71ae61"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

headers = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

st.title("王様カード交換")

# データ取得
res = requests.get(URL, headers=headers)
data = res.json()["record"]

# 欲しいカード登録フォーム
st.subheader("欲しいカードを登録")

# ユーザー名は一行
user = st.text_input("ユーザー名")

# ジャンルとカードを同じ行に並べる
col1, col2 = st.columns(2)
with col1:
    genres = []
    for c in data["cards"]:
        if c["genre"] not in genres:
            genres.append(c["genre"])
    genre = st.selectbox("ジャンルを選択", genres)

with col2:
    cards_in_genre = [c["name"] for c in data["cards"] if c["genre"] == genre]
    card_name = st.selectbox("カードを選択", cards_in_genre)

if st.button("登録"):
    new_trade = {"user": user, "want": {"genre": genre, "name": card_name}}
    data["trades"].append(new_trade)
    requests.put(URL, headers=headers, json=data)
    st.success("欲しいカードを登録しました！")
    st.rerun()

# 登録済み一覧を表で表示
st.subheader("登録済みの欲しいカード一覧")
if data["trades"]:
    df = pd.DataFrame([
        {"ユーザー": t["user"], "ジャンル": t["want"]["genre"], "カード名": t["want"]["name"]}
        for t in data["trades"]
    ])
    st.dataframe(df, use_container_width=True)
else:
    st.info("まだ登録はありません。")

# 登録済み削除フォーム
st.subheader("登録済みの欲しいカードを削除")

if data["trades"]:
    # ユーザー名は一行
    users = sorted(set([t["user"] for t in data["trades"]]))
    selected_user = st.selectbox("ユーザーを選択", users)

    user_trades = [t for t in data["trades"] if t["user"] == selected_user]
    genres_for_user = sorted(set([t["want"]["genre"] for t in user_trades]))

    # ジャンルとカードを同じ行に並べる
    col1, col2 = st.columns(2)
    with col1:
        selected_genre = st.selectbox("ジャンルを選択", genres_for_user)
    with col2:
        cards_for_genre = [t["want"]["name"] for t in user_trades if t["want"]["genre"] == selected_genre]
        selected_card = st.selectbox("カードを選択", cards_for_genre)

    if st.button("🗑️ 削除"):
        data["trades"] = [t for t in data["trades"] if not (
            t["user"] == selected_user and 
            t["want"]["genre"] == selected_genre and 
            t["want"]["name"] == selected_card
        )]
        requests.put(URL, headers=headers, json=data)
        st.success("削除しました！")
        st.rerun()
else:
    st.info("まだ登録はありません。")
