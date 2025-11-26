import streamlit as st
import requests
import pandas as pd

API_KEY = "$2a$10$wkVzPCcsW64wR96r26OsI.HDd3ijLveJn6sxJoSjfzByIRyODPCHq"
BIN_ID = "6926b417ae596e708f71ae61"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

headers = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

st.title("カード交換サイト")

# データ取得
res = requests.get(URL, headers=headers)
data = res.json()["record"]

# 欲しいカード登録フォーム
st.subheader("欲しいカードを登録")
user = st.text_input("ユーザー名")

# ジャンル選択（順番保持）
genres = []
for c in data["cards"]:
    if c["genre"] not in genres:
        genres.append(c["genre"])

genre = st.selectbox("ジャンルを選択", genres)

# 選んだジャンルのカード一覧から選択（順番保持）
cards_in_genre = [c["name"] for c in data["cards"] if c["genre"] == genre]
card_name = st.selectbox("カードを選択", cards_in_genre)

if st.button("登録"):
    new_trade = {"user": user, "want": {"genre": genre, "name": card_name}}
    data["trades"].append(new_trade)
    requests.put(URL, headers=headers, json=data)
    st.success("欲しいカードを登録しました！")
    st.rerun()  # 登録後に即更新

# 登録済みリストを DataFrame で表示
st.subheader("登録済みの欲しいカード")

if data["trades"]:
    # 表用データに変換
    df = pd.DataFrame([
        {"ユーザー": t["user"], "ジャンル": t["want"]["genre"], "カード名": t["want"]["name"]}
        for t in data["trades"]
    ])
    st.dataframe(df, use_container_width=True)

    # 削除ボタンを各行の右側に配置
    for i, trade in enumerate(data["trades"]):
        cols = st.columns([4, 1])  # 左に情報、右に削除ボタン
        with cols[0]:
            st.write(f"{trade['user']} さん → {trade['want']['genre']} / {trade['want']['name']}")
        with cols[1]:
            if st.button("🗑️ 削除", key=f"delete_{i}"):
                data["trades"].pop(i)
                requests.put(URL, headers=headers, json=data)
                st.success("削除しました！")
                st.rerun()  # 削除後に即更新
else:
    st.info("まだ登録はありません。")
