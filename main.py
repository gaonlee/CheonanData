import streamlit as st
from pathlib import Path

# 페이지 딕셔너리 설정
PAGES = {
    "천안 현황": "pages/1_EDA.py",
    "반려동물 친화시설 입지 추천": "pages/2_Location_recommendation.py",
    "부록": "pages/3_Appendix.py"
}

# 사이드바에 페이지 선택박스 생성
st.sidebar.title('메인 메뉴')  # 사이드바 제목을 "메인 메뉴"로 변경
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# 선택된 페이지 파일을 실행
page = PAGES.get(selection)
if page:
    exec(Path(page).read_text(encoding='utf-8'), globals())
else:
    st.write("Main 페이지")
