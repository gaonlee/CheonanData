import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns


# 데이터 로드
DATA_PATH = "data"  # 실제 데이터 경로로 변경하세요
df_pet_registration = pd.read_csv(f"{DATA_PATH}/반려동물 등록현황(2018~2023).csv", encoding='cp949')
df_pet_household = pd.read_excel(f"{DATA_PATH}/가구원수별_반려동물_보유_유형별가구시도_20240809190525.xlsx", engine='openpyxl')
beauty_df = pd.read_csv(f"{DATA_PATH}/농림축산식품부_반려동물 미용업 현황_20221231.csv", encoding='cp949')
express_df = pd.read_csv(f"{DATA_PATH}/농림축산식품부_반려동물 운송업 현황_20201230.csv", encoding='cp949')
funeral_df = pd.read_csv(f"{DATA_PATH}/농림축산식품부_반려동물 장묘업 현황_12_30_2020.csv", encoding='cp949')
exhibition_df = pd.read_csv(f"{DATA_PATH}/농림축산식품부_반려동물 전시업 현황_20221231.csv", encoding='cp949')

# 한글 폰트 설정 (Noto Sans CJK 폰트 사용)
font_path = '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'  # 배포 환경에서 Noto Sans CJK 경로
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)  # 전역 폰트 설정
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 부호 깨짐 방지
st.title("'행정구역별 반려동물 보유 가구 수 (가구원수=계)'")

# '전국', '동부', '읍부', '면부', '서울특별시', '경기도'를 제외한 데이터 필터링
df_filtered1 = df_pet_household[(df_pet_household['가구원수'] == '계') &
                   (~df_pet_household['행정구역별(시도)'].isin(['전국', '동부', '읍부', '면부', '서울특별시', '경기도']))]

# '행정구역별(시도)'와 '반려동물보유가구-계' 열만 선택
df_plot1 = df_filtered1[['행정구역별(시도)', '반려동물보유가구-계']]

# '반려동물보유가구-계' 값에 따라 내림차순으로 정렬
df_plot1 = df_plot1.sort_values(by='반려동물보유가구-계', ascending=False)

# 시각화
fig, ax = plt.subplots(figsize=(12, 8))
sns.barplot(x='반려동물보유가구-계', y='행정구역별(시도)', data=df_plot1, palette='viridis', ax=ax)

# 그래프 제목 및 레이블 설정
ax.set_title('행정구역별 반려동물 보유 가구 수 (가구원수=계)', fontsize=16)
ax.set_xlabel('반려동물 보유 가구 수', fontsize=12)
ax.set_ylabel('행정구역별(시도)', fontsize=12)

# Streamlit을 통해 그래프 출력
st.pyplot(fig)


# Streamlit 페이지 제목 설정
st.title('시군구별 동물소유자수 및 동물소유자당동물등록수')

# x축 위치 설정
x = range(len(df_pet_registration['시군구']))

# 그래프 설정
fig, ax1 = plt.subplots(figsize=(12, 6))

# 첫 번째 y축 (동물소유자수) 막대 그래프
color = 'tab:blue'
ax1.set_xlabel('시군구')
ax1.set_ylabel('동물소유자수', color=color)
bars1 = ax1.bar(x, df_pet_registration['동물소유자수'], color=color, width=0.4, label='동물소유자수(명)')
ax1.tick_params(axis='y', labelcolor=color)

# 두 번째 y축 (동물소유자당동물등록수) 선 그래프
ax2 = ax1.twinx()
color = 'tab:orange'
ax2.set_ylabel('동물소유자당동물등록수', color=color)
line2 = ax2.plot(x, df_pet_registration['동물소유자당동물등록수'], color=color, marker='o', linestyle='-', linewidth=2, label='동물소유자당동물등록수(마리)')
ax2.tick_params(axis='y', labelcolor=color)

# x축 레이블 설정
ax1.set_xticks(x)
ax1.set_xticklabels(df_pet_registration['시군구'], rotation=45, ha="right")

# 그래프 제목 및 레이아웃 설정
plt.title('시군구별 동물소유자수 및 동물소유자당동물등록수')
fig.tight_layout()

# 범례 추가
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Streamlit을 통해 그래프 출력
st.pyplot(fig)


# 스타일 설정
sns.set_style("whitegrid")

# 서울, 경기, 인천 제외하고 필터링하는 함수
def filter_regions(df, region_col='지역'):
    excluded_regions = ['서울', '경기', '인천']
    return df[~df[region_col].isin(excluded_regions)]

def plot_region_data(df, region_col, company_col, employee_col, title, highlight_region):
    # 지역 필터링
    df_filtered = filter_regions(df, region_col)
    
    # NaN 값 제거
    df_filtered = df_filtered.dropna(subset=[region_col, company_col, employee_col])
    
    # 데이터 타입 변환 (필요한 경우)
    df_filtered[company_col] = pd.to_numeric(df_filtered[company_col], errors='coerce')
    df_filtered[employee_col] = pd.to_numeric(df_filtered[employee_col], errors='coerce')
    
    # 내림차순 정렬
    df_company_sorted = df_filtered.sort_values(by=company_col, ascending=False)
    df_employee_sorted = df_filtered.sort_values(by=employee_col, ascending=False)
    
    # 그래프 생성
    fig, axs = plt.subplots(1, 2, figsize=(20, 8))
    
    # 업체 수 그래프
    sns.barplot(
        data=df_company_sorted,
        x=company_col,
        y=region_col,
        palette='viridis',
        ax=axs[0]
    )
    axs[0].set_title(f"{title} - {company_col}", fontsize=16)
    axs[0].set_xlabel(company_col, fontsize=12)
    axs[0].set_ylabel(region_col, fontsize=12)
    
    # 종사자 수 그래프
    sns.barplot(
        data=df_employee_sorted,
        x=employee_col,
        y=region_col,
        palette='viridis',
        ax=axs[1]
    )
    axs[1].set_title(f"{title} - {employee_col}", fontsize=16)
    axs[1].set_xlabel(employee_col, fontsize=12)
    axs[1].set_ylabel("", fontsize=12)  # y축 라벨 제거
    
    # 각 텍스트 요소에 대해 폰트 재설정
    for ax in axs:
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(fm.FontProperties(fname=font_path))
    
    # 강조할 지역 표시 함수
    def highlight_bar(ax, df_sorted, value_col):
        for i, region in enumerate(df_sorted[region_col]):
            if region == highlight_region:
                rect = ax.patches[i]
                rect.set_edgecolor('red')
                rect.set_linewidth(3)
                rect.set_facecolor('lightcoral')
    
    # 강조 표시 적용
    highlight_bar(axs[0], df_company_sorted, company_col)
    highlight_bar(axs[1], df_employee_sorted, employee_col)
    
    # 레이아웃 조정
    plt.tight_layout()

    # X축 라벨에 대한 폰트 강제 적용
    for ax in axs:
        ax.set_xticklabels(ax.get_xticklabels(), fontproperties=fm.FontProperties(fname=font_path))

    st.pyplot(fig)

# 데이터프레임 딕셔너리
dataframes = {
    '미용업': beauty_df,
    '운송업': express_df,
    '장묘업': funeral_df,
    '전시업': exhibition_df
}

# 각 데이터프레임에 대해 시각화 수행
highlight_region = '충남'

for name, df in dataframes.items():
    st.header(f"📊 {name} 데이터 시각화")
    if name == '장묘업':
        plot_region_data(
            df=df,
            region_col='지역',
            company_col='동물장묘업(업체 수)',
            employee_col='종사자수(명)',
            title=name,
            highlight_region=highlight_region
        )
    else:
        plot_region_data(
            df=df,
            region_col='지역',
            company_col='업체수(개소)',
            employee_col='종사자수(명)',
            title=name,
            highlight_region=highlight_region
        )