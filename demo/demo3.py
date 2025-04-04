# 2つのスタッツから比較したシュートマップを作成するコード

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import understatapi
from mplsoccer import VerticalPitch
import io
from matplotlib import font_manager

background_color = "#0C0D0E"

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    </style>
""", unsafe_allow_html=True)

st.title("シュートマップ作成（比較モード）")
with st.expander("ツールの説明"):
    st.markdown("""
        ### このモードについて
        2人の選手のシュートスタッツを同時に比較できるモードです。
        入力した選手IDとシーズンに基づき、2つのデータを上下に並べて視覚的に比較します。
    """)

st.sidebar.title("入力フォーム（比較モード）")
st.sidebar.markdown("[Understatのサイトはこちら](https://understat.com/)")

player1_id = st.sidebar.text_input("選手1のID", placeholder="例: 1234", key="p1")
season1 = st.sidebar.selectbox("シーズン（選手1）", [str(y) for y in range(2024, 2013, -1)], key="s1")

player2_id = st.sidebar.text_input("選手2のID", placeholder="例: 5678", key="p2")
season2 = st.sidebar.selectbox("シーズン（選手2）", [str(y) for y in range(2024, 2013, -1)], key="s2")

uploaded_file1 = st.sidebar.file_uploader("選手1のCSVアップロード", type="csv", key="file1")
uploaded_file2 = st.sidebar.file_uploader("選手2のCSVアップロード", type="csv", key="file2")

if st.sidebar.button("スタッツを比較"):
    try:
        client = understatapi.UnderstatClient()

        # Player 1
        if uploaded_file1:
            df1 = pd.read_csv(uploaded_file1)
            name1 = df1["player"].iloc[0] if "player" in df1.columns else "Player1"
            season1 = df1["season"].iloc[0] if "season" in df1.columns else "Unknown"
        else:
            data1 = client.player(player=player1_id).get_shot_data()
            df1 = pd.DataFrame(data1)
            df1 = df1[df1["season"] == season1]
            name1 = df1["player"].iloc[0] if not df1.empty else "Player1"

        # Player 2
        if uploaded_file2:
            df2 = pd.read_csv(uploaded_file2)
            name2 = df2["player"].iloc[0] if "player" in df2.columns else "Player2"
            season2 = df2["season"].iloc[0] if "season" in df2.columns else "Unknown"
        else:
            data2 = client.player(player=player2_id).get_shot_data()
            df2 = pd.DataFrame(data2)
            df2 = df2[df2["season"] == season2]
            name2 = df2["player"].iloc[0] if not df2.empty else "Player2"

        df1["X"] = df1["X"].astype(float) * 100
        df1["Y"] = df1["Y"].astype(float) * 100
        df1["xG"] = df1["xG"].astype(float)

        df2["X"] = df2["X"].astype(float) * 100
        df2["Y"] = df2["Y"].astype(float) * 100
        df2["xG"] = df2["xG"].astype(float)

        st.success(f"{name1} ({season1}) と {name2} ({season2}) のデータを取得しました。")

        total_shots_1 = df1.shape[0]
        total_goals_1 = df1[df1["result"] == "Goal"].shape[0]
        total_xG_1 = df1["xG"].sum()
        xG_per_shot_1 = total_xG_1 / total_shots_1 if total_shots_1 > 0 else 0
        dist_points_1 = df1["X"].mean()
        actual_avg_dist_1 = (120 - (df1["X"] * 1.2).mean()) * 0.9144

        total_shots_2 = df2.shape[0]
        total_goals_2 = df2[df2["result"] == "Goal"].shape[0]
        total_xG_2 = df2["xG"].sum()
        xG_per_shot_2 = total_xG_2 / total_shots_2 if total_shots_2 > 0 else 0
        dist_points_2 = df2["X"].mean()
        actual_avg_dist_2 = (120 - (df2["X"] * 1.2).mean()) * 0.9144

        fig = plt.figure(figsize=(8, 12))
        fig.patch.set_facecolor(background_color)

        # 上側のプレイヤー（player1）
        ax_title1 = fig.add_axes([0, .7, 1, .2])
        ax_title1.set_facecolor(background_color)
        ax_title1.set_xlim(0, 1)
        ax_title1.set_ylim(0, 1)
        ax_title1.set_xticks([])
        ax_title1.set_yticks([])
        ax_title1.set_frame_on(False)

        ax_title1.text(.5, .9, name1, fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax_title1.text(.5, .75, f"All shots in League {season1}", fontsize=14, fontname='Roboto', fontweight='bold', color='white', ha='center')

        for i, x in enumerate([.37, .42, .48, .54, .6]):
            ax_title1.scatter(x, .53, s=(i + 1) * 100, color=background_color, edgecolor='white', linewidth=.8)

        ax_title1.text(.2, .5, "Low Quality Chance", fontsize=12, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax_title1.text(.8, .5, "High Quality Chance", fontsize=12, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax_title1.text(.45, .27, "Goal", fontsize=10, fontname='Roboto', color='white', ha='right')
        ax_title1.scatter(.47, .3, s=100, color='red', edgecolor='white', linewidth=.8, alpha=.7)
        ax_title1.scatter(.53, .3, s=100, color=background_color, edgecolor='white', linewidth=.8)
        ax_title1.text(.55, .27, "No Goal", fontsize=10, fontname='Roboto', color='white', ha='left')

        ax_pitch1 = fig.add_axes([.05, .25, .9, .5])
        pitch = VerticalPitch(pitch_type='opta', half=True, pitch_color=background_color, pad_bottom=.5, line_color='white', linewidth=.75, axis=True, label=True)
        pitch.draw(ax=ax_pitch1)
        ax_pitch1.set_facecolor(background_color)
        ax_pitch1.set_xticks([])
        ax_pitch1.set_yticks([])
        ax_pitch1.set_frame_on(False)
        ax_pitch1.scatter(90, dist_points_1, s=100, color='white', linewidth=.8)
        ax_pitch1.plot([90, 90], [100, dist_points_1], color='white', linewidth=2)
        ax_pitch1.text(90, dist_points_1 - 4, f"Average Distance\n{actual_avg_dist_1:.1f} M", fontsize=10, fontname='Roboto', color='white', ha='center')

        ax_stats1 = fig.add_axes([0, .2, 1, .05])
        ax_stats1.set_facecolor(background_color)
        ax_stats1.set_xticks([])
        ax_stats1.set_yticks([])
        ax_stats1.set_frame_on(False)
        ax_stats1.text(.15, 4, 'Shots', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax_stats1.text(.18, 3.5, f'{total_shots_1}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax_stats1.text(.35, 4, 'Goals', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax_stats1.text(.38, 3.5, f'{total_goals_1}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax_stats1.text(.56, 4, 'xG', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax_stats1.text(.55, 3.5, f'{total_xG_1:.2f}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax_stats1.text(.7, 4, 'xG/Shot', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax_stats1.text(.73, 3.5, f'{xG_per_shot_1:.2f}', fontsize=16, fontname='Roboto', color='red', ha='left')

        for shot in df1.to_dict(orient='records'):
            pitch.scatter(shot['X'], shot['Y'], s=300 * shot['xG'], color='red' if shot['result'] == 'Goal' else background_color, ax=ax_pitch1, alpha=0.7, linewidth=0.8, edgecolor='white')

        # 下側のプレイヤー（player2）
        ax_title2 = fig.add_axes([0, -0.35, 1, 0.2])
        ax_title2.set_facecolor(background_color)
        ax_title2.set_xlim(0, 1)
        ax_title2.set_ylim(0, 1)
        ax_title2.set_xticks([])
        ax_title2.set_yticks([])
        ax_title2.set_frame_on(False)

        ax_title2.text(0.5, 0.1, name2, fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax_title2.text(0.5, 0.25, f"All shots in League {season2}", fontsize=14, fontname='Roboto', fontweight='bold', color='white', ha='center')

        for i, x in enumerate([.37, .42, .48, .54, .6]):
            ax_title2.scatter(x, .53, s=(i + 1) * 100, color=background_color, edgecolor='white', linewidth=.8)

        ax_title2.text(.2, .5, "Low Quality Chance", fontsize=12, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax_title2.text(.8, .5, "High Quality Chance", fontsize=12, fontname='Roboto', fontweight='bold', color='white', ha='center')
        ax_title2.text(.45, .7, "Goal", fontsize=10, fontname='Roboto', color='white', ha='right')
        ax_title2.scatter(.47, .73, s=100, color='red', edgecolor='white', linewidth=.8, alpha=.7)
        ax_title2.scatter(.53, .73, s=100, color=background_color, edgecolor='white', linewidth=.8)
        ax_title2.text(.55, .7, "No Goal", fontsize=10, fontname='Roboto', color='white', ha='left')

        ax_pitch2 = fig.add_axes([.05, -.2, .9, .5])
        pitch.draw(ax=ax_pitch2)
        ax_pitch2.set_facecolor(background_color)
        ax_pitch2.set_xticks([])
        ax_pitch2.set_yticks([])
        ax_pitch2.set_frame_on(False)
        ax_pitch2.scatter(90, dist_points_2, s=100, color='white', linewidth=.8)
        ax_pitch2.plot([90, 90], [100, dist_points_2], color='white', linewidth=2)
        ax_pitch2.text(90, dist_points_2 - 4, f"Average Distance\n{actual_avg_dist_2:.1f} M", fontsize=10, fontname='Robot', color='white', ha='center')
        
        ax_stats2 = fig.add_axes([0, .0, 1, .05])
        ax_stats2.set_facecolor(background_color)
        ax_stats2.set_xticks([])
        ax_stats2.set_yticks([])
        ax_stats2.set_frame_on(False)
        ax_stats2.text(.15, 3, 'Shots', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax_stats2.text(.18, 2.5, f'{total_shots_2}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax_stats2.text(.35, 3, 'Goals', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax_stats2.text(.38, 2.5, f'{total_goals_2}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax_stats2.text(.56, 3, 'xG', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax_stats2.text(.55, 2.5, f'{total_xG_2:.2f}', fontsize=16, fontname='Roboto', color='red', ha='left')
        ax_stats2.text(.7, 3, 'xG/Shot', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
        ax_stats2.text(.73, 2.5, f'{xG_per_shot_2:.2f}', fontsize=16, fontname='Roboto', color='red', ha='left')

        for shot in df2.to_dict(orient='records'):
            pitch.scatter(shot['X'], shot['Y'], s=300 * shot['xG'], color='red' if shot['result'] == 'Goal' else background_color, ax=ax_pitch2, alpha=0.7, linewidth=0.8, edgecolor='white')

        ax_pitch2.invert_yaxis()

        buf = io.BytesIO()
        st.pyplot(fig)
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
        st.download_button(
            label="画像をダウンロード",
            data=buf.getvalue(),
            file_name=f"{name1.replace(' ', '_')}_{season1}_vs_{name2.replace(' ', '_')}_{season2}.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"スタッツの取得または描画に失敗しました: {e}")