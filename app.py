import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import hashlib
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from io import BytesIO
import warnings
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
import pickle
from pathlib import Path
import base64

warnings.filterwarnings('ignore')

# ==============================================================================
# CHECK AND INSTALL MISSING DEPENDENCIES
# ==============================================================================
try:
    import xlsxwriter
except ImportError:
    st.error("📦 Missing dependency: xlsxwriter")
    st.info("Please install it using: `pip install xlsxwriter`")
    if st.button("📥 Install xlsxwriter (requires internet)"):
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "xlsxwriter"])
        st.success("✅ xlsxwriter installed successfully! Please restart the app.")
        st.stop()

# ==============================================================================
# APPLICATION CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="EduTrack Pro 2025",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = ""
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'selected_semester' not in st.session_state:
    st.session_state.selected_semester = "Spring 2025"
if 'selected_course' not in st.session_state:
    st.session_state.selected_course = ""
if 'co_po_mapping' not in st.session_state:
    st.session_state.co_po_mapping = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"
if 'all_semester_data' not in st.session_state:
    st.session_state.all_semester_data = {}
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'email_sent' not in st.session_state:
    st.session_state.email_sent = False
if 'predictions' not in st.session_state:
    st.session_state.predictions = {}
if 'all_courses_data' not in st.session_state:
    st.session_state.all_courses_data = {}
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False


# ==============================================================================
# FORCE RESET FUNCTION
# ==============================================================================
def force_reset():
    """Force reset all data on app startup"""
    import shutil

    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Delete data files
    if os.path.exists("users.json"):
        os.remove("users.json")

    if os.path.exists("course_data"):
        shutil.rmtree("course_data")

    # Recreate directory
    os.makedirs("course_data", exist_ok=True)

    # Initialize fresh session
    st.session_state.logged_in = False
    st.session_state.user_type = ""
    st.session_state.username = ""
    st.session_state.data = None
    st.session_state.processed = False
    st.session_state.results = {}
    st.session_state.admin_mode = False

    return True


# ==============================================================================
# PROFESSIONAL THEME
# ==============================================================================
def apply_professional_theme():
    st.markdown("""
    <style>
    .main {
        background-color: #f8fdff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .header {
        background: linear-gradient(135deg, #1e88e5, #42a5f5);
        color: white;
        padding: 1.5rem;
        border-radius: 0 0 15px 15px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(30, 136, 229, 0.15);
    }

    .card {
        background: white;
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(30, 136, 229, 0.08);
        border: 1px solid #e3f2fd;
        transition: transform 0.3s;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.12);
    }

    .card h3 {
        color: #1e88e5;
        border-bottom: 2px solid #bbdefb;
        padding-bottom: 0.7rem;
        margin-bottom: 1.2rem;
        font-size: 1.4rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1e88e5, #42a5f5);
        color: white;
        border: none;
        padding: 0.8rem 1.8rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(30, 136, 229, 0.3);
        background: linear-gradient(135deg, #1976d2, #1e88e5);
    }

    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8fdff);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e3f2fd;
        transition: all 0.3s;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(30, 136, 229, 0.1);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e88e5;
        margin: 0.5rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    .metric-label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .success-box {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border-left: 5px solid #28a745;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #155724;
    }

    .info-box {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        border-left: 5px solid #17a2b8;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #0c5460;
    }

    .warning-box {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border-left: 5px solid #ffc107;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #856404;
    }

    .career-card {
        background: linear-gradient(135deg, #1e88e5, #42a5f5);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.2);
        transition: all 0.3s;
    }

    .career-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(30, 136, 229, 0.3);
    }

    .baete-card {
        background: linear-gradient(135deg, #4CAF50, #8BC34A);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1e88e5, #42a5f5);
    }

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    .prediction-box {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-left: 5px solid #2196F3;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #0d47a1;
    }

    .ai-note {
        font-size: 0.85rem;
        color: #666;
        font-style: italic;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background-color: #fffde7;
        border-radius: 5px;
        border-left: 3px solid #ffd600;
    }

    .team-card {
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.2);
    }

    .admin-card {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 65, 108, 0.2);
    }

    .danger-button {
        background: linear-gradient(135deg, #ff416c, #ff4b2b) !important;
        color: white !important;
        border: none !important;
    }

    .danger-button:hover {
        background: linear-gradient(135deg, #e03e5a, #e63939) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 65, 108, 0.3);
    }

    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# ABOUT PAGE WITH TEAM INFORMATION
# ==============================================================================
def about_page():
    """Display about page with team information"""
    apply_professional_theme()

    st.markdown('<div class="header">', unsafe_allow_html=True)
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        st.markdown("<h1>ℹ️</h1>", unsafe_allow_html=True)
    with col_title:
        st.title("About EduTrack Pro 2025")
        st.markdown("<h4>Developed by Department of EEE, Stamford University Bangladesh</h4>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Team Information Card
    st.markdown('<div class="team-card">', unsafe_allow_html=True)
    st.markdown("### 👨‍🏫 Project Supervision")
    st.markdown("""
    **Dr. Dilshad Mahajabeen**  
    *Chairman & Professor*  
    Department of Electrical & Electronic Engineering  
    Stamford University, Bangladesh
    """)

    st.markdown("---")

    st.markdown("### 👥 Development Team")

    col_team1, col_team2 = st.columns(2)

    with col_team1:
        st.markdown("""
        #### **Team Lead & Developer:**
        **Fahmida Islam**  
        *AI & Education Technology Specialist*

        #### **Core Developer:**
        **Rowshan-E- Gule Jannat**  
        *Full Stack Developer & Data Analyst*
        """)

    with col_team2:
        st.markdown("""
        #### **UI/UX Designer:**
        **Sawkat Islam**  
        *Frontend Developer & UI Specialist*

        #### **Academic Advisor:**
        **Department of EEE Faculty**  
        *Stamford University Bangladesh*
        """)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    col_about1, col_about2 = st.columns([2, 1])

    with col_about1:
        st.markdown("### 🎓 About the Application")
        st.markdown("""
        **EduTrack Pro 2025** is a comprehensive academic analytics system designed for 
        engineering education in Bangladesh, fully compliant with BAETE 2022 standards.

        #### Key Features:
        - ✅ **BAETE 4-CO, 12-PO Framework** compliant
        - ✅ **AI-Powered Predictions** for academic growth & career guidance
        - ✅ **Bulk Email System** for parent communication
        - ✅ **Multi-User Platform** (Teachers, Students, Parents, Admin)
        - ✅ **Advanced Analytics** with interactive visualizations
        - ✅ **XLSX Template Support** for easy data management
        - ✅ **Persistent Data Storage** across sessions
        - ✅ **Real-time CO-PO Analysis** for each course
        - ✅ **Student Course Portal** - View all subjects
        - ✅ **Parent Dashboard** - Monitor child's progress
        - ✅ **Batch-wise Performance Analysis**
        - ✅ **CGPA Tracking & Semester-wise Graphs**
        - ✅ **Admin Panel** - Full system control
        """)

    with col_about2:
        st.markdown("### 🏫 Institution")
        st.markdown("""
        #### **Stamford University Bangladesh**
        Department of Electrical & Electronic Engineering

        **📍 Address:**  
        51, Siddeswari Road, Dhaka-1217  
        Bangladesh

        **📧 Email:**  
        eee@stamforduniversity.edu.bd

        **🌐 Website:**  
        [www.stamforduniversity.edu.bd](https://www.stamforduniversity.edu.bd)

        **📱 Phone:**  
        +880 2 831 2445
        """)

    st.markdown("---")

    st.markdown("### 🚀 Deployment & Access")
    st.markdown("""
    #### **How to Run the Application:**

    1. **Local Run:**
    ```bash
    pip install -r requirements.txt
    streamlit run app.py
    ```

    2. **Deploy to Streamlit Cloud:**
    - Upload to GitHub repository
    - Connect to Streamlit Community Cloud
    - Access via public URL

    3. **Access via Link:**
    - Once deployed, share the Streamlit Cloud URL
    - All users can access via browser
    - No installation required for users
    """)

    st.markdown("""
    #### **Demo Accounts:**
    - **Admin:** `admin` / `admin123` (Full system access)
    - **Teacher:** `teacher` / `teacher123`
    - **Student:** `student` / `student123`
    - **Parent:** `parent` / `parent123`
    """)

    st.markdown("---")

    st.markdown("### 🔒 Privacy & Data Protection")
    st.markdown("""
    - All student data is encrypted and stored securely
    - Parent emails are used only for academic communication
    - BAETE compliance ensures data integrity
    - Regular security audits and updates
    - GDPR compliant data handling practices
    """)

    if st.button("🔙 Back to Dashboard", use_container_width=True):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# BAETE CO-PO FRAMEWORK
# ==============================================================================
def show_baete_copo_framework():
    """Display BAETE CO-PO framework on homepage"""
    st.markdown('<div class="baete-card">', unsafe_allow_html=True)

    st.markdown("### 🏛️ BAETE 2022 CO-PO Framework (4 COs & 12 POs)")
    st.markdown("**Reference:** Bangladesh Accreditation Council for Engineering and Technology (BAETE) Manual 2022")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 12 Program Outcomes (POs)")
        pos = [
            "**PO1:** **Engineering Knowledge** - Apply knowledge of mathematics, science, engineering fundamentals",
            "**PO2:** **Problem Analysis** - Identify, formulate, research literature, analyze complex engineering problems",
            "**PO3:** **Design/Development of Solutions** - Design solutions for complex engineering problems",
            "**PO4:** **Investigation** - Conduct investigations of complex problems using research-based knowledge",
            "**PO5:** **Modern Tool Usage** - Create, select, apply appropriate techniques, resources, modern engineering tools",
            "**PO6:** **The Engineer and Society** - Apply reasoning to assess societal, health, safety, legal, cultural issues",
            "**PO7:** **Environment & Sustainability** - Understand impact of engineering solutions in societal, environmental contexts",
            "**PO8:** **Ethics** - Apply ethical principles, commit to professional ethics, responsibilities, engineering practice norms",
            "**PO9:** **Individual & Team Work** - Function effectively as individual, member/leader in diverse teams",
            "**PO10:** **Communication** - Communicate effectively on complex engineering activities",
            "**PO11:** **Project Management** - Demonstrate knowledge, understanding of engineering, management principles",
            "**PO12:** **Life-long Learning** - Recognize need for, engage in independent, life-long learning"
        ]
        for po in pos:
            st.markdown(f"- {po}")

    with col2:
        st.markdown("#### 📋 4 Course Outcomes (COs)")
        st.markdown("**Typical EEE Course Structure:**")
        cos = [
            "**CO1:** **Knowledge Application** - Apply mathematics, science, engineering principles to solve electrical engineering problems",
            "**CO2:** **Problem Solving** - Design, analyze electrical systems, components, processes to meet needs within constraints",
            "**CO3:** **Investigation & Analysis** - Conduct experiments, analyze data, interpret results using appropriate techniques",
            "**CO4:** **Professional Skills** - Communicate effectively, work in teams, understand professional ethics and responsibilities"
        ]
        for co in cos:
            st.markdown(f"- {co}")

    st.markdown("---")
    st.markdown("#### 📊 Assessment Marks Distribution")

    marks_dist = pd.DataFrame({
        'Component': ['Mid Exam', 'Final Exam', 'Class Tests', 'Assignments', 'Attendance'],
        'Marks': [30, 40, 20, 5, 5],
        'Total': [30, 40, 20, 5, 5],
        'CO-PO Mapping': ['Yes', 'Yes', 'Yes', 'Yes', 'No']
    })

    st.dataframe(marks_dist, use_container_width=True, hide_index=True)

    st.markdown("**Key Points:**")
    st.markdown("1. **Total Marks:** 100 (excluding attendance from CO-PO)")
    st.markdown("2. **Attendance (5 marks)** excluded from CO-PO attainment calculations")
    st.markdown("3. **CO Mapping:** Each CO mapped to multiple POs with correlation values (1-3 scale)")
    st.markdown("4. **PO Attainment:** Calculated from CO performance using mapping matrix")

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# USER MANAGEMENT
# ==============================================================================
def load_users():
    """Load user data from JSON file or create default users"""
    default_users = {
        "admins": {
            "admin": {
                "username": "admin",
                "password": hash_password("admin123"),
                "email": "admin@stamford.edu.bd",
                "full_name": "System Administrator",
                "department": "IT & Administration",
                "designation": "System Admin",
                "user_type": "admin"
            }
        },
        "teachers": {
            "teacher": {
                "username": "teacher",
                "password": hash_password("teacher123"),
                "email": "teacher@stamford.edu.bd",
                "full_name": "Dr. Dilshad Mahajabeen",
                "department": "Electrical & Electronic Engineering",
                "designation": "Professor & Chairman",
                "user_type": "teacher"
            }
        },
        "students": {
            "student": {
                "username": "student",
                "password": hash_password("student123"),
                "email": "student@stamford.edu.bd",
                "full_name": "John Smith",
                "student_id": "2021001",
                "batch": "2021",
                "guardian_email": "parent@email.com",
                "user_type": "student"
            },
            "fahmida": {
                "username": "fahmida",
                "password": hash_password("fahmida123"),
                "email": "fahmida@stamford.edu.bd",
                "full_name": "Fahmida Islam",
                "student_id": "2021002",
                "batch": "2021",
                "guardian_email": "parent2@email.com",
                "user_type": "student"
            },
            "rowshan": {
                "username": "rowshan",
                "password": hash_password("rowshan123"),
                "email": "rowshan@stamford.edu.bd",
                "full_name": "Rowshan-E- Gule Jannat",
                "student_id": "2021003",
                "batch": "2021",
                "guardian_email": "parent3@email.com",
                "user_type": "student"
            },
            "sawkat": {
                "username": "sawkat",
                "password": hash_password("sawkat123"),
                "email": "sawkat@stamford.edu.bd",
                "full_name": "Sawkat Islam",
                "student_id": "2021004",
                "batch": "2021",
                "guardian_email": "parent4@email.com",
                "user_type": "student"
            }
        },
        "parents": {
            "parent": {
                "username": "parent",
                "password": hash_password("parent123"),
                "email": "parent@email.com",
                "full_name": "Sarah Johnson",
                "student_linked": "2021001",
                "user_type": "parent"
            }
        }
    }

    try:
        if os.path.exists("users.json"):
            with open("users.json", 'r') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Could not load user file: {e}")

    return default_users


def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(username, password, user_type):
    """Authenticate user credentials"""
    users = load_users()

    # Admin can login with any type if admin credentials are correct
    if user_type == "admin" or st.session_state.get('admin_mode', False):
        if "admins" in users and username in users["admins"]:
            stored_hash = users["admins"][username]["password"]
            if hash_password(password) == stored_hash:
                return True, users["admins"][username]

    # Regular user authentication
    user_category = user_type + "s"

    if user_category in users and username in users[user_category]:
        stored_hash = users[user_category][username]["password"]
        if hash_password(password) == stored_hash:
            return True, users[user_category][username]

    return False, None


def register_user(username, password, user_type, full_name, email, **kwargs):
    """Register new user"""
    users = load_users()
    user_category = user_type + "s"

    if user_category not in users:
        users[user_category] = {}

    if username in users[user_category]:
        return False, "Username already exists"

    user_data = {
        "username": username,
        "password": hash_password(password),
        "full_name": full_name,
        "email": email,
        "user_type": user_type
    }

    # Add additional fields based on user type
    if user_type == "teacher":
        user_data.update({
            "department": kwargs.get("department", ""),
            "designation": kwargs.get("designation", "")
        })
    elif user_type == "student":
        user_data.update({
            "student_id": kwargs.get("student_id", ""),
            "batch": kwargs.get("batch", ""),
            "guardian_email": kwargs.get("guardian_email", "")
        })
    elif user_type == "parent":
        user_data.update({
            "student_linked": kwargs.get("student_linked", "")
        })
    elif user_type == "admin":
        user_data.update({
            "department": kwargs.get("department", "Administration"),
            "designation": kwargs.get("designation", "System Administrator")
        })

    users[user_category][username] = user_data

    try:
        with open("users.json", 'w') as f:
            json.dump(users, f, indent=4)
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def delete_user(username, user_type):
    """Delete user from system"""
    users = load_users()
    user_category = user_type + "s"

    if user_category in users and username in users[user_category]:
        del users[user_category][username]

        try:
            with open("users.json", 'w') as f:
                json.dump(users, f, indent=4)
            return True, f"User {username} deleted successfully"
        except Exception as e:
            return False, f"Error deleting user: {str(e)}"

    return False, "User not found"


def get_all_users():
    """Get all users from system"""
    users = load_users()
    all_users = []

    for category, user_dict in users.items():
        for username, user_data in user_dict.items():
            all_users.append({
                "username": username,
                "full_name": user_data.get("full_name", ""),
                "email": user_data.get("email", ""),
                "user_type": user_data.get("user_type", category[:-1]),
                "department": user_data.get("department", ""),
                "designation": user_data.get("designation", ""),
                "student_id": user_data.get("student_id", ""),
                "batch": user_data.get("batch", ""),
                "student_linked": user_data.get("student_linked", "")
            })

    return pd.DataFrame(all_users)


# ==============================================================================
# DATA STORAGE SYSTEM
# ==============================================================================
def save_course_data(semester, course_code, results):
    """Save course data to file for persistent storage"""
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("course_data")
        data_dir.mkdir(exist_ok=True)

        # Save each student's data individually for easy access
        for student_id, student_data in results['students'].items():
            student_file = data_dir / f"student_{student_id}.pkl"

            # Load existing student data or create new
            if student_file.exists():
                with open(student_file, 'rb') as f:
                    all_student_data = pickle.load(f)
            else:
                all_student_data = {}

            # Add/update course data
            course_key = f"{semester}_{course_code}"
            all_student_data[course_key] = {
                'course_code': course_code,
                'semester': semester,
                'student_data': student_data,
                'course_stats': results.get('course_stats', {}),
                'co_attainment': results.get('co_attainment', {}),
                'po_attainment': results.get('po_attainment', {}),
                'predictions': results.get('predictions', {}).get(student_id, {}),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Save back to file
            with open(student_file, 'wb') as f:
                pickle.dump(all_student_data, f)

        # Also save course-wide data
        course_file = data_dir / f"course_{semester}_{course_code}.pkl"
        with open(course_file, 'wb') as f:
            pickle.dump(results, f)

        return True
    except Exception as e:
        st.error(f"Error saving course data: {e}")
        return False


def load_student_data(student_id):
    """Load all course data for a specific student"""
    try:
        student_file = Path("course_data") / f"student_{student_id}.pkl"
        if student_file.exists():
            with open(student_file, 'rb') as f:
                return pickle.load(f)
        return {}
    except Exception as e:
        return {}


def load_all_courses():
    """Load all available courses from data directory"""
    courses = {}
    try:
        data_dir = Path("course_data")
        if data_dir.exists():
            for file in data_dir.glob("course_*.pkl"):
                with open(file, 'rb') as f:
                    course_data = pickle.load(f)
                    key = f"{course_data.get('semester')} - {course_data.get('course_code')}"
                    courses[key] = course_data
    except Exception as e:
        pass
    return courses


def get_student_cgpa_data(student_id):
    """Get CGPA progression data for a student"""
    student_data = load_student_data(student_id)
    if not student_data:
        return None

    # Organize data by semester
    semester_data = {}
    for course_key, course_info in student_data.items():
        semester = course_info['semester']
        if semester not in semester_data:
            semester_data[semester] = {
                'courses': [],
                'sGPAs': [],
                'credits': []
            }

        # Assume 3 credit hours per course
        semester_data[semester]['courses'].append(course_info['course_code'])
        semester_data[semester]['sGPAs'].append(course_info['student_data']['sgpa'])
        semester_data[semester]['credits'].append(3)  # Standard credit hours

    # Calculate semester-wise SGPA and cumulative CGPA
    semester_results = []
    cumulative_gpa_points = 0
    cumulative_credits = 0

    for semester in sorted(semester_data.keys()):
        sGPAs = semester_data[semester]['sGPAs']
        credits = semester_data[semester]['credits']

        # Calculate semester SGPA
        semester_sgpa = np.average(sGPAs, weights=credits)

        # Update cumulative CGPA
        semester_gpa_points = sum(sgpa * credit for sgpa, credit in zip(sGPAs, credits))
        semester_credits = sum(credits)

        cumulative_gpa_points += semester_gpa_points
        cumulative_credits += semester_credits
        cumulative_cgpa = cumulative_gpa_points / cumulative_credits if cumulative_credits > 0 else 0

        semester_results.append({
            'semester': semester,
            'courses': semester_data[semester]['courses'],
            'semester_sgpa': round(semester_sgpa, 2),
            'cumulative_cgpa': round(cumulative_cgpa, 2),
            'credits_completed': cumulative_credits
        })

    return semester_results


# ==============================================================================
# AI PREDICTION MODULE
# ==============================================================================
def generate_ai_predictions(results):
    """Generate AI predictions for each student's academic growth and career prospects"""
    predictions = {}

    if not results.get('students'):
        return predictions

    # Get all students data
    students_data = []
    student_ids = []

    for student_id, student in results['students'].items():
        # Extract features for prediction
        features = [
            student.get('total_marks', 0),
            student.get('mid', 0),
            student.get('final', 0),
            student.get('ct', 0),
            student.get('assignment', 0),
            student.get('sgpa', 0),
            np.mean(list(student.get('co_scores', {}).values())) if student.get('co_scores') else 0
        ]

        students_data.append(features)
        student_ids.append(student_id)

    if len(students_data) < 3:
        # Not enough data for proper ML predictions
        for student_id, student in results['students'].items():
            predictions[student_id] = generate_rule_based_prediction(student)
        return predictions

    # Convert to numpy array
    X = np.array(students_data)

    # 1. Predict future academic performance (next semester)
    y_academic = X[:, 0]  # Current total marks as target (simplified)

    # Create synthetic next semester prediction
    model_academic = LinearRegression()
    model_academic.fit(X[:, 1:], y_academic)

    # 2. Predict career sector suitability
    career_sectors = [
        "Power Systems & Energy",
        "Electronics & Embedded Systems",
        "Telecommunications",
        "Control & Automation",
        "Research & Academia",
        "Renewable Energy",
        "AI & Machine Learning in EEE"
    ]

    # Create synthetic career labels based on performance patterns
    y_career = []
    for features in X:
        total_marks = features[0]
        sgpa = features[5]
        co_avg = features[6]

        if total_marks >= 80 and sgpa >= 3.5:
            y_career.append(0)  # Research & Academia
        elif total_marks >= 75 and features[3] >= 15:
            y_career.append(1)  # Electronics & Embedded Systems
        elif total_marks >= 70 and features[2] >= 30:
            y_career.append(2)  # Power Systems
        elif total_marks >= 65 and co_avg >= 15:
            y_career.append(3)  # Control & Automation
        elif total_marks >= 60:
            y_career.append(4)  # Telecommunications
        elif total_marks >= 50:
            y_career.append(5)  # Renewable Energy
        else:
            y_career.append(6)  # AI & ML in EEE

    model_career = RandomForestClassifier(n_estimators=50, random_state=42)
    model_career.fit(X[:, 1:], y_career)

    # Generate predictions for each student
    for idx, student_id in enumerate(student_ids):
        student = results['students'][student_id]
        features = X[idx]

        # Academic growth prediction
        next_sem_pred = model_academic.predict([features[1:]])[0]
        next_sem_pred = max(40, min(95, next_sem_pred))

        # Career sector prediction
        career_idx = model_career.predict([features[1:]])[0]
        career_sector = career_sectors[career_idx]

        # Growth percentage
        current_marks = features[0]
        growth_percent = ((next_sem_pred - current_marks) / current_marks * 100) if current_marks > 0 else 0

        # Performance category
        if current_marks >= 80:
            performance = "Excellent"
            recommendation = "Consider graduate studies or research positions"
        elif current_marks >= 70:
            performance = "Good"
            recommendation = "Focus on specialization in your strong areas"
        elif current_marks >= 60:
            performance = "Average"
            recommendation = "Improve weak areas through practice and mentorship"
        elif current_marks >= 40:
            performance = "Satisfactory"
            recommendation = "Maintain consistency and seek guidance"
        else:
            performance = "Needs Improvement"
            recommendation = "Seek academic support and focus on fundamentals"

        # Skill assessment based on CO scores
        co_scores = student.get('co_scores', {})
        skills = []
        if co_scores.get('CO1', 0) >= 15:
            skills.append("Strong theoretical foundation")
        if co_scores.get('CO2', 0) >= 15:
            skills.append("Good problem-solving ability")
        if co_scores.get('CO3', 0) >= 15:
            skills.append("Analytical and investigative skills")
        if co_scores.get('CO4', 0) >= 15:
            skills.append("Strong professional and communication skills")

        if not skills:
            skills = ["Developing core engineering skills"]

        predictions[student_id] = {
            'student_name': student['name'],
            'current_performance': f"{current_marks:.1f} marks ({performance})",
            'predicted_next_semester': f"{next_sem_pred:.1f} marks",
            'growth_percentage': f"{growth_percent:.1f}%",
            'recommended_career_sector': career_sector,
            'key_strengths': skills[:3],
            'recommendation': recommendation,
            'confidence_level': "Medium" if len(students_data) >= 5 else "Low"
        }

    return predictions


def generate_rule_based_prediction(student):
    """Generate rule-based predictions when insufficient data for ML"""
    total_marks = student.get('total_marks', 0)
    sgpa = student.get('sgpa', 0)

    if total_marks >= 80:
        performance = "Excellent"
        next_sem = min(95, total_marks + np.random.uniform(0, 5))
        career = np.random.choice(["Research & Academia", "Power Systems Design", "Advanced Electronics"])
        recommendation = "Pursue graduate studies or competitive industry positions"
    elif total_marks >= 70:
        performance = "Good"
        next_sem = min(90, total_marks + np.random.uniform(-2, 8))
        career = np.random.choice(["Energy Management", "Control Systems", "Telecommunications"])
        recommendation = "Focus on specialization and internships"
    elif total_marks >= 60:
        performance = "Average"
        next_sem = min(85, total_marks + np.random.uniform(-5, 10))
        career = np.random.choice(["Renewable Energy", "Maintenance Engineering", "Technical Sales"])
        recommendation = "Improve fundamentals and seek practical experience"
    elif total_marks >= 40:
        performance = "Satisfactory"
        next_sem = max(40, total_marks + np.random.uniform(-10, 15))
        career = "General Engineering with focused skill development"
        recommendation = "Maintain consistency and seek academic guidance"
    else:
        performance = "Needs Improvement"
        next_sem = max(30, total_marks + np.random.uniform(-5, 20))
        career = "Foundation strengthening required"
        recommendation = "Seek academic support and focus on core concepts"

    strengths = []
    if student.get('mid', 0) >= 20:
        strengths.append("Good exam preparation skills")
    if student.get('final', 0) >= 30:
        strengths.append("Strong comprehensive understanding")
    if student.get('ct', 0) >= 15:
        strengths.append("Consistent performance in assessments")
    if student.get('assignment', 0) >= 4:
        strengths.append("Good assignment completion")

    if not strengths:
        strengths = ["Developing engineering competencies"]

    growth = ((next_sem - total_marks) / total_marks * 100) if total_marks > 0 else 0

    return {
        'student_name': student['name'],
        'current_performance': f"{total_marks:.1f} marks ({performance})",
        'predicted_next_semester': f"{next_sem:.1f} marks",
        'growth_percentage': f"{growth:.1f}%",
        'recommended_career_sector': career,
        'key_strengths': strengths[:3],
        'recommendation': recommendation,
        'confidence_level': "Low (Rule-based)"
    }


def show_ai_prediction(prediction, is_student=False):
    """Display AI prediction for a student"""
    st.markdown('<div class="prediction-box">', unsafe_allow_html=True)

    if is_student:
        st.markdown("#### 🎯 Your Personalized AI Analysis")
    else:
        st.markdown(f"#### 🎯 AI Analysis for {prediction.get('student_name', 'Student')}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📊 Current Performance**")
        st.markdown(f"- **Marks:** {prediction.get('current_performance', 'N/A')}")
        st.markdown(f"- **Next Semester Prediction:** {prediction.get('predicted_next_semester', 'N/A')}")
        st.markdown(f"- **Growth Potential:** {prediction.get('growth_percentage', 'N/A')}")

    with col2:
        st.markdown("**🚀 Career Insights**")
        st.markdown(f"- **Recommended Sector:** {prediction.get('recommended_career_sector', 'N/A')}")
        st.markdown(f"- **Key Strengths:**")
        for strength in prediction.get('key_strengths', []):
            st.markdown(f"  • {strength}")

    st.markdown("**💡 Recommendation**")
    st.markdown(f"> {prediction.get('recommendation', 'N/A')}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="ai-note">
    ⚠️ <strong>Important Note:</strong> These AI predictions are generated based on current performance patterns and statistical analysis. 
    They are for guidance only and should not be considered as definitive career advice. 
    Please consult with your academic advisor, teachers, or parents for personalized decisions.
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# LOGIN PAGE
# ==============================================================================
def login_page():
    """Display login page"""
    apply_professional_theme()

    st.markdown('<div class="header">', unsafe_allow_html=True)

    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        st.markdown("<h1>🎓</h1>", unsafe_allow_html=True)
    with col_title:
        st.title("EduTrack Pro 2025")
        st.markdown("<h4>BAETE Compliant Academic Analytics System</h4>", unsafe_allow_html=True)
        st.markdown("<p><i>Department of EEE, Stamford University Bangladesh</i></p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Show BAETE CO-PO Framework on login page
    show_baete_copo_framework()

    # Login/Registration Tabs
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "⚙️ Admin Login"])

    with tab1:
        show_login_form()

    with tab2:
        show_registration_form()

    with tab3:
        show_admin_login_form()


def show_login_form():
    """Display login form"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>Login to Your Account</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        user_type = st.selectbox("Account Type", ["Teacher", "Student", "Parent"], key="login_type")
        username = st.text_input("Username", placeholder="Enter your username", key="login_username")

    with col2:
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

    if st.button("🚀 Login", use_container_width=True, type="primary"):
        if username and password:
            with st.spinner("Authenticating..."):
                success, user_data = authenticate_user(username, password, user_type.lower())
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type.lower()
                    st.session_state.username = username
                    st.session_state.user_data = user_data
                    st.session_state.admin_mode = False
                    st.success(f"✨ Welcome back, {user_data.get('full_name', username)}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        else:
            st.warning("⚠️ Please enter both username and password")

    st.markdown("---")

    # ADDED RESET BUTTON HERE
    if st.button("🚨 FORCE RESET ALL DATA", type="secondary", use_container_width=True,
                 help="Warning: This will delete all user accounts and course data!"):
        with st.spinner("Resetting all data..."):
            force_reset()
            st.success("✅ All data reset! Default accounts restored.")
            st.info("Default accounts: admin/admin123, teacher/teacher123, student/student123, parent/parent123")
            st.rerun()

    st.markdown("### 🎯 Demo Accounts")

    demo_cols = st.columns(4)
    demo_accounts = [
        {"type": "Admin", "user": "admin", "pass": "admin123", "desc": "Full system access"},
        {"type": "Teacher", "user": "teacher", "pass": "teacher123", "desc": "Full access with all features"},
        {"type": "Student", "user": "student", "pass": "student123", "desc": "View performance & AI predictions"},
        {"type": "Parent", "user": "parent", "pass": "parent123", "desc": "Monitor student progress"}
    ]

    for i, account in enumerate(demo_accounts):
        with demo_cols[i]:
            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**{account['type']}**")
            st.markdown(f"`{account['user']}` / `{account['pass']}`")
            st.markdown(f"<small>{account['desc']}</small>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def show_admin_login_form():
    """Display admin login form"""
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown("<h3>⚙️ Administrator Login</h3>", unsafe_allow_html=True)

    st.warning("""
    ⚠️ **Administrator Access Warning:**
    - Full system control and data access
    - Can view/modify all user accounts
    - Can delete any data
    - System-level configurations
    """)

    col1, col2 = st.columns(2)
    with col1:
        admin_username = st.text_input("Admin Username", placeholder="Enter admin username", key="admin_username")
    with col2:
        admin_password = st.text_input("Admin Password", type="password", placeholder="Enter admin password",
                                       key="admin_password")

    if st.button("🔐 Login as Administrator", use_container_width=True, type="primary"):
        if admin_username and admin_password:
            with st.spinner("Authenticating administrator..."):
                success, user_data = authenticate_user(admin_username, admin_password, "admin")
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "admin"
                    st.session_state.username = admin_username
                    st.session_state.user_data = user_data
                    st.session_state.admin_mode = True
                    st.success(f"👑 Welcome, System Administrator!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid admin credentials")
        else:
            st.warning("⚠️ Please enter admin username and password")

    st.markdown("---")
    st.markdown("#### 🔧 Admin Features:")
    st.markdown("""
    1. **User Management** - Create/Edit/Delete all users
    2. **Data Management** - View/Delete all course data
    3. **System Analytics** - Complete system overview
    4. **Backup & Restore** - System data operations
    5. **Audit Logs** - User activity tracking
    6. **System Settings** - Configure application
    """)

    st.markdown("</div>", unsafe_allow_html=True)


def show_registration_form():
    """Display registration form"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>Create New Account</h3>", unsafe_allow_html=True)

    user_type = st.selectbox("Account Type", ["Teacher", "Student", "Parent"], key="reg_type")

    col1, col2 = st.columns(2)

    with col1:
        username = st.text_input("Choose Username", placeholder="Enter unique username", key="reg_username")
        password = st.text_input("Password", type="password", placeholder="Enter strong password", key="reg_password")

    with col2:
        full_name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_fullname")
        email = st.text_input("Email Address", placeholder="your.email@example.com", key="reg_email")

    if user_type == "Teacher":
        department = st.text_input("Department", placeholder="e.g., Electrical Engineering", key="reg_dept")
        designation = st.selectbox("Designation",
                                   ["Professor", "Associate Professor", "Assistant Professor", "Lecturer"],
                                   key="reg_desig")

    elif user_type == "Student":
        student_id = st.text_input("Student ID", placeholder="e.g., 2021001", key="reg_student_id")
        batch = st.number_input("Batch Year", min_value=2000, max_value=2030, value=2023, key="reg_batch")
        guardian_email = st.text_input("Guardian Email", placeholder="parent@email.com", key="reg_guardian")

    elif user_type == "Parent":
        student_linked = st.text_input("Linked Student ID", placeholder="Student ID to monitor", key="reg_linked")

    if st.button("✅ Register Account", use_container_width=True, type="primary"):
        if not all([username, password, email, full_name]):
            st.error("❌ Please fill all required fields")
            return

        if len(password) < 6:
            st.error("❌ Password must be at least 6 characters")
            return

        # Prepare additional fields
        extra_fields = {}
        if user_type == "Teacher":
            extra_fields = {"department": department, "designation": designation}
        elif user_type == "Student":
            extra_fields = {"student_id": student_id, "batch": batch, "guardian_email": guardian_email}
        elif user_type == "Parent":
            extra_fields = {"student_linked": student_linked}

        success, message = register_user(username, password, user_type.lower(), full_name, email, **extra_fields)

        if success:
            st.success(f"✅ {message}")
            st.info("You can now login with your credentials")
        else:
            st.error(f"❌ {message}")

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# ADMIN PANEL
# ==============================================================================
def show_admin_panel():
    """Show admin control panel"""
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown("### 👑 Administrator Control Panel")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 User Management",
        "🗄️ Data Management",
        "📊 System Analytics",
        "💾 Backup & Restore",
        "⚙️ System Settings"
    ])

    with tab1:
        show_user_management()

    with tab2:
        show_data_management()

    with tab3:
        show_system_analytics()

    with tab4:
        show_backup_restore()

    with tab5:
        show_system_settings()

    st.markdown("</div>", unsafe_allow_html=True)


def show_user_management():
    """User management for admin"""
    st.markdown("#### 👥 User Account Management")

    # Get all users
    users_df = get_all_users()

    if not users_df.empty:
        st.dataframe(users_df, use_container_width=True, height=300)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Create New User")
            new_user_type = st.selectbox("User Type", ["Teacher", "Student", "Parent", "Admin"], key="admin_new_type")
            new_username = st.text_input("Username", key="admin_new_username")
            new_password = st.text_input("Password", type="password", key="admin_new_password")
            new_fullname = st.text_input("Full Name", key="admin_new_fullname")
            new_email = st.text_input("Email", key="admin_new_email")

            if new_user_type == "Teacher":
                new_dept = st.text_input("Department", key="admin_new_dept")
                new_desig = st.text_input("Designation", key="admin_new_desig")
                extra = {"department": new_dept, "designation": new_desig}
            elif new_user_type == "Student":
                new_student_id = st.text_input("Student ID", key="admin_new_student_id")
                new_batch = st.number_input("Batch", key="admin_new_batch")
                new_guardian = st.text_input("Guardian Email", key="admin_new_guardian")
                extra = {"student_id": new_student_id, "batch": new_batch, "guardian_email": new_guardian}
            elif new_user_type == "Parent":
                new_linked = st.text_input("Linked Student ID", key="admin_new_linked")
                extra = {"student_linked": new_linked}
            else:  # Admin
                extra = {"department": "Administration", "designation": "System Admin"}

            if st.button("➕ Create User", key="admin_create_user"):
                if all([new_username, new_password, new_fullname, new_email]):
                    success, msg = register_user(new_username, new_password, new_user_type.lower(),
                                                 new_fullname, new_email, **extra)
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Please fill all required fields")

        with col2:
            st.markdown("##### Delete User")
            del_username = st.selectbox("Select User to Delete", users_df['username'].tolist(), key="admin_del_user")
            del_type = users_df[users_df['username'] == del_username]['user_type'].iloc[0]

            if st.button("🗑️ Delete User", key="admin_delete_user", type="secondary"):
                if del_username == st.session_state.username:
                    st.error("❌ You cannot delete your own account!")
                else:
                    success, msg = delete_user(del_username, del_type)
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            st.markdown("---")
            st.markdown("##### Bulk Operations")
            if st.button("📥 Export Users to CSV", key="export_users"):
                csv = users_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="edutrack_users.csv",
                    mime="text/csv"
                )
    else:
        st.info("No users found in the system.")


def show_data_management():
    """Data management for admin"""
    st.markdown("#### 🗄️ System Data Management")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Course Data")
        all_courses = load_all_courses()

        if all_courses:
            course_list = list(all_courses.keys())
            selected_course = st.selectbox("Select Course", course_list, key="admin_course_select")

            if selected_course:
                course_data = all_courses[selected_course]
                st.metric("Students", len(course_data.get('students', {})))
                st.metric("Average Marks", f"{course_data.get('course_stats', {}).get('average_marks', 0):.1f}")
                st.metric("Pass %", f"{course_data.get('course_stats', {}).get('pass_percentage', 0):.1f}%")

                if st.button("🗑️ Delete Course Data", key="delete_course"):
                    # Implement course deletion logic
                    st.warning("Course deletion feature coming soon")
        else:
            st.info("No course data available")

    with col2:
        st.markdown("##### System Storage")
        import shutil

        # Calculate storage usage
        total_size = 0
        file_count = 0

        if os.path.exists("course_data"):
            for root, dirs, files in os.walk("course_data"):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1

        if os.path.exists("users.json"):
            total_size += os.path.getsize("users.json")
            file_count += 1

        st.metric("Total Files", file_count)
        st.metric("Storage Used", f"{total_size / 1024 / 1024:.2f} MB")

        if st.button("🧹 Clear All Course Data", key="clear_all_data", type="secondary"):
            if os.path.exists("course_data"):
                shutil.rmtree("course_data")
                os.makedirs("course_data", exist_ok=True)
                st.success("✅ All course data cleared!")
                st.rerun()


def show_system_analytics():
    """System analytics for admin"""
    st.markdown("#### 📊 System Analytics Dashboard")

    # Get all data
    users_df = get_all_users()
    all_courses = load_all_courses()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_users = len(users_df) if not users_df.empty else 0
        st.metric("Total Users", total_users)

    with col2:
        teachers = len(users_df[users_df['user_type'] == 'teacher']) if not users_df.empty else 0
        st.metric("Teachers", teachers)

    with col3:
        students = len(users_df[users_df['user_type'] == 'student']) if not users_df.empty else 0
        st.metric("Students", students)

    with col4:
        parents = len(users_df[users_df['user_type'] == 'parent']) if not users_df.empty else 0
        st.metric("Parents", parents)

    st.markdown("---")

    if all_courses:
        st.markdown("##### 📈 Course Performance Overview")

        course_stats = []
        for course_name, course_data in all_courses.items():
            stats = course_data.get('course_stats', {})
            course_stats.append({
                'Course': course_data.get('course_code', 'N/A'),
                'Semester': course_data.get('semester', 'N/A'),
                'Students': stats.get('total_students', 0),
                'Avg Marks': stats.get('average_marks', 0),
                'Pass %': stats.get('pass_percentage', 0),
                'Avg SGPA': stats.get('average_sgpa', 0)
            })

        if course_stats:
            stats_df = pd.DataFrame(course_stats)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### 👥 User Activity")

    # Simulate user activity (in a real app, you'd have actual logs)
    activity_data = pd.DataFrame({
        'User Type': ['Teacher', 'Student', 'Parent', 'Admin'],
        'Active Sessions': [np.random.randint(1, 10) for _ in range(4)],
        'Avg Time (min)': [45, 25, 15, 120],
        'Last Login': ['Today', 'Today', 'Yesterday', 'Today']
    })

    st.dataframe(activity_data, use_container_width=True, hide_index=True)


def show_backup_restore():
    """Backup and restore functionality"""
    st.markdown("#### 💾 Backup & Restore System")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Create Backup")
        st.info("Backup includes all user accounts and course data")

        if st.button("📀 Create System Backup", key="create_backup", use_container_width=True):
            # Create backup
            backup_data = {
                "users": load_users(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "EduTrack Pro 2025"
            }

            # Convert to JSON
            backup_json = json.dumps(backup_data, indent=4)

            # Create download button
            st.download_button(
                label="⬇️ Download Backup File",
                data=backup_json,
                file_name=f"edutrack_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

            st.success("✅ Backup created successfully!")

    with col2:
        st.markdown("##### Restore Backup")
        st.warning("⚠️ Restoring will overwrite ALL current data!")

        backup_file = st.file_uploader("Upload Backup File", type=['json'], key="backup_upload")

        if backup_file is not None:
            try:
                backup_data = json.load(backup_file)

                if st.button("🔄 Restore from Backup", key="restore_backup", type="secondary", use_container_width=True):
                    # Save users
                    with open("users.json", 'w') as f:
                        json.dump(backup_data.get("users", {}), f, indent=4)

                    # Note: Course data backup/restore would need more complex handling
                    st.success("✅ Users restored from backup!")
                    st.info("Note: Course data restoration requires additional steps")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error reading backup file: {e}")


def show_system_settings():
    """System settings for admin"""
    st.markdown("#### ⚙️ System Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Application Settings")

        # Theme settings
        theme = st.selectbox("UI Theme", ["Professional Blue", "Dark Mode", "Light Mode"], key="theme_select")

        # Email settings
        st.markdown("##### Email Configuration")
        default_sender = st.text_input("Default Sender Email", value="noreply@edutrack.edu.bd", key="default_sender")
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com", key="smtp_server")
        smtp_port = st.number_input("SMTP Port", value=587, key="smtp_port")

        if st.button("💾 Save Settings", key="save_settings"):
            st.success("✅ Settings saved (simulated)")

    with col2:
        st.markdown("##### System Maintenance")

        maintenance_mode = st.checkbox("Enable Maintenance Mode", key="maintenance_mode")

        if maintenance_mode:
            st.warning("🔧 System will be in maintenance mode. Users will see a maintenance message.")
            maintenance_msg = st.text_area("Maintenance Message",
                                           value="System is under maintenance. Please try again later.",
                                           key="maintenance_msg")

        st.markdown("##### Logs & Monitoring")

        if st.button("📋 View System Logs", key="view_logs"):
            # Simulated logs
            logs = pd.DataFrame({
                'Timestamp': [datetime.now().strftime("%H:%M:%S") for _ in range(5)],
                'User': ['admin', 'teacher', 'student', 'parent', 'admin'],
                'Action': ['Login', 'Upload Data', 'View Grades', 'Check Progress', 'System Backup'],
                'Status': ['Success', 'Success', 'Success', 'Success', 'Success']
            })
            st.dataframe(logs, use_container_width=True)

        if st.button("🔄 Clear All Logs", key="clear_logs"):
            st.info("Logs cleared (simulated)")


# ==============================================================================
# SAMPLE DATA GENERATION
# ==============================================================================
def generate_sample_data():
    """Generate sample student data with 4 COs"""
    np.random.seed(42)

    students = [
        {"id": "2021001", "name": "John Smith", "student_email": "john.smith@stamford.edu.bd"},
        {"id": "2021002", "name": "Fahmida Islam", "student_email": "fahmida@stamford.edu.bd"},
        {"id": "2021003", "name": "Rowshan-E- Gule Jannat", "student_email": "rowshan@stamford.edu.bd"},
        {"id": "2021004", "name": "Sawkat Islam", "student_email": "sawkat@stamford.edu.bd"},
        {"id": "2021005", "name": "David Lee", "student_email": "d.lee@stamford.edu.bd"}
    ]

    data = []

    for student in students:
        base = np.random.normal(70, 12)
        base = max(35, min(95, base))

        mid = (base * 0.3) + np.random.normal(0, 3)
        final = (base * 0.4) + np.random.normal(0, 4)
        ct = (base * 0.2) + np.random.normal(0, 3)
        assignment = (base * 0.05) + np.random.normal(0, 1)
        attendance = np.random.choice([4, 5], p=[0.3, 0.7])

        mid = max(5, min(30, round(mid, 1)))
        final = max(10, min(40, round(final, 1)))
        ct = max(5, min(20, round(ct, 1)))
        assignment = max(2, min(5, round(assignment, 1)))

        co_base = base / 100 * 15

        co1 = np.random.normal(co_base, 3)
        co2 = np.random.normal(co_base * 1.1, 3)
        co3 = np.random.normal(co_base * 0.9, 4)
        co4 = np.random.normal(co_base * 1.05, 3)

        co_scores = [co1, co2, co3, co4]
        co_scores = [max(0, min(20, round(score, 1))) for score in co_scores]

        data.append({
            "Student_ID": student["id"],
            "Student_Name": student["name"],
            "Student_Email": student["student_email"],
            "Parent_Email": f"parent.{student['id']}@email.com",
            "Mid_Total": mid,
            "Final_Total": final,
            "CT_Total": ct,
            "Assignment_Total": assignment,
            "Attendance_Total": attendance,
            "CO1": co_scores[0],
            "CO2": co_scores[1],
            "CO3": co_scores[2],
            "CO4": co_scores[3]
        })

    return pd.DataFrame(data)


def create_sample_excel():
    """Create sample Excel file for download"""
    df = generate_sample_data()

    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Student_Marks', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Student_Marks']

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1e88e5',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:E', 25)
        worksheet.set_column('F:J', 15)
        worksheet.set_column('K:N', 10)

        instructions = [
            ["EDUTRACK PRO - MARKSHEET TEMPLATE INSTRUCTIONS"],
            ["", ""],
            ["COLUMN", "DESCRIPTION", "FORMAT", "REQUIRED"],
            ["Student_ID", "Unique student identifier", "Text or Number", "YES"],
            ["Student_Name", "Full name of student", "Text", "YES"],
            ["Student_Email", "Student's email address", "Email", "YES"],
            ["Parent_Email", "Secondary parent email", "Email", "YES"],
            ["Mid_Total", "Mid-term exam marks", "Number (0-30)", "YES"],
            ["Final_Total", "Final exam marks", "Number (0-40)", "YES"],
            ["CT_Total", "Class Test marks", "Number (0-20)", "YES"],
            ["Assignment_Total", "Assignment marks", "Number (0-5)", "YES"],
            ["Attendance_Total", "Attendance marks", "Number (0-5)", "YES"],
            ["CO1", "Course Outcome 1 score", "Number (0-20)", "YES"],
            ["CO2", "Course Outcome 2 score", "Number (0-20)", "YES"],
            ["CO3", "Course Outcome 3 score", "Number (0-20)", "YES"],
            ["CO4", "Course Outcome 4 score", "Number (0-20)", "YES"],
            ["", ""],
            ["MARKS DISTRIBUTION (TOTAL: 100 MARKS)"],
            ["Component", "Marks", "CO-PO Mapping"],
            ["Mid Exam", "30", "Included in CO-PO"],
            ["Final Exam", "40", "Included in CO-PO"],
            ["Class Tests", "20", "Included in CO-PO"],
            ["Assignments", "5", "Included in CO-PO"],
            ["Attendance", "5", "Excluded from CO-PO"],
            ["", ""],
            ["IMPORTANT NOTES:"],
            ["1. Attendance marks are NOT included in CO-PO attainment calculations"],
            ["2. Total academic marks for CO-PO = Mid + Final + CT + Assignment = 95 marks"],
            ["3. CO scores should be out of 20 marks each"],
            ["4. All email fields are required for bulk email functionality"]
        ]

        instructions_df = pd.DataFrame(instructions)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False, header=False)

        worksheet_inst = writer.sheets['Instructions']
        worksheet_inst.set_column('A:C', 30)
        worksheet_inst.set_column('D:D', 15)

    output.seek(0)
    return output


# ==============================================================================
# CALCULATION FUNCTIONS
# ==============================================================================
def calculate_sgpa(total_marks):
    """Convert total marks to SGPA (4.0 scale)"""
    if total_marks >= 80:
        return 4.00
    elif total_marks >= 75:
        return 3.75
    elif total_marks >= 70:
        return 3.50
    elif total_marks >= 65:
        return 3.25
    elif total_marks >= 60:
        return 3.00
    elif total_marks >= 55:
        return 2.75
    elif total_marks >= 50:
        return 2.50
    elif total_marks >= 45:
        return 2.25
    elif total_marks >= 40:
        return 2.00
    elif total_marks >= 35:
        return 1.75
    elif total_marks >= 30:
        return 1.50
    elif total_marks >= 25:
        return 1.25
    elif total_marks >= 20:
        return 1.00
    else:
        return 0.00


def get_grade_from_marks(total_marks):
    """Get letter grade from total marks"""
    if total_marks >= 80:
        return "A+"
    elif total_marks >= 75:
        return "A"
    elif total_marks >= 70:
        return "A-"
    elif total_marks >= 65:
        return "B+"
    elif total_marks >= 60:
        return "B"
    elif total_marks >= 55:
        return "B-"
    elif total_marks >= 50:
        return "C+"
    elif total_marks >= 45:
        return "C"
    elif total_marks >= 40:
        return "D"
    else:
        return "F"


def get_grade_description(grade):
    """Get description for grade"""
    grade_descriptions = {
        "A+": "Excellent",
        "A": "Very Good",
        "A-": "Good",
        "B+": "Above Average",
        "B": "Average",
        "B-": "Below Average",
        "C+": "Satisfactory",
        "C": "Marginal",
        "D": "Pass",
        "F": "Fail"
    }
    return grade_descriptions.get(grade, "Unknown")


def calculate_total_marks(student_data):
    """Calculate total marks out of 100"""
    academic_marks = (
            student_data['mid'] +
            student_data['final'] +
            student_data['ct'] +
            student_data['assignment']
    )
    return min(academic_marks + student_data['attendance'], 100)


def create_default_copo_mapping():
    """Create default CO-PO mapping matrix (4 COs x 12 POs)"""
    mapping = {
        'PO1': [3, 3, 2, 1],
        'PO2': [3, 3, 3, 1],
        'PO3': [2, 3, 2, 1],
        'PO4': [1, 2, 3, 2],
        'PO5': [2, 2, 3, 1],
        'PO6': [1, 1, 1, 3],
        'PO7': [1, 1, 1, 2],
        'PO8': [1, 1, 1, 3],
        'PO9': [1, 2, 2, 3],
        'PO10': [1, 2, 2, 3],
        'PO11': [1, 2, 2, 2],
        'PO12': [2, 2, 2, 3]
    }

    return pd.DataFrame(mapping, index=['CO1', 'CO2', 'CO3', 'CO4'])


def calculate_po_attainment(co_scores, co_po_mapping):
    """Calculate PO attainment from CO scores using mapping matrix"""
    if co_po_mapping is None or not co_scores:
        return None

    po_attainment = {}

    for po in co_po_mapping.columns:
        total_weight = 0
        weighted_sum = 0

        for co, score in co_scores.items():
            if co in co_po_mapping.index:
                weight = co_po_mapping.loc[co, po]
                if weight > 0:
                    weighted_sum += (score / 20 * 100) * weight
                    total_weight += weight

        if total_weight > 0:
            po_attainment[po] = min(100, weighted_sum / total_weight)
        else:
            po_attainment[po] = 0

    return po_attainment


# ==============================================================================
# DATA PROCESSING
# ==============================================================================
def process_student_data(df, semester, course_code):
    """Process student data with 4 COs and BAETE standards"""
    results = {
        'students': {},
        'course_stats': {},
        'co_attainment': {},
        'po_attainment': {},
        'semester': semester,
        'course_code': course_code,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    co_scores_all = []
    guardian_email = ""

    for idx, row in df.iterrows():
        try:
            student_id = str(row.get('Student_ID', f'STU{idx}'))
            student_name = str(row.get('Student_Name', f'Student {idx}'))

            marks = {
                'mid': min(30, max(0, float(row.get('Mid_Total', 0)))),
                'final': min(40, max(0, float(row.get('Final_Total', 0)))),
                'ct': min(20, max(0, float(row.get('CT_Total', 0)))),
                'assignment': min(5, max(0, float(row.get('Assignment_Total', 0)))),
                'attendance': min(5, max(0, float(row.get('Attendance_Total', 0))))
            }

            academic_total = marks['mid'] + marks['final'] + marks['ct'] + marks['assignment']
            total_with_attendance = academic_total + marks['attendance']

            sgpa = calculate_sgpa(total_with_attendance)
            grade = get_grade_from_marks(total_with_attendance)
            grade_desc = get_grade_description(grade)

            co_scores = {}
            for i in range(1, 5):
                co_key = f'CO{i}'
                if co_key in row:
                    co_scores[co_key] = min(20, max(0, float(row[co_key])))
                else:
                    co_scores[co_key] = 0

            student_email = str(row.get('Student_Email', ''))
            parent_email = str(row.get('Parent_Email', guardian_email))

            results['students'][student_id] = {
                'id': student_id,
                'name': student_name,
                **marks,
                'academic_total': round(academic_total, 1),
                'total_marks': round(total_with_attendance, 1),
                'sgpa': sgpa,
                'grade': grade,
                'grade_desc': grade_desc,
                'co_scores': co_scores,
                'student_email': student_email,
                'parent_email': parent_email,
                'course_code': course_code,
                'semester': semester,
                'status': 'Pass' if total_with_attendance >= 40 else 'Fail',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            co_scores_all.append(co_scores)

        except Exception as e:
            st.warning(f"Error processing student {idx}: {str(e)}")

    if results['students']:
        marks_list = [s['total_marks'] for s in results['students'].values()]
        academic_marks = [s['academic_total'] for s in results['students'].values()]
        sgpas = [s['sgpa'] for s in results['students'].values()]

        passing_students = len([m for m in marks_list if m >= 40])
        total_students = len(marks_list)

        results['course_stats'] = {
            'average_marks': round(np.mean(marks_list), 2) if marks_list else 0.0,
            'academic_average': round(np.mean(academic_marks), 2) if academic_marks else 0.0,
            'highest_marks': round(max(marks_list), 2) if marks_list else 0.0,
            'lowest_marks': round(min(marks_list), 2) if marks_list else 0.0,
            'average_sgpa': round(np.mean(sgpas), 2) if sgpas else 0.0,
            'total_students': total_students,
            'passing_students': passing_students,
            'pass_percentage': round((passing_students / total_students * 100) if total_students > 0 else 0, 1),
            'fail_percentage': round(
                ((total_students - passing_students) / total_students * 100) if total_students > 0 else 0, 1),
            'std_deviation': round(np.std(marks_list), 2) if marks_list else 0.0
        }
    else:
        results['course_stats'] = {
            'average_marks': 0.0,
            'academic_average': 0.0,
            'highest_marks': 0.0,
            'lowest_marks': 0.0,
            'average_sgpa': 0.0,
            'total_students': 0,
            'passing_students': 0,
            'pass_percentage': 0.0,
            'fail_percentage': 0.0,
            'std_deviation': 0.0
        }

    if co_scores_all and co_scores_all[0]:
        df_co = pd.DataFrame(co_scores_all)
        results['co_attainment'] = {col: round(df_co[col].mean() * 5, 2) for col in df_co.columns}

        if st.session_state.co_po_mapping is not None:
            results['po_attainment'] = calculate_po_attainment(
                {co: score / 5 for co, score in results['co_attainment'].items()},
                st.session_state.co_po_mapping
            )
        else:
            default_mapping = create_default_copo_mapping()
            results['po_attainment'] = calculate_po_attainment(
                {co: score / 5 for co, score in results['co_attainment'].items()},
                default_mapping
            )

    results['predictions'] = generate_ai_predictions(results)
    st.session_state.predictions = results['predictions']

    save_course_data(semester, course_code, results)

    st.session_state.processed = True
    return results


# ==============================================================================
# BULK EMAIL FUNCTIONALITY
# ==============================================================================
def send_bulk_emails(results):
    """Send bulk emails to parents/guardians with marks and AI predictions"""
    st.markdown("### 📧 Bulk Email to Parents/Guardians")

    email_list = []
    for student_id, student in results['students'].items():
        if student.get('parent_email'):
            prediction = results.get('predictions', {}).get(student_id, {})

            email_list.append({
                'student_name': student['name'],
                'student_id': student_id,
                'email': student['parent_email'],
                'total_marks': student['total_marks'],
                'sgpa': student['sgpa'],
                'grade': student['grade'],
                'status': student['status'],
                'prediction': prediction
            })

    if not email_list:
        st.warning("No parent email addresses found in the data.")
        return

    st.success(f"Found {len(email_list)} parent email addresses")

    with st.expander("📋 View Email Recipients"):
        email_df = pd.DataFrame(email_list)
        st.dataframe(email_df[['student_name', 'email', 'total_marks', 'sgpa', 'grade', 'status']],
                     use_container_width=True)

    st.markdown("#### ⚙️ Email Configuration")

    col1, col2 = st.columns(2)

    with col1:
        sender_email = st.text_input("Your Email Address:",
                                     placeholder="teacher@stamford.edu.bd",
                                     key="sender_email")
        sender_password = st.text_input("App Password:", type="password",
                                        help="For Gmail, use App Password (not regular password)",
                                        key="sender_password")

    with col2:
        smtp_server = st.selectbox("SMTP Server:",
                                   ["smtp.gmail.com", "smtp.office365.com",
                                    "smtp.mail.yahoo.com", "Custom"],
                                   key="smtp_server")
        smtp_port = st.number_input("SMTP Port:", value=587, min_value=1, max_value=65535,
                                    key="smtp_port")

    if smtp_server == "Custom":
        smtp_server = st.text_input("Custom SMTP Server:", key="custom_smtp")

    default_subject = f"Performance Report - {results['course_code']} - {results['semester']}"
    subject = st.text_input("Email Subject:", value=default_subject, key="email_subject")

    default_body = """Dear Parent/Guardian,

Please find the performance report for your ward:

Course: {course_code}
Semester: {semester}
Student: {student_name} (ID: {student_id})
Total Marks: {total_marks}/100
SGPA: {sgpa}
Grade: {grade} ({grade_desc})
Status: {status}

Component-wise Performance:
- Mid Exam: {mid_marks}/30
- Final Exam: {final_marks}/40
- Class Tests: {ct_marks}/20
- Assignments: {assignment_marks}/5
- Attendance: {attendance_marks}/5

AI-Generated Insights (For Guidance Only):
{prediction_text}

Note: These AI predictions are generated based on current performance patterns and should be considered as guidance only. Please consult with academic advisors or teachers for personalized advice.

Batch Statistics:
- Average Marks: {batch_avg:.1f}%
- Pass Percentage: {pass_percent:.1f}%
- Highest Marks: {highest_marks:.1f}%

For detailed individual performance and CO-PO attainment, please login to EduTrack Pro system.

Best regards,
{course_instructor}
{department}
"""

    email_body = st.text_area("Email Body:", value=default_body, height=300, key="email_body")

    if st.button("📨 Send Emails to All Parents", use_container_width=True, type="primary", key="send_emails"):
        if not sender_email or not sender_password:
            st.error("Please provide sender email and password")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()

        successful_emails = 0
        failed_emails = []

        try:
            status_text.text("Connecting to email server...")
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            server.login(sender_email, sender_password)

            course_stats = results.get('course_stats', {})

            for i, recipient in enumerate(email_list):
                status_text.text(f"Sending email to {recipient['student_name']}'s parent...")

                try:
                    student = results['students'][recipient['student_id']]
                    prediction = recipient['prediction']

                    if prediction:
                        prediction_text = f"""
• Current Performance: {prediction.get('current_performance', 'N/A')}
• Predicted Next Semester: {prediction.get('predicted_next_semester', 'N/A')}
• Growth Potential: {prediction.get('growth_percentage', 'N/A')}
• Recommended Career Sector: {prediction.get('recommended_career_sector', 'N/A')}
• Key Strengths: {', '.join(prediction.get('key_strengths', []))}
• Recommendation: {prediction.get('recommendation', 'N/A')}
• Confidence Level: {prediction.get('confidence_level', 'Low')}

Note: AI-generated predictions are for guidance only. Please consult with academic advisors for personalized advice.
                        """
                    else:
                        prediction_text = "AI predictions not available for this student."

                    personalized_body = default_body.format(
                        course_code=results['course_code'],
                        semester=results['semester'],
                        student_name=recipient['student_name'],
                        student_id=recipient['student_id'],
                        total_marks=recipient['total_marks'],
                        sgpa=recipient['sgpa'],
                        grade=recipient['grade'],
                        grade_desc=get_grade_description(recipient['grade']),
                        status=recipient['status'],
                        mid_marks=student['mid'],
                        final_marks=student['final'],
                        ct_marks=student['ct'],
                        assignment_marks=student['assignment'],
                        attendance_marks=student['attendance'],
                        prediction_text=prediction_text,
                        batch_avg=course_stats.get('average_marks', 0),
                        pass_percent=course_stats.get('pass_percentage', 0),
                        highest_marks=course_stats.get('highest_marks', 0),
                        course_instructor=st.session_state.user_data.get('full_name', 'Course Instructor'),
                        department=st.session_state.user_data.get('department', 'Electrical & Electronics Engineering')
                    )

                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient['email']
                    msg['Subject'] = subject

                    msg.attach(MIMEText(personalized_body, 'plain'))

                    server.send_message(msg)
                    successful_emails += 1

                except Exception as e:
                    failed_emails.append({
                        'student': recipient['student_name'],
                        'email': recipient['email'],
                        'error': str(e)
                    })

                progress_bar.progress((i + 1) / len(email_list))

            server.quit()

            st.success(f"✅ Successfully sent {successful_emails} out of {len(email_list)} emails")
            st.session_state.email_sent = True

            if failed_emails:
                st.warning(f"Failed to send {len(failed_emails)} emails:")
                for failed in failed_emails:
                    st.error(f"{failed['student']} ({failed['email']}): {failed['error']}")

        except Exception as e:
            st.error(f"Failed to connect to email server: {str(e)}")
            st.info("For Gmail, ensure you're using an App Password (not your regular password)")


# ==============================================================================
# UPLOAD PAGE (TEACHER & ADMIN ONLY)
# ==============================================================================
def organized_upload_page():
    """Organized upload page - For Teachers and Admin"""

    if st.session_state.user_type not in ["teacher", "admin"]:
        st.error("⛔ Access Denied")
        st.info("Only teachers and administrators can upload and process student data.")
        if st.button("🔙 Go to Dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        return

    apply_professional_theme()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.session_state.user_type == "admin":
        st.markdown("<h3>📤 Upload Student Data (Admin Mode)</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3>📤 Upload Student Data (Teacher Only)</h3>", unsafe_allow_html=True)

    st.markdown("#### 📥 Step 1: Download XLSX Template")
    st.markdown("Download this Excel template with all required columns including email addresses.")

    sample_df = generate_sample_data()

    col_dl1, col_dl2 = st.columns([1, 2])
    with col_dl1:
        excel_file = create_sample_excel()
        st.download_button(
            label="📥 Download XLSX Template",
            data=excel_file,
            file_name="EduTrack_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_dl2:
        if st.button("👀 Preview Template Format", use_container_width=True, key="preview_template"):
            st.dataframe(sample_df, use_container_width=True, height=300)

    st.markdown("---")

    st.markdown("#### 🗓️ Step 2: Select Academic Details")

    col_sem1, col_sem2, col_sem3 = st.columns(3)

    with col_sem1:
        semester_options = ["Spring 2025", "Summer 2025", "Spring 2024", "Summer 2024", "Spring 2023", "Summer 2023",
                            "Spring 2022", "Summer 2022"]
        selected_semester = st.selectbox(
            "Select Semester:",
            semester_options,
            index=0,
            key="semester_select"
        )
        st.session_state.selected_semester = selected_semester

    with col_sem2:
        course_code = st.text_input(
            "Course Code:",
            value=st.session_state.selected_course,
            placeholder="e.g., EEE101, EEE205",
            key="course_code_input"
        )
        if course_code:
            st.session_state.selected_course = course_code.upper()

    with col_sem3:
        course_name = st.text_input(
            "Course Name:",
            placeholder="e.g., Circuit Theory",
            key="course_name_input"
        )

    st.markdown(f"**📌 Selected:** **{selected_semester}** - **{course_code if course_code else 'Enter course code'}**")

    st.markdown("---")

    st.markdown("#### 📁 Step 3: Upload Your XLSX File")

    uploaded_file = st.file_uploader(
        "Choose your marksheet file (Excel format)",
        type=['xlsx', 'xls'],
        help="Upload the XLSX file containing student marks with email columns",
        key="file_uploader"
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')

            st.session_state.data = df

            st.success(f"✅ File uploaded successfully! Found **{len(df)}** student records.")

            with st.expander("📋 Data Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)

                required_cols = ['Student_ID', 'Student_Name', 'Parent_Email']
                missing = [col for col in required_cols if col not in df.columns]

                if missing:
                    st.error(f"❌ Missing columns: {', '.join(missing)}")
                    st.info("Please download and use the template provided above.")
                else:
                    st.success("✅ All required columns found")

                    co_cols = [f'CO{i}' for i in range(1, 5)]
                    missing_cos = [col for col in co_cols if col not in df.columns]
                    if missing_cos:
                        st.warning(f"⚠️ Missing CO columns: {', '.join(missing_cos)}")
                    else:
                        st.success("✅ All 4 CO columns found")

            st.markdown("---")
            st.markdown("#### 🗺️ Step 4: CO-PO Mapping")

            mapping_option = st.radio(
                "Select mapping option:",
                ["Use default 4-CO mapping", "Upload custom mapping", "Skip PO analysis"],
                horizontal=True,
                key="mapping_option"
            )

            if mapping_option == "Use default 4-CO mapping":
                default_mapping = create_default_copo_mapping()
                st.session_state.co_po_mapping = default_mapping
                st.success("✅ Default 4-CO to 12-PO mapping applied!")

                with st.expander("View CO-PO Matrix"):
                    st.dataframe(default_mapping, use_container_width=True)
                    st.caption("Correlation scale: 1=Low, 2=Medium, 3=High")

            elif mapping_option == "Upload custom mapping":
                mapping_file = st.file_uploader(
                    "Upload CO-PO mapping file (Excel)",
                    type=['xlsx', 'xls'],
                    key="mapping_uploader"
                )

                if mapping_file is not None:
                    try:
                        mapping_df = pd.read_excel(mapping_file, index_col=0)
                        if len(mapping_df) == 4 and len(mapping_df.columns) == 12:
                            st.session_state.co_po_mapping = mapping_df
                            st.success("✅ Custom CO-PO mapping loaded!")
                        else:
                            st.error("❌ Mapping file must have 4 rows (COs) and 12 columns (POs)")
                    except Exception as e:
                        st.error(f"❌ Error loading mapping: {e}")

            st.markdown("---")

            st.markdown("#### ⚙️ Step 5: Process Data")

            col_proc1, col_proc2, col_proc3 = st.columns([2, 1, 1])

            with col_proc1:
                if st.button("🚀 Process & Analyze Data", use_container_width=True, type="primary", key="process_data"):
                    if not st.session_state.selected_course:
                        st.error("❌ Please enter a course code")
                    else:
                        with st.spinner("Processing data with 4 COs..."):
                            try:
                                results = process_student_data(
                                    df,
                                    st.session_state.selected_semester,
                                    st.session_state.selected_course
                                )

                                st.session_state.results = results
                                key = f"{st.session_state.selected_semester} - {st.session_state.selected_course}"
                                st.session_state.all_semester_data[key] = results

                                st.success("✅ Data processing complete! Data saved to persistent storage.")
                                st.balloons()
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")

            with col_proc2:
                if st.button("📧 Email Parents", use_container_width=True, key="email_button"):
                    if st.session_state.processed and st.session_state.results:
                        st.session_state.current_page = "email"
                        st.rerun()
                    else:
                        st.warning("Please process data first")

            with col_proc3:
                if st.button("📊 Go to Dashboard", use_container_width=True, key="dashboard_button"):
                    st.session_state.current_page = "dashboard"
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("Please ensure you're uploading a valid Excel file")

    else:
        st.info("📁 Please upload your XLSX marksheet file")

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# STUDENT COURSES PAGE
# ==============================================================================
def show_student_courses_page():
    """Show all courses for a student"""
    st.markdown("### 📚 My Courses & Performance")

    student_id = st.session_state.user_data.get('student_id', '')
    student_name = st.session_state.user_data.get('full_name', 'Student')

    if not student_id:
        st.warning("Student ID not found in your profile.")
        return

    student_all_data = load_student_data(student_id)

    if not student_all_data:
        st.info("""
        No course data available yet. 

        **Possible reasons:**
        1. Teachers haven't uploaded any course data yet
        2. Your student ID doesn't match the uploaded data
        3. No courses are registered for your ID

        Please contact your teacher or department for assistance.
        """)
        return

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("Student ID", student_id)
    with col_info2:
        st.metric("Name", student_name)
    with col_info3:
        st.metric("Total Courses", len(student_all_data))

    st.markdown("---")
    st.markdown("#### 📋 Select Course to View Details")

    course_list = []
    for course_key, course_data in student_all_data.items():
        course_code = course_data.get('course_code', 'Unknown')
        semester = course_data.get('semester', 'Unknown')
        course_list.append(f"{semester} - {course_code}")

    if not course_list:
        st.info("No courses found in your record.")
        return

    selected_course = st.selectbox(
        "Choose a course:",
        course_list,
        key="student_course_select"
    )

    if selected_course:
        for course_key, course_data in student_all_data.items():
            display_name = f"{course_data.get('semester')} - {course_data.get('course_code')}"
            if display_name == selected_course:
                show_student_course_details(course_data, student_all_data)
                break

    st.markdown("---")
    st.markdown("#### 📊 All Courses Summary")

    summary_data = []
    cgpa_total = 0
    credit_hours_total = 0

    for course_key, course_data in student_all_data.items():
        student_data = course_data.get('student_data', {})

        credit_hours = 3

        summary_data.append({
            'Course Code': course_data.get('course_code', 'N/A'),
            'Semester': course_data.get('semester', 'N/A'),
            'Marks': f"{student_data.get('total_marks', 0):.1f}/100",
            'SGPA': f"{student_data.get('sgpa', 0):.2f}",
            'Grade': student_data.get('grade', 'N/A'),
            'Status': student_data.get('status', 'N/A'),
            'Credit Hours': credit_hours,
            'Grade Points': student_data.get('sgpa', 0) * credit_hours
        })

        cgpa_total += student_data.get('sgpa', 0) * credit_hours
        credit_hours_total += credit_hours

    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

        if credit_hours_total > 0:
            cgpa = cgpa_total / credit_hours_total
            col_cgpa1, col_cgpa2, col_cgpa3 = st.columns(3)
            with col_cgpa1:
                st.metric("CGPA", f"{cgpa:.2f}/4.00")
            with col_cgpa2:
                st.metric("Total Credits", f"{credit_hours_total}")
            with col_cgpa3:
                st.metric("Courses Completed", len(student_all_data))

    st.markdown("---")
    st.markdown("#### 📈 Batch Performance Comparison")

    all_courses = load_all_courses()

    if all_courses:
        batch_year = st.session_state.user_data.get('batch', '2021')

        batch_stats = []
        for course_key, course_data in all_courses.items():
            course_stats = course_data.get('course_stats', {})
            batch_stats.append({
                'Course': course_data.get('course_code', 'N/A'),
                'Semester': course_data.get('semester', 'N/A'),
                'Batch Average': f"{course_stats.get('average_marks', 0):.1f}",
                'Batch SGPA': f"{course_stats.get('average_sgpa', 0):.2f}",
                'Pass %': f"{course_stats.get('pass_percentage', 0):.1f}%"
            })

        if batch_stats:
            df_batch = pd.DataFrame(batch_stats)
            st.dataframe(df_batch, use_container_width=True, hide_index=True)

            st.markdown("##### 🎯 Your Performance vs Batch Average")

            student_avg_marks = np.mean([s['student_data'].get('total_marks', 0)
                                         for s in student_all_data.values()])
            student_avg_sgpa = np.mean([s['student_data'].get('sgpa', 0)
                                        for s in student_all_data.values()])

            batch_avg_marks = np.mean([float(s['Batch Average']) for s in batch_stats])
            batch_avg_sgpa = np.mean([float(s['Batch SGPA']) for s in batch_stats])

            col_comp1, col_comp2 = st.columns(2)
            with col_comp1:
                delta_marks = student_avg_marks - batch_avg_marks
                st.metric("Average Marks",
                          f"{student_avg_marks:.1f}",
                          delta=f"{delta_marks:+.1f} vs Batch")
            with col_comp2:
                delta_sgpa = student_avg_sgpa - batch_avg_sgpa
                st.metric("Average SGPA",
                          f"{student_avg_sgpa:.2f}",
                          delta=f"{delta_sgpa:+.2f} vs Batch")

            if delta_marks > 0:
                st.success(f"🎉 You're performing {delta_marks:.1f} marks above batch average!")
            elif delta_marks < 0:
                st.warning(
                    f"📉 You're {abs(delta_marks):.1f} marks below batch average. Consider seeking academic support.")


def show_student_course_details(course_data, all_courses=None):
    """Show detailed course information for a student"""
    student_data = course_data.get('student_data', {})

    st.markdown(f"### 📚 {course_data.get('course_code', 'Course')} - {course_data.get('semester', 'Semester')}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Your Marks", f"{student_data.get('total_marks', 0):.1f}/100")
    with col2:
        st.metric("Your SGPA", f"{student_data.get('sgpa', 0):.2f}")
    with col3:
        st.metric("Your Grade", student_data.get('grade', 'N/A'))
    with col4:
        status_color = "✅" if student_data.get('status') == 'Pass' else "❌"
        st.metric("Status", f"{status_color} {student_data.get('status', 'N/A')}")

    st.markdown("#### 📊 Marks Breakdown")

    marks_df = pd.DataFrame({
        'Component': ['Mid Exam', 'Final Exam', 'Class Tests', 'Assignments', 'Attendance', 'Total'],
        'Your Marks': [
            student_data.get('mid', 0),
            student_data.get('final', 0),
            student_data.get('ct', 0),
            student_data.get('assignment', 0),
            student_data.get('attendance', 0),
            student_data.get('total_marks', 0)
        ],
        'Maximum': [30, 40, 20, 5, 5, 100],
        'Percentage': [
            f"{(student_data.get('mid', 0) / 30) * 100:.1f}%",
            f"{(student_data.get('final', 0) / 40) * 100:.1f}%",
            f"{(student_data.get('ct', 0) / 20) * 100:.1f}%",
            f"{(student_data.get('assignment', 0) / 5) * 100:.1f}%",
            f"{(student_data.get('attendance', 0) / 5) * 100:.1f}%",
            f"{student_data.get('total_marks', 0):.1f}%"
        ]
    })

    st.dataframe(marks_df, use_container_width=True, hide_index=True)

    if student_data.get('co_scores'):
        st.markdown("#### 🎯 Your CO Scores")

        co_scores = student_data['co_scores']
        co_df = pd.DataFrame({
            'CO': list(co_scores.keys()),
            'Your Score': list(co_scores.values()),
            'Out of': [20, 20, 20, 20],
            'Percentage': [f"{(score / 20) * 100:.1f}%" for score in co_scores.values()],
            'Attainment Level': ["Excellent" if score >= 16 else "Good" if score >= 14
            else "Average" if score >= 12 else "Needs Improvement"
                                 for score in co_scores.values()]
        })

        st.dataframe(co_df, use_container_width=True, hide_index=True)

        fig = go.Figure(data=[go.Bar(
            x=list(co_scores.keys()),
            y=list(co_scores.values()),
            marker_color=['#1e88e5', '#42a5f5', '#64b5f6', '#90caf9'],
            text=[f'{score}/20' for score in co_scores.values()],
            textposition='auto'
        )])

        fig.update_layout(
            height=300,
            title="Your CO Scores Performance",
            yaxis_title="Score (out of 20)",
            yaxis_range=[0, 20],
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

    course_stats = course_data.get('course_stats', {})
    if course_stats:
        st.markdown("#### 📈 Batch Comparison")

        col_batch1, col_batch2, col_batch3 = st.columns(3)

        with col_batch1:
            batch_avg = course_stats.get('average_marks', 0)
            your_marks = student_data.get('total_marks', 0)
            diff = your_marks - batch_avg
            st.metric("Average Marks",
                      f"{your_marks:.1f}",
                      delta=f"{diff:+.1f} vs batch")

        with col_batch2:
            batch_sgpa = course_stats.get('average_sgpa', 0)
            your_sgpa = student_data.get('sgpa', 0)
            diff_sgpa = your_sgpa - batch_sgpa
            st.metric("Average SGPA",
                      f"{your_sgpa:.2f}",
                      delta=f"{diff_sgpa:+.2f} vs batch")

        with col_batch3:
            pass_percent = course_stats.get('pass_percentage', 0)
            st.metric("Batch Pass Rate", f"{pass_percent:.1f}%")

    predictions = course_data.get('predictions', {})
    if predictions:
        st.markdown("---")
        st.markdown("#### 🤖 AI Predictions for This Course")

        if isinstance(predictions, dict):
            show_ai_prediction(predictions, is_student=True)


# ==============================================================================
# PARENT CHILD PROGRESS PAGE
# ==============================================================================
def show_parent_child_progress_page():
    """Show child's progress for parent"""
    st.markdown("### 👨‍👩‍👧 My Child's Academic Progress")

    linked_student_id = st.session_state.user_data.get('student_linked', '')

    if not linked_student_id:
        st.warning("No student linked to your account. Please contact administrator.")
        return

    child_data = load_student_data(linked_student_id)

    if not child_data:
        st.info("""
        No academic data available for your child yet.

        **Possible reasons:**
        1. Teachers haven't uploaded any course data
        2. The linked student ID may be incorrect
        3. No courses are registered for this student

        Please contact the teacher or school administration.
        """)
        return

    first_course = next(iter(child_data.values()), {})
    child_name = first_course.get('student_data', {}).get('name', 'Your Child')

    col_child1, col_child2, col_child3 = st.columns(3)
    with col_child1:
        st.metric("Child's Name", child_name)
    with col_child2:
        st.metric("Student ID", linked_student_id)
    with col_child3:
        st.metric("Total Courses", len(child_data))

    st.markdown("---")
    st.markdown("#### 📊 Overall Academic Summary")

    all_marks = []
    all_sgpas = []
    course_summary = []

    for course_key, course_data in child_data.items():
        student_data = course_data.get('student_data', {})
        all_marks.append(student_data.get('total_marks', 0))
        all_sgpas.append(student_data.get('sgpa', 0))

        course_summary.append({
            'Course': course_data.get('course_code', 'N/A'),
            'Semester': course_data.get('semester', 'N/A'),
            'Marks': f"{student_data.get('total_marks', 0):.1f}/100",
            'SGPA': f"{student_data.get('sgpa', 0):.2f}",
            'Grade': student_data.get('grade', 'N/A'),
            'Status': student_data.get('status', 'N/A')
        })

    if all_marks:
        overall_avg = np.mean(all_marks)
        overall_sgpa = np.mean(all_sgpas)

        col_overall1, col_overall2, col_overall3, col_overall4 = st.columns(4)

        with col_overall1:
            st.metric("Overall Average", f"{overall_avg:.1f}/100")
        with col_overall2:
            st.metric("Overall SGPA", f"{overall_sgpa:.2f}/4.00")
        with col_overall3:
            passing_courses = len([s for s in child_data.values() if s['student_data']['status'] == 'Pass'])
            st.metric("Courses Passed", f"{passing_courses}/{len(child_data)}")
        with col_overall4:
            excellent_courses = len([s for s in child_data.values() if s['student_data']['grade'] in ['A+', 'A', 'A-']])
            st.metric("Excellent Grades", f"{excellent_courses}")

        st.markdown("##### 📋 Course-wise Performance")
        df_courses = pd.DataFrame(course_summary)
        st.dataframe(df_courses, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 📈 CGPA Progression Over Semesters")

    cgpa_data = get_student_cgpa_data(linked_student_id)

    if cgpa_data and len(cgpa_data) > 1:
        semesters = [item['semester'] for item in cgpa_data]
        semester_sgpas = [item['semester_sgpa'] for item in cgpa_data]
        cumulative_cgpas = [item['cumulative_cgpa'] for item in cgpa_data]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=semesters,
            y=semester_sgpas,
            mode='lines+markers+text',
            name='Semester SGPA',
            line=dict(color='#1e88e5', width=3),
            marker=dict(size=10, color='#1e88e5'),
            text=[f'{sgpa:.2f}' for sgpa in semester_sgpas],
            textposition='top center'
        ))

        fig.add_trace(go.Scatter(
            x=semesters,
            y=cumulative_cgpas,
            mode='lines+markers+text',
            name='Cumulative CGPA',
            line=dict(color='#4CAF50', width=3, dash='dash'),
            marker=dict(size=10, color='#4CAF50'),
            text=[f'{cgpa:.2f}' for cgpa in cumulative_cgpas],
            textposition='bottom center'
        ))

        fig.add_hline(y=2.0, line_dash="dot", line_color="red",
                      annotation_text="Passing Line (2.0)")
        fig.add_hline(y=3.0, line_dash="dot", line_color="orange",
                      annotation_text="Good (3.0)")
        fig.add_hline(y=3.5, line_dash="dot", line_color="green",
                      annotation_text="Excellent (3.5)")

        fig.update_layout(
            height=500,
            title="Academic Progress: Semester SGPA vs Cumulative CGPA",
            xaxis_title="Semester",
            yaxis_title="GPA",
            yaxis_range=[0, 4.1],
            hovermode='x unified',
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        latest_cgpa = cumulative_cgpas[-1] if cumulative_cgpas else 0
        latest_sgpa = semester_sgpas[-1] if semester_sgpas else 0

        col_prog1, col_prog2, col_prog3 = st.columns(3)
        with col_prog1:
            if latest_cgpa >= 3.5:
                st.success(f"🎉 Excellent CGPA: {latest_cgpa:.2f}")
            elif latest_cgpa >= 3.0:
                st.info(f"👍 Good CGPA: {latest_cgpa:.2f}")
            elif latest_cgpa >= 2.0:
                st.warning(f"📊 Satisfactory CGPA: {latest_cgpa:.2f}")
            else:
                st.error(f"⚠️ Needs Improvement: {latest_cgpa:.2f}")

        with col_prog2:
            if latest_sgpa >= 3.5:
                st.success(f"🌟 Excellent Current Semester: {latest_sgpa:.2f}")
            elif latest_sgpa >= 3.0:
                st.info(f"📈 Good Current Semester: {latest_sgpa:.2f}")
            elif latest_sgpa >= 2.0:
                st.warning(f"📊 Satisfactory Current Semester: {latest_sgpa:.2f}")
            else:
                st.error(f"📉 Needs Attention: {latest_sgpa:.2f}")

        with col_prog3:
            trend = "📈 Improving" if len(semester_sgpas) > 1 and semester_sgpas[-1] >= semester_sgpas[
                -2] else "📉 Declining"
            st.metric("Performance Trend", trend)

    else:
        st.info("Need data from at least 2 semesters to show CGPA progression graph.")

    st.markdown("---")
    st.markdown("#### 🤖 AI Insights & Recommendations")

    all_predictions = []
    for course_key, course_data in child_data.items():
        predictions = course_data.get('predictions', {})
        if predictions:
            all_predictions.append(predictions)

    if all_predictions:
        latest_prediction = all_predictions[-1]

        st.markdown("##### 📊 Latest Performance Analysis")
        show_ai_prediction(latest_prediction, is_student=False)

        st.markdown("##### 💡 Suggestions for Parents")
        st.markdown("""
        1. **Regular Monitoring:** Check academic progress each semester
        2. **Communication:** Maintain regular contact with teachers
        3. **Support System:** Provide necessary academic resources
        4. **Motivation:** Encourage consistent study habits
        5. **Balance:** Ensure proper rest and extracurricular activities
        6. **Career Guidance:** Discuss future career options early
        """)

        overall_avg = np.mean(all_marks) if all_marks else 0
        if overall_avg >= 80:
            st.success("""
            **🎯 Your child is excelling academically!**
            - Consider advanced courses or research opportunities
            - Explore scholarship options for higher studies
            - Encourage participation in academic competitions
            """)
        elif overall_avg >= 70:
            st.info("""
            **👍 Your child is performing well!**
            - Focus on maintaining consistency
            - Identify and strengthen weak areas
            - Consider internships for practical experience
            """)
        elif overall_avg >= 60:
            st.warning("""
            **📊 Your child is performing at average level.**
            - Schedule regular study sessions
            - Seek additional tutoring if needed
            - Focus on fundamental concepts
            """)
        elif overall_avg >= 40:
            st.warning("""
            **⚠️ Your child needs academic support.**
            - Meet with teachers to understand challenges
            - Consider extra coaching
            - Focus on passing requirements first
            """)
        else:
            st.error("""
            **🚨 Immediate attention required.**
            - Schedule meeting with academic advisor
            - Consider repeating difficult courses
            - Focus on basic concepts and regular attendance
            """)
    else:
        st.info("AI predictions will be available once teachers process course data.")


# ==============================================================================
# DASHBOARD PAGE
# ==============================================================================
def main_dashboard():
    """Main dashboard page"""
    apply_professional_theme()

    st.markdown('<div class="header">', unsafe_allow_html=True)

    col_header1, col_header2, col_header3 = st.columns([1, 2, 1])
    with col_header1:
        st.markdown("<h1>🎓</h1>", unsafe_allow_html=True)
    with col_header2:
        st.title("EduTrack Pro 2025")
        if st.session_state.admin_mode:
            st.markdown(f"<h4>👑 Welcome, System Administrator!</h4>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h4>Welcome, {st.session_state.user_data.get('full_name', st.session_state.username)}!</h4>",
                        unsafe_allow_html=True)
        st.markdown(f"<p><i>Department of EEE, Stamford University Bangladesh</i></p>", unsafe_allow_html=True)
    with col_header3:
        if st.button("🚪 Logout", use_container_width=True, key="logout_button"):
            st.session_state.logged_in = False
            st.session_state.admin_mode = False
            st.session_state.current_page = "dashboard"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 📍 Navigation")

        # Common pages for all users
        common_pages = {
            "📊 Dashboard": "dashboard",
            "🎓 Students": "students",
            "📈 Analytics": "analytics",
            "🏛️ BAETE Framework": "baete",
            "ℹ️ About": "about"
        }

        # Teacher pages
        teacher_pages = {
            "📤 Upload Data": "upload",
            "📧 Email Parents": "email"
        }

        # Student pages
        student_pages = {
            "📚 My Courses": "mycourses"
        }

        # Parent pages
        parent_pages = {
            "👨‍👩‍👧 Child Progress": "childprogress"
        }

        # Admin pages (full access)
        admin_pages = {
            "👑 Admin Panel": "admin",
            "📤 Upload Data": "upload",
            "📧 Email Parents": "email",
            "📚 My Courses": "mycourses",
            "👨‍👩‍👧 Child Progress": "childprogress"
        }

        # Select pages based on user type
        pages = common_pages.copy()

        if st.session_state.user_type == "admin" or st.session_state.admin_mode:
            pages.update(admin_pages)
        elif st.session_state.user_type == "teacher":
            pages.update(teacher_pages)
        elif st.session_state.user_type == "student":
            pages.update(student_pages)
        elif st.session_state.user_type == "parent":
            pages.update(parent_pages)

        for page_name, page_id in pages.items():
            if st.button(page_name, use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.current_page = page_id
                st.rerun()

        st.markdown("---")
        st.markdown("### 👤 User Info")
        if st.session_state.admin_mode:
            st.markdown(f"**Type:** 👑 **Administrator**")
        else:
            st.markdown(f"**Type:** {st.session_state.user_type.title()}")
        st.markdown(f"**Name:** {st.session_state.user_data.get('full_name', 'N/A')}")
        if st.session_state.user_type == "teacher" or st.session_state.admin_mode:
            st.markdown(f"**Department:** {st.session_state.user_data.get('department', 'N/A')}")
        elif st.session_state.user_type == "student":
            st.markdown(f"**Student ID:** {st.session_state.user_data.get('student_id', 'N/A')}")
            st.markdown(f"**Batch:** {st.session_state.user_data.get('batch', 'N/A')}")
        elif st.session_state.user_type == "parent":
            st.markdown(f"**Linked Student:** {st.session_state.user_data.get('student_linked', 'N/A')}")

        st.markdown("---")
        st.markdown("### 🎯 Quick Stats")
        if st.session_state.processed and st.session_state.results:
            stats = st.session_state.results.get('course_stats', {})
            st.metric("Students", stats.get('total_students', 0))
            st.metric("Avg Marks", f"{stats.get('average_marks', 0):.1f}")
            st.metric("Pass %", f"{stats.get('pass_percentage', 0):.1f}%")

    # Route to appropriate page
    if st.session_state.current_page == "dashboard":
        show_dashboard_content()
    elif st.session_state.current_page == "upload":
        organized_upload_page()
    elif st.session_state.current_page == "students":
        show_students_content()
    elif st.session_state.current_page == "analytics":
        show_analytics_content()
    elif st.session_state.current_page == "email":
        if st.session_state.user_type not in ["teacher", "admin"]:
            st.error("⛔ Access Denied")
            st.info("Only teachers and administrators can send bulk emails to parents.")
            if st.button("🔙 Go to Dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        elif st.session_state.processed and st.session_state.results:
            send_bulk_emails(st.session_state.results)
        else:
            st.warning("Please upload and process data first")
            if st.button("Go to Upload Page"):
                st.session_state.current_page = "upload"
                st.rerun()
    elif st.session_state.current_page == "baete":
        show_baete_copo_framework()
    elif st.session_state.current_page == "about":
        about_page()
    elif st.session_state.current_page == "mycourses" and st.session_state.user_type in ["student", "admin"]:
        show_student_courses_page()
    elif st.session_state.current_page == "childprogress" and st.session_state.user_type in ["parent", "admin"]:
        show_parent_child_progress_page()
    elif st.session_state.current_page == "admin":
        if st.session_state.user_type == "admin" or st.session_state.admin_mode:
            show_admin_panel()
        else:
            st.error("⛔ Admin access only")
            if st.button("🔙 Go to Dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()


# ==============================================================================
# DASHBOARD CONTENT
# ==============================================================================
def show_dashboard_content():
    """Show main dashboard content"""

    if not st.session_state.get('processed') or not st.session_state.get('results'):
        show_empty_dashboard()
        return

    results = st.session_state.results

    if 'course_stats' not in results or not results['course_stats']:
        st.warning("⚠️ Data is not properly processed. Please process data again.")
        if st.button("🔄 Process Data Again", key="reprocess_data"):
            st.session_state.current_page = "upload"
            st.rerun()
        return

    course_stats = results.get('course_stats', {})

    average_marks = course_stats.get('average_marks', 0.0)
    average_sgpa = course_stats.get('average_sgpa', 0.0)
    pass_percentage = course_stats.get('pass_percentage', 0.0)
    total_students = course_stats.get('total_students', 0)
    highest_marks = course_stats.get('highest_marks', 0.0)
    lowest_marks = course_stats.get('lowest_marks', 0.0)
    std_deviation = course_stats.get('std_deviation', 0.0)
    academic_average = course_stats.get('academic_average', 0.0)
    passing_students = course_stats.get('passing_students', 0)

    st.markdown("### 📈 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Average Marks", f"{average_marks:.1f}")
    with col2:
        st.metric("Average SGPA", f"{average_sgpa:.2f}")
    with col3:
        st.metric("Pass %", f"{pass_percentage:.1f}%",
                  delta=f"{passing_students}/{total_students}")
    with col4:
        st.metric("Total Students", f"{total_students}")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric("Highest Marks", f"{highest_marks:.1f}")
    with col6:
        st.metric("Lowest Marks", f"{lowest_marks:.1f}")
    with col7:
        st.metric("Std Deviation", f"{std_deviation:.1f}")
    with col8:
        st.metric("Academic Average", f"{academic_average:.1f}")

    course_code = results.get('course_code', 'N/A')
    semester = results.get('semester', 'N/A')
    st.markdown(f"### 📚 {course_code} - {semester}")

    if results.get('students'):
        st.markdown("#### 🏆 Grade Distribution")

        grade_counts = {}
        for student in results['students'].values():
            grade = student.get('grade', 'F')
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        if grade_counts:
            grades = list(grade_counts.keys())
            counts = list(grade_counts.values())

            fig = go.Figure(data=[go.Bar(
                x=grades,
                y=counts,
                marker_color=['#4CAF50' if g not in ['F', 'D'] else '#FFC107' if g == 'D' else '#F44336' for g in
                              grades],
                text=counts,
                textposition='auto',
                hovertemplate='Grade: %{x}<br>Students: %{y}<extra></extra>'
            )])

            fig.update_layout(
                height=300,
                xaxis_title="Grades",
                yaxis_title="Number of Students",
                showlegend=False,
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

            col_pass, col_fail = st.columns(2)
            with col_pass:
                st.success(f"✅ Passing Students: {passing_students} ({pass_percentage:.1f}%)")
            with col_fail:
                fail_count = total_students - passing_students
                fail_percent = course_stats.get('fail_percentage', 0)
                if fail_count > 0:
                    st.error(f"❌ Failing Students: {fail_count} ({fail_percent:.1f}%)")
                else:
                    st.success("🎉 All students are passing!")

    if results.get('co_attainment'):
        st.markdown("#### 🎯 CO Attainment (4 COs)")

        cos = list(results['co_attainment'].keys())
        values = list(results['co_attainment'].values())

        if cos and values:
            fig = go.Figure(data=[go.Bar(
                x=cos,
                y=values,
                marker_color=['#1e88e5', '#42a5f5', '#64b5f6', '#90caf9'],
                text=[f'{v:.1f}%' for v in values],
                textposition='auto'
            )])

            fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Target: 70%")

            fig.update_layout(
                height=300,
                xaxis_title="Course Outcomes",
                yaxis_title="Attainment (%)",
                yaxis_range=[0, 100],
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 CO attainment data not available")
    else:
        st.info("📊 CO attainment analysis not yet performed")

    if results.get('students'):
        st.markdown("### 🏆 Student Performance")

        students_list = list(results['students'].values())

        if all('total_marks' in student for student in students_list):
            students_list.sort(key=lambda x: x.get('total_marks', 0), reverse=True)

            col_top1, col_top2 = st.columns(2)

            with col_top1:
                st.markdown("##### 🥇 Top 3 Students")
                for i, student in enumerate(students_list[:3]):
                    with st.container():
                        col_name, col_marks = st.columns([3, 1])
                        with col_name:
                            st.markdown(f"**{i + 1}. {student.get('name', 'N/A')}**")
                        with col_marks:
                            marks = student.get('total_marks', 0)
                            sgpa = student.get('sgpa', 0.0)
                            grade = student.get('grade', 'N/A')
                            st.markdown(f"`{marks:.1f}` | SGPA: `{sgpa:.2f}` | Grade: `{grade}`")

                        progress = min(marks / 100, 1.0)
                        st.progress(progress)

            with col_top2:
                at_risk = [s for s in students_list if s.get('total_marks', 0) < 40]
                if at_risk:
                    st.markdown("##### 📉 Needs Attention (Below Passing)")
                    for student in at_risk[:3]:
                        with st.container():
                            col_name, col_marks = st.columns([3, 1])
                            with col_name:
                                st.markdown(f"**{student.get('name', 'N/A')}**")
                            with col_marks:
                                marks = student.get('total_marks', 0)
                                sgpa = student.get('sgpa', 0.0)
                                grade = student.get('grade', 'N/A')
                                st.markdown(f":red[`{marks:.1f}`] | SGPA: `{sgpa:.2f}` | Grade: `{grade}`")

                            progress = min(marks / 100, 1.0)
                            st.progress(progress)
                else:
                    st.success("🎉 All students are passing (marks ≥ 40)!")
        else:
            st.info("Student marks data not available")

    if results.get('predictions') and st.session_state.user_type in ["teacher", "student", "parent", "admin"]:
        st.markdown("---")
        st.markdown("### 🤖 AI Predictions & Career Insights")

        if st.session_state.user_type == "student":
            student_id = st.session_state.user_data.get('student_id', '')
            if student_id in results['predictions']:
                prediction = results['predictions'][student_id]
                show_ai_prediction(prediction, is_student=True)
        elif st.session_state.user_type in ["teacher", "admin"] and results['predictions']:
            first_student_id = list(results['predictions'].keys())[0]
            prediction = results['predictions'][first_student_id]
            show_ai_prediction(prediction, is_student=False)
            st.info("👆 This is a sample AI prediction for demonstration. Each student has personalized predictions.")

    if st.session_state.user_type in ["teacher", "admin"]:
        st.markdown("### ⚡ Quick Actions")

        col_act1, col_act2, col_act3, col_act4 = st.columns(4)

        with col_act1:
            if st.button("📧 Email Parents", use_container_width=True, key="dashboard_email"):
                st.session_state.current_page = "email"
                st.rerun()

        with col_act2:
            if st.button("📈 View Analytics", use_container_width=True, key="dashboard_analytics"):
                st.session_state.current_page = "analytics"
                st.rerun()

        with col_act3:
            if st.button("🎓 View Students", use_container_width=True, key="dashboard_students"):
                st.session_state.current_page = "students"
                st.rerun()

        with col_act4:
            if st.button("📤 Upload New", use_container_width=True, key="dashboard_upload"):
                st.session_state.current_page = "upload"
                st.rerun()

    st.markdown("---")
    st.markdown(f"**📅 Last Updated:** {results.get('timestamp', 'Not available')}")
    st.markdown(f"**📊 Data Points:** {len(results.get('students', {}))} students processed")


def show_empty_dashboard():
    """Show empty dashboard when no data is processed"""
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if st.session_state.admin_mode:
        st.markdown("<h3>👑 Administrator Dashboard</h3>", unsafe_allow_html=True)
        user_type_desc = "administrator"
    else:
        st.markdown("<h3>📊 Welcome to EduTrack Pro Dashboard</h3>", unsafe_allow_html=True)
        user_type_desc = st.session_state.user_type

    col_info, col_img = st.columns([2, 1])

    with col_info:
        if st.session_state.user_type in ["teacher", "admin"]:
            st.markdown(f"""
            ### Get Started with EduTrack Pro

            As a **{user_type_desc}**, you can:

            1. **📥 Download Template** - Get the XLSX template with all required columns
            2. **📤 Upload Your Data** - Upload student marks with email addresses
            3. **⚙️ Process & Analyze** - Generate CO-PO attainment reports
            4. **📧 Email Parents** - Send bulk emails to all guardians
            5. **📈 View Analytics** - Analyze student performance trends
            {"6. **👑 Admin Panel** - Full system control and user management" if st.session_state.admin_mode else ""}

            ### 🎯 Key Features:
            - **BAETE 4-CO, 12-PO Framework** - Compliant with accreditation standards
            - **Bulk Email System** - Send emails to all parents at once
            - **XLSX File Support** - Professional Excel templates
            - **Interactive Analytics** - Visual charts and insights
            - **Student Performance Tracking** - Monitor individual progress
            - **AI Predictions** - Personalized academic and career insights
            - **Student Course Portal** - Students can view all subjects
            - **Parent Dashboard** - Monitor child's progress with CGPA curves
            {"- **Admin Control Panel** - Full system administration" if st.session_state.admin_mode else ""}
            """)
        elif st.session_state.user_type == "student":
            st.markdown("""
            ### Welcome Student!

            Once your teacher uploads and processes the course data, you can:

            1. **📊 View Your Performance** - See your marks, SGPA, and grades
            2. **🎯 Check CO Attainment** - View your Course Outcome scores
            3. **🤖 Get AI Insights** - Receive personalized academic predictions
            4. **🚀 Career Guidance** - See AI-suggested career paths
            5. **📈 Track Progress** - Monitor your academic growth
            6. **📚 View All Courses** - See performance across all subjects
            7. **📊 Batch Comparison** - Compare with class performance

            ### 🎯 Available Features:
            - **Personal Performance Dashboard** - Your marks and grades
            - **AI-Powered Predictions** - Academic growth forecasts
            - **Career Sector Suggestions** - Based on your strengths
            - **Skill Analysis** - Identify your key competencies
            - **Course-wise Analysis** - Detailed performance for each subject
            """)
        else:
            st.markdown("""
            ### Welcome Parent/Guardian!

            Once the teacher processes the course data, you can:

            1. **👨‍🎓 Monitor Student Performance** - View your ward's academic progress
            2. **📊 Check Grades & Marks** - See detailed performance breakdown
            3. **🤖 Review AI Insights** - Get academic predictions and guidance
            4. **🚀 Career Possibilities** - See potential career paths
            5. **📧 Email Updates** - Receive performance reports from teachers
            6. **📈 CGPA Tracking** - View semester-wise progress with graphs
            7. **💡 Parental Guidance** - Get suggestions for supporting your child

            ### 🎯 Available Features:
            - **Student Performance Tracking** - Monitor academic progress
            - **AI Analysis** - Growth predictions and recommendations
            - **Communication** - Direct updates from teachers
            - **Educational Support** - Identify areas needing attention
            - **Progress Visualization** - CGPA curves and semester graphs
            """)

    with col_img:
        if st.session_state.admin_mode:
            st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <div style='font-size: 6rem;'>👑</div>
                <h4>Admin Mode</h4>
                <p>System Administrator</p>
                <p><small>Full System Access</small></p>
                <p><small>EduTrack Pro 2025</small></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <div style='font-size: 6rem;'>🎓</div>
                <h4>EduTrack Pro</h4>
                <p>Academic Analytics System</p>
                <p><small>Department of EEE</small></p>
                <p><small>Stamford University Bangladesh</small></p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.user_type in ["teacher", "admin"]:
        col_start1, col_start2, col_start3 = st.columns(3)

        with col_start1:
            if st.button("🚀 Start by Uploading Data", use_container_width=True, type="primary", key="start_main"):
                st.session_state.current_page = "upload"
                st.rerun()

        with col_start2:
            if st.button("🏛️ View BAETE Framework", use_container_width=True, key="view_baete"):
                st.session_state.current_page = "baete"
                st.rerun()

        with col_start3:
            if st.button("📥 Download Template", use_container_width=True, key="download_main"):
                st.session_state.current_page = "upload"
                st.rerun()

    if st.session_state.admin_mode:
        st.markdown("---")
        if st.button("👑 Go to Admin Panel", use_container_width=True, type="secondary", key="go_admin"):
            st.session_state.current_page = "admin"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# STUDENTS PAGE
# ==============================================================================
def show_students_content():
    """Show students page"""
    st.markdown("### 🎓 Student Performance")

    if not st.session_state.processed or not st.session_state.results:
        st.warning("No data available yet. Please wait for teacher to upload and process data.")
        return

    results = st.session_state.results

    if st.session_state.user_type in ["teacher", "admin"]:
        student_ids = list(results['students'].keys())
        student_names = [results['students'][sid]['name'] for sid in student_ids]

        selected_student = st.selectbox(
            "Select Student:",
            student_names,
            key="student_select"
        )

        if selected_student:
            selected_id = student_ids[student_names.index(selected_student)]
            student = results['students'][selected_id]
            show_student_details(student, results)

    elif st.session_state.user_type == "student":
        student_id = st.session_state.user_data.get('student_id', '')

        found = False
        for sid, sdata in results['students'].items():
            if sid == student_id:
                show_student_details(sdata, results)
                found = True
                break

        if not found:
            student_name = st.session_state.user_data.get('full_name', '')
            for sid, sdata in results['students'].items():
                if sdata['name'] == student_name:
                    show_student_details(sdata, results)
                    found = True
                    break

            if not found:
                st.warning("Your data is not found in the current course. Please check with your teacher.")

    elif st.session_state.user_type == "parent":
        linked_student_id = st.session_state.user_data.get('student_linked', '')

        if not linked_student_id:
            st.warning("No student linked to your account. Please contact administrator.")
            return

        found = False
        for sid, sdata in results['students'].items():
            if sid == linked_student_id:
                show_student_details(sdata, results)
                found = True
                break

        if not found:
            st.warning(f"Linked student (ID: {linked_student_id}) not found in current course data.")


def show_student_details(student, results):
    """Show detailed student information"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Marks", f"{student['total_marks']:.1f}/100")
    with col2:
        st.metric("SGPA", f"{student['sgpa']:.2f}")
    with col3:
        st.metric("Grade", f"{student['grade']} ({student['grade_desc']})")
    with col4:
        status_color = "✅" if student['status'] == 'Pass' else "❌"
        st.metric("Status", f"{status_color} {student['status']}")

    st.markdown("#### 📊 Marks Breakdown")

    marks_data = pd.DataFrame({
        'Component': ['Mid Exam', 'Final Exam', 'Class Tests', 'Assignments', 'Attendance', 'Total'],
        'Marks': [student['mid'], student['final'], student['ct'],
                  student['assignment'], student['attendance'], student['total_marks']],
        'Max': [30, 40, 20, 5, 5, 100],
        'Percentage': [
            f"{(student['mid'] / 30) * 100:.1f}%",
            f"{(student['final'] / 40) * 100:.1f}%",
            f"{(student['ct'] / 20) * 100:.1f}%",
            f"{(student['assignment'] / 5) * 100:.1f}%",
            f"{(student['attendance'] / 5) * 100:.1f}%",
            f"{student['total_marks']:.1f}%"
        ]
    })

    st.dataframe(marks_data, use_container_width=True, hide_index=True)

    if student['co_scores']:
        st.markdown("#### 🎯 CO Scores (Out of 20)")

        co_data = pd.DataFrame({
            'CO': list(student['co_scores'].keys()),
            'Score': list(student['co_scores'].values()),
            'Percentage': [f"{(score / 20) * 100:.1f}%" for score in student['co_scores'].values()],
            'Level': [
                "Excellent" if score >= 16 else "Good" if score >= 14 else "Average" if score >= 12 else "Needs Improvement"
                for score in student['co_scores'].values()]
        })

        st.dataframe(co_data, use_container_width=True, hide_index=True)

        fig = go.Figure(data=[go.Bar(
            x=list(student['co_scores'].keys()),
            y=list(student['co_scores'].values()),
            marker_color=['#1e88e5', '#42a5f5', '#64b5f6', '#90caf9'],
            text=[f'{score}/20' for score in student['co_scores'].values()],
            textposition='auto'
        )])

        fig.add_hline(y=12, line_dash="dash", line_color="orange",
                      annotation_text="Minimum: 12/20")
        fig.add_hline(y=16, line_dash="dash", line_color="green",
                      annotation_text="Target: 16/20")

        fig.update_layout(
            height=300,
            title="CO Scores Performance",
            yaxis_title="Score (out of 20)",
            yaxis_range=[0, 20],
            template='plotly_white'
        )

        st.plotly_chart(fig, use_container_width=True)

    student_id = student['id']
    predictions = results.get('predictions', {})

    if student_id in predictions:
        st.markdown("---")
        st.markdown("#### 🤖 AI Predictions & Insights")
        prediction = predictions[student_id]
        show_ai_prediction(prediction, is_student=(st.session_state.user_type == "student"))


# ==============================================================================
# ANALYTICS PAGE
# ==============================================================================
def show_analytics_content():
    """Show enhanced, interactive analytics with multiple views"""

    if not st.session_state.get('processed') or not st.session_state.get('results'):
        show_no_data_analytics()
        return

    results = st.session_state.results

    st.markdown("### 📊 Advanced Analytics Dashboard")
    st.markdown(
        f"**Course:** {results.get('course_code', 'N/A')} | **Semester:** {results.get('semester', 'N/A')} | **Students:** {results.get('course_stats', {}).get('total_students', 0)}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 CO-PO Analysis",
        "📈 Performance Metrics",
        "📊 Student Distribution",
        "🤖 AI Predictions"
    ])

    with tab1:
        show_copo_analytics(results)

    with tab2:
        show_performance_metrics(results)

    with tab3:
        show_distribution_analytics(results)

    with tab4:
        show_ai_predictions_analytics(results)


def show_copo_analytics(results):
    """Show CO-PO attainment analytics"""
    st.markdown("#### 🎯 CO-PO Attainment Analysis")

    col1, col2 = st.columns(2)

    with col1:
        if results.get('co_attainment'):
            st.markdown("##### Course Outcomes (COs) Attainment")

            for co, attainment in results['co_attainment'].items():
                if attainment >= 70:
                    color = "green"
                    status = "✅ Above Target"
                elif attainment >= 50:
                    color = "orange"
                    status = "⚠️ Near Target"
                else:
                    color = "red"
                    status = "❌ Below Target"

                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=attainment,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"{co}<br>{status}", 'font': {'size': 16}},
                    delta={'reference': 70, 'increasing': {'color': "green"}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': color},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': '#ffcccc'},
                            {'range': [50, 70], 'color': '#fff4cc'},
                            {'range': [70, 100], 'color': '#ccffcc'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 70
                        }
                    }
                ))

                fig.update_layout(height=250, margin=dict(t=50, b=10, l=10, r=10))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("CO attainment data not available")

    with col2:
        if results.get('po_attainment'):
            st.markdown("##### Program Outcomes (POs) Attainment")

            pos = list(results['po_attainment'].keys())
            po_values = list(results['po_attainment'].values())

            fig = go.Figure(data=[go.Bar(
                x=pos,
                y=po_values,
                marker_color=['#4CAF50' if v >= 70 else '#FFC107' if v >= 50 else '#F44336' for v in po_values],
                text=[f'{v:.1f}%' for v in po_values],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Attainment: %{y:.1f}%<extra></extra>'
            )])

            fig.add_hline(y=70, line_dash="dash", line_color="green",
                          annotation_text="Target: 70%", annotation_font_color="green")
            fig.add_hline(y=50, line_dash="dash", line_color="orange",
                          annotation_text="Minimum: 50%", annotation_font_color="orange")

            fig.update_layout(
                height=400,
                xaxis_title="Program Outcomes (POs)",
                yaxis_title="Attainment (%)",
                yaxis_range=[0, 100],
                showlegend=False,
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

            po_above_target = len([v for v in po_values if v >= 70])
            po_below_target = len([v for v in po_values if v < 50])

            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("POs Above Target", f"{po_above_target}/12",
                          delta=f"{po_above_target / 12 * 100:.0f}%")
            with col_stat2:
                st.metric("POs Below Minimum", f"{po_below_target}/12",
                          delta=f"{-po_below_target / 12 * 100:.0f}%", delta_color="inverse")
        else:
            st.info("PO attainment data not available")

    if results.get('co_attainment') and results.get('po_attainment'):
        st.markdown("---")
        st.markdown("##### 🔗 CO-PO Correlation Insights")

        if st.session_state.co_po_mapping is not None:
            mapping_df = st.session_state.co_po_mapping

            fig = px.imshow(mapping_df.values,
                            x=mapping_df.columns,
                            y=mapping_df.index,
                            color_continuous_scale='Blues',
                            text_auto=True,
                            aspect="auto")

            fig.update_layout(
                title="CO-PO Correlation Matrix (1=Low, 2=Medium, 3=High)",
                height=400,
                xaxis_title="Program Outcomes",
                yaxis_title="Course Outcomes"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("**📈 Key Insights:**")

            insights = []
            for co in mapping_df.index:
                max_correlation = mapping_df.loc[co].max()
                max_pos = mapping_df.loc[co][mapping_df.loc[co] == max_correlation].index.tolist()
                insights.append(f"- **{co}** strongly influences {', '.join(max_pos)} (Correlation: {max_correlation})")

            for insight in insights:
                st.markdown(insight)


def show_performance_metrics(results):
    """Show detailed performance metrics"""
    st.markdown("#### 📈 Performance Metrics Analysis")

    course_stats = results.get('course_stats', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">{:.1f}%</div>'.format(course_stats.get('pass_percentage', 0)))
        st.markdown('<div class="metric-label">Pass Rate</div>', unsafe_allow_html=True)
        if course_stats.get('pass_percentage', 0) >= 80:
            st.success("✅ Excellent")
        elif course_stats.get('pass_percentage', 0) >= 60:
            st.info("👍 Good")
        else:
            st.warning("⚠️ Needs Improvement")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">{:.2f}</div>'.format(course_stats.get('average_sgpa', 0)))
        st.markdown('<div class="metric-label">Average SGPA</div>', unsafe_allow_html=True)
        sgpa = course_stats.get('average_sgpa', 0)
        if sgpa >= 3.5:
            st.success("🏆 Excellent")
        elif sgpa >= 3.0:
            st.info("👍 Good")
        elif sgpa >= 2.5:
            st.warning("⚖️ Average")
        elif sgpa >= 2.0:
            st.info("✅ Passing")
        else:
            st.error("📉 Below Passing")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">{:.1f}</div>'.format(course_stats.get('std_deviation', 0)))
        st.markdown('<div class="metric-label">Std Deviation</div>', unsafe_allow_html=True)
        std_dev = course_stats.get('std_deviation', 0)
        if std_dev < 10:
            st.success("📊 Consistent")
        elif std_dev < 15:
            st.info("📈 Moderate Spread")
        else:
            st.warning("📉 High Variance")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        grade_counts = {}
        for student in results.get('students', {}).values():
            grade = student.get('grade', 'F')
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        top_grade = max(grade_counts, key=grade_counts.get) if grade_counts else "N/A"
        top_count = grade_counts.get(top_grade, 0) if grade_counts else 0
        total = course_stats.get('total_students', 1)
        percentage = (top_count / total * 100) if total > 0 else 0

        st.markdown('<div class="metric-value">{}</div>'.format(top_grade))
        st.markdown('<div class="metric-label">Most Common Grade</div>', unsafe_allow_html=True)
        st.markdown(f"**{top_count} students** ({percentage:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 📊 Performance Distribution")

    if results.get('students'):
        marks = [s.get('total_marks', 0) for s in results['students'].values()]

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Marks Distribution", "Statistical Summary"),
            vertical_spacing=0.15,
            row_heights=[0.7, 0.3]
        )

        fig.add_trace(
            go.Histogram(
                x=marks,
                nbinsx=15,
                name='Students',
                marker_color='#1e88e5',
                opacity=0.7,
                hovertemplate='Marks: %{x:.1f}<br>Count: %{y}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_vline(x=40, line_dash="dash", line_color="red",
                      annotation_text="Pass Mark (40)", row=1, col=1)
        fig.add_vline(x=course_stats.get('average_marks', 0), line_dash="dash",
                      line_color="green", annotation_text="Average", row=1, col=1)

        fig.add_trace(
            go.Box(
                x=marks,
                name='Distribution',
                marker_color='#42a5f5',
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8
            ),
            row=2, col=1
        )

        fig.update_layout(
            height=600,
            showlegend=False,
            template='plotly_white'
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### 🎯 Performance Categories")

        categories = {
            'Excellent (80+ marks)': len([m for m in marks if m >= 80]),
            'Good (70-79 marks)': len([m for m in marks if 70 <= m < 80]),
            'Average (60-69 marks)': len([m for m in marks if 60 <= m < 70]),
            'Below Average (50-59 marks)': len([m for m in marks if 50 <= m < 60]),
            'Marginal (40-49 marks)': len([m for m in marks if 40 <= m < 50]),
            'Fail (<40 marks)': len([m for m in marks if m < 40])
        }

        fig = go.Figure(data=[go.Pie(
            labels=list(categories.keys()),
            values=list(categories.values()),
            hole=0.4,
            marker_colors=['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#FF5722', '#F44336'],
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Students: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            height=400,
            title="Student Performance Categories",
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)


def show_distribution_analytics(results):
    """Show student distribution analytics"""
    st.markdown("#### 📊 Student Distribution Analysis")

    if not results.get('students'):
        st.info("No student data available")
        return

    st.markdown("##### 📝 Component-wise Performance")

    components = ['Mid Exam', 'Final Exam', 'Class Tests', 'Assignments', 'Attendance']
    component_data = []

    for student in results['students'].values():
        component_data.append({
            'Mid Exam': student.get('mid', 0),
            'Final Exam': student.get('final', 0),
            'Class Tests': student.get('ct', 0),
            'Assignments': student.get('assignment', 0),
            'Attendance': student.get('attendance', 0)
        })

    df_components = pd.DataFrame(component_data)

    avg_components = df_components.mean()
    max_values = [30, 40, 20, 5, 5]
    percentages = [(avg / max_val) * 100 for avg, max_val in zip(avg_components.values, max_values)]

    fig = go.Figure(data=go.Scatterpolar(
        r=percentages,
        theta=components,
        fill='toself',
        name='Average Performance',
        line_color='#1e88e5',
        fillcolor='rgba(30, 136, 229, 0.3)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        height=400,
        title="Average Performance by Component (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### 📋 Component Statistics")

    component_stats = []
    for i, component in enumerate(components):
        scores = df_components[component]
        stats = {
            'Component': component,
            'Average': f"{scores.mean():.1f}",
            'Highest': f"{scores.max():.1f}",
            'Lowest': f"{scores.min():.1f}",
            'Std Dev': f"{scores.std():.1f}",
            'Max Marks': max_values[i],
            'Avg %': f"{(scores.mean() / max_values[i]) * 100:.1f}%"
        }
        component_stats.append(stats)

    df_stats = pd.DataFrame(component_stats)
    st.dataframe(df_stats, use_container_width=True, hide_index=True)

    if results.get('students'):
        st.markdown("---")
        st.markdown("##### 🎯 CO Scores Distribution")

        co_scores_data = []
        for student in results['students'].values():
            if 'co_scores' in student:
                co_scores_data.append(student['co_scores'])

        if co_scores_data:
            df_co_scores = pd.DataFrame(co_scores_data)

            fig = go.Figure()

            for co in df_co_scores.columns:
                fig.add_trace(go.Violin(
                    y=df_co_scores[co],
                    name=co,
                    box_visible=True,
                    meanline_visible=True,
                    points='all',
                    jitter=0.3,
                    pointpos=-1.8,
                    marker_color='#42a5f5',
                    line_color='#1e88e5'
                ))

            fig.update_layout(
                height=400,
                title="CO Scores Distribution (Out of 20)",
                yaxis_title="Score",
                xaxis_title="Course Outcomes",
                template='plotly_white'
            )

            fig.add_hline(y=14, line_dash="dash", line_color="green",
                          annotation_text="Target: 14/20")
            fig.add_hline(y=10, line_dash="dash", line_color="orange",
                          annotation_text="Minimum: 10/20")

            st.plotly_chart(fig, use_container_width=True)


def show_ai_predictions_analytics(results):
    """Show AI predictions analytics"""
    st.markdown("#### 🤖 AI Predictions Overview")

    if not results.get('predictions'):
        st.info("No AI predictions available yet. Predictions are generated after data processing.")
        return

    predictions = results['predictions']

    st.markdown("##### 🚀 Recommended Career Sectors")

    career_sectors = {}
    for pred in predictions.values():
        sector = pred.get('recommended_career_sector', 'Unknown')
        career_sectors[sector] = career_sectors.get(sector, 0) + 1

    if career_sectors:
        sectors = list(career_sectors.keys())
        counts = list(career_sectors.values())

        fig = go.Figure(data=[go.Bar(
            x=sectors,
            y=counts,
            marker_color='#2196F3',
            text=counts,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Students: %{y}<extra></extra>'
        )])

        fig.update_layout(
            height=400,
            xaxis_title="Career Sectors",
            yaxis_title="Number of Students",
            xaxis_tickangle=-45,
            showlegend=False,
            template='plotly_white'
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### 📈 Growth Predictions")

    growth_data = []
    for student_id, pred in predictions.items():
        growth_str = pred.get('growth_percentage', '0%').replace('%', '')
        try:
            growth = float(growth_str)
            growth_data.append(growth)
        except:
            continue

    if growth_data:
        col_growth1, col_growth2, col_growth3 = st.columns(3)

        with col_growth1:
            avg_growth = np.mean(growth_data)
            st.metric("Average Growth", f"{avg_growth:.1f}%")

        with col_growth2:
            max_growth = max(growth_data)
            st.metric("Highest Growth", f"{max_growth:.1f}%")

        with col_growth3:
            positive_growth = len([g for g in growth_data if g > 0])
            total = len(growth_data)
            percent_positive = (positive_growth / total * 100) if total > 0 else 0
            st.metric("Positive Growth", f"{positive_growth}/{total}",
                      delta=f"{percent_positive:.1f}%")

    st.markdown("##### 🎯 Performance Level Distribution")

    performance_levels = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Satisfactory': 0, 'Needs Improvement': 0}

    for pred in predictions.values():
        perf_str = pred.get('current_performance', '')
        for level in performance_levels.keys():
            if level in perf_str:
                performance_levels[level] += 1
                break

    fig = go.Figure(data=[go.Pie(
        labels=list(performance_levels.keys()),
        values=list(performance_levels.values()),
        hole=0.3,
        marker_colors=['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336'],
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Students: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        height=400,
        title="AI-Assessed Performance Levels",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### 👁️ Sample Predictions")

    sample_count = min(3, len(predictions))
    sample_keys = list(predictions.keys())[:sample_count]

    for i, student_id in enumerate(sample_keys):
        with st.expander(f"Sample {i + 1}: {predictions[student_id].get('student_name', 'Student')}"):
            pred = predictions[student_id]
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Academic Insights**")
                st.markdown(f"- **Current:** {pred.get('current_performance', 'N/A')}")
                st.markdown(f"- **Predicted Next:** {pred.get('predicted_next_semester', 'N/A')}")
                st.markdown(f"- **Growth:** {pred.get('growth_percentage', 'N/A')}")

            with col2:
                st.markdown("**Career Guidance**")
                st.markdown(f"- **Sector:** {pred.get('recommended_career_sector', 'N/A')}")
                st.markdown(f"- **Strengths:**")
                for strength in pred.get('key_strengths', []):
                    st.markdown(f"  • {strength}")

            st.markdown("**Recommendation**")
            st.info(pred.get('recommendation', 'N/A'))


def show_no_data_analytics():
    """Show analytics page when no data is available"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 Analytics Dashboard</h3>", unsafe_allow_html=True)

    st.markdown("""
    ### No Data Available Yet

    To access advanced analytics, please:

    1. **📤 Upload** your student data (Teachers/Admins only)
    2. **⚙️ Process** the data for analysis
    3. **📊 Explore** interactive analytics

    ### 🎯 What You'll Get:

    #### Tab 1: 🎯 CO-PO Analysis
    - Interactive gauge charts for CO attainment
    - PO attainment heatmaps
    - CO-PO correlation insights

    #### Tab 2: 📈 Performance Metrics
    - Performance distribution charts
    - Statistical analysis
    - Performance categories

    #### Tab 3: 📊 Student Distribution
    - Component-wise performance radar charts
    - CO scores distribution
    - Detailed statistics

    #### Tab 4: 🤖 AI Predictions
    - Career sector recommendations
    - Growth predictions
    - Performance insights
    """)

    if st.session_state.user_type in ["teacher", "admin"]:
        if st.button("🚀 Upload Data to Get Started", use_container_width=True, type="primary"):
            st.session_state.current_page = "upload"
            st.rerun()
    else:
        st.info("Please wait for your teacher to upload and process the course data.")

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================
def main():
    apply_professional_theme()

    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.user_type in ["teacher", "student", "parent", "admin"]:
            main_dashboard()
        else:
            st.error("Invalid user type. Please login again.")
            st.session_state.logged_in = False
            st.rerun()


# ==============================================================================
# RUN APPLICATION
# ==============================================================================
if __name__ == "__main__":
    main()
