# dashboard/tab4_police_count.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def tab4_police_count():
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    fontprop = fm.FontProperties(fname=font_path)
    plt.rcParams['axes.unicode_minus'] = False

    st.subheader("🚓 부산 동별 경찰서 수")

    try:
        df_police = pd.read_csv("data/부산동별경찰서.csv", encoding="cp949")
        df_police.columns = df_police.columns.str.strip()
        df_police = df_police.sort_values("개수", ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(df_police["경찰서"], df_police["개수"], color="skyblue")

        ax.set_xticks(range(len(df_police)))
        ax.set_xticklabels(df_police["경찰서"], rotation=45, fontproperties=fontprop)
        ax.set_xlabel("지역", fontproperties=fontprop)
        ax.set_ylabel("경찰서 수", fontproperties=fontprop)
        ax.set_title("부산 동별 경찰서 수", fontproperties=fontprop)

        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f"{int(height)}",
                    ha='center', va='bottom', fontproperties=fontprop)

        st.pyplot(fig)
    except Exception as e:
        st.error(f"❌ 경찰서 수 시각화 오류: {e}")
