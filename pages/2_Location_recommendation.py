import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
import folium
from streamlit_folium import st_folium
import matplotlib.cm as cm
import matplotlib.colors as colors
import numpy as np
from folium.plugins import MarkerCluster, FastMarkerCluster

# 데이터 로드
DATA_PATH = "data"  # 실제 데이터 경로로 변경하세요
df = pd.read_csv(f"{DATA_PATH}/한국문화정보원_전국 반려동물 동반 가능 문화시설 위치 데이터_20221130.CSV", encoding='cp949')

# 첫 번째 지도: 전국 반려동물 동반 가능 문화시설 위치
st.title("반려동물 동반 가능 문화시설 위치")
m = folium.Map(location=[36.5, 127.5], zoom_start=7)
fast_marker_cluster = FastMarkerCluster(df[['위도', '경도']].values.tolist())
fast_marker_cluster.add_to(m)
st_folium(m, width=700, height=500)

# 천안시 데이터 필터링 및 지도 표시
st.title("천안시 반려동물 동반 가능 문화시설 위치")
df_pet_culture_cheonan = df[
    (df['시군구 명칭'] == '천안시 서북구') |
    (df['시군구 명칭'] == '천안시 동남구')
]
selected_columns = ['시설명', '카테고리3', '시군구 명칭', '법정읍면동명칭', '리 명칭',
       '위도', '경도', '도로명주소',
       '반려동물 동반 가능정보', '반려동물 전용 정보', '입장 가능 동물 크기', '반려동물 제한사항', '장소(실내) 여부', '장소(실외)여부',
       '기본 정보_장소설명', '애견 동반 추가 요금', '최종작성일']
df_selected_cheonan = df_pet_culture_cheonan[selected_columns]

df_pet_tourist_attraction = df_selected_cheonan[
    (df_selected_cheonan['카테고리3'] == '카페') |
    (df_selected_cheonan['카테고리3'] == '여행지') |
    (df_selected_cheonan['카테고리3'] == '문예회관') |
    (df_selected_cheonan['카테고리3'] == '박물관') |
    (df_selected_cheonan['카테고리3'] == '미술관')
]

map_center = [df_pet_tourist_attraction['위도'].mean(), df_pet_tourist_attraction['경도'].mean()]
mymap = folium.Map(location=map_center, zoom_start=12)

for _, row in df_pet_tourist_attraction.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=row['시설명'],
        tooltip=row['시설명']
    ).add_to(mymap)

st_folium(mymap, width=700, height=500)

# 두 번째 지도: 천안시 반려동물 동반 가능 문화시설 클러스터링
st.title('천안시 반려동물 동반 가능 문화시설 클러스터링')
target_areas = ['천안시 동남구', '천안시 서북구']
df_filtered = df[df['시군구 명칭'].isin(target_areas)]
exclude_categories = ['동물병원', '동물약국', '반려동물용품', '미용', '위탁관리']
df_filtered = df_filtered[~df_filtered['카테고리3'].isin(exclude_categories)]
df_filtered = df_filtered[['시도 명칭', '시군구 명칭', '법정읍면동명칭', '카테고리3', '위도', '경도']]
df_onehot = pd.get_dummies(df_filtered[['카테고리3']], prefix="", prefix_sep="")
df_onehot['법정읍면동명칭'] = df_filtered['법정읍면동명칭']
df_grouped = df_onehot.groupby('법정읍면동명칭').mean().reset_index()

n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(df_grouped.drop('법정읍면동명칭', axis=1))
df_grouped['Cluster Labels'] = kmeans.labels_

dbscan = DBSCAN(eps=0.045, min_samples=5)
df_filtered['DBSCAN_Cluster'] = dbscan.fit_predict(df_filtered[['위도', '경도']])

final_merged = df_filtered.merge(df_grouped[['법정읍면동명칭', 'Cluster Labels']], on='법정읍면동명칭')
preferred_category_per_cluster = final_merged.groupby('DBSCAN_Cluster')['Cluster Labels'].agg(lambda x: x.mode()[0])
final_merged['Preferred_Category'] = final_merged['DBSCAN_Cluster'].map(preferred_category_per_cluster)

map_clusters = folium.Map(location=[36.818, 127.156], zoom_start=12)
colors_array = cm.rainbow(np.linspace(0, 1, n_clusters))
rainbow = [colors.rgb2hex(i) for i in colors_array]

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

st_folium(map_clusters, width=700, height=500)
