import streamlit as st
import requests

API_BASE = "http://localhost:3000"

st.set_page_config(page_title="Profile Editor", page_icon="👤", layout="wide")
st.title("Profile Editor")

slug = st.text_input("Widget Slug", value="my-portfolio")

st.subheader("Current Profile")
if st.button("Load Profile"):
    try:
        r = requests.get(f"{API_BASE}/api/widget/{slug}/profile", timeout=5)
        st.session_state.profile = r.json()
    except Exception as e:
        st.error(f"Error: {e}")

profile = st.session_state.get("profile", {})

with st.form("profile_form"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Name", value=profile.get("name", ""))
        title = st.text_input("Title", value=profile.get("title", ""))
        bio = st.text_area("Bio", value=profile.get("bio", ""))
        location = st.text_input("Location", value=profile.get("location", ""))

    with col2:
        skills_text = st.text_area(
            "Skills (one per line)",
            value="\n".join(profile.get("skills", [])),
        )
        experience_text = st.text_area(
            "Experience (one per line)",
            value="\n".join(profile.get("experience", [])),
        )

    st.subheader("Contact")
    contact = profile.get("contact", {})
    col3, col4 = st.columns(2)
    with col3:
        email = st.text_input("Email", value=contact.get("email", ""))
        website = st.text_input("Website", value=contact.get("website", ""))
    with col4:
        linkedin = st.text_input("LinkedIn", value=contact.get("linkedin", ""))

    submitted = st.form_submit_button("Save Profile")
    if submitted:
        profile_data = {
            "name": name,
            "title": title,
            "bio": bio,
            "location": location,
            "skills": [s.strip() for s in skills_text.split("\n") if s.strip()],
            "experience": [e.strip() for e in experience_text.split("\n") if e.strip()],
            "contact": {
                "email": email,
                "website": website,
                "linkedin": linkedin,
            },
        }
        st.json(profile_data)
        st.info("Profile data ready. POST to /api/widget/{slug}/profile to save.")
