# dashboard/tab3_oneperson_vs_lights.py

import streamlit as st
import pandas as pd
import numpy as np
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
            url = "https://github.com/naver/nanumfont/blob/master/ttf/NanumGothic.ttf?raw=true"
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            st.error(f"❌ 한글 폰트 로드 실패: {e}")
            font_path = None

if font_path:
    fontprop = fm.FontProperties(fname=font_path)
    plt.rcParams['axes.unicode_minus'] = False
else:
    fontprop = None

# ─── CSV 로더 (인코딩 폴백) ───
@st.cache_data
def load_lights_data(path="data/가로등현황.csv"):
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = df.columns.str.strip()
            return df
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"❌ 파일 '{path}' 인코딩을 인식할 수 없습니다.")

# ─── ‘지역’ 컬럼 탐지 함수 ───
def find_and_rename_region(df, candidates=('관리부서','지역','관서','구역')):
    for col in df.columns:
        if any(kw in col for kw in candidates):
            return df.rename(columns={col: '지역'})
    raise KeyError(f"❌ '지역' 역할 컬럼을 찾을 수 없습니다. 실제 컬럼: {list(df.columns)}")

# ─── 탭3 함수 ───
def tab3_oneperson_vs_lights():
    st.subheader("🏠 1인 가구 수 vs 가로등 수")

    try:
        # 1) 고정 데이터: 1인 가구
        one_person_data = {
            '지역': ['중부','동래','영도','동부','부산진','서부','남부','해운대',
                   '사상','금정','사하','연제','강서','북부','기장'],
            '1인 가구 수': [11786,35220,20116,18603,70609,20760,40521,50516,
                         36299,40412,46442,30846,17355,36975,22500]
        }
        df_one = pd.DataFrame(one_person_data)

        # 2) 가로등 데이터 로드
        df_lights = load_lights_data()
        df_lights = find_and_rename_region(df_lights)
        # 합계 컬럼명 찾아서 '가로등 수'로 통일
        sum_col = next(c for c in df_lights.columns if '합계' in c)
        df_lights = df_lights[['지역', sum_col]].rename(columns={sum_col:'가로등 수'})

        # 3) 병합
        df_merged = pd.merge(df_one, df_lights, on='지역')

        # 4) 산점도
        fig1, ax1 = plt.subplots()
        ax1.scatter(df_merged['1인 가구 수'], df_merged['가로등 수'])
        for i, row in df_merged.iterrows():
            ax1.text(
                row['1인 가구 수'], row['가로등 수'],
                row['지역'], fontsize=9,
                fontproperties=fontprop
            )
        ax1.set_xlabel("1인 가구 수", fontproperties=fontprop)
        ax1.set_ylabel("가로등 수", fontproperties=fontprop)
        ax1.set_title("1인 가구 수 vs 가로등 수 (산점도)", fontproperties=fontprop)
        st.pyplot(fig1)

        # 5) 막대그래프
        fig2, ax2 = plt.subplots(figsize=(12,6))
        idx = np.arange(len(df_merged))
        width = 0.4
        ax2.bar(idx, df_merged['1인 가구 수'], width, label='1인 가구 수')
        ax2.bar(idx+width, df_merged['가로등 수'], width, label='가로등 수')

        ax2.set_xticks(idx + width/2)
        ax2.set_xticklabels(df_merged['지역'], rotation=45, fontproperties=fontprop)
        ax2.set_ylabel("건수", fontproperties=fontprop)
        ax2.set_title("지역별 1인 가구 수 vs 가로등 수 비교", fontproperties=fontprop)
        ax2.legend(prop=fontprop)
        ax2.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig2)

    except KeyError as ke:
        st.error(str(ke))
    except Exception as e:
        st.error(f"❌ 1인 가구 vs 가로등 시각화 오류: {type(e).__name__}: {e}")
