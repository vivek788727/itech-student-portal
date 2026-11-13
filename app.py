"""
I-Tech Computer Education — Student Portal (Professional Glass UI)
==================================================================
A complete Streamlit web app for managing students, agents, fees,
attendance, and enquiries at I-Tech Computer Education.

Design: iPhone-style glassmorphism theme
Responsive: Different layouts for web and mobile

Author: Generated for I-Tech Computer Education
Tech: Python + Streamlit + pandas (no external database)
Storage: JSON (students, agents) + CSV (enquiries)
"""

import streamlit as st
import pandas as pd
import hashlib
import json
import os
import csv
from datetime import datetime, date

# ──────────────────────────────────────────────
# CONSTANTS — Institute details, courses, fees
# ──────────────────────────────────────────────

INSTITUTE_NAME = "I-Tech Computer Education"
INSTITUTE_SHORT = "I-Tech"
TIMING = "1 hour daily (all courses)"

# Course → Fee (INR) mapping
COURSES = {
    "BCC": 4000,
    "CCC": 6000,
    "DOM": 8000,
    "DCA": 12000,
    "ADCA": 16000,
    "Graphic Design": 8000,
    "Video Editing": 8000,
}
COURSE_NAMES = list(COURSES.keys())

# File paths for data storage
STUDENTS_FILE = "students.json"
AGENTS_FILE = "agents.json"
ENQUIRIES_FILE = "enquiries.csv"

# Main admin agent ID (can add/remove other agents)
ADMIN_AGENT_ID = "AGENT01"

# ──────────────────────────────────────────────
# GLASS THEME CSS — iPhone-style glassmorphism
# ──────────────────────────────────────────────

GLASS_CSS = """
<style>
/* ── ROOT VARIABLES ── */
:root {
    --glass-bg: rgba(255, 255, 255, 0.65);
    --glass-border: rgba(255, 255, 255, 0.8);
    --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    --primary: #007AFF;
    --primary-dark: #0051D5;
    --secondary: #5856D6;
    --success: #34C759;
    --warning: #FF9500;
    --danger: #FF3B30;
    --text-dark: #1C1C1E;
    --text-light: #8E8E93;
    --bg-gradient-start: #E8ECF4;
    --bg-gradient-end: #F5F7FA;
    --radius: 20px;
    --radius-sm: 12px;
}

/* ── GLOBAL ── */
.stApp {
    background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', Helvetica, Arial, sans-serif;
}

/* ── GLASS CARD CLASS ── */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    box-shadow: var(--glass-shadow);
    padding: 28px;
    margin: 10px 0;
    transition: all 0.3s ease;
}
.glass-card:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
}

/* ── LOGIN GLASS CARD ── */
.login-card {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(30px) saturate(180%);
    -webkit-backdrop-filter: blur(30px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
    padding: 40px;
    max-width: 480px;
    margin: 0 auto;
}

/* ── STAT CARD ── */
.stat-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: var(--radius-sm);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
}
.stat-card:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
    transform: translateY(-3px);
}
.stat-icon {
    font-size: 36px;
    margin-bottom: 8px;
}
.stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-dark);
    margin: 4px 0;
}
.stat-label {
    font-size: 13px;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── HEADER BANNER ── */
.institute-header {
    background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
    border-radius: var(--radius);
    padding: 30px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 40px rgba(0, 122, 255, 0.3);
    margin-bottom: 20px;
}
.institute-header h1 {
    font-size: 28px;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}
.institute-header p {
    font-size: 14px;
    opacity: 0.85;
    margin-top: 5px;
}

/* ── SECTION TITLE ── */
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-dark);
    margin: 20px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    padding: 12px 24px;
    font-weight: 600;
    font-size: 15px;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(0, 122, 255, 0.25);
}
.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(0, 122, 255, 0.35);
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
}

/* ── LOGOUT BUTTON ── */
.logout-btn > button {
    background: linear-gradient(135deg, #FF3B30 0%, #D70015 100%);
    box-shadow: 0 4px 15px rgba(255, 59, 48, 0.25);
}

/* ── INPUT FIELDS ── */
.stTextInput > div > input,
.stNumberInput > div > input,
.stSelectbox > div > div > div {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid rgba(0, 0, 0, 0.08) !important;
    background: rgba(255, 255, 255, 0.8) !important;
    padding: 10px 14px !important;
    font-size: 15px !important;
    transition: all 0.2s ease;
}
.stTextInput > div > input:focus,
.stNumberInput > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.12) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(20px);
    border-radius: var(--radius-sm);
    padding: 6px;
    border: 1px solid rgba(255, 255, 255, 0.6);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
    color: var(--text-light);
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--primary) !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

/* ── DATAFRAME TABLES ── */
.stDataFrame {
    border-radius: var(--radius-sm);
    overflow: hidden;
}
.stDataFrame [data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(255, 255, 255, 0.6);
}

/* ── METRICS ── */
.stMetric {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(15px);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(255, 255, 255, 0.5);
    padding: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

/* ── ALERTS ── */
.stAlert {
    border-radius: var(--radius-sm) !important;
    backdrop-filter: blur(15px);
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: rgba(245, 247, 250, 0.85);
    backdrop-filter: blur(30px) saturate(180%);
    -webkit-backdrop-filter: blur(30px) saturate(180%);
    border-right: 1px solid rgba(255, 255, 255, 0.6);
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--primary);
    font-weight: 800;
}

/* ── SIDEBAR USER CARD ── */
.sidebar-user-card {
    background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
    border-radius: var(--radius-sm);
    padding: 16px;
    color: white;
    text-align: center;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(0, 122, 255, 0.2);
}
.sidebar-user-card .user-avatar {
    font-size: 40px;
    margin-bottom: 4px;
}
.sidebar-user-card .user-name {
    font-size: 17px;
    font-weight: 700;
}
.sidebar-user-card .user-id {
    font-size: 13px;
    opacity: 0.85;
}

/* ── SIDEBAR RADIO ── */
section[data-testid="stSidebar"] [role="radiogroup"] label {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    transition: all 0.2s ease;
    cursor: pointer;
    font-weight: 500;
    font-size: 14px;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(0, 122, 255, 0.08);
    border-color: rgba(0, 122, 255, 0.2);
}
section[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
    color: white;
    border-color: transparent;
}

/* ── FORM ── */
.stForm {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* ── EXPANDER ── */
.stExpander {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: var(--radius-sm);
}

/* ── DIVIDER ── */
hr {
    border: none;
    height: 1px;
    background: rgba(0, 0, 0, 0.06);
    margin: 16px 0;
}

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
    .glass-card {
        padding: 18px;
        border-radius: 16px;
    }
    .login-card {
        padding: 24px;
        border-radius: 18px;
    }
    .institute-header {
        padding: 20px;
        border-radius: 16px;
    }
    .institute-header h1 {
        font-size: 22px;
    }
    .stat-card {
        padding: 14px;
    }
    .stat-icon {
        font-size: 28px;
    }
    .stat-value {
        font-size: 22px;
    }
    .section-title {
        font-size: 18px;
    }
    .stButton > button {
        padding: 14px 20px;
        font-size: 16px;
        width: 100%;
    }
    /* Stack columns vertically on mobile */
    .stColumns {
        flex-direction: column;
    }
    /* Bigger touch targets */
    .stTextInput > div > input,
    .stNumberInput > div > input {
        padding: 14px 16px !important;
        font-size: 16px !important;
    }
    /* Tabs scrollable on mobile */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 16px;
        font-size: 13px;
        white-space: nowrap;
    }
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(0, 122, 255, 0.3);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 122, 255, 0.5);
}

/* ── HIDE STREAMLIT DEFAULT ELEMENTS ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* ── PROGRESS BAR ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #007AFF 0%, #5856D6 100%);
    border-radius: 10px;
}

/* ── BADGE ── */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.badge-success {
    background: rgba(52, 199, 89, 0.15);
    color: #248A3D;
}
.badge-warning {
    background: rgba(255, 149, 0, 0.15);
    color: #C93400;
}
.badge-danger {
    background: rgba(255, 59, 48, 0.15);
    color: #C5001A;
}
.badge-info {
    background: rgba(0, 122, 255, 0.15);
    color: #0040AF;
}
</style>
"""


def inject_glass_css():
    """Inject the glassmorphism CSS into the Streamlit app."""
    st.markdown(GLASS_CSS, unsafe_allow_html=True)


def glass_card(content: str):
    """Wrap content in a glass card div."""
    st.markdown(f'<div class="glass-card">{content}</div>', unsafe_allow_html=True)


def stat_card(icon: str, value: str, label: str):
    """Render a stat card with icon, value, and label."""
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">{icon}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_user_card(role_icon: str, name: str, user_id: str, role_label: str):
    """Render the user info card in the sidebar."""
    st.markdown(f"""
    <div class="sidebar-user-card">
        <div class="user-avatar">{role_icon}</div>
        <div class="user-name">{name}</div>
        <div class="user-id">{user_id} · {role_label}</div>
    </div>
    """, unsafe_allow_html=True)


def institute_header():
    """Render the institute header banner."""
    st.markdown(f"""
    <div class="institute-header">
        <h1>📚 {INSTITUTE_NAME}</h1>
        <p>Computer Education Portal · {TIMING}</p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HELPER FUNCTIONS — hashing, file I/O
# ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Return SHA-256 hex digest of a password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Check if a plain-text password matches a SHA-256 hash."""
    return hash_password(password) == hashed


def load_json(filepath: str) -> list:
    """Load a JSON file and return a list; return [] if file doesn't exist."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []


def save_json(filepath: str, data) -> None:
    """Save a list/dict to a JSON file with pretty formatting."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_enquiries() -> list:
    """Load enquiries from CSV; return list of dicts."""
    if not os.path.exists(ENQUIRIES_FILE):
        return []
    try:
        df = pd.read_csv(ENQUIRIES_FILE)
        return df.to_dict("records")
    except Exception:
        return []


def save_enquiry(name: str, mobile: str, course: str) -> None:
    """Append a new enquiry to the CSV file with a timestamp."""
    file_exists = os.path.exists(ENQUIRIES_FILE)
    with open(ENQUIRIES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "mobile", "course", "timestamp"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "name": name,
            "mobile": mobile,
            "course": course,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })


# ──────────────────────────────────────────────
# INITIALIZATION — create default files on first run
# ──────────────────────────────────────────────

def init_data_files():
    """Create default students.json and agents.json with demo accounts if they don't exist."""

    # Create students.json with demo students if it doesn't exist
    if not os.path.exists(STUDENTS_FILE):
        demo_students = [
            {
                "student_id": "ITECH001",
                "name": "Demo Student",
                "mobile": "9876543210",
                "course": "CCC",
                "fee_total": 6000,
                "fee_paid": 3000,
                "fee_pending": 3000,
                "password_hash": hash_password("1234"),
                "attendance": [],
                "payments": [
                    {"receipt_no": "R001", "date": "2026-01-05", "amount": 3000, "mode": "Cash"}
                ],
            },
            {
                "student_id": "ITECH002",
                "name": "Ravi Kumar",
                "mobile": "9123456780",
                "course": "DCA",
                "fee_total": 12000,
                "fee_paid": 5000,
                "fee_pending": 7000,
                "password_hash": hash_password("5678"),
                "attendance": [
                    {"date": "2026-01-10", "status": "Present"},
                    {"date": "2026-01-11", "status": "Present"},
                    {"date": "2026-01-12", "status": "Absent"},
                ],
                "payments": [
                    {"receipt_no": "R002", "date": "2026-01-10", "amount": 5000, "mode": "UPI"}
                ],
            },
        ]
        save_json(STUDENTS_FILE, demo_students)

    # Create agents.json with demo agents if it doesn't exist
    if not os.path.exists(AGENTS_FILE):
        demo_agents = [
            {
                "agent_id": "AGENT01",
                "name": "Main Admin",
                "password_hash": hash_password("admin123"),
                "is_admin": True,
            },
            {
                "agent_id": "AGENT02",
                "name": "Staff Member",
                "password_hash": hash_password("staff123"),
                "is_admin": False,
            },
        ]
        save_json(AGENTS_FILE, demo_agents)


# ──────────────────────────────────────────────
# SESSION STATE — login & role management
# ──────────────────────────────────────────────

def init_session_state():
    """Initialize session state keys for login and role tracking."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "role" not in st.session_state:
        st.session_state.role = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False


def do_logout():
    """Clear session state and log the user out."""
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.is_admin = False
    st.rerun()


# ──────────────────────────────────────────────
# LOGIN PAGE — 3 tabs (Student, Agent, Guest)
# ──────────────────────────────────────────────

def show_login_page():
    """Display the login page with three tabs: Student, Agent, Guest."""
    inject_glass_css()

    # Institute header banner
    institute_header()

    st.markdown("""
    <div style="text-align:center; margin-bottom: 20px;">
        <p style="color: #8E8E93; font-size: 15px;">Welcome! Please login to continue.</p>
    </div>
    """, unsafe_allow_html=True)

    # Login card wrapper
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    tab_student, tab_agent, tab_guest = st.tabs(["🎓 Student", "🧑‍💼 Agent", "👁️ Guest"])

    # ── Tab 1: Student Login ──
    with tab_student:
        st.markdown("### 🎓 Student Login")
        st.markdown("<p style='color:#8E8E93; font-size:13px; margin-bottom:15px;'>Apna Student ID aur password daalein</p>", unsafe_allow_html=True)
        with st.form("student_login_form"):
            sid = st.text_input("Student ID", placeholder="e.g. ITECH001")
            spass = st.text_input("Password", type="password", placeholder="••••")
            submitted = st.form_submit_button("🔑 Login", use_container_width=True)

        if submitted:
            if not sid or not spass:
                st.error("⚠️ Student ID ya Password galat hai. Dono fields bharo.")
            else:
                students = load_json(STUDENTS_FILE)
                student = next((s for s in students if s["student_id"] == sid), None)
                if student and verify_password(spass, student["password_hash"]):
                    st.session_state.logged_in = True
                    st.session_state.role = "student"
                    st.session_state.user_id = student["student_id"]
                    st.session_state.user_name = student["name"]
                    st.success(f"✅ Welcome, {student['name']}! Login successful.")
                    st.rerun()
                else:
                    st.error("❌ Student ID ya Password galat hai.")

        st.markdown("<p style='color:#8E8E93; font-size:12px; text-align:center; margin-top:10px;'>Demo: <b>ITECH001</b> / <b>1234</b></p>", unsafe_allow_html=True)

    # ── Tab 2: Agent Login ──
    with tab_agent:
        st.markdown("### 🧑‍💼 Agent Login")
        st.markdown("<p style='color:#8E8E93; font-size:13px; margin-bottom:15px;'>Staff/Admin login ke liye</p>", unsafe_allow_html=True)
        with st.form("agent_login_form"):
            aid = st.text_input("Agent ID", placeholder="e.g. AGENT01")
            apass = st.text_input("Password", type="password", placeholder="••••", key="agent_pass")
            submitted = st.form_submit_button("🔑 Login", use_container_width=True)

        if submitted:
            if not aid or not apass:
                st.error("⚠️ Agent ID ya Password galat hai. Dono fields bharo.")
            else:
                agents = load_json(AGENTS_FILE)
                agent = next((a for a in agents if a["agent_id"] == aid), None)
                if agent and verify_password(apass, agent["password_hash"]):
                    st.session_state.logged_in = True
                    st.session_state.role = "agent"
                    st.session_state.user_id = agent["agent_id"]
                    st.session_state.user_name = agent["name"]
                    st.session_state.is_admin = agent.get("is_admin", False)
                    st.success(f"✅ Welcome, {agent['name']}! Login successful.")
                    st.rerun()
                else:
                    st.error("❌ Agent ID ya Password galat hai.")

        st.markdown("<p style='color:#8E8E93; font-size:12px; text-align:center; margin-top:10px;'>Demo: <b>AGENT01</b> / <b>admin123</b></p>", unsafe_allow_html=True)

    # ── Tab 3: Guest ──
    with tab_guest:
        st.markdown("### 👁️ Guest Access")
        st.markdown("<p style='color:#8E8E93; font-size:13px; margin-bottom:15px;'>Bina login ke courses dekhein aur enquiry karein</p>", unsafe_allow_html=True)
        if st.button("👁️ Continue as Guest", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.role = "guest"
            st.session_state.user_id = None
            st.session_state.user_name = "Guest"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # Close login-card


# ──────────────────────────────────────────────
# SHARED PAGES — Home, Courses & Fees, Timing
# ──────────────────────────────────────────────

def show_home():
    """Home page — welcome message varies by role."""
    role = st.session_state.role
    name = st.session_state.user_name

    if role == "student":
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="margin:0; color:#1C1C1E;">🏠 Welcome, {name}! 👋</h2>
            <p style="color:#8E8E93; margin-top:8px;">Welcome to <b>{INSTITUTE_NAME}</b>. Aap apne course details, fees, attendance yahan dekh sakte hain.</p>
        </div>
        """, unsafe_allow_html=True)

        # Quick stats for student
        student = get_current_student()
        if student:
            col1, col2, col3 = st.columns(3)
            with col1:
                stat_card("📚", student["course"], "Your Course")
            with col2:
                fee_pct = int((student["fee_paid"] / student["fee_total"] * 100)) if student["fee_total"] > 0 else 0
                stat_card("💰", f"{fee_pct}%", "Fee Paid")
            with col3:
                attendance = student.get("attendance", [])
                present = sum(1 for a in attendance if a["status"] == "Present")
                stat_card("✅", f"{present}", "Days Present")

    elif role == "agent":
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="margin:0; color:#1C1C1E;">🏠 Welcome, {name}! 👋</h2>
            <p style="color:#8E8E93; margin-top:8px;">Welcome to <b>{INSTITUTE_NAME}</b> Agent Panel. Yahan aap students manage kar sakte hain.</p>
        </div>
        """, unsafe_allow_html=True)

        # Quick stats for agent
        students = load_json(STUDENTS_FILE)
        enquiries = load_enquiries()
        total_collected = sum(s.get("fee_paid", 0) for s in students)
        total_pending = sum(s.get("fee_pending", 0) for s in students)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            stat_card("👥", str(len(students)), "Total Students")
        with col2:
            stat_card("📨", str(len(enquiries)), "Enquiries")
        with col3:
            stat_card("💰", f"₹{total_collected:,}", "Collected")
        with col4:
            stat_card("⏳", f"₹{total_pending:,}", "Pending")

    else:
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="margin:0; color:#1C1C1E;">📚 Welcome to {INSTITUTE_NAME}!</h2>
            <p style="color:#8E8E93; margin-top:8px;">Hum various computer courses offer karte hain. Niche courses aur fees dekhein.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <p style="margin:0; font-size:16px;">⏰ <b>Timing:</b> {TIMING}</p>
    </div>
    """, unsafe_allow_html=True)


def show_courses_and_fees():
    """Display course-fee table and a fee calculator."""
    st.markdown('<div class="section-title">📚 Courses & Fees</div>', unsafe_allow_html=True)

    # Build a DataFrame for the table
    df = pd.DataFrame(
        [{"Course": c, "Fee (INR)": f"₹{f:,}"} for c, f in COURSES.items()]
    )

    # Wrap in glass card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown(f'<p style="text-align:center; color:#8E8E93; margin-top:10px;">⏰ <b>Timing:</b> {TIMING}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Fee calculator
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧮 Fee Calculator</div>', unsafe_allow_html=True)
    selected = st.multiselect("Courses select karein:", COURSE_NAMES)
    if selected:
        total = sum(COURSES[c] for c in selected)
        # Show breakdown
        for c in selected:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(0,0,0,0.05);">
                <span style="font-weight:500;">{c}</span>
                <span style="color:#007AFF; font-weight:600;">₹{COURSES[c]:,}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; padding:12px 0; margin-top:8px; border-top:2px solid rgba(0,122,255,0.2);">
            <span style="font-weight:700; font-size:18px;">Total</span>
            <span style="color:#007AFF; font-weight:800; font-size:18px;">₹{total:,}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#8E8E93; text-align:center; padding:20px 0;'>👆 Upar se courses select karke total fee dekhein</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def show_timing():
    """Display the institute timing."""
    st.markdown('<div class="section-title">⏰ Timing</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="text-align:center; padding:40px;">
        <div style="font-size:60px; margin-bottom:15px;">⏰</div>
        <h2 style="color:#1C1C1E; margin:0;">{TIMING}</h2>
        <p style="color:#8E8E93; margin-top:10px;">Sabhi courses ke liye same timing hai.<br>Classes daily 1 hour hoti hain.</p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# GUEST ENQUIRY FORM
# ──────────────────────────────────────────────

def show_guest_enquiry():
    """Guest enquiry form — validates name, 10-digit mobile, course dropdown."""
    st.markdown('<div class="section-title">📝 Enquiry Form</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <p style="color:#8E8E93; margin:0 0 20px 0;">Kuch puchna hai? Apna enquiry yahan bharo, hum aapse contact karenge.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("enquiry_form"):
        name = st.text_input("Naam *", placeholder="Apna naam likhein")
        mobile = st.text_input("Mobile Number (10 digit) *", placeholder="9876543210")
        course = st.selectbox("Interested Course", ["-- Select --"] + COURSE_NAMES)
        submitted = st.form_submit_button("📝 Submit Enquiry", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("⚠️ Naam khali nahi ho sakta.")
            return
        if not mobile.strip():
            st.error("⚠️ Mobile number khali nahi ho sakta.")
            return
        if not mobile.strip().isdigit() or len(mobile.strip()) != 10:
            st.error("⚠️ Mobile number 10 digit ka hona chahiye (sirf numbers).")
            return
        if course == "-- Select --":
            st.error("⚠️ Kripya ek course select karein.")
            return

        save_enquiry(name.strip(), mobile.strip(), course)
        st.success("✅ Aapki enquiry successfully submit ho gayi! Hum jald aapse contact karenge.")
        st.balloons()


# ──────────────────────────────────────────────
# STUDENT PANEL PAGES
# ──────────────────────────────────────────────

def get_current_student() -> dict | None:
    """Return the logged-in student's record from students.json."""
    students = load_json(STUDENTS_FILE)
    return next((s for s in students if s["student_id"] == st.session_state.user_id), None)


def show_student_profile():
    """Student profile — name, ID, course, total fee, paid, pending."""
    st.markdown('<div class="section-title">👤 My Profile</div>', unsafe_allow_html=True)
    student = get_current_student()
    if not student:
        st.error("Student data nahi mila.")
        return

    # Profile header card
    fee_pct = int((student["fee_paid"] / student["fee_total"] * 100)) if student["fee_total"] > 0 else 0
    st.markdown(f"""
    <div class="glass-card" style="text-align:center; padding:30px;">
        <div style="font-size:50px; margin-bottom:10px;">🎓</div>
        <h2 style="margin:0; color:#1C1C1E;">{student['name']}</h2>
        <p style="color:#8E8E93; margin-top:4px;">Student ID: {student['student_id']}</p>
        <span class="badge badge-info" style="margin-top:8px;">📚 {student['course']}</span>
    </div>
    """, unsafe_allow_html=True)

    # Stats grid
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card("💰", f"₹{student['fee_total']:,}", "Total Fee")
    with col2:
        stat_card("✅", f"₹{student['fee_paid']:,}", "Fee Paid")
    with col3:
        stat_card("⏳", f"₹{student['fee_pending']:,}", "Fee Pending")

    # Fee progress bar
    st.markdown(f"""
    <div class="glass-card">
        <p style="margin:0 0 8px 0; font-weight:600; color:#1C1C1E;">Fee Payment Progress</p>
        <div style="background:rgba(0,0,0,0.06); border-radius:10px; height:24px; overflow:hidden;">
            <div style="background:linear-gradient(90deg, #007AFF 0%, #5856D6 100%); height:100%; border-radius:10px; width:{fee_pct}%; transition:width 0.5s ease;"></div>
        </div>
        <p style="text-align:right; margin-top:6px; color:#8E8E93; font-size:13px;">{fee_pct}% paid</p>
    </div>
    """, unsafe_allow_html=True)

    if student["fee_pending"] > 0:
        st.warning(f"⚠️ Aapka pending fee: ₹{student['fee_pending']:,}. Kripya jaldi pay karein.")
    else:
        st.success("✅ Aapka poori fee pay ho gaya hai!")


def show_student_attendance():
    """Student attendance — present/absent count and percentage."""
    st.markdown('<div class="section-title">📅 My Attendance</div>', unsafe_allow_html=True)
    student = get_current_student()
    if not student:
        st.error("Student data nahi mila.")
        return

    attendance = student.get("attendance", [])
    if not attendance:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:40px;">
            <div style="font-size:50px; margin-bottom:15px;">📅</div>
            <p style="color:#8E8E93; font-size:16px;">Abhi tak koi attendance record nahi hai.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    present = sum(1 for a in attendance if a["status"] == "Present")
    absent = sum(1 for a in attendance if a["status"] == "Absent")
    total = len(attendance)
    pct = (present / total * 100) if total > 0 else 0

    # Attendance stats
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card("✅", str(present), "Present")
    with col2:
        stat_card("❌", str(absent), "Absent")
    with col3:
        pct_color = "#34C759" if pct >= 75 else "#FF9500" if pct >= 50 else "#FF3B30"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-value" style="color:{pct_color};">{pct:.1f}%</div>
            <div class="stat-label">Attendance</div>
        </div>
        """, unsafe_allow_html=True)

    # Attendance progress bar
    st.markdown(f"""
    <div class="glass-card">
        <p style="margin:0 0 8px 0; font-weight:600; color:#1C1C1E;">Attendance Progress</p>
        <div style="background:rgba(0,0,0,0.06); border-radius:10px; height:24px; overflow:hidden;">
            <div style="background:linear-gradient(90deg, #34C759 0%, #30D158 100%); height:100%; border-radius:10px; width:{pct:.1f}%; transition:width 0.5s ease;"></div>
        </div>
        <p style="text-align:right; margin-top:6px; color:#8E8E93; font-size:13px;">{pct:.1f}% present</p>
    </div>
    """, unsafe_allow_html=True)

    # Attendance records table
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight:600; margin-bottom:12px;'>📋 Attendance Records</p>", unsafe_allow_html=True)
    df = pd.DataFrame(attendance)
    # Add status badge column
    df["status_badge"] = df["status"].apply(
        lambda s: "🟢 Present" if s == "Present" else "🔴 Absent"
    )
    df = df[["date", "status_badge"]]
    df.columns = ["Date", "Status"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


def show_student_fee_history():
    """Student fee payment history — table of all payments."""
    st.markdown('<div class="section-title">💰 Fee Payment History</div>', unsafe_allow_html=True)
    student = get_current_student()
    if not student:
        st.error("Student data nahi mila.")
        return

    payments = student.get("payments", [])

    # Fee summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card("💰", f"₹{student['fee_total']:,}", "Total Fee")
    with col2:
        stat_card("✅", f"₹{student['fee_paid']:,}", "Fee Paid")
    with col3:
        stat_card("⏳", f"₹{student['fee_pending']:,}", "Pending")

    if not payments:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:40px;">
            <div style="font-size:50px; margin-bottom:15px;">💰</div>
            <p style="color:#8E8E93; font-size:16px;">Abhi tak koi payment record nahi hai.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Payment table
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight:600; margin-bottom:12px;'>🧾 Payment Receipts</p>", unsafe_allow_html=True)
    df = pd.DataFrame(payments)
    df.columns = ["Receipt No", "Date", "Amount (INR)", "Payment Mode"]
    df["Amount (INR)"] = df["Amount (INR)"].apply(lambda x: f"₹{x:,}")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# AGENT PANEL PAGES
# ──────────────────────────────────────────────

def show_agent_dashboard():
    """Agent dashboard — total students, enquiries, fees collected, pending."""
    st.markdown('<div class="section-title">📊 Dashboard</div>', unsafe_allow_html=True)
    students = load_json(STUDENTS_FILE)
    enquiries = load_enquiries()

    total_students = len(students)
    total_enquiries = len(enquiries)
    total_collected = sum(s.get("fee_paid", 0) for s in students)
    total_pending = sum(s.get("fee_pending", 0) for s in students)

    # Main stat cards
    col1, col2 = st.columns(2)
    with col1:
        stat_card("👥", str(total_students), "Total Students")
    with col2:
        stat_card("📨", str(total_enquiries), "Total Enquiries")

    col3, col4 = st.columns(2)
    with col3:
        stat_card("💰", f"₹{total_collected:,}", "Fees Collected")
    with col4:
        stat_card("⏳", f"₹{total_pending:,}", "Pending Fees")

    st.markdown("---")

    # Course-wise student count
    st.markdown('<div class="section-title">📚 Course-wise Students</div>', unsafe_allow_html=True)
    if students:
        course_counts = {}
        for s in students:
            c = s.get("course", "Unknown")
            course_counts[c] = course_counts.get(c, 0) + 1

        # Display as stat cards
        cols = st.columns(min(len(course_counts), 4))
        for i, (course, count) in enumerate(course_counts.items()):
            with cols[i % len(cols)]:
                stat_card("📖", str(count), course)
    else:
        st.info("Koi student nahi hai.")


def show_add_student():
    """Agent: Add a new student — auto-generate ID and default password."""
    st.markdown('<div class="section-title">➕ Add New Student</div>', unsafe_allow_html=True)

    with st.form("add_student_form"):
        name = st.text_input("Student Name *", placeholder="Student ka naam")
        mobile = st.text_input("Mobile Number (10 digit) *", placeholder="9876543210")
        course = st.selectbox("Course *", COURSE_NAMES)
        submitted = st.form_submit_button("➕ Add Student", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("⚠️ Naam khali nahi ho sakta.")
            return
        if not mobile.strip().isdigit() or len(mobile.strip()) != 10:
            st.error("⚠️ Mobile number 10 digit ka hona chahiye (sirf numbers).")
            return

        students = load_json(STUDENTS_FILE)

        # Auto-generate next student ID: ITECH001, ITECH002, ...
        max_num = 0
        for s in students:
            sid = s["student_id"]
            if sid.startswith("ITECH"):
                try:
                    num = int(sid[5:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        next_num = max_num + 1
        new_id = f"ITECH{next_num:03d}"
        default_password = "1234"

        new_student = {
            "student_id": new_id,
            "name": name.strip(),
            "mobile": mobile.strip(),
            "course": course,
            "fee_total": COURSES[course],
            "fee_paid": 0,
            "fee_pending": COURSES[course],
            "password_hash": hash_password(default_password),
            "attendance": [],
            "payments": [],
        }
        students.append(new_student)
        save_json(STUDENTS_FILE, students)

        st.success(f"✅ Student add ho gaya!")
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:24px;">
            <p style="font-size:16px; margin:0;">Student ID: <b style="color:#007AFF;">{new_id}</b></p>
            <p style="font-size:16px; margin:8px 0 0 0;">Default Password: <b style="color:#007AFF;">{default_password}</b></p>
            <p style="color:#8E8E93; font-size:13px; margin-top:12px;">Student ko ye ID aur password bata dein</p>
        </div>
        """, unsafe_allow_html=True)


def show_student_list():
    """Agent: Student list — search, filter by course, edit, delete, reset password."""
    st.markdown('<div class="section-title">📋 Student List</div>', unsafe_allow_html=True)
    students = load_json(STUDENTS_FILE)

    if not students:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:40px;">
            <div style="font-size:50px; margin-bottom:15px;">📋</div>
            <p style="color:#8E8E93;">Koi student nahi hai. Pehle 'Add New Student' se student add karein.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Search and filter
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔍 Search by name or ID", placeholder="Type name or student ID...")
    with col2:
        course_filter = st.selectbox("Filter by Course", ["All"] + COURSE_NAMES)

    # Apply filters
    filtered = students
    if search.strip():
        s_lower = search.strip().lower()
        filtered = [
            s for s in filtered
            if s_lower in s["name"].lower() or s_lower in s["student_id"].lower()
        ]
    if course_filter != "All":
        filtered = [s for s in filtered if s["course"] == course_filter]

    if not filtered:
        st.warning("Koi student match nahi hua.")
        return

    # Display student table
    df = pd.DataFrame([
        {
            "Student ID": s["student_id"],
            "Name": s["name"],
            "Mobile": s["mobile"],
            "Course": s["course"],
            "Total Fee": f"₹{s['fee_total']:,}",
            "Paid": f"₹{s['fee_paid']:,}",
            "Pending": f"₹{s['fee_pending']:,}",
        }
        for s in filtered
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Edit / Delete / Reset Password section
    st.markdown('<div class="section-title">⚙️ Manage Student</div>', unsafe_allow_html=True)
    student_ids = [s["student_id"] for s in filtered]
    selected_id = st.selectbox("Select Student", student_ids)
    selected_student = next(s for s in filtered if s["student_id"] == selected_id)

    col_edit, col_reset, col_delete = st.columns(3)

    with col_edit:
        with st.expander("✏️ Edit Student"):
            with st.form("edit_student_form"):
                edit_name = st.text_input("Name", value=selected_student["name"])
                edit_mobile = st.text_input("Mobile", value=selected_student["mobile"])
                edit_course = st.selectbox(
                    "Course",
                    COURSE_NAMES,
                    index=COURSE_NAMES.index(selected_student["course"]),
                )
                save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)

            if save_btn:
                if not edit_name.strip():
                    st.error("⚠️ Naam khali nahi ho sakta.")
                elif not edit_mobile.strip().isdigit() or len(edit_mobile.strip()) != 10:
                    st.error("⚠️ Mobile number 10 digit ka hona chahiye.")
                else:
                    all_students = load_json(STUDENTS_FILE)
                    for s in all_students:
                        if s["student_id"] == selected_id:
                            s["name"] = edit_name.strip()
                            s["mobile"] = edit_mobile.strip()
                            if s["course"] != edit_course:
                                s["course"] = edit_course
                                s["fee_total"] = COURSES[edit_course]
                                s["fee_pending"] = COURSES[edit_course] - s["fee_paid"]
                            break
                    save_json(STUDENTS_FILE, all_students)
                    st.success("✅ Student details update ho gayi!")
                    st.rerun()

    with col_reset:
        if st.button("🔑 Reset Password", use_container_width=True):
            new_pass = "1234"
            all_students = load_json(STUDENTS_FILE)
            for s in all_students:
                if s["student_id"] == selected_id:
                    s["password_hash"] = hash_password(new_pass)
                    break
            save_json(STUDENTS_FILE, all_students)
            st.success(f"✅ Password reset! Naya password: **{new_pass}**")

    with col_delete:
        if st.button("🗑️ Delete Student", use_container_width=True):
            all_students = load_json(STUDENTS_FILE)
            all_students = [s for s in all_students if s["student_id"] != selected_id]
            save_json(STUDENTS_FILE, all_students)
            st.success("✅ Student delete ho gaya!")
            st.rerun()


def show_fee_collection():
    """Agent: Fee collection — select student, enter amount, mode, date; update records."""
    st.markdown('<div class="section-title">💰 Fee Collection</div>', unsafe_allow_html=True)
    students = load_json(STUDENTS_FILE)

    if not students:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:40px;">
            <div style="font-size:50px; margin-bottom:15px;">💰</div>
            <p style="color:#8E8E93;">Koi student nahi hai.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Show students with pending fees
    pending_students = [s for s in students if s["fee_pending"] > 0]
    if pending_students:
        st.markdown("""
        <div class="glass-card">
            <p style="font-weight:600; margin-bottom:12px;">⚠️ Students with Pending Fees</p>
        """, unsafe_allow_html=True)
        df_pending = pd.DataFrame([
            {
                "Student ID": s["student_id"],
                "Name": s["name"],
                "Course": s["course"],
                "Pending": f"₹{s['fee_pending']:,}",
            }
            for s in pending_students
        ])
        st.dataframe(df_pending, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Fee collection form
    st.markdown('<div class="section-title">🧾 Collect Fee</div>', unsafe_allow_html=True)
    student_options = [
        f"{s['student_id']} — {s['name']} (Pending: ₹{s['fee_pending']:,})"
        for s in students
    ]
    selected_idx = st.selectbox("Select Student", range(len(student_options)),
                                format_func=lambda i: student_options[i])
    selected_student = students[selected_idx]

    # Student fee info cards
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card("💰", f"₹{selected_student['fee_total']:,}", "Total Fee")
    with col2:
        stat_card("✅", f"₹{selected_student['fee_paid']:,}", "Paid")
    with col3:
        stat_card("⏳", f"₹{selected_student['fee_pending']:,}", "Pending")

    with st.form("fee_collection_form"):
        amount = st.number_input("Amount (INR)", min_value=1, max_value=100000, step=500)
        payment_mode = st.selectbox("Payment Mode", ["Cash", "UPI"])
        pay_date = st.date_input("Payment Date", value=date.today())
        submit = st.form_submit_button("💰 Collect Fee", use_container_width=True)

    if submit:
        if amount > selected_student["fee_pending"]:
            st.error(f"⚠️ Amount pending fee se zyada hai! Pending: ₹{selected_student['fee_pending']:,}")
            return

        # Generate receipt number
        existing_receipts = []
        for s in students:
            existing_receipts.extend(s.get("payments", []))
        max_receipt = 0
        for p in existing_receipts:
            try:
                num = int(p["receipt_no"].lstrip("R"))
                if num > max_receipt:
                    max_receipt = num
            except (ValueError, AttributeError):
                pass
        receipt_no = f"R{max_receipt + 1:03d}"

        # Update student record
        all_students = load_json(STUDENTS_FILE)
        for s in all_students:
            if s["student_id"] == selected_student["student_id"]:
                s["fee_paid"] += int(amount)
                s["fee_pending"] -= int(amount)
                s.setdefault("payments", []).append({
                    "receipt_no": receipt_no,
                    "date": str(pay_date),
                    "amount": int(amount),
                    "mode": payment_mode,
                })
                break
        save_json(STUDENTS_FILE, all_students)

        st.success(f"✅ Fee collected! Receipt No: **{receipt_no}**")
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:24px;">
            <p style="font-size:14px; margin:0; color:#8E8E93;">Receipt No</p>
            <p style="font-size:24px; font-weight:800; color:#007AFF; margin:4px 0;">{receipt_no}</p>
            <p style="font-size:16px; margin:8px 0 0 0;">Amount: <b>₹{int(amount):,}</b> · Mode: <b>{payment_mode}</b></p>
        </div>
        """, unsafe_allow_html=True)
        st.rerun()


def show_mark_attendance():
    """Agent: Mark daily attendance — Present/Absent checkboxes for all students."""
    st.markdown('<div class="section-title">📅 Mark Attendance</div>', unsafe_allow_html=True)
    students = load_json(STUDENTS_FILE)

    if not students:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:40px;">
            <div style="font-size:50px; margin-bottom:15px;">📅</div>
            <p style="color:#8E8E93;">Koi student nahi hai.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    att_date = st.date_input("Date", value=date.today())
    date_str = str(att_date)

    st.markdown(f"""
    <div class="glass-card">
        <p style="margin:0; font-weight:600; color:#1C1C1E;">📅 Date: {date_str}</p>
        <p style="color:#8E8E93; font-size:13px; margin-top:4px;">Har student ke liye Present ya Absent select karein</p>
    </div>
    """, unsafe_allow_html=True)

    # Build checkbox state
    attendance_records = {}
    for s in students:
        existing = next(
            (a for a in s.get("attendance", []) if a["date"] == date_str),
            None,
        )
        default_present = existing["status"] == "Present" if existing else True
        key = f"att_{s['student_id']}"
        is_present = st.checkbox(
            f"{s['student_id']} — {s['name']} ({s['course']})",
            value=default_present,
            key=key,
        )
        attendance_records[s["student_id"]] = "Present" if is_present else "Absent"

    if st.button("💾 Save Attendance", use_container_width=True):
        all_students = load_json(STUDENTS_FILE)
        for s in all_students:
            status = attendance_records.get(s["student_id"], "Absent")
            s["attendance"] = [
                a for a in s.get("attendance", []) if a["date"] != date_str
            ]
            s["attendance"].append({"date": date_str, "status": status})
        save_json(STUDENTS_FILE, all_students)
        st.success(f"✅ Attendance for {date_str} save ho gayi!")
        st.rerun()


def show_enquiries():
    """Agent: View all enquiries in a table with Download CSV button."""
    st.markdown('<div class="section-title">📨 Enquiries</div>', unsafe_allow_html=True)
    enquiries = load_enquiries()

    if not enquiries:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:40px;">
            <div style="font-size:50px; margin-bottom:15px;">📨</div>
            <p style="color:#8E8E93;">Koi enquiry nahi mila.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Stat card
    stat_card("📨", str(len(enquiries)), "Total Enquiries")

    st.markdown("---")

    df = pd.DataFrame(enquiries)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Download CSV button
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=f"enquiries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
    )


def show_agent_management():
    """Agent management — only main admin agent (AGENT01) can add/remove agents."""
    st.markdown('<div class="section-title">👥 Agent Management</div>', unsafe_allow_html=True)

    if not st.session_state.get("is_admin", False):
        st.error("🔒 Aapko is page ka access nahi hai. Sirf main admin agent agents manage kar sakte hain.")
        return

    st.warning("⚠️ Yeh page sirf main admin agent (AGENT01) ke liye hai.")

    agents = load_json(AGENTS_FILE)

    # Show current agents
    st.markdown("""
    <div class="glass-card">
        <p style="font-weight:600; margin-bottom:12px;">📋 Current Agents</p>
    """, unsafe_allow_html=True)
    df = pd.DataFrame([
        {
            "Agent ID": a["agent_id"],
            "Name": a["name"],
            "Admin": "✅ Yes" if a.get("is_admin") else "❌ No",
        }
        for a in agents
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Add new agent
    st.markdown('<div class="section-title">➕ Add New Agent</div>', unsafe_allow_html=True)
    with st.form("add_agent_form"):
        new_agent_id = st.text_input("Agent ID *", placeholder="e.g. AGENT03")
        new_agent_name = st.text_input("Agent Name *", placeholder="Agent ka naam")
        new_agent_pass = st.text_input("Password *", type="password", placeholder="••••")
        submit = st.form_submit_button("➕ Add Agent", use_container_width=True)

    if submit:
        if not new_agent_id.strip() or not new_agent_name.strip() or not new_agent_pass:
            st.error("⚠️ Sabhi fields bharo.")
            return
        if any(a["agent_id"] == new_agent_id.strip() for a in agents):
            st.error("⚠️ Yeh Agent ID pehle se exist karta hai. Doosra ID try karein.")
            return
        new_agent = {
            "agent_id": new_agent_id.strip(),
            "name": new_agent_name.strip(),
            "password_hash": hash_password(new_agent_pass),
            "is_admin": False,
        }
        agents.append(new_agent)
        save_json(AGENTS_FILE, agents)
        st.success(f"✅ Agent add ho gaya! ID: **{new_agent_id.strip()}**")

    # Remove agent
    st.markdown('<div class="section-title">🗑️ Remove Agent</div>', unsafe_allow_html=True)
    removable = [a for a in agents if a["agent_id"] != ADMIN_AGENT_ID]
    if not removable:
        st.info("Main admin ke alawa koi agent nahi hai.")
    else:
        remove_id = st.selectbox(
            "Select Agent to Remove",
            [a["agent_id"] for a in removable],
        )
        if st.button("🗑️ Remove Agent", use_container_width=True):
            agents = [a for a in agents if a["agent_id"] != remove_id]
            save_json(AGENTS_FILE, agents)
            st.success(f"✅ Agent {remove_id} remove ho gaya!")
            st.rerun()


# ──────────────────────────────────────────────
# MAIN APP — role-based menu routing
# ──────────────────────────────────────────────

def show_student_panel():
    """Sidebar menu for students."""
    inject_glass_css()

    with st.sidebar:
        st.markdown(f"### 📚 {INSTITUTE_SHORT}")
        sidebar_user_card("🎓", st.session_state.user_name, st.session_state.user_id, "Student")
        st.markdown("---")
        menu = st.radio(
            "📋 Menu",
            ["🏠 Home", "📚 Courses & Fees", "⏰ Timing", "👤 My Profile",
             "📅 My Attendance", "💰 Fee History"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            do_logout()
        st.markdown('</div>', unsafe_allow_html=True)

    # Route to selected page
    if menu == "🏠 Home":
        show_home()
    elif menu == "📚 Courses & Fees":
        show_courses_and_fees()
    elif menu == "⏰ Timing":
        show_timing()
    elif menu == "👤 My Profile":
        show_student_profile()
    elif menu == "📅 My Attendance":
        show_student_attendance()
    elif menu == "💰 Fee History":
        show_student_fee_history()


def show_agent_panel():
    """Sidebar menu for agents."""
    inject_glass_css()

    with st.sidebar:
        st.markdown(f"### 📚 {INSTITUTE_SHORT}")
        admin_label = "Admin" if st.session_state.get("is_admin") else "Agent"
        sidebar_user_card("🧑‍💼", st.session_state.user_name, st.session_state.user_id, admin_label)
        st.markdown("---")
        menu = st.radio(
            "📋 Menu",
            ["📊 Dashboard", "➕ Add Student", "📋 Student List",
             "💰 Fee Collection", "📅 Attendance", "📨 Enquiries",
             "👥 Agents"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            do_logout()
        st.markdown('</div>', unsafe_allow_html=True)

    # Route to selected page
    if menu == "📊 Dashboard":
        show_agent_dashboard()
    elif menu == "➕ Add Student":
        show_add_student()
    elif menu == "📋 Student List":
        show_student_list()
    elif menu == "💰 Fee Collection":
        show_fee_collection()
    elif menu == "📅 Attendance":
        show_mark_attendance()
    elif menu == "📨 Enquiries":
        show_enquiries()
    elif menu == "👥 Agents":
        show_agent_management()


def show_guest_panel():
    """Sidebar menu for guests — limited access."""
    inject_glass_css()

    with st.sidebar:
        st.markdown(f"### 📚 {INSTITUTE_SHORT}")
        sidebar_user_card("👁️", "Guest", "No Login", "Guest Mode")
        st.markdown("---")
        menu = st.radio(
            "📋 Menu",
            ["🏠 Home", "📚 Courses & Fees", "⏰ Timing", "📝 Enquiry"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        if st.button("🚪 Exit Guest", use_container_width=True):
            do_logout()

    # Route to selected page
    if menu == "🏠 Home":
        show_home()
    elif menu == "📚 Courses & Fees":
        show_courses_and_fees()
    elif menu == "⏰ Timing":
        show_timing()
    elif menu == "📝 Enquiry":
        show_guest_enquiry()


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

def main():
    """Main entry point — initialize data, check login, route to appropriate panel."""
    # Page config
    st.set_page_config(
        page_title=f"{INSTITUTE_NAME} — Student Portal",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize data files and session state
    init_data_files()
    init_session_state()

    # Route based on login status and role
    if not st.session_state.logged_in:
        show_login_page()
    elif st.session_state.role == "student":
        show_student_panel()
    elif st.session_state.role == "agent":
        show_agent_panel()
    elif st.session_state.role == "guest":
        show_guest_panel()
    else:
        st.session_state.logged_in = False
        st.rerun()


if __name__ == "__main__":
    main()
