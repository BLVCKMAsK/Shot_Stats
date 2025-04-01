import streamlit as st
import pandas as pd
import understatapi
import altair as alt

st.title("player_shot_stats")

player_id = st.text_input("選手IDを入力",placeholder = "例: 1234")
season = st.selectbox("シーズンを選択",["2024","2023","2022"])

if st.button("スタッツを取得"):
    try:
        client = understatapi.UnderstatClient()
        player_data = client.player(player = player_id).get_shot_data()
        df = pd.DataFrame(player_data)
        df_season = df[df["season"] == season]

        st.success(f"選手ID {player_id}のシーズン{season}のデータを取得しました。")
        st.dataframe(df_season)

        csv = df_season.to_csv(index = False).encode("utf-8")
        st.download_button(
            label = "スタッツをダウンロード",
            data = csv,
            file_name = f"player_{player_id}_shots_{season}.csv",
            mime = "text/csv"
        )

    except Exception as e:
        st.error(f"スタッツの取得に失敗しました。: {e}")