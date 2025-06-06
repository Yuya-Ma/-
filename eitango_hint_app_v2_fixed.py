
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="英単語テスト（ヒント付き・日⇄英対応）", layout="centered")

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="作成")
    left = df[["Unnamed: 0", "英語", "日本語"]].dropna()
    right = df[["No.", "英語.1", "日本語.1"]].dropna()
    left.columns = ["単語番号", "英語", "日本語"]
    right.columns = ["単語番号", "英語", "日本語"]
    all_data = pd.concat([left, right], ignore_index=True)
    all_data["単語番号"] = all_data["単語番号"].astype(int)
    return all_data

df = load_data()

st.title("英単語テスト（日⇄英・ヒント付き・自己採点式）")

# 出題方向の選択
direction = st.radio("出題方向", ["英語 → 日本語", "日本語 → 英語"])

# 単語番号の範囲指定
col1, col2 = st.columns(2)
with col1:
    start_no = st.number_input("開始番号（例：100）", min_value=1, step=1)
with col2:
    end_no = st.number_input("終了番号（例：300）", min_value=1, step=1)

# ステート初期化
if "page" not in st.session_state:
    st.session_state.page = "quiz"
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "show_hints" not in st.session_state:
    st.session_state.show_hints = set()

# 出題準備
if st.button("テストを作成する"):
    if start_no >= end_no:
        st.error("開始番号は終了番号より小さくしてください。")
    else:
        filtered = df[(df["単語番号"] >= start_no) & (df["単語番号"] <= end_no)]
        if len(filtered) < 1:
            st.warning("指定範囲に単語がありません。")
        else:
            st.session_state.quiz_data = filtered.sample(n=min(20, len(filtered))).reset_index(drop=True).to_dict("records")
            st.session_state.show_hints = set()
            st.session_state.page = "quiz"

# クイズページ
if st.session_state.page == "quiz" and st.session_state.quiz_data:
    st.subheader("問題（最大20問）")
    for i, row in enumerate(st.session_state.quiz_data):
        q_key = f"hint_{i}"
        # 出題テキスト
        if direction == "英語 → 日本語":
            prompt = row["英語"]
            answer = row["日本語"]
            hint_pool = df["日本語"].tolist()
        else:
            prompt = row["日本語"]
            answer = row["英語"]
            hint_pool = df["英語"].tolist()

        st.markdown(f"**Q{i+1}.（No.{row['単語番号']}）** {prompt}")
        if st.button("ヒントを見る", key=q_key):
            st.session_state.show_hints.add(i)
        if i in st.session_state.show_hints:
            choices = random.sample([c for c in hint_pool if c != answer], 3)
            choices.append(answer)
            random.shuffle(choices)
            st.radio(
                f"Q{i+1} の選択肢",
                options=choices,
                index=None,
                key=f"opt_{i}"
            )
    if st.button("解答を見る"):
        st.session_state.page = "answer"

# 解答ページ
if st.session_state.page == "answer":
    st.subheader("解答一覧（自己採点）")
    for i, row in enumerate(st.session_state.quiz_data):
        if direction == "英語 → 日本語":
            prompt = row["英語"]
            answer = row["日本語"]
        else:
            prompt = row["日本語"]
            answer = row["英語"]
        st.markdown(f"**Q{i+1}.（No.{row['単語番号']}）** {prompt} → ✅ {answer}")
    if st.button("もう一度テストを作成する"):
        st.session_state.page = "quiz"
