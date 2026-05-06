import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="MC ALOYO ANALYSIS", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background-color: #1e3a8a; color: white; font-weight: bold; border: none;
    }
    .report-card { 
        padding: 30px; border-radius: 15px; background-color: white; 
        border: 1px solid #e5e7eb; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px; page-break-after: always;
    }
    .teacher-box { 
        padding: 20px; border-radius: 12px; background-color: #ffffff; 
        border-left: 8px solid #1e3a8a; margin-bottom: 15px;
    }
    .header-style { color: #1e3a8a; font-weight: bold; }
    @media print {
        .no-print { display: none !important; }
        .report-card { border: none; box-shadow: none; }
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
        "MR. ELIARS OPONDO": {"phone": "", "photo": None, "assignments": [{"sub": "English Literature", "grade": "Grade 7"}, {"sub": "English Literature", "grade": "Grade 8"}, {"sub": "English Literature", "grade": "Grade 9"}, {"sub": "Pretechnical studies", "grade": "Grade 7"}, {"sub": "Creative Arts and Sports", "grade": "Grade 8"}]},
        "MR. LUCAS ODHIAMBO": {"phone": "", "photo": None, "assignments": [{"sub": "Integrated Science", "grade": "Grade 7"}, {"sub": "Integrated Science", "grade": "Grade 8"}, {"sub": "Agriculture", "grade": "Grade 8"}, {"sub": "Agriculture", "grade": "Grade 9"}]},
        "MR. VINCENT OMWANDA": {"phone": "", "photo": None, "assignments": [{"sub": "Social studies", "grade": "Grade 7"}, {"sub": "Social studies", "grade": "Grade 8"}, {"sub": "Social studies", "grade": "Grade 9"}, {"sub": "Kiswahili", "grade": "Grade 8"}, {"sub": "Kiswahili", "grade": "Grade 9"}]},
        "MISS GRACE OTIENO": {"phone": "", "photo": None, "assignments": [{"sub": "Agriculture", "grade": "Grade 7"}, {"sub": "CRE", "grade": "Grade 7"}, {"sub": "CRE", "grade": "Grade 8"}, {"sub": "Integrated Science", "grade": "Grade 9"}]},
        "MR. ELIJAH ALOYO": {"phone": "", "photo": None, "assignments": [{"sub": "Creative Arts and Sports", "grade": "Grade 7"}, {"sub": "Creative Arts and Sports", "grade": "Grade 9"}, {"sub": "Pretechnical studies", "grade": "Grade 8"}, {"sub": "Pretechnical studies", "grade": "Grade 9"}, {"sub": "Mathematics", "grade": "Grade 8"}]},
        "MR. ACHIYO ELIAS": {"phone": "", "photo": None, "assignments": [{"sub": "Kiswahili", "grade": "Grade 7"}, {"sub": "CRE", "grade": "Grade 9"}]},
        "MR. TIBERIUS": {"phone": "", "photo": None, "assignments": [{"sub": "Mathematics", "grade": "Grade 7"}, {"sub": "Mathematics", "grade": "Grade 9"}]}
    }

# --- CONSTANTS ---
SUBJECTS = ["English Literature", "Kiswahili", "Mathematics", "Integrated Science", "Pretechnical studies", "Social studies", "CRE", "Agriculture", "Creative Arts and Sports"]
GRADES = ["Grade 7", "Grade 8", "Grade 9"]

# --- FUNCTIONS ---
def calculate_analysis(score):
    if score >= 90: return 8, "Exceeding Expectation 1"
    elif score >= 80: return 7, "Exceeding Expectation 2"
    elif score >= 70: return 6, "Meeting Expectation 1"
    elif score >= 60: return 5, "Meeting Expectation 2"
    elif score >= 50: return 4, "Approaching Expectation 1"
    elif score >= 40: return 3, "Approaching Expectation 2"
    elif score >= 30: return 2, "Below Expectation 1"
    else: return 1, "Below Expectation 2"

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='text-align: center;'>🏫</h1>", unsafe_allow_html=True)
st.sidebar.title("MC ALOYO ANALYSIS")
menu = st.sidebar.radio("Navigation Menu", ["📂 Admin: Student Upload", "👤 Admin: Teacher Management", "✍️ Teacher: Marks Entry", "📜 Reports: Student Assessment"])

# --- 1. STUDENT UPLOAD ---
if "📂 Admin: Student Upload" in menu:
    st.markdown("<h2 class='header-style'>📂 Register Students</h2>", unsafe_allow_html=True)
    selected_grade = st.selectbox("Select Grade", GRADES)
    uploaded_file = st.file_uploader(f"Upload Excel for {selected_grade}", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        name_col = next((c for c in df.columns if 'name' in str(c).lower()), None)
        if name_col:
            new_records = []
            for name in df[name_col].dropna().unique():
                for sub in SUBJECTS:
                    new_records.append({'Name': str(name).strip().upper(), 'Grade': selected_grade, 'Subject': sub, 'Score': 0, 'Points': 1, 'Performance Level': 'Below Expectation 2'})
            st.session_state.students_db = pd.concat([st.session_state.students_db, pd.DataFrame(new_records)]).drop_duplicates(subset=['Name', 'Grade', 'Subject']).reset_index(drop=True)
            st.success(f"✅ Loaded students for {selected_grade}!")

# --- 2. TEACHER MANAGEMENT ---
elif "👤 Admin: Teacher Management" in menu:
    st.markdown("<h2 class='header-style'>👤 Teacher Management</h2>", unsafe_allow_html=True)
    with st.expander("Update Profile"):
        with st.form("up_teacher"):
            t_name = st.selectbox("Teacher", list(st.session_state.teacher_registry.keys()))
            t_phone = st.text_input("WhatsApp")
            t_photo = st.file_uploader("Photo", type=['jpg', 'png'])
            if st.form_submit_button("Update"):
                if t_phone: st.session_state.teacher_registry[t_name]["phone"] = t_phone
                if t_photo: st.session_state.teacher_registry[t_name]["photo"] = t_photo.read()
                st.success("Updated!")
    for name, data in st.session_state.teacher_registry.items():
        st.markdown(f'<div class="teacher-box">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 5])
        with c1:
            if data["photo"]: st.image(data["photo"], width=100)
            else: st.markdown("👤")
        with c2:
            st.write(f"**{name}** | WhatsApp: {data['phone']}")
            for a in data["assignments"]:
                msg = f"Marks entry for {a['sub']} ({a['grade']}): https://mc-aloyo.streamlit.app/"
                st.markdown(f"📖 {a['sub']} ({a['grade']}) | [Send Link](https://wa.me/{data['phone']}?text={msg.replace(' ', '%20')})")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 3. TEACHER MARKS ENTRY (GRADE-SPECIFIC) ---
elif "✍️ Teacher: Marks Entry" in menu:
    st.markdown("<h2 class='header-style'>✍️ Grade-Wise Marks Entry</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    sel_grade = col1.selectbox("Filter by Grade", GRADES)
    sel_sub = col2.selectbox("Select Subject", SUBJECTS)
    
    # Strictly filter the pool to the selected grade and subject
    mask = (st.session_state.students_db['Grade'] == sel_grade) & (st.session_state.students_db['Subject'] == sel_sub)
    students = st.session_state.students_db[mask]
    
    if not students.empty:
        search = st.text_input("🔍 Search Student in " + sel_grade).upper()
        with st.form(key=f"form_{sel_grade}_{sel_sub}"):
            updated_scores = {}
            for idx, row in students.iterrows():
                if not search or search in row['Name']:
                    updated_scores[idx] = st.number_input(f"{row['Name']} (%)", 0, 100, int(row['Score']), key=f"s_{idx}")
            if st.form_submit_button("Save Marks"):
                for idx, val in updated_scores.items():
                    pts, lvl = calculate_analysis(val)
                    st.session_state.students_db.at[idx, 'Score'] = val
                    st.session_state.students_db.at[idx, 'Points'] = pts
                    st.session_state.students_db.at[idx, 'Performance Level'] = lvl
                st.success(f"Marks for {sel_grade} {sel_sub} saved!")
    else: st.warning(f"No students registered in {sel_grade}.")

# --- 4. REPORTS & BATCH PRINTING ---
elif "📜 Reports: Student Assessment" in menu:
    st.markdown("<h2 class='header-style'>📜 Assessment Reports & Batch Printing</h2>", unsafe_allow_html=True)
    rep_grade = st.selectbox("Select Grade for Report", GRADES)
    grade_data = st.session_state.students_db[st.session_state.students_db['Grade'] == rep_grade]
    
    if not grade_data.empty:
        tab1, tab2 = st.tabs(["🏆 Merit List", "🖨️ Batch Print (All Students)"])
        
        with tab1:
            summary = grade_data.groupby('Name')['Points'].sum().reset_index()
            summary['Mean %'] = ((summary['Points'] / 72) * 100).round(2)
            st.dataframe(summary.sort_values(by='Points', ascending=False), use_container_width=True)
            
        with tab2:
            st.info("💡 To save as PDF: Click 'Prepare Batch', then press Ctrl+P (or Cmd+P) and select 'Save as PDF'.")
            if st.button("Prepare Batch for " + rep_grade):
                all_student_names = grade_data['Name'].unique()
                for student in all_student_names:
                    report = grade_data[grade_data['Name'] == student]
                    st.markdown(f"""
                        <div class="report-card">
                            <h2 style='text-align: center;'>🎓 MC ALOYO ANALYSIS</h2>
                            <h4 style='text-align: center;'>Student Report Card: {rep_grade}</h4>
                            <hr>
                            <p><b>Name:</b> {student} &nbsp;&nbsp; | &nbsp;&nbsp; <b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.table(report[['Subject', 'Score', 'Points', 'Performance Level']])
                    st.write(f"**Total Points:** {report['Points'].sum()} / 72")
                    st.markdown("<br><hr style='border: 1px dashed #ccc;'><br>", unsafe_allow_html=True)
    else: st.info("No data for this grade.")
