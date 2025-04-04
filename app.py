import streamlit as st
import pandas as pd
import understatapi
import altair as alt
from streamlit_option_menu import option_menu
from demo4 import app as demo4_app
from demo5 import app as demo5_app

selected = option_menu(
    menu_title=None,
    options=["Desktop", "Mobile"],
    icons=["laptop", "phone"],
    orientation="horizontal"
)

if selected == "Desktop":
    demo4_app()
elif selected == "Mobile":
    demo5_app()