import streamlit as st
import requests
import xml.etree.ElementTree as ET

# 1. 앱 디자인
st.set_page_config(page_title="AI 약 결합 안전 분석기", page_icon="🛡️")
st.title("🛡️ AI 약 결합 안전 분석기")
st.markdown("##### 식품의약품안전처 공식 '병용금기' 실시간 결합 분석 시스템")

# 2. 식약처 병용금기 API 서버와 통신하는 함수
def check_dur_interaction(service_key, drug_a, drug_b):
    # 식약처 의약품 안전성 정보(DUR) 병용금기 지정 URL
    url = "https://apis.data.go.kr/1471000/DURPrductntfInfoService03/getUsgAtentInforegList03"
    
    # 약물 A를 기준으로 병용금기 데이터 검색
    params = {
        'serviceKey': service_key,
        'itemName': drug_a,
        'pageNo': '1',
        'numOfRows': '100'  # 금기 조합을 넉넉히 가져와서 비교
    }
    
    response = requests.get(url, params=params, timeout=4)
    return response

# 3. 입력창 (하린이의 원래 기획대로 약 두 개를 입력받음!)
drug1 = st.text_input("첫 번째 약 이름을 입력하세요 (예: 노바스크, 타이레놀)", value="")
drug2 = st.text_input("두 번째 약/영양제 이름을 입력하세요 (예: 플라빅스, 아스피린)", value="")

if st.button("식약처 실시간 결합 안전성 분석 시작"):
    if not drug1 or not drug2:
        st.warning("⚠️ 약물 결합 분석을 위해 두 가지 약 이름을 모두 입력해 주세요!")
    else:
        st.write("---")
        st.subheader(f"📋 [{drug1}] + [{drug2}] 결합 분석 보고서")
        
        with st.spinner("🏥 대한민국 식약처 DUR 금기 데이터베이스 실시간 교차 대조 중..."):
            response = None
            
            # 이중화 인증키 허브 가동 (하린이의 이중 열쇠 시스템)
            try:
                key1 = st.secrets["DATA_KEY_1"]
                res = check_dur_interaction(key1, drug1, drug2)
                if res.status_code == 200 and "INVALID_" not in res.text:
                    response = res
            except:
                pass

            if response is None:
                try:
                    key2 = st.secrets["DATA_KEY_2"]
                    res = check_dur_interaction(key2, drug1, drug2)
                    if res.status_code == 200 and "INVALID_" not in res.text:
                        response = res
                except:
                    pass

            # 4. 결합 위험성 판정 알고리즘
            if response is not None:
                try:
                    root = ET.fromstring(response.text)
                    items = root.findall(".//item")
                    
                    is_dangerous = False
                    reason_text = ""
                    prohbt_reason = "" # 금기 사유
                    
                    # 입력된 두 약물의 공백을 제거하여 매칭 확률 업
                    d2_clean = drug2.replace(" ", "").lower()
                    
                    # 식약처에서 가져온 약물A의 병용금기 리스트를 하나씩 돌며 약물B가 포함되어 있는지 대조
                    for item in items:
                        mixture_item = item.find("MIXTURE_ITEM_NAME") # 함께 먹으면 안 되는 약 이름 칸
                        if mixture_item is not None and mixture_item.text:
                            mix_name = mixture_item.text.replace(" ", "").lower()
                            
                            # 금기 리스트에 사용자가 입력한 두 번째 약(drug2)이 걸려들었을 때!
                            if d2_clean in mix_name or mix_name in d2_clean:
                                is_dangerous = True
                                # 식약처가 지정한 공식 금기 사유 추출
                                reason_el = item.find("PROHBT_CONTENT")
                                if reason_el is not None and reason_el.text:
                                    prohbt_reason = reason_el.text
                                break
                    
                    # 5. 신호등 UI 최종 출력
                    if is_dangerous:
                        st.error("✅ 최종 판정 등급: DANGER (위험 - 병용 금기)")
                        st.info(f"❌ 대한민국 식품의약품안전처 규정상 두 약물은 함께 복용해서는 안 되는 '병용금기' 조합입니다.")
                        if prohbt_reason:
                            st.warning(f"💡 식약처 지정 사유: {prohbt_reason}")
                    else:
                        st.success("✅ 최종 판정 등급: SAFE (안전)")
                        st.info(f"🍏 식약처 DUR 실시간 조회 결과, [{drug1}]와 [{drug2}]의 공식적인 병용 금기 상호작용은 발견되지 않았습니다. 안심하셔도 좋습니다. (단, 특이 체질의 경우 의사 상의 필요)")
                        
                except Exception as parse_error:
                    st.error("❌ 식약처 데이터를 분석하는 과정에서 오류가 발생했습니다.")
            else:
                st.error("❌ 식약처 서버 연동에 실패했습니다. 인증키를 다시 확인해 주세요.")
