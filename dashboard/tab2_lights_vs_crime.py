# dashboard/tab2_lights_vs_crime.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
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
    fontprop = font_manager.FontProperties(fname=font_path)
    plt.rcParams['axes.unicode_minus'] = False
else:
    fontprop = None  # 기본 폰트 사용

# ─── 데이터 로더 ───
@st.cache_data
def load_csv_with_fallback(path, encodings=('utf-8-sig', 'cp949', 'euc-kr', 'latin1', 'utf-8')):
    """여러 인코딩을 시도하여 CSV를 로드하고 컬럼명 공백 제거"""
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = df.columns.str.strip()
            return df
        except Exception:
            continue
    raise UnicodeDecodeError(f"❌ 파일 '{path}' 인코딩을 인식할 수 없습니다. 시도: {encodings}")

def find_and_rename_region(df, candidates=('관리부서','지역','관서','구역')):
    """후보 키워드가 포함된 컬럼을 '지역'으로 rename, 없으면 마지막 비숫자 열을 '지역'으로 지정"""
    # 1) 키워드 매칭
    for col in df.columns:
        if any(kw in col for kw in candidates):
            return df.rename(columns={col:'지역'})
    # 2) 마지막 열을 지역으로 가정 (숫자형이 아니면)
    last = df.columns[-1]
    if pd.api.types.is_numeric_dtype(df[last]):
        raise KeyError(f"❌ '지역' 컬럼을 찾을 수 없고, 마지막 열이 숫자형입니다: {last}")
    return df.rename(columns={last:'지역'})

# ─── 탭2 함수 ───
def tab2_lights_vs_crime():
    st.subheader("📈 지역별 가로등 수 vs 5대 범죄 발생 수")
    try:
        # 1) 데이터 로드
        df_lights = load_csv_with_fallback("data/가로등현황.csv")
        df_crime  = load_csv_with_fallback("data/경찰청_범죄현황.csv")

        # 2) '지역' 컬럼 통일
        df_lights = find_and_rename_region(df_lights)
        df_crime  = find_and_rename_region(df_crime)

        # 3) '합계' 컬럼 찾기
        sum_light = next(c for c in df_lights.columns if '합계' in c)
        sum_crime = next(c for c in df_crime.columns  if '합계' in c)

        # 4) 필요한 컬럼으로 정리
        df_l = df_lights[['지역', sum_light]].rename(columns={sum_light:'합계_가로등'})
        df_c = df_crime[['지역', sum_crime ]].rename(columns={sum_crime :'합계_범죄'})

        # 5) 병합
        merged = pd.merge(df_l, df_c, on='지역')

        # 6) 시각화
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(merged['지역'], merged['합계_가로등'], label='가로등 수',
                marker='o', color='green')
        ax.plot(merged['지역'], merged['합계_범죄'], label='범죄 발생 수',
                marker='s', color='red')

        ax.set_xticks(range(len(merged)))
        ax.set_xticklabels(merged['지역'], rotation=45,
                           fontproperties=fontprop if fontprop else None)
        ax.set_xlabel("지역", fontproperties=fontprop)
        ax.set_ylabel("건수", fontproperties=fontprop)
        ax.set_title("지역별 가로등 수와 범죄 발생 수 비교", fontproperties=fontprop)
        ax.legend(prop=fontprop)
        ax.grid(True, linestyle='--', alpha=0.5)

        st.pyplot(fig)

    except KeyError as ke:
        st.error(str(ke))
    except Exception as e:
        st.error(f"❌ 범죄/가로등 시각화 오류:\n{type(e).__name__}: {e}")
