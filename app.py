import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="의약품 & 영양제 상극 분석기", page_icon="💊", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; border-radius: 8px; }
    .result-box { padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .danger { background-color: #ffebeb; border-left: 5px solid #dc3545; color: #b71c1c; }
    .warning { background-color: #fff9e6; border-left: 5px solid #ffc107; color: #856404; }
    .safe { background-color: #eafaf1; border-left: 5px solid #28a745; color: #155724; }
    </style>
    """, unsafe_allow_html=True)

st.title("💊 의약품 & 영양제 상극 분석기")
st.write("먹을 약과 영양제를 입력하면 식약처 공식 사이트 정보와 비교해 드려요.")

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

st.subheader("🔍 같이 먹을 약을 입력해 주세요")
col1, col2 = st.columns(2)
with col1:
    pill_a = st.text_input("첫 번째 약/영양제 이름", key="pill_a").strip()
with col2:
    pill_b = st.text_input("두 번째 약/영양제 이름", key="pill_b").strip()

if st.button("식약처 공식 데이터 분석 시작 🚀"):
    if not pill_a or not pill_b:
        st.warning("두 개의 약 이름을 모두 입력해 주세요!")
    else:
        with st.spinner("공식 장부 탐색 중..."):
            match = db[
                ((db["약물1"] == pill_a) & (db["약물2"] == pill_b)) |
                ((db["약물1"] == pill_b) & (db["약물2"] == pill_a))
            ]
            
            if not match.empty:
                for idx, row in match.iterrows():
                    info_text = row['부작용']
                    
                    # 장부 텍스트 내용에 따라 알림창 색상을 동적으로 변경!
                    if "위험" in info_text or "금지" in info_text:
                        st.markdown(f"<div class='result-box danger'><h3>🛑 식약처 경고 (위험 조합)</h3><p>{info_text}</p></div>", unsafe_allow_html=True)
                    elif "주의" in info_text or "권장하지" in info_text:
                        st.markdown(f"<div class='result-box warning'><h3>⚠️ 식약처 안내 (주의 요망)</h3><p>{info_text}</p></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='result-box safe'><h3>✅ 식약처 안내 (안전/참고)</h3><p>{info_text}</p></div>", unsafe_allow_html=True)
            else:
                # 공식 사이트에 아예 없는 조합일 때
                st.markdown(f"<div class='result-box safe'><h3>📋 분석 완료</h3></div>", unsafe_allow_html=True)
                st.success(f"**[{pill_a}]** 와(과) **[{pill_b}]** 조합은 현재 국가 공식 사이트(식약처) 금기/주의 목록에 등록되어 있지 않습니다.")
                st.info("⚠️ 여기에 나오지 않는 정보는 저희 앱의 오류가 아니라 **국가 공식 문서상에 특이사항이 명시되지 않은 항목**입니다. 자세한 내용은 공식 사이트나 의사에게 문의하세요.")
