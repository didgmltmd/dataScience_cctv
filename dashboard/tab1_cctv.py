# dashboard/tab1_cctv.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import urllib.request
import pydeck as pdk

# ────── 한글 폰트 로드 ──────
win_font = "C:\\Windows\\Fonts\\malgun.ttf"
if os.path.exists(win_font):
    font_path = win_font
else:
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        try:
            url = (
                "https://github.com/naver/nanumfont/"
                "blob/master/ttf/NanumGothic.ttf?raw=true"
            )
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            st.error(f"❌ 한글 폰트 로드 실패: {e}")
            font_path = None

if font_path:
    fontprop = fm.FontProperties(fname=font_path)
    plt.rcParams['axes.unicode_minus'] = False
else:
    fontprop = None

# ────── 데이터 로더 (Excel→CSV 캐싱) ──────
@st.cache_data(show_spinner=False)
def load_cctv_data_csv():
    csv_path = "data/cctv.csv"
    if not os.path.exists(csv_path):
        df_x = pd.read_excel("data/12_04_08_E_CCTV정보.xlsx", engine="openpyxl")
        df_x.to_csv(csv_path, index=False, encoding="utf-8")
    df = pd.read_csv(csv_path, encoding="utf-8")
    # 기존 컬럼명 찾아 대체
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

@st.cache_data(show_spinner=False)
def load_crime_data_csv():
    df = pd.read_csv(
        "data/경찰청 부산광역시경찰청_경찰서별 5대 범죄 발생 현황_20231231.csv",
        encoding="utf-8"
    )
    df.columns = df.columns.str.strip()
    # 컬럼 동적 탐색
    cols = df.columns.tolist()
    station_col = next((c for c in cols if "경찰서" in c), None)
    cctv_col    = next((c for c in cols if "cctv" in c.lower()), None)
    crime_keys  = ["살인","강도","성범죄","폭력"]
    crime_cols  = [c for c in cols for kw in crime_keys if kw in c]
    df["5대 범죄 합계"] = df[crime_cols].sum(axis=1)
    return df.rename(columns={station_col:"경찰서", cctv_col:"cctv개수"}).sort_values("경찰서")

# ────── 탭1 함수 (PyDeck으로 대체) ──────
def tab1_cctv():
    col1, col2 = st.columns([1,1.5])

    with col1:
        st.subheader("📍 CCTV 위치 분포도 (PyDeck)")
        df = load_cctv_data_csv()
        # ScatterplotLayer로 WebGL 렌더링
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["경도","위도"],
            get_radius=100,
            pickable=True,
            opacity=0.8,
            get_fill_color=[255,140,0]
        )
        view = pdk.ViewState(
            latitude=df["위도"].mean(),
            longitude=df["경도"].mean(),
            zoom=11
        )
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))

    with col2:
        st.subheader("📊 CCTV 개수 vs 5대 범죄 발생 수")
        df_crime = load_crime_data_csv()
        fig, ax = plt.subplots(figsize=(10,5), dpi=80)
        ax.plot(df_crime["경찰서"], df_crime["cctv개수"], "o-", label="CCTV 개수", color="orange")
        ax.plot(df_crime["경찰서"], df_crime["5대 범죄 합계"], "s-", label="범죄 건수", color="orangered")

        ax.set_title("지역별 CCTV 개수와 범죄 발생 건수 비교", fontproperties=fontprop, fontsize=16)
        ax.set_xlabel("경찰서", fontproperties=fontprop)
        ax.set_ylabel("건수", fontproperties=fontprop)
        ax.set_xticks(np.arange(len(df_crime)))
        ax.set_xticklabels(df_crime["경찰서"], rotation=45, fontproperties=fontprop)
        ax.grid(True)
        ax.legend(prop=fontprop)

        st.pyplot(fig)
