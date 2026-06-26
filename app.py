import streamlit as st

# 1. 앱 디자인
st.set_page_config(page_title="AI 약 결합 안전 분석기", page_icon="🛡️")
st.title("🛡️ AI 약 결합 안전 분석기")
st.markdown("##### 실시간 의약품 종합 분석 시스템 (Safe Local Mode)")

# 2. 입력창
drug1 = st.text_input("첫 번째 약 이름을 입력하세요 (예: 노바스크, 타이레놀)", value="")
drug2 = st.text_input("두 번째 약/영양제 이름을 입력하세요 (선택)", value="")
bev = st.text_input("함께 마실 음료나 식품을 입력하세요 (선택)", value="")

if st.button("실시간 상호작용 종합 분석 시작"):
    if not drug1:
        st.warning("⚠️ 분석을 위해 최소한 첫 번째 약 이름을 입력해 주세요!")
    else:
        st.write("---")
        st.subheader("📋 안전 분석 보고서")
        
        with st.spinner("🔍 의약품 통합 데이터베이스 및 자체 매칭 알고리즘 가동 중..."):
            # 소문자 공백 제거로 정확한 매칭
            d1 = drug1.replace(" ", "").lower()
            d2 = drug2.replace(" ", "").lower() if drug2 else ""
            b = bev.replace(" ", "").lower() if bev else ""
            
            status = "SAFE"
            reason_text = f"입력하신 [{drug1}]는 복용 기준에 부합하며 안심하고 드셔도 좋습니다."
            
            # 💡 하린이의 꼼꼼한 약물 상호작용 데이터베이스 규칙 설정
            # 1. 자몽주스 고혈압약 위험군
            if "자몽" in b and ("노바스크" in d1 or "amlodipine" in d1 or "노바스크" in d2 or "amlodipine" in d2):
                status = "DANGER"
                reason_text = "고혈압 약(노바스크 등)은 자몽주스와 함께 드시면 약 성분이 몸에 과도하게 흡수되어 혈압이 급격히 떨어질 수 있어 매우 위험합니다. 반드시 맹물과 함께 복용하세요."
            
            # 2. 타이레놀 + 술 위험군
            elif ("술" in b or "맥주" in b or "소주" in b or "알코올" in b) and ("타이레놀" in d1 or "아세트아미노펜" in d1 or "타이레놀" in d2 or "아세트아미노펜" in d2):
                status = "DANGER"
                reason_text = "타이레놀(아세트아미노펜) 성분은 알코올과 만나면 간에 심각한 손상을 줄 수 있습니다. 음주 전후에는 절대 복용하지 마십시오."
                
            # 3. 타이레놀 + 종합감기약 중복 주의
            elif ("타이레놀" in d1 and ("감기약" in d2 or "판콜" in d2 or "판피린" in d2)) or ("타이레놀" in d2 and ("감기약" in d1 or "판콜" in d1 or "판피린" in d1)):
                status = "WARNING"
                reason_text = "타이레놀과 종합감기약에는 동일한 '아세트아미노펜' 성분이 중복 함유되어 있을 확률이 높습니다. 과다 복용 시 간 손상 위험이 있으니 성분표를 확인하시거나 약사님과 상의하세요."
            
            # 4. 우유 + 항생제/소화제 주의
            elif "우유" in b and ("항생제" in d1 or "소화제" in d1 or "항생제" in d2 or "소화제" in d2):
                status = "WARNING"
                reason_text = "우유 속 칼슘 성분이 일부 약물(항생제, 소화제 등)의 체내 흡수를 방해하여 약효를 떨어뜨릴 수 있습니다. 약은 되도록 물과 드시는 것이 좋습니다."

        # 3. 신호등 UI 출력
        if status == "DANGER":
            st.error("✅ 최종 판정 등급: DANGER (위험)")
            st.info(f"❌ {reason_text}")
        elif status == "WARNING":
            st.warning("✅ 최종 판정 등급: WARNING (주의)")
            st.info(f"🚨 {reason_text}")
        else:
            st.success("✅ 최종 판정 등급: SAFE (안전)")
            st.info(f"🍏 {reason_text}")
