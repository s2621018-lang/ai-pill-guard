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

# 1. csv 파일 읽어오기 함수 (에러 방어벽 탑재)
@st.cache_data
def load_data():
    file_name = "pills.csv"
    if os.path.exists(file_name):
        try:
            # 콤마 오타가 난 줄이 있으면 에러를 내지 않고 스킵합니다!
            df = pd.read_csv(
                file_name, 
                names=["약물1", "약물2", "부작용"], 
                header=None, 
                encoding='utf-8',
                on_bad_lines='skip'
            )
            # 결측치 제거 및 텍스트 공백 제거
            df = df.dropna(subset=["약물1", "약물2"])
            df["약물1"] = df["약물1"].astype(str).str.strip()
            df["약물2"] = df["약물2"].astype(str).str.strip()
            df["부작용"] = df["부작용"].fillna("상호작용 주의 필요").astype(str).str.strip()
            return df
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            return pd.DataFrame(columns=["약물1", "약물2", "부작용"])
    else:
        st.error("pills.csv 파일을 찾을 수 없습니다! 깃허브에 파일이 있는지 확인해 주세요.")
        return pd.DataFrame(columns=["약물1", "약물2", "부작용"])

db = load_data()

st.divider()

# 2. 사용자 입력 받기
st.subheader("🔍 같이 먹을 약을 입력해 주세요")
col1, col2 = st.columns(2)
with col1:
    pill_a = st.text_input("첫 번째 약/영양제 이름 (예: 타이레놀)", key="pill_a").strip()
with col2:
    pill_b = st.text_input("두 번째 약/영양제 이름 (예: 맥주)", key="pill_b").strip()

# 3. 분석하기 버튼 클릭 시 로직
if st.button("상호작용 분석 시작 🚀"):
    if not pill_a or not pill_b:
        st.warning("두 개의 약 이름을 모두 입력해 주세요!")
    else:
        with st.spinner("마스터 장부를 정밀 탐색하는 중..."):
            
            # 장부에서 두 약물이 교차로 들어간 행이 있는지 검색
            match = db[
                ((db["약물1"] == pill_a) & (db["약물2"] == pill_b)) |
                ((db["약물1"] == pill_b) & (db["약물2"] == pill_a))
            ]
            
            if not match.empty:
                st.markdown(f"<div class='result-box danger'><h3>⚠️ 위험한 조합 발견!</h3></div>", unsafe_allow_html=True)
                for idx, row in match.iterrows():
                    st.error(f"**[{row['약물1']}]** 와(과) **[{row['약물2']}]** 은(는) 함께 복용 시 위험할 수 있습니다.")
                    st.write(f"🛑 **부작용 경고:** {row['부작용']}")
            else:
                st.markdown(f"<div class='result-box safe'><h3>✅ 분석 완료</h3></div>", unsafe_allow_html=True)
                # 하린이의 요청에 따라 결과 메시지에서도 장부 개수(966개) 문구를 삭제했습니다!
                st.success(f"**[{pill_a}]** 와(과) **[{pill_b}]** 의 특이 상극 반응이 현재 장부에는 등록되어 있지 않습니다.")
                st.caption("※ 본 서비스는 식약처 데이터를 기반으로 하며, 체질에 따른 부작용이 있을 수 있으니 전문의와 상의하세요.")
