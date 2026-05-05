import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="MC ALOYO ANALYSIS", layout="wide", page_icon="📊")

# Custom CSS for better UI
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .report-card { padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE INITIALIZATION ---
if 'students_db' not in st.session_state:
    # This acts as our central registry
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

# --- GRADING LOGIC ---
def get_performance_metrics(score_out_of_8):
    grading = {
        1: "Below Expectation 2",
        2: "Below Expectation 1",
        3: "Approaching Expectation 2",
        4: "Approaching Expectation 1",
        5: "Meeting Expectation 2",
        6: "Meeting Expectation 1",
        7: "Exceeding Expectation 2",
        8: "Exceeding Expectation 1"
    }
    # Standardize score between 1 and 8
    val = int(round(max(1, min(score_out_of_8, 8))))
    return val, grading.get(val)

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
    st.info("The Excel sheet should contain a column with the heading **'Name'**.")
    
    selected_grade = st.selectbox("Select Grade to Upload", GRADES)
    uploaded_file = st.file_uploader(f"Choose Excel file for {selected_grade}", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            # Clean column names for easier matching
            df.columns = [str(c).strip() for c in df.columns]
            name_col = next((c for c in df.columns if c.lower() == 'name'), None)

            if name_col:
                new_records = []
                # Filter out empty names and duplicates
                unique_names = df[name_col].dropna().unique()
                
                for name in unique_names:
                    for sub in SUBJECTS:
                        new_records.append({
                            'Name': str(name).strip().upper(), 
                            'Grade': selected_grade, 
                            'Subject': sub, 
                            'Score': 0, 'Points': 0, 'Performance Level': 'Pending'
                        })
                
                temp_df = pd.DataFrame(new_records)
                # Append to main DB and remove exact duplicates (Name+Grade+Subject)
                st.session_state.students_db = pd.concat([st.session_state.students_db, temp_df]).drop_duplicates(
                    subset=['Name', 'Grade', 'Subject'], keep='first'
                )
                st.success(f"✅ Successfully registered {len(unique_names)} students to {selected_grade} registry!")
            else:
                st.error("❌ The file is missing a column named 'Name'. Please check your Excel headers.")
        except Exception as e:
            st.error(f"Error processing file: {e}")

# --- 2. TEACHER MANAGEMENT ---
elif menu == "Admin: Teacher Management":
    st.header("👨‍🏫 Teacher Management Directory")
    
    with st.expander("Add New Teacher"):
        with st.form("teacher_reg"):
            col1, col2 = st.columns(2)
            t_name = col1.text_input("Teacher's Full Name")
            t_phone = col2.text_input("WhatsApp Number (e.g., +254...)")
            t_sub = col1.selectbox("Teaching Subject", SUBJECTS)
            t_grade = col2.selectbox("Assigned Grade", GRADES)
            
            if st.form_submit_button("Register Teacher & Generate Link"):
                if t_name and t_phone:
                    t_id = str(uuid.uuid4())[:6]
                    st.session_state.teacher_db.append({
                        "id": t_id, "name": t_name, "phone": t_phone, "sub": t_sub, "grade": t_grade
                    })
                    st.success(f"Teacher {t_name} registered!")
                else:
                    st.warning("Please fill in all details.")

    if st.session_state.teacher_db:
        st.subheader("Active Teacher Entry Links")
        for t in st.session_state.teacher_db:
            # Construction of the WhatsApp link with pre-filled text
            # Note: In a real deploy, replace 'localhost' with your Streamlit URL
            msg = f"Hello {t['name']}, enter marks for {t['sub']} ({t['grade']}) here: https://mc-aloyo.streamlit.app/"
            whatsapp_url = f"https://wa.me/{t['phone']}?text={msg.replace(' ', '%20')}"
            
            with st.container():
                st.markdown(f"""
                **{t['name']}** - {t['sub']} ({t['grade']})  
                [Send Entry Link via WhatsApp]({whatsapp_url})
                """)
                st.divider()

# --- 3. TEACHER MARKS ENTRY ---
elif menu == "Teacher: Marks Entry":
    st.header("📝 Subject Marks Entry")
    
    col1, col2 = st.columns(2)
    active_grade = col1.selectbox("Select Your Grade", GRADES)
    active_sub = col2.selectbox("Select Your Subject", SUBJECTS)
    
    # Filter DB for students in this specific class/subject
    mask = (st.session_state.students_db['Grade'] == active_grade) & \
           (st.session_state.students_db['Subject'] == active_sub)
    
    entry_df = st.session_state.students_db[mask]
    
    if not entry_df.empty:
        st.write(f"Entering marks for: **{active_sub}** | **{active_grade}**")
        search_query = st.text_input("🔍 Search Student Name")
        
        with st.form("marks_submission"):
            updated_data = {}
            for idx, row in entry_df.iterrows():
                if search_query.upper() in row['Name']:
                    updated_data[idx] = st.number_input(
                        f"{row['Name']}", min_value=1, max_value=8, value=int(row['Score']), key=f"score_{idx}"
                    )
            
            if st.form_submit_button("Submit and Update Analysis"):
                for idx, score_val in updated_data.items():
                    pts, level = get_performance_metrics(score_val)
                    st.session_state.students_db.at[idx, 'Score'] = score_val
                    st.session_state.students_db.at[idx, 'Points'] = pts
                    st.session_state.students_db.at[idx, 'Performance Level'] = level
                st.success("Analysis Updated Automatically!")
    else:
        st.warning("No students registered for this grade yet. Go to 'Student Upload' first.")

# --- 4. ASSESSMENT REPORTS ---
elif menu == "Reports: Student Assessment":
    st.header("📊 Final Assessment Reports")
    
    rep_grade = st.selectbox("Select Grade to Analyze", GRADES)
    grade_data = st.session_state.students_db[st.session_state.students_db['Grade'] == rep_grade]
    
    if not grade_data.empty:
        # Calculate Aggregates
        student_totals = grade_data.groupby('Name')['Points'].sum().reset_index()
        student_totals['Percentage'] = ((student_totals['Points'] / 72) * 100).round(2)
        student_totals = student_totals.sort_values(by='Points', ascending=False)
        
        st.subheader(f"Rank List - {rep_grade}")
        st.dataframe(student_totals, use_container_width=True)
        
        st.divider()
        
        # Individual Report Printing
        st.subheader("🖨️ Individual Student Report")
        target_name = st.selectbox("Select Student", student_totals['Name'])
        
        if target_name:
            report = grade_data[grade_data['Name'] == target_name]
            total_p = report['Points'].sum()
            perc = (total_p / 72) * 100
            
            st.markdown(f"""
            <div class="report-card">
                <h2 style='text-align: center;'>MC ALOYO ANALYSIS</h2>
                <h4 style='text-align: center;'>Official Student Assessment Report</h4>
                <hr>
                <p><b>Student Name:</b> {target_name} &nbsp;&nbsp;&nbsp; <b>Grade:</b> {rep_grade}</p>
                <p><b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.table(report[['Subject', 'Points', 'Performance Level']])
            
            c1, c2 = st.columns(2)
            c1.metric("Total Points", f"{total_p} / 72")
            c2.metric("Mean Percentage", f"{perc:.2f}%")
            
            if st.button("Print Report (Browser)"):
                st.info("To print: Use Ctrl+P (or Cmd+P) and save as PDF.")
    else:
        st.info("No data available for this grade.")
