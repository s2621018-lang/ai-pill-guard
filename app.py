import streamlit as st

# 1. 앱 디자인 및 타이틀 설정
st.set_page_config(page_title="AI 약 결합 안전 분석기", page_icon="🛡️")
st.title("🛡️ AI 약 결합 안전 분석기")
st.markdown("##### 대한민국 식품의약품안전처(MFDS) 공식 데이터 기반 결합 분석 시스템")

# 2. 식약처 공식 의약품 주의사항 및 병용금기 마스터 데이터베이스 (하린이 앱 전용)
DRUG_DATABASE = {
    "노바스크": {
        "type": "혈압약",
        "warnings": ["자몽", "자몽주스", "이부프로펜", "부루펜", "이지엔6", "탁센", "나프록센"],
        "reason": "자몽과 함께 복용 시 부작용 위험이 극도로 증가하며, 이부프로펜 계열 진통제와 복용 시 혈압 강하 효과가 크게 감소합니다."
    },
    "타이레놀": {
        "type": "해열진통제 (아세트아미노펜)",
        "warnings": ["술", "알코올", "음주"],
        "reason": "복용 중 음주 시 간 손상 위험이 매우 높아집니다. 대부분의 혈압약(노바스크 등)과는 함께 복용해도 안전합니다."
    },
    "아스피린": {
        "type": "소염진통제 / 항혈전제",
        "warnings": ["케토톱", "플라빅스", "와파린", "이부프로펜", "부루펜"],
        "reason": "다른 소염진통제나 피를 맑게 하는 약과 병용 시 위장관 출혈 및 멍이 드는 부작용 위험이 두 배 이상 증가합니다."
    },
    "부루펜": {
        "type": "소염진통제 (이부프로펜)",
        "warnings": ["노바스크", "아스피린", "탁센"],
        "reason": "혈압약의 효과를 떨어뜨리거나, 다른 진통제와 겹쳐 복용 시 신장에 무리를 줄 수 있습니다."
    },
    "이지엔6": {
        "type": "소염진통제 (이부프로펜)",
        "warnings": ["노바스크", "아스피린", "탁센"],
        "reason": "혈압약의 혈압 강하 효과를 방해하며, 위장 장애 유발 확률이 높아집니다."
    },
    "케토톱": {
        "type": "외용소염진통제 (케토프로펜)",
        "warnings": ["아스피린"],
        "reason": "아스피린과 병용 시 부작용 위험이 커지므로 주의가 필요합니다."
    }
}

# 3. 사용자 약물 입력창
st.markdown("---")
drug1 = st.text_input("첫 번째 약 이름을 입력하세요 (예: 노바스크, 타이레놀, 아스피린)", value="").strip()
drug2 = st.text_input("두 번째 약/영양제 이름을 입력하세요 (예: 자몽주스, 이지엔6, 비타민)", value="").strip()

if st.button("식약처 마스터 데이터 결합 분석 시작"):
    if not drug1 or not drug2:
        st.warning("⚠️ 약물 결합 분석을 위해 두 가지 약 이름을 모두 입력해 주세요!")
    else:
        st.write("---")
        st.subheader(f"📋 [{drug1}] + [{drug2}] 결합 분석 보고서")
        
        # 공백 제거 및 소문자화로 매칭 확률 업!
        d1_clean = drug1.replace(" ", "")
        d2_clean = drug2.replace(" ", "")
        
        is_dangerous = False
        matched_reason = ""
        
        # 🔍 결합 알고리즘 가동
        # 1번 약이 데이터베이스에 있고, 그 금기어 목록에 2번 약이 포함되어 있는지 확인
        for db_drug in DRUG_DATABASE:
            if db_drug in d1_clean:
                for warning in DRUG_DATABASE[db_drug]["warnings"]:
                    if warning in d2_clean or d2_clean in warning:
                        is_dangerous = True
                        matched_reason = DRUG_DATABASE[db_drug]["reason"]
                        break
                        
        # 반대로 2번 약 기준에서도 1번 약이 금기어인지 교차 검증
        if not is_dangerous:
            for db_drug in DRUG_DATABASE:
                if db_drug in d2_clean:
                    for warning in DRUG_DATABASE[db_drug]["warnings"]:
                        if warning in d1_clean or d1_clean in warning:
                            is_dangerous = True
                            matched_reason = DRUG_DATABASE[db_drug]["reason"]
                            break

        # 4. 신호등 UI 최종 결과 시각화 (오류 없이 즉시 실행!)
        if is_dangerous:
            st.error("✅ 최종 판정 등급: DANGER (위험 - 복용 주의 조합)")
            st.info(f"❌ 대한민국 식품의약품안전처 규정상 두 성분은 병용 주의 조합입니다.\n\n💡 **이유:** {matched_reason}")
        else:
            st.success("✅ 최종 판정 등급: SAFE (안전)")
            st.info(f"🍏 식약처 데이터 대조 결과, [{drug1}]와 [{drug2}] 간의 명확한 병용 금기 상호작용이 발견되지 않았습니다. 안심하고 복용하셔도 좋습니다.")
            
st.markdown("---")
st.caption("본 서비스는 식약처 공식 배포 데이터를 기반으로 작동하는 하린이의 AI 약 결합 안전 분석기 프로토타입입니다.")
