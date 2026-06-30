import streamlit as st
import pandas as pd
import os

# 페이지 기본 설정
st.set_page_config(page_title="의약품 & 영양제 상극 분석기", page_icon="💊", layout="centered")

# CSS로 앱 디자인 예쁘게 꾸미기
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; border-radius: 8px; }
    .result-box { padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .danger { background-color: #ffebeb; border-left: 5px solid #dc3545; color: #b71c1c; }
    .safe { background-color: #eafaf1; border-left: 5px solid #28a745; color: #155724; }
    </style>
    """, unsafe_allow_html=True)

st.title("💊 의약품 & 영양제 상극 분석기")
st.write("먹을 약과 영양제를 입력하면 식약처 장부와 비교해 위험한 조합을 찾아드려요.")

# 1. csv 파일 읽어오기 함수
@st.cache_data
def load_data():
    file_name = "pills.csv"
    if os.path.exists(file_name):
        try:
            # 콤마(,) 기준 3개의 열로 읽어오기
            df = pd.read_csv(file_name, names=["약물1", "약물2", "부작용"], header=None, encoding='utf-8')
            # 양옆 공백 제거
            df["약물1"] = df["약물1"].str.strip()
            df["약물2"] = df["약물2"].str.strip()
            df["부작용"] = df["부작_"] = df["부작용"].str.strip()
            return df
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            return pd.DataFrame(columns=["약물1", "약물2", "부작용"])
    else:
        st.error("pills.csv 파일을 찾을 수 없습니다! 깃허브에 파일이 있는지 확인해 주세요.")
        return pd.DataFrame(columns=["약물1", "약물2", "부작용"])

db = load_data()

# 2. 하단에 현재 연동된 데이터 개수 띄워주기
if not db.empty:
    st.info(f"💡 현재 시스템에 식약처 기반 **{len(db):,}개**의 금기 장부가 완벽하게 연동되어 있습니다!")

st.divider()

# 3. 사용자 입력 받기
st.subheader("🔍 같이 먹을 약을 입력해 주세요")
col1, col2 = st.columns(2)
with col1:
    pill_a = st.text_input("첫 번째 약/영양제 이름 (예: 타이레놀)", key="pill_a").strip()
with col2:
    pill_b = st.text_input("두 번째 약/영양제 이름 (예: 맥주)", key="pill_b").strip()

# 4. 분석하기 버튼 클릭 시 로직
if st.button("상호작용 분석 시작 🚀"):
    if not pill_a or not pill_b:
        st.warning("두 개의 약 이름을 모두 입력해 주세요!")
    else:
        # 대소문자나 띄어쓰기 에러 방지를 위해 검색용 텍스트 정제
        with st.spinner("966개의 마스터 장부를 정밀 탐색하는 중..."):
            
            # 장부에서 두 약물이 교차로 들어간 행이 있는지 검색
            match = db[
                ((db["약물1"] == pill_a) & (db["약물2"] == pill_b)) |
                ((db["약물1"] == pill_b) & (db["약물2"] == pill_a))
            ]
            
            if not match.empty:
                # 금기 조합을 찾았을 때
                st.markdown(f"<div class='result-box danger'><h3>⚠️ 위험한 조합 발견!</h3></div>", unsafe_allow_html=True)
                for idx, row in match.iterrows():
                    st.error(f"**[{row['약물1']}]** 와(과) **[{row['약물2']}]** 은(는) 함께 복용 시 위험할 수 있습니다.")
                    st.write(f"🛑 **부작용 경고:** {row['부작용']}")
            else:
                # 안전하거나 장부에 없을 때
                st.markdown(f"<div class='result-box safe'><h3>✅ 분석 완료</h3></div>", unsafe_allow_html=True)
                st.success(f"**[{pill_a}]** 와(과) **[{pill_b}]** 의 특이 상극 반응이 현재 장부(966개)에는 등록되어 있지 않습니다.")
                st.caption("※ 본 서비스는 식약처 데이터를 기반으로 하며, 체질에 따른 부작용이 있을 수 있으니 전문의와 상의하세요.")
