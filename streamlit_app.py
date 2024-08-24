import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
import folium
from streamlit_folium import st_folium
import matplotlib.cm as cm
import matplotlib.colors as colors
import numpy as np

# 데이터 로드
DATA_PATH = "data"  # 실제 데이터 경로로 변경하세요
df = pd.read_csv(f"{DATA_PATH}/한국문화정보원_전국 반려동물 동반 가능 문화시설 위치 데이터_20221130.CSV", encoding='cp949')

# Streamlit 앱 제목
st.title('천안시 반려동물 동반 가능 문화시설 클러스터링')

# 천안시 데이터 필터링
target_areas = ['천안시 동남구', '천안시 서북구']
df_filtered = df[df['시군구 명칭'].isin(target_areas)]

# '동물병원', '동물약국' 등 제외한 카테고리 필터링
exclude_categories = ['동물병원', '동물약국', '반려동물용품', '미용', '위탁관리']
df_filtered = df_filtered[~df_filtered['카테고리3'].isin(exclude_categories)]

# 필요한 컬럼만 선택
df_filtered = df_filtered[['시도 명칭', '시군구 명칭', '법정읍면동명칭', '카테고리3', '위도', '경도']]

# 원핫 인코딩 수행
df_onehot = pd.get_dummies(df_filtered[['카테고리3']], prefix="", prefix_sep="")
df_onehot['법정읍면동명칭'] = df_filtered['법정읍면동명칭']

# 법정읍면동명칭별로 그룹화하여 평균 계산
df_grouped = df_onehot.groupby('법정읍면동명칭').mean().reset_index()

# K-means 클러스터링 수행
n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(df_grouped.drop('법정읍면동명칭', axis=1))
df_grouped['Cluster Labels'] = kmeans.labels_

# DBSCAN 클러스터링 (위도, 경도 사용)
dbscan = DBSCAN(eps=0.045, min_samples=5)
df_filtered['DBSCAN_Cluster'] = dbscan.fit_predict(df_filtered[['위도', '경도']])

# DBSCAN 클러스터와 K-means 클러스터 결합
final_merged = df_filtered.merge(df_grouped[['법정읍면동명칭', 'Cluster Labels']], on='법정읍면동명칭')

# 각 DBSCAN 클러스터에서 가장 선호되는 K-means 카테고리를 찾기
preferred_category_per_cluster = final_merged.groupby('DBSCAN_Cluster')['Cluster Labels'].agg(lambda x: x.mode()[0])

# 각 DBSCAN 클러스터 내에서 선호되는 카테고리를 가진 관광지 찾기
final_merged['Preferred_Category'] = final_merged['DBSCAN_Cluster'].map(preferred_category_per_cluster)

# 시각화 준비
map_clusters = folium.Map(location=[36.818, 127.156], zoom_start=12)
colors_array = cm.rainbow(np.linspace(0, 1, n_clusters))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# DBSCAN 클러스터 시각화 및 각 클러스터에서 선호되는 카테고리 표시
for lat, lon, poi, dbscan_cluster, preferred_category in zip(final_merged['위도'], final_merged['경도'], final_merged['법정읍면동명칭'], final_merged['DBSCAN_Cluster'], final_merged['Preferred_Category']):
    label = folium.Popup(f"{poi}<br>DBSCAN Cluster: {dbscan_cluster}<br>Preferred Category: {preferred_category}", parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[int(preferred_category) % len(rainbow)],
        fill=True,
        fill_color=rainbow[int(preferred_category) % len(rainbow)],
        fill_opacity=0.7).add_to(map_clusters)

# Streamlit에서 지도 표시
st_folium(map_clusters, width=700, height=500)
