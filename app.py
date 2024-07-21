import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
 
# Load environment variables
load_dotenv()  # take environment variables from .env.
 
# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
print("API Key:", api_key)
genai.configure(api_key=api_key)
 
# Function to convert text to Markdown format
def to_markdown(text):
    text = text.replace('•', '  *')
    return text
 
# Function to get response from Gemini model
def get_gemini_response(input_text, pdf_content=None, prompt=None):
    try:
        if not input_text:
            raise ValueError("Input text must not be empty")
 
        if pdf_content:
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([input_text, pdf_content[0], prompt])
        else:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(input_text)
        return response.text
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return f"Error: {ve}"
    except TypeError as te:
        print(f"TypeError: {te}")
        return f"Error: {te}"
    except Exception as e:
        print(f"Exception: {e}")
        return f"Error generating content: {e}"
 
# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text
 
# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide
best assistance for improving the resumes. Assign the percentage Matching based
on JD and
the missing keywords with high accuracy
resume:{text}
description:{jd}
 
I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""
 
# Set page configuration
st.set_page_config(
    page_title="Q&A Demo and ATS Resume Expert",
    page_icon="🌟",
    layout="centered",
    initial_sidebar_state="auto"
)
 
# Page header
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Conversational AI for Tailored Educational Pathways</h1>", unsafe_allow_html=True)
 
# Tabs for different functionalities
tab1, tab2 = st.tabs(["Q&A Chatbot", "ATS Resume Expert"])
 
with tab1:
    # Input section for Q&A Chatbot
    st.markdown("<h3 style='color: #4CAF50;'>Ask your question:</h3>", unsafe_allow_html=True)
    input_text = st.text_input("", key="input", placeholder="Type your question here...", help="Enter the question you want to ask Gemini")
 
    # Submit button for Q&A Chatbot
    submit = st.button("Ask the Question")
 
    # If ask button is clicked
    if submit:
        if input_text.strip():
            with st.spinner("Generating response..."):
                response = get_gemini_response(input_text)
            st.markdown("<h2 style='color: #4CAF50;'>The Response:</h2>", unsafe_allow_html=True)
            st.success(response)
        else:
            st.error("Please enter a question.")
 
with tab2:
    # Input section for ATS Resume Expert
    st.markdown("<h3 style='color: #4CAF50;'>Enter your resume or profile:</h3>", unsafe_allow_html=True)
    jd = st.text_area("Paste the Job Description", key="job_desc", placeholder="Paste your job description here...", help="Enter the job description to evaluate the resume against", height=200)
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)...", type=["pdf"], help="Please upload the PDF")
 
    if uploaded_file is not None:
        st.write("PDF Uploaded Successfully")
 
    # Button for ATS Resume Expert
    submit = st.button("Submit")
 
    if submit:
        if uploaded_file is not None and jd.strip():
            text = input_pdf_text(uploaded_file)
            if text.strip():
                response = get_gemini_response(input_prompt.format(text=text, jd=jd))
                st.subheader("The Response is")
                st.write(response)
            else:
                st.error("Extracted text from PDF is empty.")
        else:
            st.error("Please upload the resume and ensure the job description is not empty.")
 
# Add a sidebar with project overview and key features
st.sidebar.title("Project Overview")
st.sidebar.info("""
**Title:** Personalized Educational and Career Pathway AI Chatbot
 
**Key Features:**
 
1. **Personalized Recommendations:**
   - The AI chatbot will recommend courses and educational pathways based on individual academic and career aspirations.
   - It will craft bespoke educational trajectories tailored to each learner's background, experience, and career objectives.
 
2. **Skill Extraction and Job Recommendations:**
   - The bot will analyze resumes to extract current skills and suggest suitable job opportunities.
   - It will identify skill gaps and recommend additional skills needed to achieve targeted job roles.
 
3. **Explainable AI:**
   - Developed with best practices in explainable AI to ensure transparency and trust.
   - Provides clear explanations for its recommendations, allowing users to understand and evaluate their future career evolution and options.
 
4. **Data-Driven Insights:**
   - Trained on survey data, market trends, and stakeholder inputs.
   - Adaptable to gender considerations, present and future job market needs, and STEM/non-STEM profiles.
 
5. **Interactive and Adaptive:**
   - The chatbot will ask targeted questions to understand the user's background, expectations, and needs.
   - Adapts its recommendations based on the user's input, providing a tailored program for both students and professionals.
 
6. **Career Guidance:**
   - Guides users in choosing the appropriate educational structure depending on their expertise and career stage.
   - Helps professionals assess their current skill set and suggests improvements for career advancement.
 
""")
 
# Add a footer
st.markdown("""
    <hr style="height:2px;border:none;color:#4CAF50;background-color:#4CAF50;" />
    <footer style="text-align: center;">
        <p>© 2024 Conversational AI for Tailored Educational Pathways. All rights reserved.</p>
    </footer>
""", unsafe_allow_html=True)import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
 
# Load environment variables
load_dotenv()  # take environment variables from .env.
 
# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
print("API Key:", api_key)
genai.configure(api_key=api_key)
 
# Function to convert text to Markdown format
def to_markdown(text):
    text = text.replace('•', '  *')
    return text
 
# Function to get response from Gemini model
def get_gemini_response(input_text, pdf_content=None, prompt=None):
    try:
        if not input_text:
            raise ValueError("Input text must not be empty")
 
        if pdf_content:
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([input_text, pdf_content[0], prompt])
        else:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(input_text)
        return response.text
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return f"Error: {ve}"
    except TypeError as te:
        print(f"TypeError: {te}")
        return f"Error: {te}"
    except Exception as e:
        print(f"Exception: {e}")
        return f"Error generating content: {e}"
 
# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text
 
# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide
best assistance for improving the resumes. Assign the percentage Matching based
on JD and
the missing keywords with high accuracy
resume:{text}
description:{jd}
 
I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""
 
# Set page configuration
st.set_page_config(
    page_title="Q&A Demo and ATS Resume Expert",
    page_icon="🌟",
    layout="centered",
    initial_sidebar_state="auto"
)
 
# Page header
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Conversational AI for Tailored Educational Pathways</h1>", unsafe_allow_html=True)
 
# Tabs for different functionalities
tab1, tab2 = st.tabs(["Q&A Chatbot", "ATS Resume Expert"])
 
with tab1:
    # Input section for Q&A Chatbot
    st.markdown("<h3 style='color: #4CAF50;'>Ask your question:</h3>", unsafe_allow_html=True)
    input_text = st.text_input("", key="input", placeholder="Type your question here...", help="Enter the question you want to ask Gemini")
 
    # Submit button for Q&A Chatbot
    submit = st.button("Ask the Question")
 
    # If ask button is clicked
    if submit:
        if input_text.strip():
            with st.spinner("Generating response..."):
                response = get_gemini_response(input_text)
            st.markdown("<h2 style='color: #4CAF50;'>The Response:</h2>", unsafe_allow_html=True)
            st.success(response)
        else:
            st.error("Please enter a question.")
 
with tab2:
    # Input section for ATS Resume Expert
    st.markdown("<h3 style='color: #4CAF50;'>Enter your resume or profile:</h3>", unsafe_allow_html=True)
    jd = st.text_area("Paste the Job Description", key="job_desc", placeholder="Paste your job description here...", help="Enter the job description to evaluate the resume against", height=200)
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)...", type=["pdf"], help="Please upload the PDF")
 
    if uploaded_file is not None:
        st.write("PDF Uploaded Successfully")
 
    # Button for ATS Resume Expert
    submit = st.button("Submit")
 
    if submit:
        if uploaded_file is not None and jd.strip():
            text = input_pdf_text(uploaded_file)
            if text.strip():
                response = get_gemini_response(input_prompt.format(text=text, jd=jd))
                st.subheader("The Response is")
                st.write(response)
            else:
                st.error("Extracted text from PDF is empty.")
        else:
            st.error("Please upload the resume and ensure the job description is not empty.")
 
# Add a sidebar with project overview and key features
st.sidebar.title("Project Overview")
st.sidebar.info("""
**Title:** Personalized Educational and Career Pathway AI Chatbot
 
**Key Features:**
 
1. **Personalized Recommendations:**
   - The AI chatbot will recommend courses and educational pathways based on individual academic and career aspirations.
   - It will craft bespoke educational trajectories tailored to each learner's background, experience, and career objectives.
 
2. **Skill Extraction and Job Recommendations:**
   - The bot will analyze resumes to extract current skills and suggest suitable job opportunities.
   - It will identify skill gaps and recommend additional skills needed to achieve targeted job roles.
 
3. **Explainable AI:**
   - Developed with best practices in explainable AI to ensure transparency and trust.
   - Provides clear explanations for its recommendations, allowing users to understand and evaluate their future career evolution and options.
 
4. **Data-Driven Insights:**
   - Trained on survey data, market trends, and stakeholder inputs.
   - Adaptable to gender considerations, present and future job market needs, and STEM/non-STEM profiles.
 
5. **Interactive and Adaptive:**
   - The chatbot will ask targeted questions to understand the user's background, expectations, and needs.
   - Adapts its recommendations based on the user's input, providing a tailored program for both students and professionals.
 
6. **Career Guidance:**
   - Guides users in choosing the appropriate educational structure depending on their expertise and career stage.
   - Helps professionals assess their current skill set and suggests improvements for career advancement.
 
""")
 
# Add a footer
st.markdown("""
    <hr style="height:2px;border:none;color:#4CAF50;background-color:#4CAF50;" />
    <footer style="text-align: center;">
        <p>© 2024 Conversational AI for Tailored Educational Pathways. All rights reserved.</p>
    </footer>
""", unsafe_allow_html=True)
