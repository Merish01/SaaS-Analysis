# 📊 SaaS Analytics Dashboard

A full-featured SaaS analytics dashboard built with **Streamlit** and **Google OAuth**.

## Features

| Section | Metrics |
|---|---|
| 📊 Overview | MRR, ARR, Users, ARPU — quick snapshot charts |
| 💰 Revenue | MRR/ARR trends, plan breakdown, ARPU over time |
| 👥 Users | Growth, daily signups, plan distribution |
| 📉 Churn | Churn rate, LTV, cohort retention table |
| 🔥 Engagement | DAU/WAU/MAU, session duration, feature heatmap |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → **APIs & Services → Credentials**
3. Click **+ CREATE CREDENTIALS → OAuth client ID**
4. Application type: **Web application**
5. Authorised redirect URIs: `http://localhost:8501`
6. Copy **Client ID** and **Client Secret**

### 3. Add credentials to Streamlit secrets

Edit `.streamlit/secrets.toml`:

```toml
[google]
client_id     = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri  = "http://localhost:8501"
```

### 4. Run the app
```bash
streamlit run app.py
```

Visit `http://localhost:8501` → click **Sign in with Google** → you're in!

---

## Deploying to Streamlit Cloud

1. Push all files to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. In **App Settings → Secrets**, paste:
```toml
[google]
client_id     = "..."
client_secret = "..."
redirect_uri  = "https://your-app.streamlit.app"
```
4. Also add `https://your-app.streamlit.app` as an Authorised redirect URI in Google Console

---

## Project Structure

```
├── app.py              # Main dashboard (all 5 pages)
├── auth.py             # Google OAuth2 logic
├── style.css           # Dark theme styles
├── requirements.txt
└── .streamlit/
    └── secrets.toml    # Google credentials (never commit!)
```

> **Note:** The dashboard uses mock/generated data. To connect real data,
> replace the `generate_data()` function in `app.py` with your own database
> queries or API calls.
