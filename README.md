# AI Interview Preparation System

An AI-powered interview preparation platform built with Streamlit and Google Gemini API. This application helps users practice mock interviews by generating customized questions based on job roles and experience levels, evaluating their answers, and providing actionable feedback.

## Features

- **User Authentication**: Secure login and registration using `passlib` and `bcrypt`.
- **Mock Interview Engine**: Generates role-specific interview questions using Google's Generative AI.
- **Answer Evaluation**: Analyzes your answers for confidence, relevance, completeness, and communication skills.
- **Analytics Dashboard**: Tracks your performance over time with interactive Plotly charts.
- **History & Reporting**: View your past interviews and export detailed performance reports as PDFs.

## Tech Stack

- **Frontend**: Streamlit
- **Backend/AI**: Python, Google Generative AI (Gemini)
- **Database**: SQLite (Local)
- **Data Visualization**: Plotly, Pandas
- **Reporting**: FPDF

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/piyushBh007/AI-Interview-Preparation.git
   cd AI-Interview-Preparation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Register/Login** to create your profile.
2. Go to **Mock Interview Setup** to choose your target job role, experience level, and difficulty.
3. Answer the generated questions thoughtfully.
4. Review your performance in the **Analytics** and **History** sections.
