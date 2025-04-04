import streamlit as st
import pandas as pd
import understatapi
import altair as alt
from streamlit_option_menu import option_menu

from demo.demo4 import app as demo4_app
from demo.demo5 import app as demo5_app

selected = option_menu(
    menu_title=None,
    options=["Mobile", "Desktop"],
    icons=["phone", "laptop"],
    orientation="horizontal"
)

if selected == "Mobile":
    demo4_app()
elif selected == "Desktop":
    demo5_app()
