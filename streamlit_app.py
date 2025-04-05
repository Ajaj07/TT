import streamlit as st
import pandas as pd
import random

# Initialize session state variables if they don't exist
if 'subjects' not in st.session_state:
    st.session_state.subjects = []
if 'timetable_generated' not in st.session_state:
    st.session_state.timetable_generated = False

# Constants
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIME_SLOTS = ["9-10 AM", "10-11 AM", "11-12 PM", "1-2 PM", "2-3 PM", "3-4 PM"]

# Page Configuration
st.set_page_config(page_title="Timetable Generator", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        width: 100%;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        margin-bottom: 1rem;
    }
    div[data-testid="stTable"] {
        width: 100%;
    }
    thead tr th {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    tbody tr:nth-of-type(odd) {
        background-color: #f5f5f5;
    }
    .title {
        text-align: center;
        color: #4CAF50;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("<h1 class='title'>📅 Timetable Generator</h1>", unsafe_allow_html=True)

# Create two columns for input and subject list
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Enter Timetable Details")
    
    # Input fields
    semester = st.selectbox(
        "Select Semester",
        ["2nd Semester", "4th Semester", "6th Semester"],
        key="semester"
    )
    
    faculty = st.text_input("Faculty Name", key="faculty")
    subject = st.text_input("Subject Name", key="subject")
    lecture_hours = st.number_input("Weekly Lecture Hours", min_value=0, max_value=10, value=0, key="lecture_hours")
    lab_hours = st.number_input("Weekly Lab Hours (Each lab = 2 lecture slots)", min_value=0, max_value=5, value=0, key="lab_hours")

    # Add subject button
    if st.button("➕ Add Subject"):
        if not faculty or not subject or lecture_hours == 0:
            st.error("Please fill all required fields!")
        else:
            st.session_state.subjects.append({
                "semester": semester,
                "faculty": faculty,
                "subject": subject,
                "lectureHours": lecture_hours,
                "labHours": lab_hours
            })
            # Clear input fields
            st.session_state.faculty = ""
            st.session_state.subject = ""
            st.session_state.lecture_hours = 0
            st.session_state.lab_hours = 0

with col2:
    st.subheader("Subject List")
    if st.session_state.subjects:
        df = pd.DataFrame(st.session_state.subjects)
        st.dataframe(
            df,
            column_config={
                "semester": "Semester",
                "faculty": "Faculty",
                "subject": "Subject",
                "lectureHours": "Lecture Hours",
                "labHours": "Lab Hours"
            },
            hide_index=True
        )
    else:
        st.info("No subjects added yet. Please add subjects using the form.")

# Generate Timetable Button
if st.session_state.subjects and st.button("📅 Generate Timetable"):
    st.session_state.timetable_generated = True
    
    # Initialize empty timetable
    timetable = {slot: {day: "" for day in DAYS} for slot in TIME_SLOTS}
    
    # Helper function to check if slot is available
    def is_slot_available(slot_idx, day, slots_needed=1):
        return all(
            timetable[TIME_SLOTS[i]][day] == "" 
            for i in range(slot_idx, min(slot_idx + slots_needed, len(TIME_SLOTS)))
        )
    
    # Schedule subjects
    for subject in st.session_state.subjects:
        # Schedule lectures
        for _ in range(subject['lectureHours']):
            scheduled = False
            for day in random.sample(DAYS, len(DAYS)):
                for slot_idx, slot in enumerate(TIME_SLOTS):
                    if is_slot_available(slot_idx, day):
                        timetable[slot][day] = f"{subject['subject']}\n({subject['faculty']})"
                        scheduled = True
                        break
                if scheduled:
                    break
        
        # Schedule labs (2 consecutive slots)
        for _ in range(subject['labHours']):
            scheduled = False
            for day in random.sample(DAYS, len(DAYS)):
                for slot_idx in range(len(TIME_SLOTS) - 1):
                    if is_slot_available(slot_idx, day, 2):
                        lab_text = f"{subject['subject']} Lab\n({subject['faculty']})"
                        timetable[TIME_SLOTS[slot_idx]][day] = lab_text
                        timetable[TIME_SLOTS[slot_idx + 1]][day] = lab_text
                        scheduled = True
                        break
                if scheduled:
                    break

    # Display timetable
    st.subheader("Generated Timetable")
    
    # Convert timetable to DataFrame for better display
    df_timetable = pd.DataFrame(timetable)
    df_timetable = df_timetable.transpose()
    
    # Apply custom styling
    st.dataframe(
        df_timetable,
        height=400,
        use_container_width=True
    )

# Clear all button
if st.session_state.subjects:
    if st.button("🗑️ Clear All"):
        st.session_state.subjects = []
        st.session_state.timetable_generated = False
        st.experimental_rerun()
