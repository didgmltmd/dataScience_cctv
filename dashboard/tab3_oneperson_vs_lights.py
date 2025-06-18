# dashboard/tab3_oneperson_vs_lights.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def tab3_oneperson_vs_lights():
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    fontprop = fm.FontProperties(fname=font_path)
    plt.rcParams['axes.unicode_minus'] = False

    st.subheader("🏠 1인가구 수 vs 가로등 수")

    try:
        one_person_data = {
            '지역': ['중부', '동래', '영도', '동부', '부산진', '서부', '남부', '해운대',
                    '사상', '금정', '사하', '연제', '강서', '북부', '기장'],
            '1인가구수': [11786, 35220, 20116, 18603, 70609, 20760, 40521, 50516,
                        36299, 40412, 46442, 30846, 17355, 36975, 22500]
        }
        df_one = pd.DataFrame(one_person_data)
        df_lights = pd.read_csv("data/가로등현황.csv", encoding="cp949")
        df_lights.columns = df_lights.columns.str.strip()
        df_lights.rename(columns={"관리부서": "지역", "합계": "가로등수"}, inplace=True)
        df_lights['지역'] = df_lights['지역'].str.replace(" ", "")
        df_merged = pd.merge(df_one, df_lights[['지역', '가로등수']], on='지역')

        # 산점도
        fig1, ax1 = plt.subplots()
        ax1.scatter(df_merged['1인가구수'], df_merged['가로등수'])
        for i in range(len(df_merged)):
            ax1.text(df_merged['1인가구수'][i], df_merged['가로등수'][i],
                    df_merged['지역'][i], fontsize=9, fontproperties=fontprop)
        ax1.set_xlabel("1인가구 수", fontproperties=fontprop)
        ax1.set_ylabel("가로등 수", fontproperties=fontprop)
        ax1.set_title("1인가구 수 vs 가로등 수 (산점도)", fontproperties=fontprop)
        st.pyplot(fig1)

        # 막대 그래프
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        index = np.arange(len(df_merged))
        bar_width = 0.4
        ax2.bar(index, df_merged['1인가구수'], bar_width, label='1인가구 수')
        ax2.bar(index + bar_width, df_merged['가로등수'], bar_width, label='가로등 수')
        ax2.set_xticks(index + bar_width / 2)
        ax2.set_xticklabels(df_merged['지역'], rotation=45, fontproperties=fontprop)
        ax2.set_ylabel("건수", fontproperties=fontprop)
        ax2.set_title("지역별 1인가구 수 vs 가로등 수 비교", fontproperties=fontprop)
        ax2.legend(prop=fontprop)
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ 1인가구/가로등 시각화 오류: {e}")
