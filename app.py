import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import folium
from streamlit_folium import folium_static
import openai
from geopy.geocoders import Nominatim
from math import radians, cos, sin, sqrt, atan2
import base64
import os
import random


# OpenAI API 설정
openai.api_key = ''


# 페이지 구성
st.set_page_config(page_title="청년 Farm Planner", layout="wide")

# 제목 및 설명
st.markdown("""
# 청년 Farm Planner 🌾
**지금 바로 청년 Farm Planner와 함께 새로운 도전을 시작해보세요!** 🍀
""")
st.markdown("---")



# Navigation bar
selected = option_menu(
    menu_title=None,  # required
    options=["메인", "입지 추천", "컨설팅 리포트", "유통 센터 매칭"],
    icons=["house", "map", "file-earmark-text", "building"],
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
)


# 데이터 로드
@st.cache_data
def load_data():
    data = pd.read_csv('cluster_mapping.csv').drop(columns='Unnamed: 0')
    data2 = pd.read_csv('유통센터_공판장_도매시장_정리.csv', encoding='euc-kr')
    data2.rename(columns={'위도': '위도', '경도': '경도', '종류': '종류', '명칭': '명칭'}, inplace=True)
    return data, data2

data, data2 = load_data()

# 작물별 이미지와 URL 매핑
# 작물별 클러스터, 이미지, 태블로 URL 매핑
# 작물 정보 매핑 로직
# 작물별 클러스터, 이미지, 태블로 URL 매핑 (폴더 경로 포함)
crop_info_map = {
    '딸기': {"cluster": 0, "image": "시각화이미지/딸기지도.png", "url": "https://public.tableau.com/shared/DDM8N5Y7B?:display_count=n&:origin=viz_share_link"},
    '땅콩': {"cluster": 0, "image": "시각화이미지/땅콩지도.png", "url": "https://public.tableau.com/shared/DDM8N5Y7B?:display_count=n&:origin=viz_share_link"},
    '수수': {"cluster": 0, "image": "시각화이미지/수수지도.png", "url": "https://public.tableau.com/shared/DDM8N5Y7B?:display_count=n&:origin=viz_share_link"},
    '대파': {"cluster": 1, "image": "시각화이미지/대파지도.png", "url": "https://public.tableau.com/shared/H9KQQ4X5K?:display_count=n&:origin=viz_share_link"},
    '배추': {"cluster": 1, "image": "시각화이미지/대파지도.png", "url": "https://public.tableau.com/shared/H9KQQ4X5K?:display_count=n&:origin=viz_share_link"},
    '상추': {"cluster": 1, "image": "시각화이미지/대파지도.png", "url": "https://public.tableau.com/shared/H9KQQ4X5K?:display_count=n&:origin=viz_share_link"},
    '잎들깨': {"cluster": 1, "image": "시각화이미지/대파지도.png", "url": "https://public.tableau.com/shared/H9KQQ4X5K?:display_count=n&:origin=viz_share_link"},
    '토마토': {"cluster": 3, "image": "시각화이미지/토마토지도.png", "url": "https://public.tableau.com/shared/RC5T39HNH?:display_count=n&:origin=viz_share_link"},
    '무': {"cluster": 4, "image": "시각화이미지/무지도.png", "url": "https://public.tableau.com/shared/RT97QTFG5?:display_count=n&:origin=viz_share_link"},
    '당근': {"cluster": 4, "image": "시각화이미지/당근지도.png", "url": "https://public.tableau.com/shared/RT97QTFG5?:display_count=n&:origin=viz_share_link"},
    '옥수수': {"cluster": 6, "image": "시각화이미지/옥수수지도.png", "url": "https://public.tableau.com/shared/MKK5MQZTG?:display_count=n&:origin=viz_share_link"}
}

# 이미지 인코딩 함수
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
# 하버사인 거리 계산 함수
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 지구 반지름 (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# 주소를 위도와 경도로 변환
def get_lat_lon(address):
    import time
    geolocator = Nominatim(user_agent="geoapi", timeout=10)  # 타임아웃 설정
    time.sleep(1)  # 요청 간 대기
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError("주소를 찾을 수 없습니다. 정확한 주소를 입력하세요.")


if selected == "메인":
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>청년 Farm Planner에 오신 것을 환영합니다!</h1>
            <p><strong>🌾 청년 농업의 새로운 시작, Farm Planner와 함께하세요! 🌾</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # # 이미지 추가
    # st.image("강아지.png", caption="청년 Farm Planner 소개", width=600)



    
    st.markdown("---")
    
    # 3열 구성으로 주요 기능 소개
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### **입지 추천**
        원하는 작물을 입력하면, 가장 적합한 입지를 추천해드립니다.  
        여러분의 성공적인 농업을 위한 최적의 환경을 찾아보세요!
        """)

    with col2:
        st.markdown("""
        ### **컨설팅 리포트**
        예산과 작물을 입력하면, 맞춤형 청년 농부 컨설팅 리포트를 제공합니다.  
        체계적이고 전문적인 분석으로 성공적인 귀농을 돕습니다.
        """)

    with col3:
        st.markdown("""
        ### **유통 센터 매칭**
        위치를 입력하면, 근처 유통 센터 정보를 한눈에 확인할 수 있습니다.  
        지역 유통망과의 연결로 효율적인 농업을 실현하세요!
        """)




# Content based on selection
elif selected == "입지 추천":
    st.header("작물에 알맞은 입지 추천")
    
    #col1, col2의 경우에는 좌우로 두 열로 나눠서 시각화 하기 편하게 바꿔놓은것임!
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("작물 선택")
        crop = st.text_input('원하는 작물을 입력하세요:')

        # 기본값 초기화
        recommended_region = None
        image_path, tableau_url = None, None

        if crop in crop_info_map:
            crop_info = crop_info_map[crop]
            cluster_index = crop_info["cluster"]
            image_path = crop_info["image"]
            tableau_url = crop_info["url"]

            # 클러스터로 데이터 필터링
            recommended_region = data[data['cluster'] == cluster_index]

            st.subheader("Recommended Locations:")
            # 지점명 쉼표로 분리
            all_locations = recommended_region['지점명'].str.split(',').explode().dropna().str.strip()
            # 랜덤으로 10개 샘플 선택
            sample_locations = random.sample(list(all_locations), min(10, len(all_locations)))
            # 텍스트 형식으로 출력
            st.text("\n".join(sample_locations))
        else:
            st.error(f"'{crop}'에 대한 정보가 없습니다. 다른 작물을 입력하세요.")
    
    with col2:
        st.subheader("시각화")
        if image_path and tableau_url:
            try:
                base64_image = encode_image_to_base64(image_path)
                st.markdown(f"""
                    <a href="{tableau_url}" target="_blank">
                        <img src="data:image/png;base64,{base64_image}" alt="{crop} Visualization" style="width:100%; height:auto;">
                    </a>
                """, unsafe_allow_html=True)
            except FileNotFoundError:
                st.error(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        else:
            st.write("선택한 작물에 대한 시각화 이미지가 없습니다.")



elif selected == "컨설팅 리포트":
    st.header("예산과 작물을 입력하고 컨설팅 리포트를 출력해보세요.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("예산 입력")
        budget = st.number_input("예산:", min_value=0)

    with col2:
        st.subheader("작물 입력")
        crop = st.text_input("작물:")

    if st.button("컨설팅 리포트 출력하기"):
        if budget > 0 and crop:
            st.write("Generating your report...")
            
            data = { 
                '항목': ['수도광열비', '기타재료비', '소농구비', '대농구상각비', '영농시설상각비', '수리유지비', '기타비용', '농기계-시설임차료', 
                        '토지임차료', '위탁영농비', '고용노동비', '자동차비', '생산관리비', '종자&종묘비', '보통비료비', '부산물비료비', '농약비'],
                '딸기': [0.09484, 0.15984, 0.0, 0.03826, 0.19724, 0.00685, 0.00674, 0.00137, 0.02234, 0.00247, 0.14724, 0.0, 0.0, 0.23044, 0.04123, 0.01077, 0.03876],
                '땅콩': [0.0195, 0.058, 0.005, 0.08325, 0.06725, 0.00675, 0.00925, 0.0265, 0.13425, 0.0, 0.3445, 0.0, 0.0, 0.091, 0.04425, 0.08375, 0.027],
                '수수': [0.05909, 0.01449, 0.00111, 0.24526, 0.01226, 0.02007, 0.00669, 0.01003, 0.18171, 0.08027, 0.02118, 0.0, 0.0, 0.10368, 0.11706, 0.09921, 0.02564],
                '대파': [0.02389, 0.05345, 0.00168, 0.10145, 0.035, 0.01237, 0.01069, 0.00629, 0.08971, 0.02913, 0.25257, 0.0, 0.0, 0.1178, 0.07001, 0.09327, 0.10291],
                '배추': [0.03265, 0.07899, 0.00316, 0.1248, 0.04081, 0.01185, 0.0029, 0.00527, 0.06846, 0.01659, 0.23433, 0.0, 0.0, 0.10005, 0.08399, 0.08741, 0.10848],
                '상추': [0.04774, 0.21559, 0.0013, 0.0548, 0.13844, 0.00706, 0.00483, 0.00111, 0.05455, 0.00074, 0.29045, 0.0, 0.0, 0.06718, 0.03845, 0.05622, 0.02155],
                '잎들깨': [0.07229, 0.08872, 0.00219, 0.04336, 0.31229, 0.00455, 0.00306, 0.00342, 0.01694, 0.00342, 0.28332, 0.0, 0.0, 0.04172, 0.03644, 0.04594, 0.04234],
                '토마토': [0.1653, 0.21578, 0.00118, 0.03477, 0.22758, 0.01128, 0.00444, 0.00037, 0.03041, 0.00205, 0.13369, 0.0, 0.0, 0.08029, 0.05839, 0.01628, 0.01822],
                '무': [0.0425, 0.05387, 0.00271, 0.11397, 0.02139, 0.03032, 0.00433, 0.00487, 0.09312, 0.02084, 0.32729, 0.0, 0.0, 0.09204, 0.06497, 0.0536, 0.07336],
                '당근': [0.02919, 0.10309, 0.00062, 0.08104, 0.01149, 0.00637, 0.00155, 0.00047, 0.12172, 0.02795, 0.30383, 0.0, 0.0, 0.12203, 0.03711, 0.10449, 0.04906],
                '옥수수': [0.03797, 0.12952, 0.00532, 0.14798, 0.05607, 0.01348, 0.00568, 0.01207, 0.09617, 0.00958, 0.16856, 0.0, 0.0, 0.06884, 0.06742, 0.15117, 0.03016]
            }

            budget_list = {
                "딸기": 0.06817,
                "땅콩": 0.08735,
                "수수": 0.0704,
                "대파": 0.07706,
                "배추": 0.1097,
                "상추": 0.06739,
                "잎들깨": 0.1664,
                "토마토": 0.06743,
                "무": 0.0917,
                "당근": 0.0296,
                "옥수수": 0.14324
            }

            prompt=f'''당신은 청년 농부 컨설턴트입니다. "{budget}"원의 예산을 가지고 "{crop}" 작물을 재배하려는 청년 농부를 위해 스마트 노지 농업 기반의 컨설팅 리포트를 작성하세요. 리포트는 다음의 세부 항목을 포함해야 합니다.\n
                    브랜드 정체성
                    (1) 브랜드 이름 및 슬로건:
                    작물의 특징과 소비자에게 전달하고자 하는 가치를 반영한 브랜드 이름과 슬로건을 각각 2가지 이상 제안하세요.
                    (2) 브랜드 스토리:
                    브랜드의 기원, 가치관, 농업 철학을 담아 500자 이내의 브랜드 스토리를 작성하세요.
                    "왜 이 브랜드가 특별한가?"에 대한 명확한 메시지를 포함.
                    지역 사회와의 연계 가능성 및 환경 친화적인 메시지를 포함.

                    경제적 통찰
                    (1) 예상 순수익:
                    "{crop}"의 예상 순수익은 {budget * budget_list[crop]}입니다.
                    (2) 주요 경영비 분석:
                    제공된 데이터를 기반으로 '{crop}' 작물의 주요 경영비 상위 6가지 항목과 해당 비용을 내림차순으로 정렬한 표로 제시하세요.

                    비용은 예산에 각 항목의 비율을 곱하여 계산합니다.
                    각 항목이 어떤 용도로 사용되는지 간단히 설명합니다.
                    표의 예시는 다음과 같은 형식을 따릅니다:

                    항목	비용 (원)	용도 설명
                    고용노동비 농장 운영을 위한 인건비

                    농업 전략
                    (1) 스마트 노지 농업 전략:
                    농업 생산성과 효율성을 높이기 위한 구체적인 전략 3가지를 제안하세요.

                    (2) 병해충 관리 방안:
                    병해충 예방 및 대응 방안 각각 2가지 제안:

                    비용 최적화
                    (1) 주요 비용 관리 전략:
                    상위 6개 경영비를 절감하기 위한 구체적인 관리 방안을 제시하세요.

                    (2) 리스크 관리:
                    작물 재배 중 발생할 수 있는 주요 리스크를 분석하고, 비용 손실을 최소화하기 위한 전략 2가지를 제안하세요.

                    세부사항:
                    리포트는 각 항목에 대해 구체적이고 실용적인 제안을 포함해야 합니다.
                    혁신성, 지속 가능성, 지역 농업과의 연계를 중심으로 내용을 구성하세요.
                    최종 결과물은 표, 목록, 서술형 답변을 적절히 조합하여 시각적이고 이해하기 쉬운 형태로 구성하세요.'''

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # 최신 모델 사용
                messages=[
                    {"role": "system",
                    "content": prompt}
                ],
                temperature=0.7,
                #max_tokens=300,
            )
            report = response['choices'][0]['message']['content']
            st.subheader("Consulting Report:")
            st.write(report)
        
        else:
            st.error("Please provide both budget and crop details.")



elif selected == "유통 센터 매칭":
    st.header("위치 기반 최적의 유통 센터 정보를 출력해보세요.")
    
    my_address = st.text_input("나의 위치를 입력해주세요 (예: 서울특별시 중구 세종대로 110): ")
    if my_address:
        try:
            # 주소를 위경도로 변환
            my_lat, my_lon = get_lat_lon(my_address)
            st.write(f"입력된 주소: {my_address}")
            st.write(f"위도: {my_lat}, 경도: {my_lon}")
            
            # 거리 계산
            data2['거리'] = data2.apply(
                lambda row: haversine(my_lat, my_lon, row['위도'], row['경도']), axis=1
            )
            
            # 거리 기준으로 필터링
            max_distances = {'유통센터': 50, '공판장': 35, '도매시장': 20}

            def filter_or_nearest(group, type_name):
                filtered = group[group['거리'] <= max_distances[type_name]]
                if not filtered.empty:
                    return filtered.nsmallest(3, '거리')
                return group.nsmallest(1, '거리')

            filtered_top_3_by_type = data2.groupby('종류', group_keys=False).apply(
                lambda group: filter_or_nearest(group, group.name)
            ).reset_index(drop=True)

            # 지도 생성
            m = folium.Map(location=[my_lat, my_lon], zoom_start=12)

            # 사용자의 위치 마커 추가
            folium.Marker(
                location=[my_lat, my_lon],
                popup=f"나의 위치: {my_address}",
                tooltip="나의 위치",
                icon=folium.Icon(color="red")
            ).add_to(m)

            # 추천 유통 센터 마커 추가
            for _, row in filtered_top_3_by_type.iterrows():
                marker_color = "blue" if row['종류'] == "유통센터" else "green" if row['종류'] == "공판장" else "gray"
                popup_content = f"""
                <b>이름:</b> {row['명칭']}<br>
                <b>종류:</b> {row['종류']}<br>
                <b>거리:</b> {row['거리']:.2f} km<br>
                <b>주소:</b> {row.get('주소', '정보 없음')}
                """
                folium.Marker(
                    location=[row['위도'], row['경도']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"{row['명칭']} ({row['거리']:.2f} km)",
                    icon=folium.Icon(color=marker_color)
                ).add_to(m)

            # 지도 및 결과 출력
            folium_static(m)
            st.dataframe(filtered_top_3_by_type)
        except ValueError as e:
            st.error(str(e))


elif selected == "연구":
    st.write("연구 페이지입니다.")
elif selected == "산학/창업":
    st.write("산학/창업 페이지입니다.")
elif selected == "국제화":
    st.write("국제화 페이지입니다.")
elif selected == "대학생활":
    st.write("대학생활 페이지입니다.")
