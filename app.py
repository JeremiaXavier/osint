# app.py

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from osint import run_osint_app

# --- Load configuration and user credentials ---
try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file 'config.yaml' not found. Please create one.")
    st.stop()

# --- Create the authenticator object ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- Render the login form ---
authenticator.login(location='main')

# --- Get authentication values from session_state ---
name = st.session_state.get("name")
authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# --- Display content based on authentication status ---
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.title(f"Welcome, {name}")
    run_osint_app()

elif authentication_status is False:
    st.error("Username/password is incorrect")

elif authentication_status is None:
    st.warning("Please enter your username and password")
