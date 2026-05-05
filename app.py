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
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE INITIALIZATION ---
if 'students_db' not in st.session_state:
    st.session_state.students_db = pd.DataFrame(columns=[
        'Name', 'Grade', 'Subject', 'Score', 'Points', 'Performance Level'
    ])

if 'teacher_db' not in st.session_state:
    st.session_state.teacher_db = []

# --- CONSTANTS ---
SUBJECTS = [
    "English Literature", "Kiswahili", "Mathematics", "Integrated Science",
    "Pretechnical studies", "Social studies", "CRE", "Agriculture", "Creative Arts and Sports"
]
GRADES = ["Grade 7", "Grade 8", "Grade 9"]

# --- GRADING & CONVERSION LOGIC ---
def calculate_analysis(percentage_score):
    """Converts 0-100% score into Points (1-8) and Performance Levels."""
    # Define mapping based on percentage brackets
    if percentage_score >= 90: return 8, "Exceeding Expectation 1"
    elif percentage_score >= 80: return 7, "Exceeding Expectation 2"
    elif percentage_score >= 70: return 6, "Meeting Expectation 1"
    elif percentage_score >= 60: return 5, "Meeting Expectation 2"
    elif percentage_score >= 50: return 4, "Approaching Expectation 1"
    elif percentage_score >= 40: return 3, "Approaching Expectation 2"
    elif percentage_score >= 30: return 2, "Below Expectation 1"
    else: return 1, "Below Expectation 2"

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🏫 MC ALOYO ANALYSIS")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Main Menu", [
    "Admin: Student Upload", 
    "Admin: Teacher Management", 
    "Teacher: Marks Entry", 
    "Reports: Student Assessment"
])

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
                unique_names = df[name_col].dropna().unique()
                for name in unique_names:
                    for sub in SUBJECTS:
                        new_records.append({
                            'Name': str(name).strip().upper(), 
                            'Grade': selected_grade, 
                            'Subject': sub, 
                            'Score': 0, # Default percentage
                            'Points': 1, 
                            'Performance Level': 'Below Expectation 2'
                        })
                
                temp_df = pd.DataFrame(new_records)
                st.session_state.students_db = pd.concat([st.session_state.students_db, temp_df]).drop_duplicates(
                    subset=['Name', 'Grade', 'Subject'], keep='first'
                ).reset_index(drop=True)
                st.success(f"✅ Registered {len(unique_names)} students to {selected_grade}!")
            else:
                st.error("❌ Column 'Name' not found.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- 2. TEACHER MANAGEMENT ---
elif menu == "Admin: Teacher Management":
    st.header("👨‍🏫 Teacher Management Directory")
    with st.expander("Add New Teacher"):
        with st.form("teacher_reg"):
            t_name = st.text_input("Teacher's Full Name")
            t_phone = st.text_input("WhatsApp Number")
            t_sub = st.selectbox("Teaching Subject", SUBJECTS)
            t_grade = st.selectbox("Assigned Grade", GRADES)
            if st.form_submit_button("Register Teacher"):
                st.session_state.teacher_db.append({"name": t_name, "phone": t_phone, "sub": t_sub, "grade": t_grade})
                st.success("Teacher added!")

    for t in st.session_state.teacher_db:
        msg = f"Hello {t['name']}, enter marks for {t['sub']} ({t['grade']}) here: https://mc-aloyo.streamlit.app/"
        st.markdown(f"**{t['name']}** - {t['sub']} | [WhatsApp Link](https://wa.me/{t['phone']}?text={msg.replace(' ', '%20')})")

# --- 3. TEACHER MARKS ENTRY (FIXED FOR 100%) ---
elif menu == "Teacher: Marks Entry":
    st.header("📝 Subject Marks Entry (0-100%)")
    active_grade = st.selectbox("Select Grade", GRADES)
    active_sub = st.selectbox("Select Subject", SUBJECTS)
    
    mask = (st.session_state.students_db['Grade'] == active_grade) & (st.session_state.students_db['Subject'] == active_sub)
    entry_df = st.session_state.students_db[mask]
    
    if not entry_df.empty:
        search_query = st.text_input("🔍 Search Student Name").upper()
        with st.form(key=f"form_{active_grade}_{active_sub}"):
            updated_data = {}
            for idx, row in entry_df.iterrows():
                if not search_query or search_query in row['Name']:
                    # Teachers enter marks out of 100
                    updated_data[idx] = st.number_input(
                        label=f"{row['Name']} (%)", 
                        min_value=0, 
                        max_value=100, 
                        value=int(row['Score']), 
                        key=f"in_{idx}_{active_grade}_{active_sub}"
                    )
            
            if st.form_submit_button("Submit Marks"):
                for idx, score_perc in updated_data.items():
                    pts, level = calculate_analysis(score_perc)
                    st.session_state.students_db.at[idx, 'Score'] = score_perc
                    st.session_state.students_db.at[idx, 'Points'] = pts
                    st.session_state.students_db.at[idx, 'Performance Level'] = level
                st.success("Marks saved and converted to points automatically!")
    else:
        st.warning("No students found.")

# --- 4. ASSESSMENT REPORTS ---
elif menu == "Reports: Student Assessment":
    st.header("📊 Final Assessment Reports")
    rep_grade = st.selectbox("Select Grade", GRADES)
    grade_data = st.session_state.students_db[st.session_state.students_db['Grade'] == rep_grade]
    
    if not grade_data.empty:
        student_totals = grade_data.groupby('Name')['Points'].sum().reset_index()
        student_totals['Percentage'] = ((student_totals['Points'] / 72) * 100).round(2)
        st.dataframe(student_totals.sort_values(by='Points', ascending=False), use_container_width=True)
        
        target_name = st.selectbox("Select Student for Detailed Report", student_totals['Name'])
        if target_name:
            report = grade_data[grade_data['Name'] == target_name]
            st.markdown(f"<div class='report-card'><h3>{target_name} - {rep_grade}</h3></div>", unsafe_allow_html=True)
            st.table(report[['Subject', 'Score', 'Points', 'Performance Level']])
            st.metric("Total Points", f"{report['Points'].sum()} / 72")
    else:
        st.info("No data available.")
