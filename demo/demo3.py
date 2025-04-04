import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import io
from matplotlib import font_manager

background_color = "#0C0D0E"
font_path = "/Users/masksmacbook/Documents/Fonts/arvo/Arvo-Regular.ttf"
font_props = font_manager.FontProperties(fname=font_path)

st.title("シュートマップ作成")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type = "csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    df["X"] = df["X"] * 100
    df["Y"] = df["Y"] * 100

    total_shots = df.shape[0]
    total_goals = df[df["result"] == "Goal"].shape[0]
    total_xG = df["xG"].sum()
    xG_per_shot = total_xG / total_shots
    points_average_distance = df["X"].mean()
    actual_average_distance = 120 - (df["X"] * 1.2).mean()
    actual_average_distance = actual_average_distance * 0.9144

    fig = plt.figure(figsize=(8, 12))
    fig.patch.set_facecolor(background_color)

    ax1 = fig.add_axes([0, .7, 1, .2])
    ax1.set_facecolor(background_color)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_frame_on(False)

    ax1.text(.5, .9, 'Raphinha', fontsize=20, fontproperties=font_props, fontweight='bold', color='white', ha='center')
    ax1.text(.5, .75, 'All shots in La liga 2024-25', fontsize=14, fontproperties=font_props, fontweight='bold', color='white', ha='center')
    ax1.text(.25, .5, 'Low Quality Chance', fontsize=12, fontproperties=font_props, fontweight='bold', color='white', ha='center')

    for i, s in enumerate([100, 200, 300, 400, 500]):
        ax1.scatter(x=0.37 + i * 0.05, y=0.53, s=s, color=background_color, edgecolor='white', linewidth=0.8)

    ax1.text(.75, .5, 'Hight Quality Chance', fontsize=12, fontproperties=font_props, fontweight='bold', color='white', ha='center')
    ax1.text(0.45, 0.27, 'Goal', fontsize=10, fontproperties=font_props, color='white', ha='right')
    ax1.scatter(0.47, 0.3, s=100, color='red', edgecolor='white', linewidth=0.8, alpha=0.7)
    ax1.scatter(0.53, 0.3, s=100, color=background_color, edgecolor='white', linewidth=0.8)
    ax1.text(0.55, 0.27, 'No Goal', fontsize=10, fontproperties=font_props, color='white', ha='left')

    ax2 = fig.add_axes([.05, .25, .9, .5])
    ax2.set_facecolor(background_color)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_frame_on(False)

    pitch = VerticalPitch(
        pitch_type='opta',
        half=True,
        pitch_color=background_color,
        pad_bottom=0.5,
        line_color='white',
        linewidth=0.75,
        axis=True,
        label=True
    )
    pitch.draw(ax=ax2)

    ax2.scatter(x=90, y=points_average_distance, s=100, color='white', linewidth=0.8)
    ax2.plot([90, 90], [100, points_average_distance], color='white', linewidth=2)
    ax2.text(90, points_average_distance - 4, f'Average Distance\n{actual_average_distance:.1f} yards', fontsize=10, fontproperties=font_props, color='white', ha='center')

    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x['X'],
            x['Y'],
            s=300 * x['xG'],
            color='red' if x['result'] == 'Goal' else background_color,
            ax=ax2,
            alpha=0.7,
            linewidth=0.8,
            edgecolor='white'
        )

    ax3 = fig.add_axes([0, .2, 1, .05])
    ax3.set_facecolor(background_color)
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.set_frame_on(False)

    ax3.text(.15, .5, 'Shots', fontsize=20, fontproperties=font_props, fontweight='bold', color='white', ha='left')
    ax3.text(.18, 0, f'{total_shots}', fontsize=16, fontproperties=font_props, color='red', ha='left')

    ax3.text(.35, .5, 'Goals', fontsize=20, fontproperties=font_props, fontweight='bold', color='white', ha='left')
    ax3.text(.38, 0, f'{total_goals}', fontsize=16, fontproperties=font_props, color='red', ha='left')

    ax3.text(.56, .5, 'xG', fontsize=20, fontproperties=font_props, fontweight='bold', color='white', ha='left')
    ax3.text(.55, 0, f'{total_xG:.2f}', fontsize=16, fontproperties=font_props, color='red', ha='left')

    ax3.text(.7, .5, 'xG/Shot', fontsize=20, fontproperties=font_props, fontweight='bold', color='white', ha='left')
    ax3.text(.73, 0, f'{xG_per_shot:.2f}', fontsize=16, fontproperties=font_props, color='red', ha='left')

    buf = io.BytesIO()
    st.pyplot(fig)
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    st.download_button(
        label="画像をダウンロード",
        data=buf.getvalue(),
        file_name="shotmap.png",
        mime="image/png"
    )


