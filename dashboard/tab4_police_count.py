# dashboard/tab4_police_count.py

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
def load_police_data(path="data/부산동별경찰서.csv"):
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = df.columns.str.strip()
            return df
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"❌ 파일 '{path}' 인코딩을 인식할 수 없습니다.")

# ─── ‘지역’·‘개수’ 컬럼 탐지 ───
def find_column(df, keywords):
    for col in df.columns:
        if any(kw in col for kw in keywords):
            return col
    return None

# ─── 탭4 함수 ───
def tab4_police_count():
    st.subheader("🚓 부산 동별 경찰서 수")

    try:
        df = load_police_data()

        # 컬럼 동적 탐색
        region_col = find_column(df, ["경찰서","지역"]) or find_column(df, ["동별","구별"])
        count_col  = find_column(df, ["개수","수","건수"])
        if not region_col or not count_col:
            raise KeyError(f"❌ 컬럼 탐색 실패:\n지역컬럼: {df.columns}\n개수컬럼: {df.columns}")

        df = df.rename(columns={region_col: "지역", count_col: "개수"})
        df = df.sort_values("개수", ascending=False)

        # 시각화
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(df["지역"], df["개수"], color="skyblue")

        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df["지역"], rotation=45,
                           fontproperties=fontprop if fontprop else None)
        ax.set_xlabel("지역", fontproperties=fontprop)
        ax.set_ylabel("경찰서 수", fontproperties=fontprop)
        ax.set_title("부산 동별 경찰서 수", fontproperties=fontprop)

        for bar in bars:
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2, h,
                f"{int(h)}", ha="center", va="bottom",
                fontproperties=fontprop
            )

        st.pyplot(fig)

    except KeyError as ke:
        st.error(str(ke))
    except Exception as e:
        st.error(f"❌ 경찰서 수 시각화 오류:\n{type(e).__name__}: {e}")
