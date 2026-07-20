import streamlit as st

st.set_page_config(page_title="Integration Guide", page_icon="📦", layout="wide")
st.title("Integration Guide")

slug = st.text_input("Your Widget Slug", value="my-portfolio")

st.markdown("---")

st.subheader("Step 1: Copy Your Embed Code")

embed_code = f"""<script
  src="http://localhost:3000/widget.js"
  data-widget-id="{slug}"
  async
></script>"""

st.code(embed_code, language="html")

if st.button("Copy to Clipboard"):
    st.code(embed_code)
    st.success("Copied!")

st.markdown("---")

st.subheader("Step 2: Paste Before </body>")

platforms = {
    "HTML / Static Sites": "Paste the code before </body> in your HTML file.",
    "WordPress": 'Appearance → Theme Editor → footer.php → paste before </body>\nOr use a plugin like "Insert Headers and Footers".',
    "Webflow": "Project Settings → Custom Code → Footer Code → paste → Save & Publish",
    "Squarespace": "Settings → Advanced → Code Injection → Footer → paste → Save",
    "Wix": "Settings → Custom Code → Add Code → Body (End) → paste → Publish",
    "Shopify": "Online Store → Themes → Edit Code → theme.liquid → paste before </body>",
    "Next.js / React": "Add to _app.js or layout.js using useEffect to create script dynamically.",
}

for platform, instruction in platforms.items():
    with st.expander(platform):
        st.markdown(instruction)

st.markdown("---")

st.subheader("Widget Options")

options_data = {
    "data-widget-id": f'"{slug}" — Your widget ID (required)',
    "data-position": '"bottom-right" — Position: bottom-right | bottom-left | top-right | top-left',
    "data-greeting": '"Hey!" — Custom greeting override',
}

for attr, desc in options_data.items():
    st.code(f"{attr}={desc}", language="html")

st.markdown("---")

st.subheader("Live Preview")
st.markdown(f"[Open Widget Preview →](http://localhost:3000/widget/{slug})")
