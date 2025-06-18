# dashboard/tab3_oneperson_vs_lights.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import urllib.request

# ─── 한글 폰트 설정 (기존 코드 그대로) ───
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

# ─── 가로등 데이터 로더 (UTF-8 + 헤더 정제) ───
@st.cache_data
def load_lights_data(path="data/가로등현황.csv"):
    # 1) CSV 읽기
    df = pd.read_csv(path, encoding="utf-8")
    # 2) 칼럼명 공백 제거
    df.columns = df.columns.str.strip()
    # 3) 완전히 빈(모두 NaN) 열은 제거
    df = df.dropna(axis=1, how='all')
    # 4) ‘관리부서’ → ‘지역’ 리네임
    if '관리부서' in df.columns:
        df = df.rename(columns={'관리부서': '지역'})
    else:
        # 없을 땐 빈 열 뒤의 실제 지역 컬럼이름으로 강제 지정
        # 예시: 마지막에서 두 번째 열이 ‘지역’일 가능성이 높다면
        df = df.rename(columns={df.columns[-2]: '지역'})
    # 5) ‘합계’ 칼럼 → ‘가로등 수’
    sum_cols = [c for c in df.columns if '합계' in c]
    if not sum_cols:
        raise KeyError(f"❌ 가로등 합계 칼럼을 찾을 수 없습니다. 실제 칼럼: {list(df.columns)}")
    df = df.rename(columns={sum_cols[0]: '가로등 수'})

    return df[['지역', '가로등 수']]

# ─── 탭3 함수 ───
def tab3_oneperson_vs_lights():
    st.subheader("🏠 1인 가구 수 vs 가로등 수")

    try:
        # 1) 1인 가구 하드코딩
        one_person = {
            '지역': ['중부','동래','영도','동부','부산진','서부','남부','해운대',
                   '사상','금정','사하','연제','강서','북부','기장'],
            '1인 가구 수': [
                11786,35220,20116,18603,70609,
                20760,40521,50516,36299,40412,
                46442,30846,17355,36975,22500
            ]
        }
        df_one = pd.DataFrame(one_person)

        # 2) 가로등 데이터 로드
        df_lights = load_lights_data()

        # 3) 병합
        df = pd.merge(df_one, df_lights, on='지역')

        # 4) 산점도
        fig1, ax1 = plt.subplots()
        ax1.scatter(df['1인 가구 수'], df['가로등 수'])
        for _, row in df.iterrows():
            ax1.text(
                row['1인 가구 수'], row['가로등 수'], row['지역'],
                fontsize=9, fontproperties=fontprop
            )
        ax1.set_xlabel("1인 가구 수", fontproperties=fontprop)
        ax1.set_ylabel("가로등 수", fontproperties=fontprop)
        ax1.set_title("1인 가구 수 vs 가로등 수 (산점도)", fontproperties=fontprop)
        st.pyplot(fig1)

        # 5) 막대 그래프
        fig2, ax2 = plt.subplots(figsize=(12,6), dpi=80)
        idx = np.arange(len(df))
        width = 0.4
        ax2.bar(idx, df['1인 가구 수'], width, label='1인 가구 수')
        ax2.bar(idx + width, df['가로등 수'], width, label='가로등 수')
        ax2.set_xticks(idx + width/2)
        ax2.set_xticklabels(df['지역'], rotation=45, fontproperties=fontprop)
        ax2.set_ylabel("건수", fontproperties=fontprop)
        ax2.set_title("지역별 1인 가구 수 vs 가로등 수 비교", fontproperties=fontprop)
        ax2.legend(prop=fontprop)
        ax2.grid(True)
        st.pyplot(fig2)

    except KeyError as ke:
        st.error(str(ke))
    except Exception as e:
        st.error(f"❌ 1인 가구 vs 가로등 시각화 오류: {type(e).__name__}: {e}")
