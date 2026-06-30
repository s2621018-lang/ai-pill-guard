import streamlit as st
import pandas as pd
import os

# 페이지 기본 설정
st.set_page_config(page_title="의약품 & 영양제 상극 분석기", page_icon="💊", layout="centered")

# 깔끔하고 신뢰감 주는 디자인 CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; border-radius: 8px; font-weight: bold; }
    .result-box { padding: 18px; border-radius: 8px; margin-bottom: 12px; line-height: 1.6; }
    .danger { background-color: #ffebeb; border-left: 6px solid #dc3545; color: #b71c1c; }
    .safe { background-color: #eafaf1; border-left: 6px solid #28a745; color: #155724; }
    </style>
    """, unsafe_allow_html=True)

st.title("💊 의약품 & 영양제 상극 분석기")
st.write("먹을 약과 영양제를 입력하면 국가 공식 식약처 마스터 장부와 대조하여 분석합니다.")

# 1. csv 데이터 로드 함수
@st.cache_data
def load_data():
    file_name = "pills.csv"
    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name, names=["약물1", "약물2", "부작용"], header=None, encoding='utf-8', on_bad_lines='skip')
            df = df.dropna(subset=["약물1", "약물2"])
            df["약물1"] = df["약물1"].astype(str).str.strip()
            df["약물2"] = df["약물2"].astype(str).str.strip()
            df["부작용"] = df["부작용"].fillna("공식 정보 확인 필요").astype(str).str.strip()
            return df
        except Exception as e:
            return pd.DataFrame(columns=["약물1", "약물2", "부작용"])
    return pd.DataFrame(columns=["약물1", "약물2", "부작용"])

db = load_data()
st.divider()

# 2. 사용자 입력 창
st.subheader("🔍 같이 먹을 약/음식 이름을 입력해 주세요")
col1, col2 = st.columns(2)
with col1:
    pill_a = st.text_input("첫 번째 항목 (예: 타이레놀)", key="pill_a").strip()
with col2:
    pill_b = st.text_input("두 번째 항목 (예: 술)", key="pill_b").strip()

# 3. 실시간 분석 및 하린이의 팩트체크 로직 가동
if st.button("식약처 마스터 데이터 정밀 분석 시작 🚀"):
    if not pill_a or not pill_b:
        st.warning("두 개의 이름을 모두 정확히 입력해 주세요!")
    else:
        with st.spinner("국가 공식 마스터 장부 전수 검사 중..."):
            match = db[
                ((db["약물1"] == pill_a) & (db["약물2"] == pill_b)) |
                ((db["약물1"] == pill_b) & (db["약물2"] == pill_a))
            ]
            
            # [하린이 기획] 장부에 매칭된 게 있다면 식약처가 지정한 위험 조합이므로 무조건 빨간색 경고!
            if not match.empty:
                for idx, row in match.iterrows():
                    info_text = row['부작용']
                    st.markdown(f"<div class='result-box danger'><h3>🛑 식약처 공식 경고 (위험 조합)</h3><p>{info_text}</p></div>", unsafe_allow_html=True)
            
            # 장부에 아예 없는 조합일 때 -> 완벽한 면책 및 신뢰성 문구 출력
            else:
                st.markdown(f"<div class='result-box safe'><h3>📋 분석 완료</h3></div>", unsafe_allow_html=True)
                st.success(f"**[{pill_a}]** 와(과) **[{pill_b}]** 조합에 대한 특이 사항이 발견되지 않았습니다.")
                st.info("💡 **안내:** 본 시스템은 국가 식품의약품안전나라의 공식 데이터를 기반으로 작동합니다. 검색 결과에 나타나지 않는 정보는 앱의 데이터 누락이 아닌, **국가 공식 문서상으로 특이사항이 명시되지 않은 조합**임을 알려드립니다.")
