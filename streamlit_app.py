# streamlit_app.py

import streamlit as st

# ✅ 가장 첫 줄에서 단 한 번 호출
st.set_page_config(page_title="부산시 통합 시각화", layout="wide")

from dashboard.tab1_cctv import tab1_cctv
from dashboard.tab2_lights_vs_crime import tab2_lights_vs_crime
from dashboard.tab3_oneperson_vs_lights import tab3_oneperson_vs_lights
from dashboard.tab4_police_count import tab4_police_count

st.title("📊 부산시 통합 시각화 대시보드")

tab1, tab2, tab3, tab4 = st.tabs([
    "📍 CCTV 지도 + 범죄 비교",
    "📈 가로등 vs 범죄",
    "🏠 1인 가구 vs 가로등",
    "🚓 동별 경찰서 수"
])

with tab1:
    tab1_cctv()

with tab2:
    tab2_lights_vs_crime()

with tab3:
    tab3_oneperson_vs_lights()

with tab4:
    tab4_police_count()
