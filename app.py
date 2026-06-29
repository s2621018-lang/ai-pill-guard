import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# 1. 앱 디자인
st.set_page_config(page_title="AI 약 결합 안전 분석기", page_icon="🛡️")
st.title("🛡️ AI 약 결합 안전 분석기")
st.markdown("##### 식품의약품안전처 공식 'e약은요' 실시간 결합 안전 시스템")

# 2. 식약처 서버에서 약 정보를 가져오는 함수
def get_drug_details(service_key, drug_name):
    url = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
    
    # ⚠️ 인증키 인코딩 에러 방지 처리
    encoded_key = urllib.parse.unquote(service_key)
    
    params = {
        'serviceKey': encoded_key,
        'itemName': drug_name,
        'pageNo': '1',
        'numOfRows': '1'
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content.decode('utf-8', errors='ignore'))
            item = root.find(".//item")
            if item is not None:
                def clean_text(element):
                    if element is not None and element.text:
                        import re
                        return re.sub('<[^<]+?>', '', element.text).strip()
                    return ""
                
                return {
                    "warning": clean_text(item.find("atpnQesitm")),
                    "side_effect": clean_text(item.find("seQesitm"))
                }
    except:
        pass
    return None

# 3. 입력창
drug1 = st.text_input("첫 번째 약 이름을 입력하세요 (예: 타이레놀)", value="")
drug2 = st.text_input("두 번째 약/영양제 이름을 입력하세요 (예: 아스피린)", value="")

if st.button("식약처 공식 데이터 실시간 결합 분석 시작"):
    if not drug1 or not drug2:
        st.warning("⚠️ 약물 결합 분석을 위해 두 가지 약 이름을 모두 입력해 주세요!")
    else:
        st.write("---")
        st.subheader(f"📋 [{drug1}] + [{drug2}] 실시간 결합 분석 보고서")
        
        with st.spinner("🏥 대한민국 식약처 e약은요 데이터베이스 실시간 대조 중..."):
            # 금고에서 단 하나의 마스터 키만 가져옵니다!
            use_key = st.secrets.get("DATA_KEY_1", "")
            
            info_drug1 = get_drug_details(use_key, drug1)
            info_drug2 = get_drug_details(use_key, drug2)
            
            if info_drug1 or info_drug2:
                is_dangerous = False
                matched_reason = ""
                
                # 🔍 결합 대조 알고리즘
                if info_drug1:
                    d2_clean = drug2.replace(" ", "")
                    if d2_clean in info_drug1["warning"].replace(" ", "") or d2_clean in info_drug1["side_effect"].replace(" ", ""):
                        is_dangerous = True
                        matched_reason = f"[{drug1}]의 식약처 주의사항/부작용 문서에 [{drug2}] 성분과의 병용 위험성이 명시되어 있습니다."
                
                if not is_dangerous and info_drug2:
                    d1_clean = drug1.replace(" ", "")
                    if d1_clean in info_drug2["warning"].replace(" ", "") or d1_clean in info_drug2["side_effect"].replace(" ", ""):
                        is_dangerous = True
                        matched_reason = f"[{drug2}]의 식약처 주의사항/부작용 문서에 [{drug1}] 성분과의 병용 위험성이 명시되어 있습니다."
                
                # 4. 신호등 UI 출력
                if is_dangerous:
                    st.error("✅ 최종 판정 등급: DANGER (위험 - 복용 주의 조합)")
                    st.info(f"❌ {matched_reason}\n\n부작용이 증가할 수 있으므로, 복용 전 반드시 의사 또는 약사와 상의하세요.")
                else:
                    st.success("✅ 최종 판정 등급: SAFE (안전)")
                    st.info(f"🍏 식약처 데이터베이스 실시간 대조 결과, [{drug1}]와 [{drug2}] 간의 명확한 상호작용 위험이 발견되지 않았습니다.")
            else:
                # 💡 아직 키가 식약처 서버에 등록 승인이 안 완료되었을 때 뜨는 친절한 안내
                st.error("❌ 식약처 서버 연결에 실패했습니다. 공공데이터포털에서 발급받은 '일반 인증키'가 완전히 활성화되기까지 최대 1~2시간이 걸릴 수 있습니다. 잠시 후 다시 시도해 주세요!")
