import streamlit as st
import subprocess
import json
import os
import requests
from io import BytesIO

# You'll need to install these via pip
import instaloader
import whois
import exifread

# This is a custom library, requires manual installation
from socid_extractor import extract

st.set_page_config(page_title="OSINT Dashboard", layout="wide")
st.title("🕵️ OSINT Investigation Dashboard")

# Sidebar menu
tool = st.sidebar.selectbox(
    "Choose an OSINT Tool:",
    [
        "Instagram Profile Info",
        "Username Check (Maigret)",
        "Username Check (Sherlock)",
        "Email Lookup (Holehe)",
        "Domain Recon (theHarvester)",
        "Phone Number Lookup (PhoneInfoga)",

        "Domain Whois", "Image EXIF Metadata"
    ]
)


# ---------------- Instagram Profile Info ---------------- #
if tool == "Instagram Profile Info":  # I'm assuming you'll rename the menu option to "Instagram Profile Info"
    st.header("📷 Instagram Profile OSINT")
    username = st.text_input("Enter Instagram username:")

    if st.button("Get Profile Details"):
        if username:
            try:
                L = instaloader.Instaloader()
                profile = instaloader.Profile.from_username(
                    L.context, username)

                st.success("Profile data fetched successfully ✅")

                # Create two columns for profile picture and details
                col1, col2 = st.columns(2)

                # Place the image in the first column
                with col1:
                    st.image(profile.profile_pic_url,
                             caption=f"Profile Picture of {profile.username}")

                # Place the text details in the second column
                with col2:
                    st.write("**Username:**", profile.username)
                    st.write("**Full Name:**", profile.full_name)
                    st.write("**Bio:**", profile.biography)
                    st.write("**Followers:**", profile.followers)
                    st.write("**Following:**", profile.followees)
                    st.write("**Posts:**", profile.mediacount)

                st.divider()  # A visual separator

                st.subheader("Public Posts")

                # Create a generator for the posts
                posts = profile.get_posts()

                # Iterate through a few posts and display them
                for post in posts:
                    # Only process a limited number of posts to avoid a long wait time
                    if post.is_sponsored:  # Skip sponsored posts
                        continue

                    # Display the post image or video thumbnail and caption
                    st.image(
                        post.url, caption=f"Likes: {post.likes} | Comments: {post.comments}", width=300)
                    st.markdown(f"**Caption:** {post.caption}")
                    st.markdown(f"**Post URL:** {post.url}")
                    st.markdown("---")

            except Exception as e:
                st.error(f"Error fetching profile or posts: {e}")
        else:
            st.warning("Please enter an Instagram username.")
# ---------------- Username OSINT (Maigret) ---------------- #
elif tool == "Username Check (Maigret)":
    st.header("🌍 OSINT across websites (Maigret)")
    uname = st.text_input("Enter username to check across platforms:")

    if st.button("Run Maigret"):
        if uname:
            st.info("Running Maigret... this may take a while ⏳")
            try:
                # Run Maigret with JSON output
                result = subprocess.run(
                    ["python", "-m", "maigret", uname,
                        "-J", "simple"],  # Removed --print-found
                    capture_output=True, text=True
                )

                if result.stdout:
                    # Load JSON into app
                    try:
                        data = json.loads(result.stdout)
                        st.json(data)
                        st.success("Results fetched successfully ✅")
                    except json.JSONDecodeError:
                        st.warning(
                            "Could not parse JSON output. Showing raw output instead:")
                        st.code(result.stdout)
                else:
                    st.warning("No output from Maigret.")

                if result.stderr:
                    st.error(result.stderr)

            except Exception as e:
                st.error(f"Error running Maigret: {e}")
        else:
            st.warning("Please enter a username")
# ---------------- Metadata Extraction (socid_extractor) ---------------- #
elif tool == "Metadata from Instagram Post":
    st.header("📝 Metadata Extraction from Instagram Post")
    url = st.text_input("Enter Instagram Post URL:")

    if st.button("Extract Metadata"):
        if url:
            try:
                info = extract(url)
                if info:
                    st.json(info)
                else:
                    st.warning("No metadata found for this post.")
            except Exception as e:
                st.error(f"Error extracting metadata: {e}")
        else:
            st.warning("Please enter a post URL")
# ---------------- Sherlock ---------------- #
elif tool == "Username Check (Sherlock)":
    st.header("🕵️ Username OSINT with Sherlock")
    uname = st.text_input("Enter username to check across platforms:")

    if st.button("Run Sherlock"):
        if uname:
            st.info("Running Sherlock... ⏳")
            try:
                result = subprocess.run(
                    ["sherlock", uname, "--print-found", "--no-color"],
                    capture_output=True, text=True
                )

                if result.stdout:
                    st.code(result.stdout)
                else:
                    st.warning("No accounts found.")
                """ if result.stderr:
                    st.error(result.stderr) """
            except Exception as e:
                st.error(f"Error running Sherlock: {e}")
        else:
            st.warning("Please enter a username")
# ---------------- Holehe ---------------- #
elif tool == "Email Lookup (Holehe)":
    st.header("📧 Email OSINT with Holehe")
    email = st.text_input("Enter email address:")

    if st.button("Run Holehe"):
        if email:
            st.info("Checking email with Holehe... ⏳")
            try:
                result = subprocess.run(
                    ["holehe", email],
                    capture_output=True, text=True
                )
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
# ---------------- theHarvester ---------------- #
elif tool == "Domain Recon (theHarvester)":
    st.header("🌐 Domain OSINT with theHarvester")
    domain = st.text_input("Enter domain (e.g. example.com):")

    if st.button("Run theHarvester"):
        if domain:
            st.info("Running theHarvester... ⏳")
            try:
                result = subprocess.run(
                    ["theHarvester", "-d",
                        domain, "-l", "100", "-b", "all"],
                    capture_output=True, text=True
                )
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
elif tool == "Domain Whois":
    st.header("🌐 Domain Whois Lookup")
    domain = st.text_input("Enter domain (e.g., example.com):")

    if st.button("Run Whois"):
        if domain:
            try:
                # Using the python-whois library
                import whois
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

# ---------------- Image EXIF Metadata ---------------- #
elif tool == "Image EXIF Metadata":
    st.header("🖼️ Image EXIF Metadata Extractor")
    image_file = st.file_uploader(
        "Upload an image file", type=["jpg", "jpeg", "png"])
    image_url = st.text_input("...or enter an image URL:")

    if st.button("Extract Metadata"):
        if image_file or image_url:
            st.info("Extracting EXIF data... ⏳")
            try:
                import exifread
                import requests
                from io import BytesIO

                if image_file:
                    image_data = image_file
                elif image_url:
                    response = requests.get(image_url)
                    image_data = BytesIO(response.content)

                tags = exifread.process_file(image_data)

                if tags:
                    st.success("EXIF data extracted successfully ✅")
                    formatted_tags = {str(k): str(v) for k, v in tags.items()}
                    st.json(formatted_tags)
                else:
                    st.warning("No EXIF metadata found in this image.")

            except Exception as e:
                st.error(f"Error extracting metadata: {e}")
        else:
            st.warning("Please upload an image or enter a URL.")
