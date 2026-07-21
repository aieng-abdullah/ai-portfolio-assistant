import streamlit as st
import requests

API_BASE = "http://localhost:3000"

st.set_page_config(page_title="Widget Customizer", page_icon="🎨", layout="wide")
st.title("Widget Customizer")

slug = st.text_input("Widget Slug", value="my-portfolio")

if st.button("Load Config"):
    try:
        r = requests.get(f"{API_BASE}/api/widget/{slug}/config", timeout=5)
        st.session_state.config = r.json()
    except Exception as e:
        st.error(f"Error: {e}")

config = st.session_state.get("config", {})
theme = config.get("theme", {})
personality = config.get("personality", {})

col1, col2 = st.columns(2)

with col1:
    st.subheader("Theme")
    primary_color = st.color_picker("Primary Color", value=theme.get("primaryColor", "#4F46E5"))
    secondary_color = st.color_picker("Secondary Color", value=theme.get("secondaryColor", "#1E1B4B"))
    font_family = st.selectbox(
        "Font Family",
        ["Inter", "system-ui", "Poppins", "Roboto", "Open Sans"],
        index=0,
    )
    border_radius = st.slider("Border Radius (px)", 0, 24, int(theme.get("borderRadius", "12px").replace("px", "") or 12))
    chat_title = st.text_input("Chat Title", value=theme.get("chatTitle", "Portfolio Assistant"))
    chat_subtitle = st.text_input("Chat Subtitle", value=theme.get("chatSubtitle", "Ask me anything"))
    welcome_message = st.text_area("Welcome Message", value=theme.get("welcomeMessage", "Hi! Ask me about my work."))
    position = st.selectbox(
        "Position",
        ["bottom-right", "bottom-left", "top-right", "top-left"],
        index=0,
    )

with col2:
    st.subheader("Personality")
    tone = st.select_slider(
        "Tone",
        options=["Professional", "Balanced", "Witty", "Casual"],
        value=personality.get("tone", "Witty"),
    )
    humor_level = st.slider("Humor Level", 0, 10, personality.get("humorLevel", 7))
    custom_prompt = st.text_area(
        "Custom System Prompt (advanced)",
        value=personality.get("systemPrompt", ""),
        height=200,
    )

st.markdown("---")

theme_config = {
    "primaryColor": primary_color,
    "secondaryColor": secondary_color,
    "fontFamily": font_family,
    "borderRadius": f"{border_radius}px",
    "chatTitle": chat_title,
    "chatSubtitle": chat_subtitle,
    "welcomeMessage": welcome_message,
    "position": position,
}

personality_config = {
    "tone": tone,
    "humorLevel": humor_level,
    "systemPrompt": custom_prompt,
}

st.subheader("Preview")
st.json({"theme": theme_config, "personality": personality_config})

st.subheader("Embed Code")
embed_code = f'<script src="http://localhost:3000/widget.js" data-widget-id="{slug}" data-position="{position}" async></script>'
st.code(embed_code, language="html")
