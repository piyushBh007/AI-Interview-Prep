import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* Dark Mode Support via Streamlit settings handles most, 
       but we can define specific overrides here */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
    }
    
    /* Custom Cards */
    .stCard {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    @media (prefers-color-scheme: dark) {
        .stCard {
            background-color: #1e2126;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
        }
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    
    /* Metrics Override */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)
