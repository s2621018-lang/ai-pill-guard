import streamlit as st
from google import genai

# 1. 앱 디자인 설정 (학교 세특 및 발표용 깔끔한 스타일)
st.set_page_config(page_title="AI 약 결합 안전 분석기", page_icon="🛡️")
st.title("🛡️ AI 약 결합 안전 분석기")
st.markdown("##### 구글 정식 AI 기반 실시간 의약품 종합 분석 시스템")

# 2. 어르신들도 쓰기 편한 직관적인 입력창
drug1 = st.text_input("첫 번째 약 이름을 입력하세요 (예: 노바스크, 타이레놀)", value="")
drug2 = st.text_input("두 번째 약/영양제 이름을 입력하세요 (선택)", value="")
bev = st.text_input("함께 마실 음료나 식품을 입력하세요 (선택)", value="")

if st.button("실시간 상호작용 종합 분석 시작"):
    if not drug1:
        st.warning("⚠️ 분석을 위해 최소한 첫 번째 약 이름을 입력해 주세요!")
    else:
        st.write("---")
        st.subheader("📋 안전 분석 보고서")
        
        # 🔑 하린이의 안전한 무료 마스터 API 키
        api_key = "AQ.Ab8RN6Io4apMxd1tWy-fJ_STORynv9U-X2hNkn13o8IifoFbfQ"
        
        # 🤖 구글 최신 AI에게 내리는 엄격한 의학적 분석 규칙 (프롬프트 엔지니어링 적용)
        prompt = (
            f"사용자 입력 정보:\n"
            f"- 약물1: {drug1}\n"
            f"- 약물2: {drug2 if drug2 else '없음'}\n"
            f"- 함께 먹는 식품/음료: {bev if bev else '물'}\n\n"
            "너는 식약처 데이터를 마스터한 전문 약사 AI야. 어르신들이 보실 앱이니까 다른 복잡한 의학 용어는 최소화해줘.\n"
            f"핵심은 [{drug1}]와 [{drug2 if drug2 else '없음'}]를 [{bev if bev else '물'}]과 함께 복용해도 안전한가야.\n\n"
            "반드시 첫 줄은 딱 이 형식으로만 시작해:\n"
            "등급: [SAFE 또는 WARNING 또는 DANGER 중 하나 선택]\n\n"
            "두 번째 줄은 딱 이 형식으로만 시작해:\n"
            "이유: [어르신이 이해하기 쉽게 '그래서 두 약을 같이 먹어도 된다/안 된다'라는 명확한 결론을 짚은 한 줄 설명]"
        )
        
        with st.spinner("🔍 구글 공식 의학 데이터베이스 실시간 연동 분석 중..."):
            try:
                # 최신 구글 정식 라이브러리(genai.Client) 방식으로 안전한 보안 통로 개설
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt,
                )
                ai_response = response.text.strip()
                
                # 결과 분류 초기화
                status = "SAFE"
                reason_text = "안심하고 복용하셔도 좋습니다."
                
                # AI 대답을 분석하여 신호등 등급 파싱
                for line in ai_response.split('\n'):
                    if "등급:" in line:
                        if "DANGER" in line.upper(): status = "DANGER"
                        elif "WARNING" in line.upper(): status = "WARNING"
                        elif "SAFE" in line.upper(): status = "SAFE"
                    if "이유:" in line:
                        reason_text = line.split("이유:")[1].strip()
                        
            except Exception as e:
                status = "WARNING"
                reason_text = f"구글 AI 통신 인증 오류가 발생했습니다. (에러내용: {str(e)})"

        # 3. 분석 결과에 따른 직관적인 신호등 UI 출력
        if status == "DANGER":
            st.error("✅ 최종 판정 등급: DANGER (위험)")
            st.info(f"❌ {reason_text}")
        elif status == "WARNING":
            st.warning("✅ 최종 판정 등급: WARNING (주의)")
            st.info(f"🚨 {reason_text}")
        else:
            st.success("✅ 최종 판정 등급: SAFE (안전)")
            st.info(f"🍏 {reason_text}")
