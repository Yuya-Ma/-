
import streamlit as st
import pandas as pd
import random

# タイトル
st.title("英単語テスト - 4択式（入門編）")

# Excelからデータ読み込み
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="作成")
    left_pairs = df[['英語', '日本語']].dropna()
    right_pairs = df[['英語.1', '日本語.1']].dropna()
    right_pairs.columns = ['英語', '日本語']
    all_pairs = pd.concat([left_pairs, right_pairs], ignore_index=True)
    return all_pairs

data = load_data()

# 出題方向
direction = st.radio("出題方向を選択", ("英語 → 日本語", "日本語 → 英語"))

# 出題数
num_questions = st.radio("出題数を選択", (10, 20))

# 問題生成関数
def generate_questions(df, direction="英語 → 日本語", num_questions=10):
    questions = []
    for _ in range(num_questions):
        correct_row = df.sample(1).iloc[0]
        if direction == "英語 → 日本語":
            question = correct_row['英語']
            answer = correct_row['日本語']
            choices_pool = df['日本語'].tolist()
        else:
            question = correct_row['日本語']
            answer = correct_row['英語']
            choices_pool = df['英語'].tolist()
        distractors = random.sample([c for c in choices_pool if c != answer], 3)
        choices = distractors + [answer]
        random.shuffle(choices)
        questions.append({"question": question, "choices": choices, "answer": answer})
    return questions

# セッションに問題と回答を保持
if 'quiz' not in st.session_state:
    st.session_state.quiz = generate_questions(data, direction, num_questions)
    st.session_state.user_answers = [None] * num_questions

# 回答リセットボタン
if st.button("テストを再作成"):
    st.session_state.quiz = generate_questions(data, direction, num_questions)
    st.session_state.user_answers = [None] * num_questions

# 問題表示
st.write("### テスト問題")
for i, q in enumerate(st.session_state.quiz):
    st.write(f"**Q{i+1}:** {q['question']}")
    st.session_state.user_answers[i] = st.radio(
        f"選択肢 {i+1}", q['choices'], key=f"q{i}"
    )

# 採点
if st.button("採点する"):
    score = 0
    for i, q in enumerate(st.session_state.quiz):
        if st.session_state.user_answers[i] == q['answer']:
            score += 1
    st.write("---")
    st.success(f"正解数: {score} / {num_questions}")
    for i, q in enumerate(st.session_state.quiz):
        is_correct = st.session_state.user_answers[i] == q['answer']
        result = "✅ 正解" if is_correct else f"❌ 不正解（正解: {q['answer']}）"
        st.write(f"Q{i+1}: {result}")
