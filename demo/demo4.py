# モバイル用のコード

import streamlit as st

def app():

    st.markdown("[Understatのサイトはこちら](https://understat.com/)")
    mode = st.radio("モードを選択", ["スタッツの取得", "スタッツの比較", "CSVファイルとして保存"], horizontal=True)

    if mode == "スタッツの取得":
        import pandas as pd
        import matplotlib.pyplot as plt
        import understatapi
        from mplsoccer import VerticalPitch
        import io
    
        # スタイル設定
        background_color = "#0C0D0E"
    
        from matplotlib import font_manager

        font_path = Path(os.getcwd()) / "demo" / "fonts" / "NotoSansJP-Regular.otf"
        font_prop = font_manager.FontProperties(fname=str(font_path))
    
        # タイトルと説明
        st.title("シュートマップ作成")
        with st.expander("ツールについて"):
            st.markdown("""
                ここでは特定の選手のシーズンにおけるシュートデータを取得し、そこから視覚的に選手のシュートの傾向を分析しやすいようシュートマップ画像を作成するツールです。
            """)

        with st.expander("ツールの使い方"):
            st.markdown("""
                1.**選手IDの取得**: サイドバーにある"Understatのサイトはこちら"からUnderstatに飛び、スタッツを取得したい選手の名前をサイト内で検索。検索後URLの末尾にある数字のみをコピーし選手IDを取得。

                2.**入力フォームの入力**: ID取得後元のページに戻り入力フォームの内容を埋めてください。"選手IDを入力"に先ほどコピーしたIDをペーストし、"シーズンを選択"から特定のシーズンを選択してください。もしCSVからシュートマップを作成する場合、モードの"CSVファイルとして保存"から同じ手順でスタッツを取得し保存したファイルをアップロードしてください。

                3.**シュートマップを作成 & ダウンロード**: 入力フォームの入力後サイドバー内の"スタッツを取得"のボタンを押しシュートマップを作成。作成されたシュートマップを保存したい場合は、作成されたシュートマップの下にある"シュートマップをダウンロード"のボタンをクリックし画像をダウンロードしてください。
            """)

        with st.expander("ツールを使う上での注意"):
            st.markdown("""
                - このツールはUnderstatのサイトをスクレイピングして運用しているためUnderstatに大きく依存します。そのためUnderstat内のデータが破損したり、Understatのサイトそのものがなくなった場合、ツールが使えなくなる可能性があります。長期的にスタッツを扱いたい場合CSVファイルとして一度データを保存し、そこからシュートマップを作成することをお勧めします。

                - このツールで扱える選手データはヨーロッパの5大リーグ(イングランド、イタリア、ドイツ、フランス、スペイン)のみかつ、14-15シーズンから24-25シーズンまでの範囲までになります。そのためこの要件に該当しない選手のスタッツを取得することはできません。

                - Understatで選手を検索する場合は英語のみでの検索になるのでご注意ください。また、選手IDに関しては選手によって数字の桁数が違うのでその点もご注意ください。

                - 選手IDとシーズンを選択してシュートマップを作成する場合CSVファイルをアップロードする必要はありません。逆も同様にすでにCSVファイルとしてスタッツを取得している場合、選手IDとシーズンを入力する必要はありません。用途に合わせてお使いください。
            """)

        st.markdown("---")
    
        # サイドバー UI
        player_id = st.text_input("選手IDを入力", placeholder="例: 1234", key='id_get_mobile')
        season = st.selectbox("シーズンを選択", [str(y) for y in range(2024, 2013, -1)], key='season_get_mobile')
        with st.expander("CSVからシュートマップを作成する場合"):
            uploaded_file = st.file_uploader("CSVファイルをアップロード", type="csv", key='file_get_mobile')
    
        # 状態初期化
        if "df_season" not in st.session_state:
            st.session_state["df_season"] = None
            st.session_state["player_name"] = ""
            st.session_state["season"] = ""
    
        # ボタンで取得トリガー
        if st.button("スタッツを取得", key='btn_1_mobile') or uploaded_file:
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
                ax1.text(.5, .9, player_name, fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax1.text(.5, .75, f'{season_from_csv} シーズンのリーグ戦でのシュートスタッツ', fontsize=14, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax1.text(.2, .5, 'ゴール期待値(小)', fontsize=12, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                for i, x in enumerate([.37, .42, .48, .54, .6]):
                    ax1.scatter(x, .53, s=(i+1)*100, color=background_color, edgecolor='white', linewidth=0.8)
                ax1.text(.8, .5, 'ゴール期待値(大)', fontsize=12, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax1.text(.45, .27, 'ゴール', fontsize=10, fontproperties=font_prop, color='white', ha='right')
                ax1.scatter(.47, .3, s=100, color='red', edgecolor='white', linewidth=0.8, alpha=0.7)
                ax1.scatter(.53, .3, s=100, color=background_color, edgecolor='white', linewidth=0.8)
                ax1.text(.55, .27, 'ノーゴール', fontsize=10, fontproperties=font_prop, color='white', ha='left')
    
                ax2 = fig.add_axes([.05, .25, .9, .5])
                pitch = VerticalPitch(pitch_type='opta', half=True, pitch_color=background_color, pad_bottom=0.5, line_color='white', linewidth=0.75, axis=True, label=True)
                pitch.draw(ax=ax2)
                ax2.set_facecolor(background_color)
                ax2.axis("off")
                ax2.scatter(90, points_average_distance, s=100, color='white', linewidth=0.8)
                ax2.plot([90, 90], [100, points_average_distance], color='white', linewidth=2)
                ax2.text(90, points_average_distance - 4, f'平均シュート距離\n{actual_average_distance:.1f} M', fontsize=10, fontproperties=font_prop, color='white', ha='center')
                for shot in df.to_dict(orient='records'):
                    pitch.scatter(shot['X'], shot['Y'], s=300 * shot['xG'], color='red' if shot['result'] == 'Goal' else background_color, ax=ax2, alpha=0.7, linewidth=0.8, edgecolor='white')
    
                ax3 = fig.add_axes([0, .2, 1, .05])
                ax3.set_facecolor(background_color)
                ax3.axis("off")
                ax3.text(.05, .5, 'シュート数', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax3.text(.11, 0, f'{total_shots}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax3.text(.28, .5, 'ゴール数', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax3.text(.33, 0, f'{total_goals}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax3.text(.48, .5, 'ゴール期待値', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax3.text(.54, 0, f'{total_xG:.2f}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax3.text(.75, .5, 'シュート効率', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax3.text(.82, 0, f'{xG_per_shot:.2f}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
    
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
    
   

    elif mode == "スタッツの比較":
        import pandas as pd
        import matplotlib.pyplot as plt
        import understatapi
        from mplsoccer import VerticalPitch
        import io
        from matplotlib import font_manager

        background_color = "#0C0D0E"

        from matplotlib import font_manager

        font_path = "fonts/NotoSansJP-Regular.otf"
        font_prop = font_manager.FontProperties(fname=font_path)

        st.title("シュートマップ作成(比較)")
        with st.expander("ツールの説明"):
            st.markdown("""
                ここでは2つのスタッツを取得しそこからそれぞれのスタッツを比較したシュートマップを作成することができます。
            """)

        with st.expander("ツールの使い方"):
            st.markdown("""
                基本的な使い方は"スタッツを取得"モードの時と同じなので詳細はそちらを確認してください。
            """)

        st.markdown("---")

        player1_id = st.text_input("選手1のIDを入力", placeholder="例: 1234", key="p1_mobile")
        season1 = st.selectbox("選手1のシーズンを選択", [str(y) for y in range(2024, 2013, -1)], key="s1_mobile")

        player2_id = st.text_input("選手2のIDを入力", placeholder="例: 5678", key="p2_mobile")
        season2 = st.selectbox("選手2のシーズンを選択", [str(y) for y in range(2024, 2013, -1)], key="s2_mobile")

        with st.expander("CSVからシュートマップを作成する場合"):
            uploaded_file1 = st.file_uploader("選手1のCSVファイルをここにアップロード", type="csv", key="file1_mobile")
            uploaded_file2 = st.file_uploader("選手2のCSVファイルをここにアップロード", type="csv", key="file2_mobile")

        if st.button("スタッツを比較", key='btn_2_mobile'):
            try:
                client = understatapi.UnderstatClient()

                if uploaded_file1:
                    df1 = pd.read_csv(uploaded_file1)
                    name1 = df1["player"].iloc[0] if "player" in df1.columns else "Player1"
                    season1 = df1["season"].iloc[0] if "season" in df1.columns else "Unknown"
                else:
                    data1 = client.player(player=player1_id).get_shot_data()
                    df1 = pd.DataFrame(data1)
                    df1 = df1[df1["season"] == season1]
                    name1 = df1["player"].iloc[0] if not df1.empty else "Player1"

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
    
                ax_title1.text(.5, .9, name1, fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax_title1.text(.5, .75, f"{season1} シーズンのリーグ戦でのシュートスタッツ", fontsize=14, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
    
                for i, x in enumerate([.37, .42, .48, .54, .6]):
                    ax_title1.scatter(x, .53, s=(i + 1) * 100, color=background_color, edgecolor='white', linewidth=.8)
    
                ax_title1.text(.2, .5, "ゴール期待値(小)", fontsize=12, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax_title1.text(.8, .5, "ゴール期待値(大)", fontsize=12, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax_title1.text(.45, .27, "ゴール", fontsize=10, fontproperties=font_prop, color='white', ha='right')
                ax_title1.scatter(.47, .3, s=100, color='red', edgecolor='white', linewidth=.8, alpha=.7)
                ax_title1.scatter(.53, .3, s=100, color=background_color, edgecolor='white', linewidth=.8)
                ax_title1.text(.55, .27, "ノーゴール", fontsize=10, fontproperties=font_prop, color='white', ha='left')
    
                ax_pitch1 = fig.add_axes([.05, .25, .9, .5])
                pitch = VerticalPitch(pitch_type='opta', half=True, pitch_color=background_color, pad_bottom=.5, line_color='white', linewidth=.75, axis=True, label=True)
                pitch.draw(ax=ax_pitch1)
                ax_pitch1.set_facecolor(background_color)
                ax_pitch1.set_xticks([])
                ax_pitch1.set_yticks([])
                ax_pitch1.set_frame_on(False)
                ax_pitch1.scatter(90, dist_points_1, s=100, color='white', linewidth=.8)
                ax_pitch1.plot([90, 90], [100, dist_points_1], color='white', linewidth=2)
                ax_pitch1.text(90, dist_points_1 - 4, f"平均シュート距離\n{actual_avg_dist_1:.1f} M", fontsize=10, fontproperties=font_prop, color='white', ha='center')
    
                ax_stats1 = fig.add_axes([0, .2, 1, .05])
                ax_stats1.set_facecolor(background_color)
                ax_stats1.set_xticks([])
                x_stats1.set_yticks([])
                ax_stats1.set_frame_on(False)
                ax_stats1.text(.05, 4, 'シュート数', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax_stats1.text(.11, 3.5, f'{total_shots_1}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax_stats1.text(.28, 4, 'ゴール数', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax_stats1.text(.33, 3.5, f'{total_goals_1}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax_stats1.text(.48, 4, 'ゴール期待値', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax_stats1.text(.54, 3.5, f'{total_xG_1:.2f}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax_stats1.text(.75, 4, 'シュート効率', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax_stats1.text(.82, 3.5, f'{xG_per_shot_1:.2f}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
    
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
    
                ax_title2.text(0.5, 0.1, name2, fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax_title2.text(0.5, 0.25, f"{season2} シーズンのリーグ戦でのシュートスタッツ", fontsize=14, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
    
                for i, x in enumerate([.37, .42, .48, .54, .6]):
                    ax_title2.scatter(x, .53, s=(i + 1) * 100, color=background_color, edgecolor='white', linewidth=.8)
    
                ax_title2.text(.2, .5, "ゴール期待値(小)", fontsize=12, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax_title2.text(.8, .5, "ゴール期待値(大)", fontsize=12, fontproperties=font_prop, fontweight='bold', color='white', ha='center')
                ax_title2.text(.45, .7, "ゴール", fontsize=10, fontproperties=font_prop, color='white', ha='right')
                ax_title2.scatter(.47, .73, s=100, color='red', edgecolor='white', linewidth=.8, alpha=.7)
                ax_title2.scatter(.53, .73, s=100, color=background_color, edgecolor='white', linewidth=.8)
                ax_title2.text(.55, .7, "ノーゴール", fontsize=10, fontproperties=font_prop, color='white', ha='left')
    
                ax_pitch2 = fig.add_axes([.05, -.2, .9, .5])
                pitch.draw(ax=ax_pitch2)
                ax_pitch2.set_facecolor(background_color)
                ax_pitch2.set_xticks([])
                ax_pitch2.set_yticks([])
                ax_pitch2.set_frame_on(False)
                ax_pitch2.scatter(90, dist_points_2, s=100, color='white', linewidth=.8)
                ax_pitch2.plot([90, 90], [100, dist_points_2], color='white', linewidth=2)
                ax_pitch2.text(90, dist_points_2 - 4, f"平均シュート距離\n{actual_avg_dist_2:.1f} M", fontsize=10, fontname='Robot', color='white', ha='center')
            
                ax_stats2 = fig.add_axes([0, .0, 1, .05])
                ax_stats2.set_facecolor(background_color)
                ax_stats2.set_xticks([])
                ax_stats2.set_yticks([])
                ax_stats2.set_frame_on(False)
                ax_stats2.text(.05, 3, 'シュート数', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax_stats2.text(.11, 2.5, f'{total_shots_2}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax_stats2.text(.28, 3, 'ゴール数', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax_stats2.text(.33, 2.5, f'{total_goals_2}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax_stats2.text(.48, 3, 'ゴール期待値', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax_stats2.text(.54, 2.5, f'{total_xG_2:.2f}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
                ax_stats2.text(.75, 3, 'シュート効率', fontsize=20, fontproperties=font_prop, fontweight='bold', color='white', ha='left')
                ax_stats2.text(.82, 2.5, f'{xG_per_shot_2:.2f}', fontsize=16, fontproperties=font_prop, color='red', ha='left')
    
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



    elif mode == "CSVファイルとして保存":
        import pandas as pd
        import understatapi
        import altair as alt
    
        st.title("CSVファイルとして保存")
    
        with st.expander("ツールについて"):
            st.markdown("""
                ここではUnderstatから取得したデータをCSVファイルとして保存できるツールです。
            """)

        with st.expander("CSVファイルとして保存するメリット"):
            st.markdown("""
                1.**データの再利用**: 一度Understatから取得したデータを保存しておけば、次回以降データを取得することなく同じデータを再利用することができる。また、このツール以外の場所でもファイルとして保存しておけば利用することが可能。

                2.**データの編集**: Understatから取得したデータを後から編集したい際、CSVファイルとして保存しておけばExcelなどで開き自分自身でデータの整理、分析、編集が可能。

                3.**データの共有**: データを他者と共有したい際、CSVデータとして保存しておけばそのデータを他者と簡単に共有することが可能。

                4.**データの保険**: 使用上の注意でも記載した通り、このツールはUnderstatに大きく依存しているため、Understat側でデータが破損や消滅した場合データを正常に扱えなくなる可能性が高いです。CSVファイルとして保存しておけば仮にUnderstat側のデータに異常が生じた場合でもCSVファイルが破損、消滅することはありません。そのためデータを大量かつ頻繁に、また長期的に扱う場合CSVファイルとして保存し運用することをお勧めします。
            """)

        st.markdown("---")
    
        player_id = st.text_input("選手IDを入力",placeholder = "例: 1234", key='id_csv_mobile')
        season = st.selectbox("シーズンを選択",["2024","2023","2022","2021","2020","2019","2018","2017","2016","2015","2014"], key='season_csv_mobile')
    
        if st.button("スタッツを取得", key='btn_3_mobile'):
            try:
                client = understatapi.UnderstatClient()
                player_data = client.player(player = player_id).get_shot_data()
                df = pd.DataFrame(player_data)
                df_season = df[df["season"] == season]
                player_name = df["player"].iloc[0] if "player" in df.columns else "Player"
    
                st.success(f"{player_name} の {season} シーズンのデータを取得しました。")
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