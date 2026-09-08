import streamlit as st

st.set_page_config(
    page_title="Wi-Fi Scanner",
    page_icon="📶",
    layout="wide"
)

st.title("📶 Wi-Fi Network & Signal Scanner")

st.write("Streamlit is working correctly!")

if st.button("Test Button"):
    st.success("Button is working!")
