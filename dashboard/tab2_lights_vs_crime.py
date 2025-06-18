# dashboard/tab2_lights_vs_crime.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import urllib.request

# ─── 한글 폰트 설정 ───
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
    # 폰트 등록
    fm.fontManager.addfont(font_path)
    # 폰트 이름 얻기
    font_name = fm.FontProperties(fname=font_path).get_name()
    # 전역 rcParam 설정
    plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False

# ─── 데이터 로더 (UTF-8 전용) ───
@st.cache_data
def load_lights_data(path="data/가로등현황.csv"):
    df = pd.read_csv(path, encoding="utf-8")
    df.columns = df.columns.str.strip()
    df = df.dropna(axis=1, how='all')       # 완전 빈 열 제거
    if '관리부서' in df.columns:
        df = df.rename(columns={'관리부서': '지역'})
    else:
        df = df.rename(columns={df.columns[-2]: '지역'})
    sum_cols = [c for c in df.columns if '합계' in c]
    if not sum_cols:
        raise KeyError(f"❌ 가로등 합계 칼럼을 찾을 수 없습니다: {df.columns.tolist()}")
    df = df.rename(columns={sum_cols[0]: '합계_가로등'})
    return df[['지역', '합계_가로등']]

@st.cache_data
def load_crime_data(path="data/경찰청_범죄현황.csv"):
    df = pd.read_csv(path, encoding="utf-8")
    df.columns = df.columns.str.strip()
    crime_keys = ["살인", "강도", "성범죄", "폭력"]
    df['합계_범죄'] = df[crime_keys].sum(axis=1)
    if '지역' not in df.columns:
        for c in df.columns:
            if "관서" in c or "지역" in c:
                df = df.rename(columns={c: '지역'})
                break
    return df[['지역', '합계_범죄']]

# ─── 탭2 함수 ───
def tab2_lights_vs_crime():
    st.subheader("지역별 가로등 수 vs 5대 범죄 발생 수")

    try:
        df_l = load_lights_data()
        df_c = load_crime_data()

        merged = pd.merge(df_l, df_c, on='지역')

        fig, ax = plt.subplots(figsize=(12, 6), dpi=80)
        ax.plot(merged['지역'], merged['합계_가로등'], marker='o', label='가로등 수', color='green')
        ax.plot(merged['지역'], merged['합계_범죄'], marker='s', label='범죄 발생 수', color='red')

        ax.set_xticks(range(len(merged)))
        ax.set_xticklabels(merged['지역'], rotation=45)
        ax.set_xlabel("지역")
        ax.set_ylabel("건수")
        ax.set_title("지역별 가로등 수와 범죄 발생 수 비교")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ 범죄/가로등 시각화 오류: {type(e).__name__}: {e}")
