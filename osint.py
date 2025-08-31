import streamlit as st
import subprocess
import json
import whois

import requests
import instaloader
from io import BytesIO
import sys
# --- 1. Instagram Profile OSINT --- #

import os

def cleanup_txt_files(given_name, root="."):
    """
    Deletes all .txt files in the given root folder that start with a given name.

    :param given_name: the prefix of the filenames to delete (e.g. "report")
    :param root: folder to clean (default: current folder)
    """
    for item in os.listdir(root):
        path = os.path.join(root, item)
        if os.path.isfile(path) and item.startswith(given_name) and item.endswith(".txt"):
            try:
                os.remove(path)
               
            except Exception as e:
                print(f"Error deleting {item}: {e}")

def instagram_osint():
    """Fetches and displays public Instagram profile information."""
    st.header("📷 Instagram Profile Details")
    username = st.text_input("Enter Instagram username:")
    if st.button("Get Profile Details"):
        if username:
            try:
                st.info("Fetching profile data... ⏳")
                L = instaloader.Instaloader()
                profile = instaloader.Profile.from_username(
                    L.context, username)
                st.success("Profile data fetched successfully ✅")
                col1, col2 = st.columns(2)
                with col1:
                    st.image(profile.profile_pic_url,
                             caption=f"Profile Picture of {profile.username}")
                with col2:
                    st.write("**Username:**", profile.username)
                    st.write("**Full Name:**", profile.full_name)
                    st.write("**Bio:**", profile.biography)
                    st.write("**Followers:**", profile.followers)
                    st.write("**Following:**", profile.followees)
                    st.write("**Posts:**", profile.mediacount)
                st.divider()
                st.subheader("Public Posts")
                posts = profile.get_posts()
                for post in posts:
                    if post.is_sponsored:
                        continue
                    st.image(
                        post.url, caption=f"Likes: {post.likes} | Comments: {post.comments}", width=300)
                    st.markdown(f"**Caption:** {post.caption}")
                    st.markdown(f"**Post URL:** {post.url}")
                    st.markdown("---")
            except Exception as e:
                st.error(f"Error fetching profile or posts: {e}")
        else:
            st.warning("Please enter an Instagram username.")

# --- 2. Username Check (Maigret) --- #


def maigret_osint():
    """Checks for a username's existence across multiple websites using Maigret."""
    st.header("🌍 Username Intelligence across websites ")
    uname = st.text_input("Enter username to check across platforms:")
    if st.button("Run scan"):
        if uname:
            st.info("Running scan... this may take a while ⏳")
            try:
                # Add --no-files flag to prevent report generation
                result = subprocess.run(
                    ["maigret", uname], 
                    capture_output=True, 
                    text=True
                )
                if result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        st.json(data)
                        st.success("Results fetched successfully ✅")
                    except json.JSONDecodeError:
                        st.warning(
                            "Could not parse JSON output. Showing raw output instead:"
                        )
                        st.code(result.stdout)
                else:
                    st.warning("No output.")
                if result.stderr:
                    st.error(result.stderr)
            except Exception as e:
                st.error(f"Error running scan: {e}")
        else:
            st.warning("Please enter a username")
# --- 3. Username Check (Sherlock) --- #


def sherlock_osint():
    """Searches for a username on various social networks using Sherlock."""
    st.header("🕵️ Username Intelligence")
    uname = st.text_input("Enter username to check across platforms:")
    if st.button("Run scan"):
        if uname:
            st.info("Running scan... ⏳")
            try:
                result = subprocess.run(
                    # Add --no-color and --print-found to prevent file generation
                    ["sherlock", uname, "--no-color", "--print-found"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    st.code(result.stdout)
                    cleanup_txt_files(uname)
                else:
                    st.warning("No accounts found.")
            except Exception as e:
                st.error(f"Error running scan: {e}")
        else:
            st.warning("Please enter a username")
# --- 4. Email Lookup (Holehe) --- #


def holehe_osint():
    """Checks if an email is registered on various websites using Holehe."""
    st.header("📧 Email Intelligence")
    email = st.text_input("Enter email address:")
    if st.button("Run Scan"):
        if email:
            st.info("Checking email  ... ⏳")
            try:
                result = subprocess.run(
                    ["holehe", email], capture_output=True, text=True)
                if result.stdout:
                    st.code(result.stdout)
                else:
                    st.warning("No results.")
                if result.stderr:
                    st.error(result.stderr)
            except Exception as e:
                st.error(f"Error running scan: {e}")
        else:
            st.warning("Please enter an email address")

def social_analyzer_osint():
    st.header("👤 Social Analyzer")
    username = st.text_input("Enter a username to analyze:")
    
    if st.button("Run Social Analyzer"):
        if username:
            st.info("Running Social Analyzer... ⏳ This may take a moment.")
            try:
                # The -m flag runs the package as a module
                result = subprocess.run(
                    ["python3", "-m", "social-analyzer", "--username", username, "--mode", "fast", "--websites" ,"facebook instagram twitter linkedin youtube tumblr quora snapchat telegram pinterest whatsapp reddit github gitlab medium tiktok vimeo dailymotion soundcloud spotify clubhouse discord twitch slack stackoverflow wechat kakaotalk signal messenger"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if result.stdout:
                    st.success("Analysis complete. Results:")
                    st.code(result.stdout)
                else:
                    st.warning("No profiles found for this username.")
            except subprocess.CalledProcessError as e:
                st.error(f"Social Analyzer exited with an error. Check the input.")
                st.code(e.stderr)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter a username.")

def whois_lookup():
    """Performs a Whois lookup on a given domain."""
    st.header("🌐 Domain  Lookup")
    domain = st.text_input("Enter domain (e.g., example.com):")
    if st.button("Run Whois"):
        if domain:
            try:
                st.info("Querying Whois database... ⏳")
                w = whois.whois(domain)
                st.json(w)
                st.success("Whois data fetched successfully ✅")
            except whois.parser.PywhoisError as e:
                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Error fetching Whois data: {e}")
        else:
            st.warning("Please enter a domain.")

# --- 7. Image EXIF Metadata --- #




# --- Main App Logic --- #


def run_osint_app():
    st.sidebar.title("Intelligence Wing of Hexabyte")
    st.sidebar.markdown(
        "Select a tool from the list to get started. "
    )

    tool = st.sidebar.radio(
        "Choose a tool:",
        [
            "Instagram Profile Info",
            "Username Check 1",
            "Username Check 2",
            "Email Lookup",
            "Domain Details",
            "Social Media"
        ]
    )

    if tool == "Instagram Profile Info":
        instagram_osint()
    elif tool == "Username Check 1":
        maigret_osint()
    elif tool == "Username Check 2":
        sherlock_osint()
    elif tool == "Email Lookup":
        holehe_osint()
    
    elif tool == "Domain Details":
        whois_lookup()
    elif tool == "Social Media":

        social_analyzer_osint()
   
