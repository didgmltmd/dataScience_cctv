# dashboard/tab1_cctv.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import folium
from folium.plugins import MarkerCluster
import os

# CCTV 데이터 로더
@st.cache_data
def load_cctv_data():
    df = pd.read_excel("data/12_04_08_E_CCTV정보.xlsx", engine="openpyxl")
    cols = df.columns.tolist()
    find = lambda kw: next((c for c in cols if kw in c), None)
    return df.rename(columns={
        find("설치목적"): "목적",
        find("도로명주소"): "설치장소",
        find("위도"): "위도",
        find("경도"): "경도",
        find("설치연"): "설치연도",
        find("카메라대수"): "대수"
    }).dropna(subset=["위도", "경도"])

# 범죄 데이터 로더 (키워드 기반 컬럼 탐지)
@st.cache_data
def load_crime_data():
    path = "data/경찰청 부산광역시경찰청_경찰서별 5대 범죄 발생 현황_20231231.csv"
    # 여러 인코딩 시도
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise UnicodeDecodeError(f"❌ 파일 '{path}' 인코딩 오류. UTF-8 또는 CP949 확인 요망.")

    # 공백 제거
    df.columns = df.columns.str.strip()
    cols = df.columns.tolist()

    # 컬럼 탐색 함수
    def find_cols(keywords):
        found = []
        for kw in keywords:
            matches = [c for c in cols if kw in c]
            if matches:
                found.extend(matches)
        return found

    # 경찰서 컬럼
    station_col = next((c for c in cols if "경찰서" in c), None)
    if not station_col:
        raise KeyError(f"❌ '경찰서' 컬럼을 찾을 수 없습니다. 실제 컬럼: {cols}")

    # CCTV 개수 컬럼
    cctv_cols = find_cols(["cctv"])
    if not cctv_cols:
        raise KeyError(f"❌ 'CCTV' 키워드 포함 컬럼이 없습니다. 실제 컬럼: {cols}")
    cctv_col = cctv_cols[0]

    # 5대 범죄 키워드 컬럼
    crime_keys = ["살인", "강도", "성범죄", "폭력"]
    crime_cols = find_cols(crime_keys)
    if not crime_cols:
        raise KeyError(f"❌ 5대 범죄 컬럼을 찾을 수 없습니다. 실제 컬럼: {cols}")
    
    # 합계 컬럼 추가
    df["5대 범죄 합계"] = df[crime_cols].sum(axis=1)
    df.rename(columns={cctv_col: "cctv개수", station_col: "경찰서"}, inplace=True)

    return df.sort_values("경찰서")

def tab1_cctv():
    # 한글 폰트
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        st.error(f"❌ 폰트 파일 없음:\n{font_path}")
        return
    fontprop = fm.FontProperties(fname=font_path)
    plt.rcParams['axes.unicode_minus'] = False

    col1, col2 = st.columns([1, 1.5])

    # CCTV 지도
    with col1:
        st.subheader("📍 CCTV 위치 분포도")
        try:
            df_vis = load_cctv_data()
            m = folium.Map(location=[df_vis["위도"].mean(), df_vis["경도"].mean()], zoom_start=11)
            cluster = MarkerCluster().add_to(m)
            for _, row in df_vis.iterrows():
                popup = (
                    f"<b>목적:</b> {row['목적']}<br>"
                    f"<b>장소:</b> {row['설치장소']}<br>"
                    f"<b>연도:</b> {row['설치연도']}<br>"
                    f"<b>대수:</b> {row['대수']}"
                )
                folium.Marker([row["위도"], row["경도"]],
                              popup=folium.Popup(popup, max_width=300)
                ).add_to(cluster)
            from streamlit_folium import st_folium
            st_folium(m, width=450, height=500)
        except Exception as e:
            st.error(f"❌ CCTV 지도 오류:\n{e}")

    # CCTV vs 범죄
    with col2:
        st.subheader("📊 CCTV 개수 vs 5대 범죄 발생 수")
        try:
            df = load_crime_data()
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df["경찰서"], df["cctv개수"], label="CCTV 개수", marker='o', color='orange')
            ax.plot(df["경찰서"], df["5대 범죄 합계"], label="범죄 건수", marker='s', color='orangered')

            ax.set_title(
                "지역별 CCTV 개수와 범죄 발생 건수 비교(강도, 살인,성범죄, 폭력)",
                fontproperties=fontprop, fontsize=16
            )
            ax.set_xlabel("경찰서", fontproperties=fontprop)
            ax.set_ylabel("건수", fontproperties=fontprop)
            ax.set_xticks(np.arange(len(df)))
            ax.set_xticklabels(df["경찰서"], rotation=45, fontproperties=fontprop)
            ax.legend(prop=fontprop)
            ax.grid(True)

            st.pyplot(fig)
        except Exception as e:
            st.error(f"❌ CCTV/범죄 시각화 오류:\n{e}")
