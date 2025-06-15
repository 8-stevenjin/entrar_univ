import streamlit as st
import pandas as pd
from logic.calc_score import calculate_score

st.set_page_config(page_title="대학가야지!!", layout="wide")
st.markdown("<h1 style='text-align: center;'>대학가야지!! 🔥🔥🔥</h1>", unsafe_allow_html=True)

# 과목별 선택과목 옵션
subject_options = {
    "국어": ["화법과작문", "언어와매체", "독서"],
    "수학": ["확률과통계", "미적분", "기하"],
    "탐구1": ["생활과윤리", "사회문화", "한국지리", "세계지리", "생명과학I", "화학I"],
    "탐구2": ["생활과윤리", "사회문화", "한국지리", "세계지리", "생명과학II", "화학II"]
}

# 백분위 → 등급 자동 변환 함수
def percent_to_grade(p):
    if p >= 96: return 1
    elif p >= 89: return 2
    elif p >= 77: return 3
    elif p >= 64: return 4
    elif p >= 50: return 5
    elif p >= 36: return 6
    elif p >= 23: return 7
    elif p >= 11: return 8
    else: return 9

# 🎓 성적 입력 UI
st.markdown("### 🎓 수능 성적 입력")
cols = st.columns(5)
row = {}
for i, subject in enumerate(["국어", "수학", "영어", "탐구1", "탐구2"]):
    with cols[i]:
        selected = None
        if subject != "영어":
            selected = st.selectbox(f"{subject} 선택과목", subject_options[subject], key=f"sel_{subject}")
            per = st.number_input(f"{subject} 백분위", min_value=0.0, max_value=100.0, value=0.0, key=f"per_{subject}")
            grade = percent_to_grade(per)
        else:
            grade = st.selectbox(f"{subject} 등급", list(range(1, 10)), key=f"grade_{subject}")
            st.markdown(" ")  # 줄 정렬용
            per = None  # 영어는 백분위 없음

        row[subject] = {
            "선택과목": selected if subject != "영어" else None,
            "백분위": per,
            "등급": grade
        }

# 조회 조건
col1, col2 = st.columns(2)
with col1:
    계열 = st.selectbox("계열", ["전체", "인문", "자연"])
with col2:
    대학 = st.selectbox("대학교", ["전체", "건국대학교", "고려대학교", "경희대학교"])

# 조회 버튼 스타일 적용
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #ff6b6b;
        color: navy;
        font-weight: bold;
        font-size: 18px;
        padding: 0.5em 2em;
        border-radius: 8px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# 조회 실행
if st.button("🔥🔥🔥 조회하기 🔥🔥🔥"):
    input_data = row

    @st.cache_data
    def load_standard_table():
        return pd.read_csv("data/기준점수통합.csv")

    @st.cache_data
    def load_weights():
        return pd.read_csv("data/weights.csv")

    @st.cache_data
    def load_english_scores():
        return pd.read_csv("data/english_score.csv")

    df_base = load_standard_table()
    weights_df = load_weights()
    english_df = load_english_scores()

    if 대학 != "전체":
        df_base = df_base[df_base["대학명"] == 대학]
    if 계열 != "전체":
        df_base = df_base[df_base["계열"] == 계열]

    result_rows = []
    for _, row_ in df_base.iterrows():
        univ = row_["대학명"]
        major_type = row_["계열"]
        기준 = row_["기준점수(백분위)"]

        total_score = calculate_score(input_data, univ, major_type, weights_df, english_df)
        total_score = float(f"{total_score:.2f}")  # 소수점 둘째자리 고정

        판별 = (
            "가능" if total_score >= 기준
            else "경고" if total_score >= 기준 * 0.9
            else "불가능"
        )

        result_rows.append({
            "대학명": univ,
            "계열": major_type,
            "학과명": row_["학과명"],
            "기준점수(백분위)": 기준,
            "내 백분위 총점": total_score,
            "판별결과": 판별
        })

    # 🎯 결과 출력
    st.markdown("### 📊 결과 조회 (백분위 기준)")

    def color_result(val):
        if val == "가능": return "color: green; font-weight: bold;"
        elif val == "경고": return "color: orange; font-weight: bold;"
        else: return "color: red; font-weight: bold;"

    df_result = pd.DataFrame(result_rows)

    styled_df = df_result.style \
        .format({
            "기준점수(백분위)": "{:.2f}",
            "내 백분위 총점": "{:.2f}"
        }) \
        .applymap(color_result, subset=["판별결과"])

    st.dataframe(styled_df, use_container_width=True)
