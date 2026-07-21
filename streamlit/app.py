import streamlit as st
import requests

API_BASE = "http://localhost:3000"

st.set_page_config(
    page_title="AI Portfolio Assistant - Dashboard",
    page_icon="🤖",
    layout="wide",
)

st.title("AI Portfolio Assistant Dashboard")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Widget Status")
    slug = st.text_input("Widget Slug", value="my-portfolio")
    if st.button("Check Health"):
        try:
            r = requests.get(f"{API_BASE}/api/health", timeout=5)
            st.json(r.json())
        except Exception as e:
            st.error(f"API not reachable: {e}")

with col2:
    st.subheader("Quick Actions")
    if st.button("Disable Widget"):
        try:
            r = requests.post(f"{API_BASE}/api/admin/widget/{slug}/disable", timeout=5)
            st.json(r.json())
        except Exception as e:
            st.error(f"Error: {e}")
    if st.button("Enable Widget"):
        try:
            r = requests.post(f"{API_BASE}/api/admin/widget/{slug}/enable", timeout=5)
            st.json(r.json())
        except Exception as e:
            st.error(f"Error: {e}")
    if st.button("View Stats"):
        try:
            r = requests.get(f"{API_BASE}/api/admin/widget/{slug}/stats", timeout=5)
            st.json(r.json())
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")

st.subheader("Embed Code")
embed_code = f'<script src="http://localhost:3000/widget.js" data-widget-id="{slug}" async></script>'
st.code(embed_code, language="html")

st.markdown("---")

st.subheader("Chat Test")
st.caption("Test the chat widget directly from here")
user_message = st.text_input("Your message", placeholder="Ask about my work...")
if st.button("Send") and user_message:
    with st.spinner("Thinking..."):
        try:
            r = requests.post(
                f"{API_BASE}/api/chat/{slug}",
                json={"sessionId": "streamlit-test", "message": user_message},
                timeout=30,
            )
            data = r.json()
            st.success(data.get("response", "No response"))
        except Exception as e:
            st.error(f"Error: {e}")
