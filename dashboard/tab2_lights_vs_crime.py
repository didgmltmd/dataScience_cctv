# dashboard/tab2_lights_vs_crime.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

def load_csv_with_fallback(path, encodings=['utf-8-sig', 'cp949', 'utf-8']):
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = df.columns.str.strip()
            return df
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"❌ 파일 '{path}' 의 인코딩을 인식할 수 없습니다. UTF-8 또는 CP949인지 확인하세요.")

def find_and_rename_region(df, possible_names):
    """
    df 내에서 possible_names 리스트 중 하나라도 포함된 컬럼을 찾아
    '지역'으로 rename. 없으면 KeyError 발생.
    """
    for name in possible_names:
        for col in df.columns:
            if name in col:
                return df.rename(columns={col: '지역'})
    raise KeyError(f"❌ DataFrame에 '지역' 역할을 하는 컬럼이 없습니다. 가능한 후보: {possible_names}, 실제 컬럼: {list(df.columns)}")

def tab2_lights_vs_crime():
    st.subheader("📈 지역별 가로등 수 vs 5대 범죄 발생 수")

    # 폰트 설정
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        st.error(f"❌ 폰트 파일이 없습니다: {font_path}")
        return
    fontprop = font_manager.FontProperties(fname=font_path)
    plt.rcParams['axes.unicode_minus'] = False

    try:
        # 데이터 로드
        df_lights = load_csv_with_fallback("data/가로등현황.csv")
        df_crime  = load_csv_with_fallback("data/경찰청_범죄현황.csv")

        # '지역' 컬럼 찾고 rename
        df_lights = find_and_rename_region(df_lights, ['관리부서', '지역'])
        df_crime  = find_and_rename_region(df_crime,  ['지역', '관서', '구역'])

        # 숫자 합계 컬럼명도 strip
        df_lights.columns = df_lights.columns.str.strip()
        df_crime.columns  = df_crime.columns.str.strip()

        # 합계 컬럼이름 찾기 (예: '합계' 혹은 '총합' 등)
        sum_col_lights = next(c for c in df_lights.columns if '합계' in c)
        sum_col_crime  = next(c for c in df_crime.columns  if '합계' in c)

        # merge 준비
        df_lights = df_lights[['지역', sum_col_lights]].rename(columns={sum_col_lights: '합계_가로등'})
        df_crime  = df_crime[['지역', sum_col_crime ]].rename(columns={sum_col_crime : '합계_범죄'})

        merged = pd.merge(df_lights, df_crime, on='지역')

        # 시각화
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(merged['지역'], merged['합계_가로등'], label='가로등 수', marker='o', color='green')
        ax.plot(merged['지역'], merged['합계_범죄'], label='범죄 발생 수', marker='s', color='red')

        ax.set_xticks(range(len(merged['지역'])))
        ax.set_xticklabels(merged['지역'], rotation=45, fontproperties=fontprop)
        ax.set_xlabel("지역", fontproperties=fontprop)
        ax.set_ylabel("건수", fontproperties=fontprop)
        ax.set_title("지역별 가로등 수와 범죄 발생 수 비교", fontproperties=fontprop)
        ax.legend(prop=fontprop)
        ax.grid(True, linestyle="--", alpha=0.5)

        st.pyplot(fig)

    except KeyError as ke:
        st.error(str(ke))
    except Exception as e:
        st.error(f"❌ 범죄/가로등 시각화 오류:\n{type(e).__name__}: {e}")
