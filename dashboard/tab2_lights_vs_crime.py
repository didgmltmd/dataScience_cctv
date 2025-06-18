# dashboard/tab2_lights_vs_crime.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os
import urllib.request

# ─── 한글 폰트 설정 (생략) ───
# fontprop 세팅 부분은 기존 코드 그대로 가져오시면 됩니다.

# ─── 가로등 데이터 로더 (빈 칼럼 자동 제거, UTF-8 인코딩) ───
@st.cache_data
def load_lights_data(path="data/가로등현황.csv"):
    # 1) 파일을 UTF-8로 읽고
    df = pd.read_csv(path, encoding="utf-8")
    # 2) 칼럼명 공백 제거
    df.columns = df.columns.str.strip()
    # 3) 완전히 빈(이름만 있고 값 전부 NaN) 칼럼 제거
    df = df.dropna(axis=1, how="all")
    # 4) '관리부서' 를 '지역' 으로 리네임
    if "관리부서" in df.columns:
        df = df.rename(columns={"관리부서": "지역"})
    else:
        # 마지막 칼럼이 '지역' 역할일 수도 있으니
        df = df.rename(columns={df.columns[-2]: "지역"})  # 두 번째 마지막이 실제 합계 뒤 빈 열
    # 5) '합계' 칼럼을 '합계_가로등' 으로 리네임
    if "합계" in df.columns:
        df = df.rename(columns={"합계": "합계_가로등"})
    else:
        raise KeyError(f"❌ 합계 칼럼을 찾을 수 없습니다. 실제 칼럼: {list(df.columns)}")

    return df[["지역", "합계_가로등"]]

# ─── 범죄 데이터 로더 (UTF-8) ───
@st.cache_data
def load_crime_data(path="data/경찰청_범죄현황.csv"):
    df = pd.read_csv(path, encoding="utf-8")
    df.columns = df.columns.str.strip()
    # 5대 범죄 합계 계산
    crime_keys = ["살인", "강도", "성범죄", "폭력"]
    df["합계_범죄"] = df[crime_keys].sum(axis=1)
    # '지역' 컬럼이 '지역'이 아니라면 강제 리네임
    if "지역" not in df.columns:
        for col in df.columns:
            if "지역" in col or "관서" in col:
                df = df.rename(columns={col: "지역"})
                break
    return df[["지역", "합계_범죄"]]

# ─── 탭2 함수 ───
def tab2_lights_vs_crime():
    st.subheader("📈 지역별 가로등 수 vs 5대 범죄 발생 수")

    try:
        df_l = load_lights_data()
        df_c = load_crime_data()

        # 병합
        merged = pd.merge(df_l, df_c, on="지역")

        # 시각화
        fig, ax = plt.subplots(figsize=(12, 6), dpi=80)
        ax.plot(merged["지역"], merged["합계_가로등"], label="가로등 수",
                marker="o", color="green")
        ax.plot(merged["지역"], merged["합계_범죄"], label="범죄 발생 수",
                marker="s", color="red")

        ax.set_xticks(range(len(merged)))
        ax.set_xticklabels(merged["지역"], rotation=45,
                           fontproperties=fontprop)
        ax.set_xlabel("지역", fontproperties=fontprop)
        ax.set_ylabel("건수", fontproperties=fontprop)
        ax.set_title("지역별 가로등 수와 범죄 발생 수 비교", fontproperties=fontprop)
        ax.legend(prop=fontprop)
        ax.grid(True)

        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ 범죄/가로등 시각화 오류: {type(e).__name__}: {e}")
