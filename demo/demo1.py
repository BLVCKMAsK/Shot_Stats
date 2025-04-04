# CSVファイルとして保存するコード

import streamlit as st
import pandas as pd
import understatapi
import altair as alt

player_id = st.text_input("選手IDを入力", placeholder="例: 1234", key='a1')
season = st.selectbox("シーズンを選択", [str(y) for y in range(2024, 2013, -1)], key='a2')

if st.button("スタッツを取得", key='a3'):
    try:
        client = understatapi.UnderstatClient()
        player_data = client.player(player=player_id).get_shot_data()
        df = pd.DataFrame(player_data)
        df_season = df[df["season"] == season]
        player_name = df["player"].iloc[0] if "player" in df.columns else "Player"

        st.success(f"{player_name} の {season} シーズンのデータを取得しました。")
        st.dataframe(df_season)

        csv = df_season.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="スタッツをダウンロード",
            data=csv,
            file_name=f"{player_name.replace(' ', '_')}_{season}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"スタッツの取得に失敗しました。: {e}")