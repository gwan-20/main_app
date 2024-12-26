import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import openai
from geopy.geocoders import Nominatim
from math import radians, cos, sin, sqrt, atan2
import base64
import os

# OpenAI API 설정
openai.api_key = ''
# 페이지 구성
st.set_page_config(page_title="청년 Farm Planner", layout="wide")

# 제목 및 설명
st.markdown("""
# 청년 Farm Planner 🌾
""")
st.markdown("""
---

**지금 바로 청년 Farm Planner와 함께 새로운 도전을 시작해보세요!** 🍀
""")
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



st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a feature:", [
    "입지 추천",
    "청년 농부 컨설팅 리포트",
    "유통 센터 지도"
])

# CSS 스타일 추가
st.markdown("""
    <style>
    .header {
        display: flex;
        justify-content: space-between;
        padding: 10px 50px;
        background-color: rgba(0, 0, 0, 0.7);
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    .header a {
        text-decoration: none;
        color: white;
        margin: 0 15px;
        font-size: 18px;
    }
    .header a:hover {
        color: #f0a500;
    }
    </style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class="header">
    <a href="#home">Home</a>
    <a href="#입지 추천">입지 추천</a>
    <a href="#청년 농부 리포트">청년 농부 리포트</a>
    <a href="#유통센터 매칭">유통센터 매칭</a>
</div>
""", unsafe_allow_html=True)

# 공통 데이터 로드 
@st.cache_data
def load_data():
    # 데이터를 여기에 로드하거나 생성
    data = pd.read_csv('cluster_mapping.csv').drop(columns='Unnamed: 0')
    
    file_path = '유통센터_공판장_도매시장_정리.csv'
    data2 = pd.read_csv(file_path, encoding='euc-kr')
    # 위경도 컬럼 이름 통일
    data2.rename(columns={'위도': '위도', '경도': '경도', '종류': '종류', '명칭': '명칭'}, inplace=True)
    
    return data, data2

data, data2 = load_data()

# 작물별 이미지와 URL 매핑
# 작물별 클러스터, 이미지, 태블로 URL 매핑
crop_info_map = {
    '딸기': {"cluster": 0, "image": "C:\\Users\\user\\Desktop\\메프\\딸기지도.png", "url": "https://public.tableau.com/shared/DDM8N5Y7B?:display_count=n&:origin=viz_share_link"},
    '땅콩': {"cluster": 0, "image": "C:\\Users\\user\\Desktop\\메프\\땅콩지도.png", "url": "https://public.tableau.com/shared/DDM8N5Y7B?:display_count=n&:origin=viz_share_link"},
    '수수': {"cluster": 0, "image": "C:\\Users\\user\\Desktop\\메프\\수수지도.png", "url": "https://public.tableau.com/shared/DDM8N5Y7B?:display_count=n&:origin=viz_share_link"},
    '대파': {"cluster": 1, "image": "C:\\Users\\user\\Desktop\\메프\\대파지도.png", "url": "https://public.tableau.com/shared/H9KQQ4X5K?:display_count=n&:origin=viz_share_link"},
    '배추': {"cluster": 1, "image": "C:\\Users\\user\\Desktop\\메프\\대파지도.png", "url": "https://public.tableau.com/shared/H9KQQ4X5K?:display_count=n&:origin=viz_share_link"},
    '상추': {"cluster": 1, "image": "C:\\Users\\user\\Desktop\\메프\\대파지도.png", "url": "https://public.tableau.com/shared/H9KQQ4X5K?:display_count=n&:origin=viz_share_link"},
    '잎들깨': {"cluster": 1, "image": "C:\\Users\\user\\Desktop\\메프\\대파지도.png", "url": "https://public.tableau.com/shared/H9KQQ4X5K?:display_count=n&:origin=viz_share_link"},
    '토마토': {"cluster": 3, "image": "C:\\Users\\user\\Desktop\\메프\\토마토지도.png", "url": "https://public.tableau.com/shared/RC5T39HNH?:display_count=n&:origin=viz_share_link"},
    '무': {"cluster": 4, "image": "C:\\Users\\user\\Desktop\\메프\\무지도.png", "url": "https://public.tableau.com/shared/RT97QTFG5?:display_count=n&:origin=viz_share_link"},
    '당근': {"cluster": 4, "image": "C:\\Users\\user\\Desktop\\메프\\당근지도.png", "url": "https://public.tableau.com/shared/RT97QTFG5?:display_count=n&:origin=viz_share_link"},
    '옥수수': {"cluster": 6, "image": "C:\\Users\\user\\Desktop\\메프\\옥수수지도.png", "url": "https://public.tableau.com/shared/MKK5MQZTG?:display_count=n&:origin=viz_share_link"}
}

# 이미지 인코딩 함수
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

if page == "입지 추천":
    st.header("작물에 알맞은 입지 추천")
    
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
            st.dataframe(recommended_region['지점명'])
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


if page == "청년 농부 컨설팅 리포트":
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

            # GPT 프롬프트 생성
            prompt = f"당신은 청년농부 컨설턴트입니다. '{budget}'원 예산을 가지고고 '{crop}' 작물을 기르는 귀농을 하려는 청년 농부에게 아래 내용을 포함하여 컨설팅 리포트를 작성해주세요. 청년 농부는 데이터를 바탕으로 스마트 노지 귀농을 하려 하고 있으며, 청년 농부의 예상 순수익은 {budget*2}원입니다."
            "1. 브랜드 이름과 슬로건 제안\n"
            "2. 브랜드 스토리 작성\n"
            "3. 스마트 노지 경영 전략 3가지\n"
            "4. 재배 전략 및 병해충 관리 방안 2가지\n"
            
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

if page == "유통 센터 지도":
    st.header("위치 기반 최적의 유통 센터 정보를 출력해보세요")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("주소 입력")
        my_address=st.text_input("나의 위치를 입력해주세요 (예: 서울특별시 중구 세종대로 110): ")

    with col2:
        st.subheader("위치 계산")
        if my_address:
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371  # 지구의 반지름 (단위: km)
                dlat = radians(lat2 - lat1)
                dlon = radians(lat2 - lon1)
                a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                return R * c

            def get_lat_lon(address):
                geolocator = Nominatim(user_agent="geoapi")
                location = geolocator.geocode(address)
                if location:
                    return location.latitude, location.longitude
                else:
                    raise ValueError("주소를 찾을 수 없습니다. 정확한 주소를 입력하세요.")

            my_lat, my_lon = get_lat_lon(my_address)
            st.write(f"입력된 주소의 위경도: {my_lat}, {my_lon}")

            data2['거리'] = data2.apply(
                lambda row: haversine(my_lat, my_lon, row['위도'], row['경도']), axis=1
            )

            max_distances = {'유통센터': 50, '공판장': 35, '도매시장': 20}

            def filter_or_nearest(group, type_name):
                filtered = group[group['거리'] <= max_distances[type_name]]
                if not filtered.empty:
                    return filtered.nsmallest(3, '거리')
                return group.nsmallest(1, '거리')

            filtered_top_3_by_type = data2.groupby('종류', group_keys=False).apply(lambda group: filter_or_nearest(group, group.name)).reset_index(drop=True)

            m = folium.Map(location=[my_lat, my_lon], zoom_start=12)

            folium.Marker(
                location=[my_lat, my_lon],
                popup=f"나의 위치: {my_address}",
                tooltip="나의 위치",
                icon=folium.Icon(color="red")
            ).add_to(m)

            for _, row in filtered_top_3_by_type.iterrows():
                marker_color = "blue" if row['종류'] == "유통센터" else "green" if row['종류'] == "공판장" else "gray"
                popup_content = f"<b>이름:</b> {row['명칭']}<br><b>종류:</b> {row['종류']}<br><b>거리:</b> {row['거리']:.2f} km"
                folium.Marker(
                    location=[row['위도'], row['경도']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"{row['명칭']} ({row['거리']:.2f} km)",
                    icon=folium.Icon(color=marker_color)
                ).add_to(m)

            folium_static(m)
            st.dataframe(filtered_top_3_by_type)
