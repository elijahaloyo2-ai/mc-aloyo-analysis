import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="MC ALOYO ANALYSIS", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .report-card { padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #e0e0e0; }
    .teacher-box { padding: 15px; border-radius: 10px; background-color: #ffffff; border-left: 5px solid #007bff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE INITIALIZATION ---
if 'students_db' not in st.session_state:
    st.session_state.students_db = pd.DataFrame(columns=[
        'Name', 'Grade', 'Subject', 'Score', 'Points', 'Performance Level'
    ])

# Teacher Registry: Organized by Name to prevent redundancy
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
    if percentage_score >= 100: return 8, "Exceeding Expectation 1"
    elif percentage_score >= 89: return 7, "Exceeding Expectation 2"
    elif percentage_score >= 74: return 6, "Meeting Expectation 1"
    elif percentage_score >= 57: return 5, "Meeting Expectation 2"
    elif percentage_score >= 40: return 4, "Approaching Expectation 1"
    elif percentage_score >= 30: return 3, "Approaching Expectation 2"
    elif percentage_score >= 20: return 2, "Below Expectation 1"
    else: return 1, "Below Expectation 2"

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🏫 MC ALOYO ANALYSIS")
menu = st.sidebar.radio("Main Menu", ["Admin: Student Upload", "Admin: Teacher Management", "Teacher: Marks Entry", "Reports: Student Assessment"])

# --- 1. STUDENT UPLOAD ---
if menu == "Admin: Student Upload":
    st.header("📂 Register Students via Excel")
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
                        new_records.append({'Name': str(name).strip().upper(), 'Grade': selected_grade, 'Subject': sub, 'Score': 0, 'Points': 1, 'Performance Level': 'Below Expectation 2'})
                st.session_state.students_db = pd.concat([st.session_state.students_db, pd.DataFrame(new_records)]).drop_duplicates(subset=['Name', 'Grade', 'Subject']).reset_index(drop=True)
                st.success(f"Registered {len(df[name_col].unique())} students!")
            else: st.error("No 'Name' column found.")
        except Exception as e: st.error(f"Error: {e}")

# --- 2. TEACHER MANAGEMENT ---
elif menu == "Admin: Teacher Management":
    st.header("👨‍🏫 Teacher Registry & Profile Management")
    
    with st.expander("Update Teacher Details (Photo & WhatsApp)"):
        with st.form("update_teacher"):
            t_name = st.selectbox("Select Teacher to Update", list(st.session_state.teacher_registry.keys()))
            t_phone = st.text_input("WhatsApp Number (Include Country Code, e.g., 254...)")
            t_photo = st.file_uploader("Upload Profile Photo", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("Save to Teacher Folder"):
                if t_phone: st.session_state.teacher_registry[t_name]["phone"] = t_phone
                if t_photo: st.session_state.teacher_registry[t_name]["photo"] = t_photo.read()
                st.success(f"Profile updated for {t_name}")

    st.subheader("📋 Teacher Directory")
    for name, data in st.session_state.teacher_registry.items():
        with st.container():
            st.markdown(f'<div class="teacher-box">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 4])
            with col1:
                if data["photo"]: st.image(data["photo"], width=120)
                else: st.info("No Photo")
            with col2:
                st.write(f"### {name}")
                st.write(f"**WhatsApp:** {data['phone'] if data['phone'] else 'Not Set'}")
                st.write("**Assigned Subjects:**")
                for a in data["assignments"]:
                    msg = f"Hello {name}, enter marks for {a['sub']} ({a['grade']}) here: https://mc-aloyo.streamlit.app/"
                    whatsapp_url = f"https://wa.me/{data['phone']}?text={msg.replace(' ', '%20')}"
                    st.markdown(f"• {a['sub']} - {a['grade']} | [Send Entry Link]({whatsapp_url})")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 3. TEACHER MARKS ENTRY ---
elif menu == "Teacher: Marks Entry":
    st.header("📝 Subject Marks Entry (0-100%)")
    col1, col2 = st.columns(2)
    active_grade = col1.selectbox("Select Grade", GRADES)
    active_sub = col2.selectbox("Select Subject", SUBJECTS)
    
    mask = (st.session_state.students_db['Grade'] == active_grade) & (st.session_state.students_db['Subject'] == active_sub)
    entry_df = st.session_state.students_db[mask]
    
    if not entry_df.empty:
        search_query = st.text_input("🔍 Search Student Name").upper()
        with st.form(key=f"form_{active_grade}_{active_sub}"):
            updated_data = {}
            for idx, row in entry_df.iterrows():
                if not search_query or search_query in row['Name']:
                    updated_data[idx] = st.number_input(label=f"{row['Name']} (%)", min_value=0, max_value=100, value=int(row['Score']), key=f"in_{idx}")
            if st.form_submit_button("Submit Marks"):
                for idx, score_perc in updated_data.items():
                    pts, lvl = calculate_analysis(score_perc)
                    st.session_state.students_db.at[idx, 'Score'] = score_perc
                    st.session_state.students_db.at[idx, 'Points'] = pts
                    st.session_state.students_db.at[idx, 'Performance Level'] = lvl
                st.success("Marks submitted and analyzed!")
    else: st.warning("No students found for this subject/grade.")

# --- 4. ASSESSMENT REPORTS ---
elif menu == "Reports: Student Assessment":
    st.header("📊 Final Assessment Reports")
    rep_grade = st.selectbox("Select Grade", GRADES)
    grade_data = st.session_state.students_db[st.session_state.students_db['Grade'] == rep_grade]
    if not grade_data.empty:
        # Ranking
        student_totals = grade_data.groupby('Name')['Points'].sum().reset_index()
        student_totals['Percentage'] = ((student_totals['Points'] / 72) * 100).round(2)
        st.dataframe(student_totals.sort_values(by='Points', ascending=False), use_container_width=True)
        
        target_name = st.selectbox("View Individual Report", student_totals['Name'])
        if target_name:
            report = grade_data[grade_data['Name'] == target_name]
            st.markdown(f"<div class='report-card'><h3>{target_name} - {rep_grade}</h3></div>", unsafe_allow_html=True)
            st.table(report[['Subject', 'Score', 'Points', 'Performance Level']])
            st.metric("Total Points", f"{report['Points'].sum()} / 72")
    else: st.info("No data available.")
