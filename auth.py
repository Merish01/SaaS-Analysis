# auth.py

"""
Google OAuth2 authentication for Streamlit.
"""

import os
import urllib.parse
import requests
import streamlit as st

# ── Read credentials from Streamlit secrets (or env vars as fallback) ─────────
def _get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets["google"][key]
    except Exception:
        return os.getenv(key, default)

CLIENT_ID     = _get_secret("client_id",     "YOUR_GOOGLE_CLIENT_ID")
CLIENT_SECRET = _get_secret("client_secret", "YOUR_GOOGLE_CLIENT_SECRET")
REDIRECT_URI  = _get_secret("redirect_uri",  "http://localhost:8501")

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO  = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPE = "openid email profile"

# ── Public helpers ─────────────────────────────────────────────────────────────

def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def get_user_info() -> dict:
    return st.session_state.get("user_info", {})


def logout():
    # Clear session state completely
    for key in ["authenticated", "user_info", "oauth_state"]:
        if key in st.session_state:
            del st.session_state[key]


# ── OAuth helpers ──────────────────────────────────────────────────────────────

def _build_auth_url() -> str:
    import secrets
    # Use a persistent or safely set state token
    if "oauth_state" not in st.session_state:
        st.session_state["oauth_state"] = secrets.token_urlsafe(16)
    
    state = st.session_state["oauth_state"]
    params = {
        "client_id":     CLIENT_ID,
        "redirect_uri":  REDIRECT_URI,
        "response_type": "code",
        "scope":         SCOPE,
        "state":         state,
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


def _exchange_code(code: str) -> dict:
    payload = {
        "code":          code,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri":  REDIRECT_URI,
        "grant_type":    "authorization_code",
    }
    resp = requests.post(GOOGLE_TOKEN_URL, data=payload, timeout=10)
    
    if resp.status_code != 200:
        raise Exception(f"Token error {resp.status_code}: {resp.text}")
    
    return resp.json()


def _fetch_user(access_token: str) -> dict:
    resp = requests.get(GOOGLE_USERINFO,
                        headers={"Authorization": f"Bearer {access_token}"},
                        timeout=10)
    resp.raise_for_status()
    return resp.json()


# ── Login page ─────────────────────────────────────────────────────────────────

def login_page():
    """Render the login page and handle the OAuth callback."""

    # ── Handle OAuth callback ──────────────────────────────────────────────────
    query = st.query_params
    code  = query.get("code")
    state = query.get("state")

    if code:
        # Check if we have an expected state to compare against
        saved_state = st.session_state.get("oauth_state")
        
        # Guard clause for missing or invalid state matching
        if saved_state and state != saved_state:
            st.error("Invalid OAuth state verification failed. Please try again.")
            st.query_params.clear()
            return

        with st.spinner("Signing you in …"):
            try:
                tokens    = _exchange_code(code)
                user_info = _fetch_user(tokens["access_token"])
                
                # Assign authorization parameters securely
                st.session_state["user_info"]     = user_info
                st.session_state["authenticated"] = True
                
                # Wipe query strings explicitly before rerunning to cleanly swap context
                st.query_params.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
                st.query_params.clear()
        return

    # ── Render login UI ────────────────────────────────────────────────────────
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    st.markdown("""
    <div class="login-container">
        <div class="login-logo">📊</div>
        <h1 class="login-title">SaaS Analytics</h1>
        <p class="login-subtitle">Your complete business intelligence dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        auth_url = _build_auth_url()
        st.markdown(f"""
        <a href="{auth_url}" class="google-btn" target="_self">
            <svg width="20" height="20" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0
                                     11.27 0 .88 8.88.05 20.53L8.73 27c2.09-6.25 7.93-10.8 14.76-11.05H24z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94
                                     c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-8.68-6.47
                                     C.49 16.35 0 20.1 0 24c0 3.9.49 7.65 1.85 11.06l8.68-6.47z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3
                                     -6.83 0-12.67-4.55-14.76-10.8l-8.68 6.47C5.99 44.08 14.47 48 24 48z"/>
            </svg>
            &nbsp; Sign in with Google
        </a>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;color:#64748b;font-size:0.78rem;margin-top:1.5rem;">
            Secure login via Google OAuth 2.0
        </p>
        """, unsafe_allow_html=True)