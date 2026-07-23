import streamlit as st
import requests
import json
from streamlit_oauth import OAuth2Component
from datetime import datetime, timezone, timedelta

st.set_page_config(
    page_title="Dev Testing - AI Portfolio Assistant",
    page_icon="🧪",
    layout="wide",
)

if "api_base" not in st.session_state:
    st.session_state.api_base = "http://localhost:3000"

with st.sidebar:
    st.header("API Connection")
    api_base = st.text_input("Base URL", value=st.session_state.api_base, key="api_base_input")
    st.session_state.api_base = api_base

    if st.button("Health Check", use_container_width=True):
        with st.spinner("Checking..."):
            try:
                r = requests.get(f"{api_base}/api/health", timeout=5)
                st.session_state.health = r.json()
            except Exception as e:
                st.session_state.health = {"error": str(e)}

    health = st.session_state.get("health")
    if health:
        if "error" in health:
            st.error(f"Error: {health['error']}")
        else:
            status = health.get("status", "unknown")
            st.success(f"Status: {status}")
            st.caption(f"DB: {health.get('services', {}).get('database', '?')}")
            st.caption(health.get("timestamp", ""))

    st.divider()
    st.caption("Dev Dashboard v1.0")

st.title("🧪 Dev Testing Dashboard")
st.caption("Test all core API endpoints for the AI Portfolio Assistant.")

slug = st.text_input("Widget Slug", value="my-portfolio", key="main_slug")

tab1, tab2, tab3 = st.tabs(["📋 Widget Info", "📅 Calendar", "⚙️ Widget Management"])

# ─── Tab 1: Widget Info ────────────────────────────────────────────
with tab1:
    endpoint_cols = st.columns(5)
    endpoints = [
        ("Config", f"/api/widget/{slug}/config"),
        ("Profile", f"/api/widget/{slug}/profile"),
        ("Projects", f"/api/widget/{slug}/projects"),
        ("Services", f"/api/widget/{slug}/services"),
        ("FAQ", f"/api/widget/{slug}/faq"),
    ]

    for col, (label, path) in zip(endpoint_cols, endpoints):
        with col:
            if st.button(label, use_container_width=True, key=f"btn_{label.lower()}"):
                with st.spinner(f"Fetching {label}..."):
                    try:
                        r = requests.get(f"{api_base}{path}", timeout=5)
                        st.session_state[f"result_{label.lower()}"] = (label, r.status_code, r.json())
                    except Exception as e:
                        st.session_state[f"result_{label.lower()}"] = (label, 0, str(e))

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Clear Results", key="clear_widget"):
            for key in list(st.session_state.keys()):
                if key.startswith("result_"):
                    del st.session_state[key]
            st.rerun()

    for key in ["result_config", "result_profile", "result_projects", "result_services", "result_faq"]:
        result = st.session_state.get(key)
        if result:
            label, status, data = result
            if status == 0:
                st.error(f"**{label}** — Connection failed: {data}")
            elif status != 200:
                st.error(f"**{label}** — HTTP {status}")
                st.json(data)
            else:
                with st.container(border=True):
                    st.success(f"**{label}** — HTTP {status}")
                    st.json(data)

# ─── Tab 2: Calendar ───────────────────────────────────────────────
with tab2:
    # ── Status ──
    with st.container(border=True):
        st.subheader("Connection Status")
        col_status, col_check = st.columns([1, 1])
        with col_check:
            if st.button("Check Status", use_container_width=True, key="btn_cal_status"):
                try:
                    r = requests.get(f"{api_base}/api/widget/{slug}/calendar/status", timeout=5)
                    st.session_state.cal_status = r.json()
                except Exception as e:
                    st.session_state.cal_status = {"error": str(e)}

        cal_status = st.session_state.get("cal_status")
        if cal_status:
            if "error" in cal_status:
                st.error(f"Error: {cal_status['error']}")
            elif cal_status.get("connected"):
                st.success(f"Connected: {cal_status.get('email')}")
            else:
                st.warning("Not connected")

    # ── Connect Options ──
    col_oauth, col_manual = st.columns(2)

    with col_oauth:
        with st.container(border=True):
            st.subheader("OAuth Connect")
            try:
                google_client_id = st.secrets.google_calendar.client_id
                google_client_secret = st.secrets.google_calendar.client_secret
            except Exception:
                st.error("OAuth creds not configured in `.streamlit/secrets.toml`")
                st.stop()

            oauth2 = OAuth2Component(
                client_id=google_client_id,
                client_secret=google_client_secret,
                authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                refresh_token_endpoint="https://oauth2.googleapis.com/token",
                revoke_token_endpoint="https://oauth2.googleapis.com/revoke",
            )

            if "google_calendar_token" not in st.session_state:
                result = oauth2.authorize_button(
                    name="Connect Google Calendar",
                    redirect_uri="http://localhost:8501",
                    scope="https://www.googleapis.com/auth/calendar",
                    key="google_calendar",
                    extras_params={"prompt": "consent", "access_type": "offline"},
                    use_container_width=True,
                )

                if result and "token" in result:
                    token = result["token"]
                    id_token = token.get("id_token", "")
                    payload = id_token.split(".")[1] if "." in id_token else ""
                    payload += "=" * (-len(payload) % 4)
                    try:
                        claims = json.loads(__import__("base64").urlsafe_b64decode(payload))
                        email = claims.get("email", "unknown")
                    except Exception:
                        email = "unknown"

                    expires_in = token.get("expires_in", 3600)
                    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()

                    try:
                        r = requests.post(
                            f"{api_base}/api/widget/{slug}/calendar/connect",
                            json={
                                "access_token": token["access_token"],
                                "refresh_token": token.get("refresh_token", ""),
                                "calendar_email": email,
                                "expires_at": expires_at,
                            },
                            timeout=5,
                        )
                        if r.status_code == 200:
                            st.session_state.google_calendar_token = token
                            st.session_state.cal_status = {"connected": True, "email": email}
                            st.success(f"Connected: {email}")
                            st.rerun()
                        else:
                            st.error(f"Backend error: {r.text}")
                    except Exception as e:
                        st.error(f"Failed to save credentials: {e}")
            else:
                st.success("Google Calendar is connected.")

    with col_manual:
        with st.container(border=True):
            st.subheader("Manual Connect")
            with st.form("manual_calendar_form"):
                cal_email = st.text_input("Calendar Email")
                access_token = st.text_input("Access Token", type="password")
                refresh_token = st.text_input("Refresh Token", type="password")
                expires_at = st.text_input("Expires At (ISO)", value=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())
                submitted = st.form_submit_button("Connect", type="primary", use_container_width=True)
                if submitted:
                    with st.spinner("Connecting..."):
                        try:
                            r = requests.post(
                                f"{api_base}/api/widget/{slug}/calendar/connect",
                                json={
                                    "access_token": access_token,
                                    "refresh_token": refresh_token,
                                    "calendar_email": cal_email,
                                    "expires_at": expires_at,
                                },
                                timeout=5,
                            )
                            if r.status_code == 200:
                                st.session_state.cal_status = {"connected": True, "email": cal_email}
                                st.success(f"Connected: {cal_email}")
                                st.rerun()
                            else:
                                st.error(f"Backend error: {r.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")

# ─── Tab 3: Widget Management ──────────────────────────────────────
with tab3:
    with st.container(border=True):
        st.subheader("Create Widget")
        col_name, col_btn = st.columns([3, 1])
        with col_name:
            create_name = st.text_input("Widget Name", value="My Portfolio", key="create_name")
        with col_btn:
            if st.button("Create", type="primary", use_container_width=True, key="btn_create"):
                with st.spinner("Creating..."):
                    try:
                        r = requests.post(
                            f"{api_base}/api/widget/{slug}/create",
                            json={"name": create_name},
                            timeout=5,
                        )
                        st.session_state.create_result = (r.status_code, r.json())
                    except Exception as e:
                        st.session_state.create_result = (0, str(e))

        create_res = st.session_state.get("create_result")
        if create_res:
            status, data = create_res
            if status in (200, 201):
                st.success(f"HTTP {status} — Created!")
            else:
                st.error(f"HTTP {status}")
            st.json(data)

    # ── Load Widget Data ──
    with st.container(border=True):
        st.subheader("Edit Widget Data")
        col_load, col_save_all, _, col_clear = st.columns([1, 1, 1, 1])
        with col_load:
            if st.button("Load Current Data", use_container_width=True, key="btn_load_widget"):
                with st.spinner("Loading..."):
                    wdata = {}
                    try:
                        r = requests.get(f"{api_base}/api/widget/{slug}/config", timeout=5)
                        if r.status_code == 200:
                            wdata["config"] = r.json()
                    except Exception:
                        pass
                    try:
                        r = requests.get(f"{api_base}/api/widget/{slug}/profile", timeout=5)
                        if r.status_code == 200:
                            wdata["profile"] = r.json()
                    except Exception:
                        pass
                    for k in ["projects", "services", "faq"]:
                        try:
                            r = requests.get(f"{api_base}/api/widget/{slug}/{k}", timeout=5)
                            if r.status_code == 200:
                                wdata[k] = r.json()
                        except Exception:
                            pass
                    st.session_state.widget_data = wdata
                    st.rerun()

        wdata = st.session_state.get("widget_data", {})
        config = wdata.get("config", {})
        profile = wdata.get("profile", {})
        projects = wdata.get("projects", [])
        services = wdata.get("services", [])
        faq = wdata.get("faq", [])

        col_save_status, _ = st.columns(2)
        with col_save_status:
            save_msg = st.session_state.get("save_msg")
            if save_msg:
                status, msg = save_msg
                if status == 200:
                    st.success(msg)
                else:
                    st.error(msg)
                st.session_state.pop("save_msg")

        # ── Profile ──
        with st.expander("Profile", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                p_name = st.text_input("Name", value=profile.get("name", "") or "", key="p_name")
                p_title = st.text_input("Title", value=profile.get("title", "") or "", key="p_title")
                p_bio = st.text_area("Bio", value=profile.get("bio", "") or "", key="p_bio", height=80)
                p_location = st.text_input("Location", value=profile.get("location", "") or "", key="p_location")
            with col_b:
                skills = profile.get("skills", [])
                p_skills = st.text_area("Skills (one per line)", value="\n".join(skills) if skills else "", key="p_skills", height=80)
                exp = profile.get("experience", [])
                p_exp = st.text_area("Experience (one per line)", value="\n".join(exp) if exp else "", key="p_exp", height=80)
            contact = profile.get("contact", {})
            with st.container():
                st.caption("Contact")
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    p_email = st.text_input("Email", value=contact.get("email", "") or "", key="p_email")
                with cc2:
                    p_website = st.text_input("Website", value=contact.get("website", "") or "", key="p_website")
                with cc3:
                    p_linkedin = st.text_input("LinkedIn", value=contact.get("linkedin", "") or "", key="p_linkedin")

        # ── Projects / Services / FAQ ──
        with st.expander("Projects"):
            p_projects = st.text_area("Projects JSON array", value=json.dumps(projects, indent=2) if projects else "[]", key="p_projects", height=150)

        with st.expander("Services"):
            p_services = st.text_area("Services JSON array", value=json.dumps(services, indent=2) if services else "[]", key="p_services", height=150)

        with st.expander("FAQ"):
            p_faq = st.text_area("FAQ JSON array", value=json.dumps(faq, indent=2) if faq else "[]", key="p_faq", height=150)

        # ── Theme ──
        theme = config.get("theme", {})
        with st.expander("Theme"):
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                t_primary = st.color_picker("Primary Color", value=theme.get("primaryColor", "#4F46E5"), key="t_primary")
                t_font = st.selectbox("Font Family", ["Inter", "system-ui", "Poppins", "Roboto", "Open Sans"],
                    index=["Inter", "system-ui", "Poppins", "Roboto", "Open Sans"].index(theme.get("fontFamily", "Inter")) if theme.get("fontFamily") in ["Inter", "system-ui", "Poppins", "Roboto", "Open Sans"] else 0, key="t_font")
            with tc2:
                t_secondary = st.color_picker("Secondary Color", value=theme.get("secondaryColor", "#1E1B4B"), key="t_secondary")
                t_radius = st.slider("Border Radius (px)", 0, 24, int(str(theme.get("borderRadius", "12px")).replace("px", "") or 12), key="t_radius")
            with tc3:
                t_position = st.selectbox("Position", ["bottom-right", "bottom-left", "top-right", "top-left"],
                    index=["bottom-right", "bottom-left", "top-right", "top-left"].index(theme.get("position", "bottom-right")) if theme.get("position") in ["bottom-right", "bottom-left", "top-right", "top-left"] else 0, key="t_position")
            t_title = st.text_input("Chat Title", value=theme.get("chatTitle", "Portfolio Assistant") or "", key="t_title")
            t_subtitle = st.text_input("Chat Subtitle", value=theme.get("chatSubtitle", "Ask me anything") or "", key="t_subtitle")
            t_welcome = st.text_area("Welcome Message", value=theme.get("welcomeMessage", "Hi! Ask me about my work.") or "", key="t_welcome", height=60)

        # ── Personality ──
        personality = config.get("personality", {})
        with st.expander("Personality"):
            per_tone = st.select_slider("Tone", options=["Professional", "Balanced", "Witty", "Casual"],
                value=personality.get("tone", "Witty") if personality.get("tone") in ["Professional", "Balanced", "Witty", "Casual"] else "Witty", key="per_tone")
            per_humor = st.slider("Humor Level", 0, 10, personality.get("humorLevel", 7), key="per_humor")
            per_prompt = st.text_area("Custom System Prompt", value=personality.get("systemPrompt", "") or "", key="per_prompt", height=150)

        # ── Settings ──
        with st.expander("Settings"):
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                s_rate = st.number_input("Rate Limit (msgs/hr)", min_value=1, value=30, key="s_rate")
            with sc2:
                s_daily = st.number_input("Daily Limit (msgs/day)", min_value=1, value=1000, key="s_daily")
            with sc3:
                s_active = st.checkbox("Widget Active", value=True, key="s_active")

        # ── Save Button ──
        with col_save_all:
            if st.button("Save All", type="primary", use_container_width=True, key="btn_save_widget"):
                with st.spinner("Saving..."):
                    profile_data = {
                        "name": p_name,
                        "title": p_title,
                        "bio": p_bio,
                        "location": p_location,
                        "skills": [s.strip() for s in p_skills.split("\n") if s.strip()],
                        "experience": [s.strip() for s in p_exp.split("\n") if s.strip()],
                        "contact": {"email": p_email, "website": p_website, "linkedin": p_linkedin},
                    }
                    theme_data = {
                        "primaryColor": t_primary,
                        "secondaryColor": t_secondary,
                        "fontFamily": t_font,
                        "borderRadius": f"{t_radius}px",
                        "chatTitle": t_title,
                        "chatSubtitle": t_subtitle,
                        "welcomeMessage": t_welcome,
                        "position": t_position,
                    }
                    personality_data = {
                        "tone": per_tone,
                        "humorLevel": per_humor,
                        "systemPrompt": per_prompt,
                    }
                    body = {
                        "name": p_name,
                        "profile": profile_data,
                        "theme": theme_data,
                        "personality": personality_data,
                        "rateLimit": s_rate,
                        "dailyMessageLimit": s_daily,
                        "isActive": s_active,
                    }
                    for key, val in [("projects", p_projects), ("services", p_services), ("faq", p_faq)]:
                        try:
                            body[key] = json.loads(val)
                        except json.JSONDecodeError:
                            st.session_state.save_msg = (400, f"Invalid JSON in {key}")
                            st.rerun()
                            break
                    else:
                        try:
                            r = requests.put(f"{api_base}/api/widget/{slug}", json=body, timeout=5)
                            st.session_state.save_msg = (r.status_code, f"HTTP {r.status_code} — Saved!" if r.status_code == 200 else f"HTTP {r.status_code}: {r.text}")
                        except Exception as e:
                            st.session_state.save_msg = (0, f"Error: {e}")
                        st.rerun()

        with col_clear:
            if st.button("Clear", use_container_width=True, key="clear_mgmt"):
                for key in ["create_result", "widget_data", "save_msg"]:
                    st.session_state.pop(key, None)
                st.rerun()
