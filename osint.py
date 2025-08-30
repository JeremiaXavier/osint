import streamlit as st
import subprocess
import json
import whois
import exifread
import requests
import instaloader
from io import BytesIO

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
    st.header("📷 Instagram Profile OSINT")
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
    st.header("🌍 OSINT across websites (Maigret)")
    uname = st.text_input("Enter username to check across platforms:")
    if st.button("Run Maigret"):
        if uname:
            st.info("Running Maigret... this may take a while ⏳")
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
                    st.warning("No output from Maigret.")
                if result.stderr:
                    st.error(result.stderr)
            except Exception as e:
                st.error(f"Error running Maigret: {e}")
        else:
            st.warning("Please enter a username")
# --- 3. Username Check (Sherlock) --- #


def sherlock_osint():
    """Searches for a username on various social networks using Sherlock."""
    st.header("🕵️ Username OSINT with Sherlock")
    uname = st.text_input("Enter username to check across platforms:")
    if st.button("Run Sherlock"):
        if uname:
            st.info("Running Sherlock... ⏳")
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
                st.error(f"Error running Sherlock: {e}")
        else:
            st.warning("Please enter a username")
# --- 4. Email Lookup (Holehe) --- #


def holehe_osint():
    """Checks if an email is registered on various websites using Holehe."""
    st.header("📧 Email OSINT with Holehe")
    email = st.text_input("Enter email address:")
    if st.button("Run Holehe"):
        if email:
            st.info("Checking email with Holehe... ⏳")
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
                st.error(f"Error running Holehe: {e}")
        else:
            st.warning("Please enter an email address")

# --- 5. Domain Recon (theHarvester) --- #


def harvester_osint():
    """Gathers information about a domain using theHarvester."""
    st.header("🌐 Domain OSINT with theHarvester")
    domain = st.text_input("Enter domain (e.g. example.com):")
    if st.button("Run theHarvester"):
        if domain:
            st.info("Running theHarvester... ⏳")
            try:
                result = subprocess.run(
                    ["theHarvester", "-d", domain, "-l", "100", "-b", "all"], capture_output=True, text=True)
                if result.stdout:
                    st.code(result.stdout)
                else:
                    st.warning("No results.")
                if result.stderr:
                    st.error(result.stderr)
            except Exception as e:
                st.error(f"Error running theHarvester: {e}")
        else:
            st.warning("Please enter a domain")

# --- 6. Domain Whois --- #


def whois_lookup():
    """Performs a Whois lookup on a given domain."""
    st.header("🌐 Domain Whois Lookup")
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


def exif_extractor():
    """Extracts EXIF metadata from an uploaded image or image URL."""
    st.header("🖼️ Image EXIF Metadata Extractor")
    image_file = st.file_uploader(
        "Upload an image file", type=["jpg", "jpeg", "png"])
    st.write("OR")
    image_url = st.text_input("...enter an image URL:")
    if st.button("Extract Metadata"):
        if image_file or image_url:
            st.info("Extracting EXIF data... ⏳")
            try:
                if image_file:
                    image_data = BytesIO(image_file.read())
                elif image_url:
                    response = requests.get(image_url)
                    image_data = BytesIO(response.content)
                tags = exifread.process_file(image_data)
                if tags:
                    st.success("EXIF data extracted successfully ✅")
                    formatted_tags = {str(k): str(v)
                                      for k, v in tags.items()}
                    st.json(formatted_tags)
                else:
                    st.warning("No EXIF metadata found in this image.")
            except Exception as e:
                st.error(f"Error extracting metadata: {e}")
        else:
            st.warning("Please upload an image or enter a URL.")

# --- Main App Logic --- #


def run_osint_app():
    st.sidebar.title("OSINT Toolkit")
    st.sidebar.markdown(
        "Select an OSINT tool from the list to get started. "
    )

    tool = st.sidebar.radio(
        "Choose a tool:",
        [
            "Instagram Profile Info",
            "Username Check (Maigret)",
            "Username Check (Sherlock)",
            "Email Lookup (Holehe)",
            "Domain Recon (theHarvester)",
            "Domain Whois",
            "Image EXIF Metadata",
        ]
    )

    if tool == "Instagram Profile Info":
        instagram_osint()
    elif tool == "Username Check (Maigret)":
        maigret_osint()
    elif tool == "Username Check (Sherlock)":
        sherlock_osint()
    elif tool == "Email Lookup (Holehe)":
        holehe_osint()
    elif tool == "Domain Recon (theHarvester)":
        harvester_osint()
    elif tool == "Domain Whois":
        whois_lookup()
    elif tool == "Image EXIF Metadata":
        exif_extractor()
