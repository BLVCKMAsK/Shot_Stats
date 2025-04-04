import streamlit as st
import pandas as pd
import understatapi
import altair as alt
from streamlit_option_menu import option_menu
from demo1 import app as demo1_app
from demo6 import app as demo6_app

selected = option_menu(
    menu_title=None,
    options=["Desktop", "Mobile"],
    icons=["laptop", "phone"],
    orientation="horizontal"
)

if selected == "Desktop":
    demo1_app()
elif selected == "Mobile":
    demo6_app()