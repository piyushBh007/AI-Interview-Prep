import os
from fpdf import FPDF

def generate_pdf_report(metrics_data, user_info, filename="Interview_Report.pdf"):
    """
    Generates a PDF report of the user's interview performance.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI Interview Performance Report", ln=1, align='C')
    pdf.ln(10)
    
    # User Info
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Candidate: {user_info.get('username', 'User')}", ln=1, align='L')
    pdf.ln(5)
    
    # Metrics
    pdf.set_font("Arial", size=12)
    for idx, metric in enumerate(metrics_data):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"Interview #{idx+1} - Role: {metric['role']} ({metric['timestamp'][:10]})", ln=1)
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, txt=f"Avg Confidence: {metric['avg_confidence']:.2f}/10", ln=1)
        pdf.cell(200, 8, txt=f"Avg Relevance: {metric['avg_relevance']:.2f}/10", ln=1)
        pdf.cell(200, 8, txt=f"Avg Completeness: {metric['avg_completeness']:.2f}/10", ln=1)
        pdf.cell(200, 8, txt=f"Avg Communication: {metric['avg_communication']:.2f}/10", ln=1)
        pdf.ln(5)
    
    # Save
    report_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    file_path = os.path.join(report_dir, filename)
    pdf.output(file_path)
    return file_path
