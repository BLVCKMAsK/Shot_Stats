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

st.title("シュートマップ作成")
with st.expander("ツールの説明"):
    st.markdown("""
        ### ツールについて
        このツールは選手のシーズンのシュートデータをCSV形式で書き出し、そこからシュートマップ画像を作成するツールです。文字や数字だけのデータを視覚的にシュートの傾向を分析できるツールです。

        ### ツールの使い方
        1. **選手IDを入手**: サイドバーにある"Understat"にアクセスし特定の選手をサイト内で検索。検索後、URLの末尾についた数字のみをコピーし選手IDを取得します。(例: 1234)

        2. **選手IDを入力**: 選手ID取得後このページに戻り、サイドバーにある"選手IDを入力”のフォームに先ほどコピーしたIDを貼り付けます。

        3. **シーズンを選択**: 取得したいシーズンを"シーズンを選択"の欄から選択。

        4. **スタッツを取得**: サイドバーの"スタッツを取得"ボタンを押し特定のデータを出力。出力されたデータがメイン画面に表示され、その下に"スタッツをダウンロード"というボタンが出るのでそのボタンを押し出力されたデータをCSV形式で保存。

        5. **ダウンロードしたファイルをアップロード**: ステップ4でダウンロードしたファイルをサイドバーの"CSVファイルをアップロードしてください"の欄にファイルをアップロード。

        6. **作成されたシュートマップを保存**: ファイルをアップロード後メイン画面に指定されたデータのシュートマップが作成されるので、下の"画像をダウンロード"のボタンから作成されたシュートマップをダウンロード。
    """)

st.sidebar.title("入力フォーム")
st.sidebar.markdown("[Understatのサイトはこちら](https://understat.com/)")

player_id = st.sidebar.text_input("選手IDを入力",placeholder = "例: 1234")
season = st.sidebar.selectbox("シーズンを選択",["2024","2023","2022","2021","2020","2019","2018","2017","2016","2015","2014"])

if st.sidebar.button("スタッツを取得"):
    try:
        client = understatapi.UnderstatClient()
        player_data = client.player(player = player_id).get_shot_data()
        df = pd.DataFrame(player_data)
        df_season = df[df["season"] == season]
        player_name = df["player"].iloc[0] if "player" in df.columns else "Player"

        st.success(f"{player_name} のシーズン {season} のデータを取得しました。")
        st.dataframe(df_season)

        csv = df_season.to_csv(index = False).encode("utf-8")
        st.download_button(
            label = "スタッツをダウンロード",
            data = csv,
            file_name = f"{player_name.replace(' ', '_')}_{season}.csv",
            mime = "text/csv"
        )

    except Exception as e:
        st.error(f"スタッツの取得に失敗しました。: {e}")

uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type = "csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    player_name = df["player"].iloc[0] if "player" in df.columns else "Player"
    season_from_csv = df["season"].iloc[0] if "season" in df.columns else "Unknown"

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

    ax1.text(.5, .9, player_name, fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='center')
    ax1.text(.5, .75, f'All shots in League {season_from_csv}', fontsize=14, fontname='Roboto', fontweight='bold', color='white', ha='center')
    ax1.text(.2, .5, 'Low Quality Chance', fontsize=12, fontname='Roboto', fontweight='bold', color='white', ha='center')

    ax1.scatter(
    x = .37,
    y = .53,
    s = 100,
    color = background_color,
    edgecolor = 'white',
    linewidth = .8
    )

    ax1.scatter(
    x = .42,
    y = .53,
    s = 200,
    color = background_color,
    edgecolor = 'white',
    linewidth = .8
    )

    ax1.scatter(
    x = .48,
    y = .53,
    s = 300,
    color = background_color,
    edgecolor = 'white',
    linewidth = .8
    )

    ax1.scatter(
    x = .54,
    y = .53,
    s = 400,
    color = background_color,
    edgecolor = 'white',
    linewidth = .8
    )

    ax1.scatter(
    x = .6,
    y = .53,
    s = 500,
    color = background_color,
    edgecolor = 'white',
    linewidth = .8
    )

    ax1.text(.8, .5, 'Hight Quality Chance', fontsize=12, fontname='Roboto', fontweight='bold', color='white', ha='center')
    ax1.text(0.45, 0.27, 'Goal', fontsize=10, fontname='Roboto', color='white', ha='right')
    ax1.scatter(0.47, 0.3, s=100, color='red', edgecolor='white', linewidth=0.8, alpha=0.7)
    ax1.scatter(0.53, 0.3, s=100, color=background_color, edgecolor='white', linewidth=0.8)
    ax1.text(0.55, 0.27, 'No Goal', fontsize=10, fontname='Roboto', color='white', ha='left')

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
    ax2.text(90, points_average_distance - 4, f'Average Distance\n{actual_average_distance:.1f} M', fontsize=10, fontname='Roboto', color='white', ha='center')

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

    ax3.text(.15, .5, 'Shots', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
    ax3.text(.185, 0, f'{total_shots}', fontsize=16, fontname='Roboto', color='red', ha='left')

    ax3.text(.35, .5, 'Goals', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
    ax3.text(.385, 0, f'{total_goals}', fontsize=16, fontname='Roboto', color='red', ha='left')

    ax3.text(.56, .5, 'xG', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
    ax3.text(.555, 0, f'{total_xG:.2f}', fontsize=16, fontname='Roboto', color='red', ha='left')

    ax3.text(.7, .5, 'xG/Shot', fontsize=20, fontname='Roboto', fontweight='bold', color='white', ha='left')
    ax3.text(.74, 0, f'{xG_per_shot:.2f}', fontsize=16, fontname='Roboto', color='red', ha='left')

    buf = io.BytesIO()
    st.pyplot(fig)
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    st.download_button(
        label="画像をダウンロード",
        data=buf.getvalue(),
        file_name = f"{player_name.replace(' ', '_')}_{season}.png",
        mime="image/png"
    )