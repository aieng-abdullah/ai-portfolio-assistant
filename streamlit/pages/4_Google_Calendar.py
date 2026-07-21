import streamlit as st
import requests
import json
from streamlit_oauth import OAuth2Component
from datetime import datetime, timezone

API_BASE = "http://localhost:3000"

st.set_page_config(page_title="Google Calendar", page_icon="📅", layout="wide")
st.title("Google Calendar Integration")

slug = st.text_input("Widget Slug", value="my-portfolio")

# --- Check current status ---
st.subheader("Connection Status")
if st.button("Check Status"):
    try:
        r = requests.get(f"{API_BASE}/api/widget/{slug}/calendar/status", timeout=5)
        st.session_state.cal_status = r.json()
    except Exception as e:
        st.error(f"Error: {e}")

status = st.session_state.get("cal_status", {})
if status.get("connected"):
    st.success(f"Connected: {status.get('email')}")
    if st.button("Disconnect Calendar"):
        try:
            r = requests.post(f"{API_BASE}/api/widget/{slug}/calendar/disconnect", timeout=5)
            st.session_state.cal_status = {"connected": False}
            st.success("Disconnected")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.warning("Not connected")

st.markdown("---")

# --- OAuth Flow ---
st.subheader("Connect Google Calendar")

try:
    client_id = st.secrets.google_calendar.client_id
    client_secret = st.secrets.google_calendar.client_secret
except (AttributeError, FileNotFoundError):
    st.error("Google OAuth credentials not configured. Add them to `.streamlit/secrets.toml`.")
    st.stop()

oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
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

        # Decode id_token to get email
        import base64
        id_token = token.get("id_token", "")
        payload = id_token.split(".")[1] if "." in id_token else ""
        payload += "=" * (-len(payload) % 4)
        try:
            claims = json.loads(base64.urlsafe_b64decode(payload))
            email = claims.get("email", "unknown")
        except Exception:
            email = "unknown"

        # Calculate expiry
        expires_at = datetime.now(timezone.utc).isoformat()

        # Save to backend
        try:
            r = requests.post(
                f"{API_BASE}/api/widget/{slug}/calendar/connect",
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
                st.success(f"Connected! Calendar: {email}")
                st.rerun()
            else:
                st.error(f"Backend error: {r.text}")
        except Exception as e:
            st.error(f"Failed to save credentials: {e}")
else:
    st.success("Google Calendar is connected!")
    token = st.session_state.google_calendar_token

    if st.button("Refresh Token"):
        try:
            token = oauth2.refresh_token(token)
            st.session_state.google_calendar_token = token
            st.success("Token refreshed")
        except Exception as e:
            st.error(f"Refresh failed: {e}")

    if st.button("Disconnect"):
        del st.session_state.google_calendar_token
        try:
            requests.post(f"{API_BASE}/api/widget/{slug}/calendar/disconnect", timeout=5)
        except Exception:
            pass
        st.rerun()
