# 1つのスタッツからシュートマップを作成するコード

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import understatapi
from mplsoccer import VerticalPitch
import io

# スタイル設定
background_color = "#0C0D0E"
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    </style>
""", unsafe_allow_html=True)

# タイトルと説明
st.title("シュートマップ作成")
with st.expander("ツールの説明"):
    st.markdown("""
        ### ツールについて
        このツールは選手のシーズンのシュートデータをCSV形式で書き出し、そこからシュートマップ画像を作成するツールです。
        文字や数字だけのデータを視覚的にシュートの傾向を分析できます。
    """)

# サイドバー UI
st.sidebar.title("入力フォーム")
st.sidebar.markdown("[Understatのサイトはこちら](https://understat.com/)")
player_id = st.sidebar.text_input("選手IDを入力", placeholder="例: 1234")
season = st.sidebar.selectbox("シーズンを選択", [str(y) for y in range(2024, 2013, -1)])
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type="csv")

# 状態初期化
if "df_season" not in st.session_state:
    st.session_state["df_season"] = None
    st.session_state["player_name"] = ""
    st.session_state["season"] = ""

# ボタンで取得トリガー
if st.sidebar.button("スタッツを取得") or uploaded_file:
    try:
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            df_season = df
            player_name = df["player"].iloc[0] if "player" in df.columns else "Player"
            season_from_csv = df["season"].iloc[0] if "season" in df.columns else "Unknown"
        else:
            client = understatapi.UnderstatClient()
            player_data = client.player(player=player_id).get_shot_data()
            df = pd.DataFrame(player_data)
            df_season = df[df["season"] == season]
            player_name = df["player"].iloc[0] if not df_season.empty else "Player"
            season_from_csv = season

        # セッション保存
        st.session_state["df_season"] = df_season
        st.session_state["player_name"] = player_name
        st.session_state["season"] = season_from_csv

        st.success(f"{player_name} のシーズン {season_from_csv} のデータを取得しました。")

        # データ整形
        df = df_season.copy()
        df["X"] = df["X"].astype(float) * 100
        df["Y"] = df["Y"].astype(float) * 100
        df["xG"] = df["xG"].astype(float)

        total_shots = df.shape[0]
        total_goals = df[df["result"] == "Goal"].shape[0]
        total_xG = df["xG"].sum()
        xG_per_shot = total_xG / total_shots if total_shots > 0 else 0
        points_average_distance = df["X"].mean()
        actual_average_distance = (120 - (df["X"] * 1.2).mean()) * 0.9144

        # プロット
        fig = plt.figure(figsize=(8, 12))
        fig.patch.set_facecolor(background_color)

        ax1 = fig.add_axes([0, .7, 1, .2])
        ax1.set_facecolor(background_color)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis("off")
        ax1.text(.5, .9, player_name, fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax1.text(.5, .75, f'All shots in League {season_from_csv}', fontsize=14, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax1.text(.2, .5, 'Low Quality Chance', fontsize=12, fontname='Roboto', fontweight='bold', color='white', ha='center')
        for i, x in enumerate([.37, .42, .48, .54, .6]):
            ax1.scatter(x, .53, s=(i+1)*100, color=background_color, edgecolor='white', linewidth=0.8)
        ax1.text(.8, .5, 'High Quality Chance', fontsize=12, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax1.text(.45, .27, 'Goal', fontsize=10, fontname='Roboto', color='white', ha='right')
        ax1.scatter(.47, .3, s=100, color='red', edgecolor='white', linewidth=0.8, alpha=0.7)
        ax1.scatter(.53, .3, s=100, color=background_color, edgecolor='white', linewidth=0.8)
        ax1.text(.55, .27, 'No Goal', fontsize=10, fontname='Roboto', color='white', ha='left')

        ax2 = fig.add_axes([.05, .25, .9, .5])
        pitch = VerticalPitch(pitch_type='opta', half=True, pitch_color=background_color, pad_bottom=0.5, line_color='white', linewidth=0.75, axis=True, label=True)
        pitch.draw(ax=ax2)
        ax2.set_facecolor(background_color)
        ax2.axis("off")
        ax2.scatter(90, points_average_distance, s=100, color='white', linewidth=0.8)
        ax2.plot([90, 90], [100, points_average_distance], color='white', linewidth=2)
        ax2.text(90, points_average_distance - 4, f'Average Distance\n{actual_average_distance:.1f} M', fontsize=10, fontname='Roboto', color='white', ha='center')
        for shot in df.to_dict(orient='records'):
            pitch.scatter(shot['X'], shot['Y'], s=300 * shot['xG'], color='red' if shot['result'] == 'Goal' else background_color, ax=ax2, alpha=0.7, linewidth=0.8, edgecolor='white')

        ax3 = fig.add_axes([0, .2, 1, .05])
        ax3.set_facecolor(background_color)
        ax3.axis("off")
        ax3.text(.15, .5, 'Shots', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax3.text(.185, 0, f'{total_shots}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax3.text(.35, .5, 'Goals', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax3.text(.385, 0, f'{total_goals}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax3.text(.56, .5, 'xG', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax3.text(.555, 0, f'{total_xG:.2f}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax3.text(.7, .5, 'xG/Shot', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax3.text(.74, 0, f'{xG_per_shot:.2f}', fontsize=16, fontname='Roboto', color='red', ha='left')

        # 表示と保存
        buf = io.BytesIO()
        st.pyplot(fig)
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
        st.download_button(
            label="画像をダウンロード",
            data=buf.getvalue(),
            file_name=f"{player_name.replace(' ', '_')}_{season_from_csv}.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"スタッツの取得または描画に失敗しました: {e}")





