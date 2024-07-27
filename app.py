import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import textwrap
from IPython.display import Markdown
import json
import urllib.parse
from pymongo import MongoClient
import certifi

# Load environment variables
load_dotenv()  # take environment variables from .env.

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# MongoDB connection
def connect_db():
    uri = os.getenv("MONGODB_URI")  # Assuming MONGODB_URI is set in your .env file
    client = MongoClient(uri, tlsCAFile=certifi.where())
    return client

# Function to convert text to Markdown format
def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Function to get response from Gemini model
def get_gemini_response(input, pdf_content=None, prompt=None):
    if pdf_content:
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([input, pdf_content[0], prompt])
    else:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input)
    return response.text

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Function to fetch job data from MongoDB
def fetch_jobs(skill_name, location):
    client = connect_db()
    db = client['job_database']
    collection = db['jobs']
    query = {
        "Job Title": {"$regex": skill_name, "$options": "i"},
        "Location": {"$regex": location, "$options": "i"}
    }
    jobs = list(collection.find(query))
    return jobs

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

# Streamlit UI
st.set_page_config(
    page_title="Q&A Demo and ATS Resume Expert",
    page_icon="🌟",
    layout="centered",
    initial_sidebar_state="auto"
)

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Conversational AI for Tailored Educational Pathways</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Q&A Chatbot", "ATS Resume Expert"])

with tab1:
    st.markdown("<h3 style='color: #4CAF50;'>Ask your question:</h3>", unsafe_allow_html=True)
    input_text = st.text_input("", key="input", placeholder="Type your question here...", help="Enter the question you want to ask Gemini")
    submit = st.button("Ask the Question")

    if submit:
        with st.spinner("Generating response..."):
            response = get_gemini_response(input_text)
        st.markdown("<h2 style='color: #4CAF50;'>The Response:</h2>", unsafe_allow_html=True)
        st.success(response)

with tab2:
    st.markdown("<h3 style='color: #4CAF50;'>Skill gap finder:</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)...", type=["pdf"], help="Please upload the PDF")
    scrape_skill = st.text_input("Enter Job title", key="skill", placeholder="Enter the Job title you wish to join...", help="Enter the skill you want to search for jobs")
    scrape_location = st.text_input("Location", key="scrape_location", placeholder="Enter the location for job...", help="Enter the location for job search")

    if uploaded_file is not None:
        st.write("PDF Uploaded Successfully")

    submit = st.button("Submit")

    if submit:
        if uploaded_file is not None:
            text = input_pdf_text(uploaded_file)
            if scrape_skill and scrape_location:
                with st.spinner("Fetching job data..."):
                    job_data = fetch_jobs(skill_name=scrape_skill, location=scrape_location)
                    if job_data:
                        job_descriptions = "\n\n".join([job['Description'] for job in job_data])
                        response = get_gemini_response(input_prompt.format(text=text, jd=job_descriptions))
                        response_data = json.loads(response)
                        missing_keywords = response_data.get("MissingKeywords", [])
                        if missing_keywords:
                            coursera_url1 = f"https://www.coursera.org/search?query={urllib.parse.quote_plus(missing_keywords[0])}"
                            udemy_url1 = f"https://www.udemy.com/courses/search/?src=ukw&q={urllib.parse.quote_plus(missing_keywords[0])}"
                            coursera_url2 = f"https://www.coursera.org/search?query={urllib.parse.quote_plus(missing_keywords[1])}" if len(missing_keywords) > 1 else ""
                            udemy_url2 = f"https://www.udemy.com/courses/search/?src=ukw&q={urllib.parse.quote_plus(missing_keywords[1])}" if len(missing_keywords) > 1 else ""
                            st.subheader("The response is")
                            st.write(response)
                            st.subheader("To learn a missing skill")  
                            st.write(f"Coursera:\n{coursera_url1}\n{coursera_url2}")
                            st.write(f"Udemy:\n{udemy_url1}\n{udemy_url2}") 
                        else:
                            st.write("No missing keywords found.")
                    else:
                        st.write("No job data found matching the criteria.")
            else:
                st.write("Please enter the skill and location for job search")
        else:
            st.write("Please upload the resume")

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

st.markdown("""
    <hr style="height:2px;border:none;color:#4CAF50;background-color:#4CAF50;" />
    <footer style="text-align: center;">
        <p>© 2024 Conversational AI for Tailored Educational Pathways. All rights reserved.</p>
    </footer>
""", unsafe_allow_html=True)
