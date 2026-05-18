import streamlit as st
import os
import time
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

from database import init_db, get_connection
from authentication import login_user, register_user, logout_user
from interview_engine import generate_questions
from analysis import evaluate_answer, save_evaluation, get_performance_metrics
from utils import generate_pdf_report
from styles import apply_custom_styles

load_dotenv()

# Initialize Database
init_db()

# --- Page Config ---
st.set_page_config(
    page_title="AI Interview Prep",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_custom_styles()

# --- Session State Management ---
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'
if 'interview_session' not in st.session_state:
    st.session_state['interview_session'] = None

# --- Helper Navigation ---
def navigate_to(page_name):
    st.session_state['current_page'] = page_name
    st.rerun()

# --- Auth Pages ---
def render_auth_page():
    st.title("Welcome to AI Interview Prep 🎯")
    st.markdown("Practice mock interviews with AI and get instant feedback.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Login")
        with st.form("login_form"):
            l_user = st.text_input("Username")
            l_pass = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                success, msg = login_user(l_user, l_pass)
                if success:
                    st.session_state['user_id'] = msg
                    st.session_state['username'] = l_user
                    st.success("Login successful!")
                    time.sleep(1)
                    navigate_to("Dashboard")
                else:
                    st.error(msg)
                    
    with col2:
        st.subheader("Register")
        with st.form("register_form"):
            r_user = st.text_input("Choose Username")
            r_pass = st.text_input("Choose Password", type="password")
            submitted = st.form_submit_button("Register")
            if submitted:
                if len(r_user) < 3 or len(r_pass) < 6:
                    st.error("Username must be >= 3 chars, Password >= 6 chars.")
                else:
                    success, msg = register_user(r_user, r_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

# --- Dashboard ---
def render_dashboard():
    st.title(f"Dashboard - Welcome, {st.session_state.get('username', 'User')}!")
    
    col1, col2, col3 = st.columns(3)
    
    metrics = get_performance_metrics(st.session_state['user_id'])
    total_interviews = len(metrics)
    avg_overall = sum([(m['avg_confidence'] + m['avg_relevance'] + m['avg_completeness'] + m['avg_communication'])/4 for m in metrics]) / total_interviews if total_interviews > 0 else 0
    
    with col1:
        st.metric("Total Interviews", total_interviews)
    with col2:
        st.metric("Average Score", f"{avg_overall:.1f} / 10")
    with col3:
        st.button("Start New Interview", on_click=navigate_to, args=("Mock Interview Setup",), use_container_width=True, type="primary")

    st.divider()
    st.subheader("Recent Interviews")
    if metrics:
        recent = metrics[:5] # Top 5
        for m in recent:
            with st.expander(f"{m['role']} - {m['timestamp'][:10]}"):
                st.write(f"Confidence: {m['avg_confidence']:.1f} | Relevance: {m['avg_relevance']:.1f} | Completeness: {m['avg_completeness']:.1f} | Communication: {m['avg_communication']:.1f}")
    else:
        st.info("No interviews taken yet. Start practicing!")

# --- Mock Interview Setup ---
def render_interview_setup():
    st.title("Setup Mock Interview")
    
    with st.form("setup_interview"):
        role = st.text_input("Job Role", placeholder="e.g., Software Engineer, Data Scientist")
        experience = st.selectbox("Experience Level", ["Entry Level", "Mid Level", "Senior", "Executive"])
        difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"])
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=3)
        
        submitted = st.form_submit_button("Start Interview")
        if submitted:
            if not role:
                st.error("Please enter a job role.")
                return
            
            with st.spinner("Generating customized questions via AI..."):
                questions = generate_questions(role, experience, difficulty, num_questions)
                
                # Create interview record
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO interviews (user_id, role, difficulty) VALUES (?, ?, ?)", 
                               (st.session_state['user_id'], role, difficulty))
                interview_id = cursor.lastrowid
                
                # Save questions
                db_questions = []
                for q in questions:
                    cursor.execute("INSERT INTO questions (interview_id, question_text, question_type, expected_skills) VALUES (?, ?, ?, ?)",
                                   (interview_id, q['text'], q['type'], q.get('skills', '')))
                    q_id = cursor.lastrowid
                    db_questions.append({
                        "id": q_id,
                        "text": q['text'],
                        "type": q['type'],
                        "skills": q.get('skills', '')
                    })
                conn.commit()
                conn.close()
                
                st.session_state['interview_session'] = {
                    "id": interview_id,
                    "role": role,
                    "questions": db_questions,
                    "current_q_index": 0,
                    "answers": {}
                }
                st.success("Questions generated! Let's begin.")
                time.sleep(1)
                navigate_to("Active Interview")

# --- Active Interview ---
def render_active_interview():
    session = st.session_state.get('interview_session')
    if not session:
        st.warning("No active session.")
        st.button("Go to Setup", on_click=navigate_to, args=("Mock Interview Setup",))
        return
        
    questions = session['questions']
    idx = session['current_q_index']
    
    if idx >= len(questions):
        st.success("Interview Completed! Calculating results...")
        time.sleep(2)
        st.session_state['interview_session'] = None
        navigate_to("Dashboard")
        return
        
    current_q = questions[idx]
    
    st.title(f"Question {idx + 1} of {len(questions)}")
    st.progress((idx) / len(questions))
    
    st.markdown(f"**Type:** {current_q['type']}")
    st.info(f"### {current_q['text']}")
    
    # Form for answer
    with st.form(f"answer_form_{idx}"):
        answer = st.text_area("Your Answer", height=200, placeholder="Type your answer here...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_btn = st.form_submit_button("Submit Answer", type="primary")
            
        if submit_btn:
            if len(answer.strip()) < 10:
                st.error("Please provide a more detailed answer.")
            else:
                with st.spinner("Analyzing answer..."):
                    eval_result = evaluate_answer(current_q['text'], answer, session['role'], current_q['skills'])
                    
                    # Update DB
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE questions SET user_answer = ? WHERE id = ?", (answer, current_q['id']))
                    conn.commit()
                    conn.close()
                    
                    save_evaluation(current_q['id'], eval_result)
                    
                    st.success("Answer recorded and analyzed!")
                    st.session_state['interview_session']['current_q_index'] += 1
                    time.sleep(1)
                    st.rerun()

# --- Analytics ---
def render_analytics():
    st.title("Performance Analytics")
    metrics = get_performance_metrics(st.session_state['user_id'])
    
    if not metrics:
        st.info("No data available. Complete an interview first.")
        return
        
    df = pd.DataFrame(metrics)
    
    # Trend Chart
    st.subheader("Progress Over Time")
    df['overall_score'] = (df['avg_confidence'] + df['avg_relevance'] + df['avg_completeness'] + df['avg_communication']) / 4
    fig_line = px.line(df, x='timestamp', y='overall_score', markers=True, title='Overall Score Trend')
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Radar Chart for latest
    st.subheader("Latest Interview Profile")
    latest = df.iloc[0]
    categories = ['Confidence', 'Relevance', 'Completeness', 'Communication']
    values = [latest['avg_confidence'], latest['avg_relevance'], latest['avg_completeness'], latest['avg_communication']]
    
    radar_df = pd.DataFrame(dict(Score=values, Category=categories))
    fig_radar = px.line_polar(radar_df, r='Score', theta='Category', line_close=True, range_r=[0,10])
    fig_radar.update_traces(fill='toself')
    st.plotly_chart(fig_radar, use_container_width=True)

# --- History ---
def render_history():
    st.title("Interview History")
    metrics = get_performance_metrics(st.session_state['user_id'])
    
    if not metrics:
        st.info("No interview history found.")
        return
        
    df = pd.DataFrame(metrics)
    st.dataframe(df[['role', 'timestamp', 'avg_confidence', 'avg_relevance', 'avg_completeness', 'avg_communication']], use_container_width=True)
    
    st.subheader("Export Report")
    if st.button("Generate PDF Report"):
        with st.spinner("Generating PDF..."):
            user_info = {"username": st.session_state.get('username', 'User')}
            filepath = generate_pdf_report(metrics, user_info)
            with open(filepath, "rb") as file:
                st.download_button(
                    label="Download PDF",
                    data=file,
                    file_name="Interview_Report.pdf",
                    mime="application/pdf"
                )

# --- Sidebar Navigation ---
if st.session_state['user_id'] is None:
    render_auth_page()
else:
    with st.sidebar:
        st.title("Navigation")
        if st.button("Dashboard", use_container_width=True): navigate_to("Dashboard")
        if st.button("Mock Interview", use_container_width=True): navigate_to("Mock Interview Setup")
        if st.button("Analytics", use_container_width=True): navigate_to("Analytics")
        if st.button("History", use_container_width=True): navigate_to("History")
        st.divider()
        if st.button("Logout", type="primary", use_container_width=True):
            logout_user()
            navigate_to("Home")
            
    # Page Routing
    if st.session_state['current_page'] == 'Dashboard':
        render_dashboard()
    elif st.session_state['current_page'] == 'Mock Interview Setup':
        render_interview_setup()
    elif st.session_state['current_page'] == 'Active Interview':
        render_active_interview()
    elif st.session_state['current_page'] == 'Analytics':
        render_analytics()
    elif st.session_state['current_page'] == 'History':
        render_history()
    else:
        render_dashboard()
