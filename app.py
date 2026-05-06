import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="MC ALOYO ANALYSIS", layout="wide", page_icon="🎓")

# Enhanced Decorative CSS
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #1e3a8a; 
        color: white; 
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2563eb; border: none; }
    .report-card { 
        padding: 30px; 
        border-radius: 15px; 
        background-color: white; 
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .teacher-box { 
        padding: 20px; 
        border-radius: 12px; 
        background-color: #ffffff; 
        border-left: 8px solid #1e3a8a; 
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .header-style {
        color: #1e3a8a;
        font-family: 'Arial';
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE INITIALIZATION ---
if 'students_db' not in st.session_state:
    st.session_state.students_db = pd.DataFrame(columns=[
        'Name', 'Grade', 'Subject', 'Score', 'Points', 'Performance Level'
    ])

if 'teacher_registry' not in st.session_state:
    st.session_state.teacher_registry = {
        "MR. ELIARS OPONDO": {
            "phone": "", "photo": None, 
            "assignments": [
                {"sub": "English Literature", "grade": "Grade 7"}, {"sub": "English Literature", "grade": "Grade 8"},
                {"sub": "English Literature", "grade": "Grade 9"}, {"sub": "Pretechnical studies", "grade": "Grade 7"},
                {"sub": "Creative Arts and Sports", "grade": "Grade 8"}
            ]
        },
        "MR. LUCAS ODHIAMBO": {
            "phone": "", "photo": None,
            "assignments": [
                {"sub": "Integrated Science", "grade": "Grade 7"}, {"sub": "Integrated Science", "grade": "Grade 8"},
                {"sub": "Agriculture", "grade": "Grade 8"}, {"sub": "Agriculture", "grade": "Grade 9"}
            ]
        },
        "MR. VINCENT OMWANDA": {
            "phone": "", "photo": None,
            "assignments": [
                {"sub": "Social studies", "grade": "Grade 7"}, {"sub": "Social studies", "grade": "Grade 8"},
                {"sub": "Social studies", "grade": "Grade 9"}, {"sub": "Kiswahili", "grade": "Grade 8"},
                {"sub": "Kiswahili", "grade": "Grade 9"}
            ]
        },
        "MISS GRACE OTIENO": {
            "phone": "", "photo": None,
            "assignments": [
                {"sub": "Agriculture", "grade": "Grade 7"}, {"sub": "CRE", "grade": "Grade 7"},
                {"sub": "CRE", "grade": "Grade 8"}, {"sub": "Integrated Science", "grade": "Grade 9"}
            ]
        },
        "MR. ELIJAH ALOYO": {
            "phone": "", "photo": None,
            "assignments": [
                {"sub": "Creative Arts and Sports", "grade": "Grade 7"}, {"sub": "Creative Arts and Sports", "grade": "Grade 9"},
                {"sub": "Pretechnical studies", "grade": "Grade 8"}, {"sub": "Pretechnical studies", "grade": "Grade 9"},
                {"sub": "Mathematics", "grade": "Grade 8"}
            ]
        },
        "MR. ACHIYO ELIAS": {
            "phone": "", "photo": None,
            "assignments": [
                {"sub": "Kiswahili", "grade": "Grade 7"}, {"sub": "CRE", "grade": "Grade 9"}
            ]
        },
        "MR. TIBERIUS": {
            "phone": "", "photo": None,
            "assignments": [
                {"sub": "Mathematics", "grade": "Grade 7"}, {"sub": "Mathematics", "grade": "Grade 9"}
            ]
        }
    }

# --- CONSTANTS ---
SUBJECTS = [
    "English Literature", "Kiswahili", "Mathematics", "Integrated Science",
    "Pretechnical studies", "Social studies", "CRE", "Agriculture", "Creative Arts and Sports"
]
GRADES = ["Grade 7", "Grade 8", "Grade 9"]

# --- FUNCTIONS ---
def calculate_analysis(percentage_score):
    if percentage_score >= 90: return 8, "Exceeding Expectation 1"
    elif percentage_score >= 80: return 7, "Exceeding Expectation 2"
    elif percentage_score >= 70: return 6, "Meeting Expectation 1"
    elif percentage_score >= 60: return 5, "Meeting Expectation 2"
    elif percentage_score >= 50: return 4, "Approaching Expectation 1"
    elif percentage_score >= 40: return 3, "Approaching Expectation 2"
    elif percentage_score >= 30: return 2, "Below Expectation 1"
    else: return 1, "Below Expectation 2"

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🏫</h1>", unsafe_allow_html=True)
st.sidebar.title("MC ALOYO ANALYSIS")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigation Menu", [
    "📂 Admin: Student Upload", 
    "👤 Admin: Teacher Management", 
    "✍️ Teacher: Marks Entry", 
    "📜 Reports: Student Assessment"
])

# --- 1. STUDENT UPLOAD ---
if "📂 Admin: Student Upload" in menu:
    st.markdown("<h2 class='header-style'>📂 Register Students via Excel</h2>", unsafe_allow_html=True)
    st.info("💡 Ensure your Excel sheet has a column labeled 'Name'.")
    
    selected_grade = st.selectbox("Select Grade to Upload", GRADES)
    uploaded_file = st.file_uploader(f"Choose Excel file for {selected_grade}", type=["xlsx"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns]
            name_col = next((c for c in df.columns if c.lower() == 'name'), None)
            if name_col:
                new_records = []
                for name in df[name_col].dropna().unique():
                    for sub in SUBJECTS:
                        new_records.append({
                            'Name': str(name).strip().upper(), 
                            'Grade': selected_grade, 
                            'Subject': sub, 
                            'Score': 0, 'Points': 1, 'Performance Level': 'Below Expectation 2'
                        })
                st.session_state.students_db = pd.concat([st.session_state.students_db, pd.DataFrame(new_records)]).drop_duplicates(subset=['Name', 'Grade', 'Subject']).reset_index(drop=True)
                st.success(f"✅ Successfully loaded {len(df[name_col].unique())} students into the {selected_grade} Registry.")
            else: st.error("❌ 'Name' column not found in Excel.")
        except Exception as e: st.error(f"Error: {e}")

# --- 2. TEACHER MANAGEMENT ---
elif "👤 Admin: Teacher Management" in menu:
    st.markdown("<h2 class='header-style'>👥 Teacher Profile Management</h2>", unsafe_allow_html=True)
    
    with st.expander("🖼️ Update Teacher Photo & Contact"):
        with st.form("update_teacher_form"):
            t_name = st.selectbox("Select Teacher", list(st.session_state.teacher_registry.keys()))
            t_phone = st.text_input("WhatsApp Number (e.g. 254...)")
            t_photo = st.file_uploader("Upload Profile Picture", type=['jpg', 'jpeg', 'png'])
            if st.form_submit_button("Update Teacher File"):
                if t_phone: st.session_state.teacher_registry[t_name]["phone"] = t_phone
                if t_photo: st.session_state.teacher_registry[t_name]["photo"] = t_photo.read()
                st.success(f"✅ Folder for {t_name} has been updated.")

    st.markdown("### 📋 Teacher Registry Directory")
    for name, data in st.session_state.teacher_registry.items():
        st.markdown(f'<div class="teacher-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 5])
        with col1:
            if data["photo"]: st.image(data["photo"], width=130)
            else: st.markdown("<h1 style='font-size: 80px;'>👤</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<h3 style='color: #1e3a8a;'>{name}</h3>", unsafe_allow_html=True)
            st.write(f"📞 **WhatsApp:** {data['phone'] if data['phone'] else 'Not Provided'}")
            st.write("📚 **Assigned Classes:**")
            for a in data["assignments"]:
                msg = f"Hello {name}, enter marks for {a['sub']} ({a['grade']}) here: https://mc-aloyo.streamlit.app/"
                wa_url = f"https://wa.me/{data['phone']}?text={msg.replace(' ', '%20')}"
                st.markdown(f"📖 {a['sub']} - {a['grade']} | [📤 Send Link]({wa_url})")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 3. TEACHER MARKS ENTRY ---
elif "✍️ Teacher: Marks Entry" in menu:
    st.markdown("<h2 class='header-style'>✍️ Subject Marks Entry</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    active_grade = c1.selectbox("Select Grade", GRADES)
    active_sub = c2.selectbox("Select Subject", SUBJECTS)
    
    mask = (st.session_state.students_db['Grade'] == active_grade) & (st.session_state.students_db['Subject'] == active_sub)
    entry_df = st.session_state.students_db[mask]
    
    if not entry_df.empty:
        search = st.text_input("🔍 Search Student Name").upper()
        with st.form(key=f"marks_{active_grade}_{active_sub}"):
            st.markdown(f"#### 📝 Entering scores for {active_sub}")
            updated_vals = {}
            for idx, row in entry_df.iterrows():
                if not search or search in row['Name']:
                    updated_vals[idx] = st.number_input(f"Score for {row['Name']} (%)", 0, 100, int(row['Score']), key=f"s_{idx}")
            if st.form_submit_button("💾 Save and Analyze Marks"):
                for idx, val in updated_vals.items():
                    pts, lvl = calculate_analysis(val)
                    st.session_state.students_db.at[idx, 'Score'] = val
                    st.session_state.students_db.at[idx, 'Points'] = pts
                    st.session_state.students_db.at[idx, 'Performance Level'] = lvl
                st.success("🎉 Marks successfully saved and analyzed!")
    else: st.warning("⚠️ No students registered for this class yet.")

# --- 4. ASSESSMENT REPORTS ---
elif "📜 Reports: Student Assessment" in menu:
    st.markdown("<h2 class='header-style'>📜 Student Assessment Reports</h2>", unsafe_allow_html=True)
    rep_grade = st.selectbox("Select Grade to View", GRADES)
    grade_data = st.session_state.students_db[st.session_state.students_db['Grade'] == rep_grade]
    
    if not grade_data.empty:
        # Ranking Table
        summary = grade_data.groupby('Name')['Points'].sum().reset_index()
        summary['Percentage (%)'] = ((summary['Points'] / 72) * 100).round(2)
        st.markdown("### 🏆 Class Merit List")
        st.dataframe(summary.sort_values(by='Points', ascending=False), use_container_width=True, hide_index=True)
        
        # Individual Report Card
        st.markdown("---")
        target = st.selectbox("🔍 Select Student for Detailed Report Card", summary['Name'])
        if target:
            report = grade_data[grade_data['Name'] == target]
            st.markdown(f"""
                <div class="report-card">
                    <h2 style='text-align: center; color: #1e3a8a;'>🎓 MC ALOYO ANALYSIS</h2>
                    <h4 style='text-align: center;'>Official Exam Assessment Report</h4>
                    <hr>
                    <p><b>Student Name:</b> {target} &nbsp;&nbsp; | &nbsp;&nbsp; <b>Grade:</b> {rep_grade}</p>
                    <p><b>Date:</b> {datetime.now().strftime('%d %B %Y')}</p>
                </div>
            """, unsafe_allow_html=True)
            st.table(report[['Subject', 'Score', 'Points', 'Performance Level']])
            colA, colB = st.columns(2)
            colA.metric("Total Points", f"{report['Points'].sum()} / 72")
            colB.metric("Overall Percentage", f"{((report['Points'].sum()/72)*100):.2f}%")
    else: st.info("📚 No data available for this grade yet.")
