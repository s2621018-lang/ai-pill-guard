import streamlit as st
import requests
import xml.etree.ElementTree as ET

# 1. 앱 디자인
st.set_page_config(page_title="AI 약 결합 안전 분석기", page_icon="🛡️")
st.title("🛡️ AI 약 결합 안전 분석기")
st.markdown("##### 식품의약품안전처 공식 데이터 이중화 연동 시스템 (Fail-Safe Mode)")

# 2. 식약처 서버와 통신하는 핵심 함수 구상
def fetch_drug_info(service_key, drug_name):
    url = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
    params = {
        'serviceKey': service_key,
        'itemName': drug_name,
        'pageNo': '1',
        'numOfRows': '1'
    }
    # 3초 동안 응답 없으면 타임아웃 에러를 내도록 설정
    response = requests.get(url, params=params, timeout=3)
    return response

# 3. 입력창
drug_name = st.text_input("조회할 약 이름을 입력하세요 (예: 타이레놀, 노바스크)", value="")

if st.button("식약처 실시간 약효 및 부작용 분석 시작"):
    if not drug_name:
        st.warning("⚠️ 약 이름을 입력해 주세요!")
    else:
        st.write("---")
        st.subheader(f"📋 식약처 등록 [{drug_name}] 공식 정보")
        
        with st.spinner("🏥 대한민국 식약처 서버 이중 경로 실시간 대조 중..."):
            response = None
            success_key_name = ""
            
            # 🔄 [하린이의 이중화 알고리즘] 
            # 시도 1: 첫 번째 인증키(DATA_KEY_1)로 먼저 찔러보기
            try:
                key1 = st.secrets["DATA_KEY_1"]
                res = fetch_drug_info(key1, drug_name)
                # 서버가 정상 응답(200)을 주고, 결과에 에러 메시지가 없는지 검증
                if res.status_code == 200 and "INVALID_" not in res.text:
                    response = res
                    success_key_name = "인증키 1번"
            except Exception as e:
                pass # 에러가 나면 무시하고 2번 키로 넘어갑니다.

            # 시도 2: 만약 1번 키가 실패했다면, 두 번째 인증키(DATA_KEY_2)로 즉시 자동 전환!
            if response is None:
                try:
                    key2 = st.secrets["DATA_KEY_2"]
                    res = fetch_drug_info(key2, drug_name)
                    if res.status_code == 200 and "INVALID_" not in res.text:
                        response = res
                        success_key_name = "인증키 2번 (교체 완료)"
                except Exception as e:
                    pass

            # 4. 화면 출력 알고리즘
            if response is not None:
                try:
                    root = ET.fromstring(response.text)
                    item = root.find(".//item")
                    
                    if item is not None:
                        # HTML 태그 지워주는 꼼꼼한 세부 필터링
                        def clean_text(element):
                            if element is not None and element.text:
                                import re
                                return re.sub('<[^<]+?>', '', element.text).strip()
                            return "등록된 정보가 없습니다."

                        effect = clean_text(item.find("efcyQesitm"))
                        use_method = clean_text(item.find("useMethodQesitm"))
                        warning = clean_text(item.find("atpnQesitm"))
                        side_effect = clean_text(item.find("seQesitm"))
                        
                        # 몇 번 키로 성공했는지 화면에 슬쩍 표시해 주기!
                        st.success(f"✅ 식약처 데이터베이스 매칭 성공! ({success_key_name} 사용됨)")
                        
                        st.markdown("### 🍏 이 약의 효능")
                        st.info(effect)
                        
                        st.markdown("### 🕒 올바른 복용 방법")
                        st.info(use_method)
                        
                        st.markdown("### 🚨 복용 시 주의사항 (병용 금기 및 식품)")
                        st.warning(warning)
                        
                        st.markdown("### ❌ 발생 가능한 부작용")
                        st.error(side_effect)
                    else:
                        st.warning(f"🔍 식약처에 [{drug_name}] 등록 정보를 찾지 못했습니다. 이름을 확인해 주세요.")
                except Exception as parse_error:
                    st.error("❌ 데이터 해석 중 오류가 발생했습니다.")
            else:
                # 두 열쇠가 모두 거부당했을 때의 최종 경고
                st.error("❌ [연동 실패] 발급받으신 두 개의 식약처 인증키가 모두 만료되었거나 올바르지 않습니다. 공공데이터포털에서 키 상태를 확인해 주세요.")
