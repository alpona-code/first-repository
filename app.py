import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import textwrap
import json
import urllib.parse
from pymongo import MongoClient, errors
import certifi
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# MongoDB connection
def connect_db():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        st.error("MongoDB URI not found in environment variables.")
        return None
    try:
        client = MongoClient(uri, tlsCAFile=certifi.where())
        return client
    except errors.ConfigurationError as e:
        st.error(f"Configuration Error: {e}")
    except errors.ConnectionError as e:
        st.error(f"Connection Error: {e}")
    except errors.OperationFailure as e:
        st.error(f"Operation Failure: {e}")
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
    return None

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
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to fetch job data from MongoDB
def fetch_jobs(skill_name, location):
    client = connect_db()
    if not client:
        return []
    try:
        db = client['job_database']
        collection = db['jobs']
        query = {
            "Job Title": {"$regex": skill_name, "$options": "i"}
        }
        jobs = list(collection.find(query))
        return jobs
    except errors.PyMongoError as e:
        st.error(f"Error fetching job data: {e}")
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
    return []

# Function to extract text from a PDF
def extract_text_from_pdf(file):
    reader = pdf.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to match keywords in the extracted text
def match_keywords(text, keywords):
    found_keywords = []
    for keyword in keywords:
        if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
            found_keywords.append(keyword)
    return found_keywords

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
{{"MissingKeywords:[]","Profile Summary":""}}
"""

# Streamlit UI
st.set_page_config(
    page_title="Conversational AI for tailored educational pathways",
    page_icon="🌟",
    layout="centered",
    initial_sidebar_state="auto"
)
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Conversational AI for Tailored Educational Pathways</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["AI Chatbot", "ATS Resume Expert", "Job Recommendation"])

with tab1:
    st.markdown("<h3 style='color: #4CAF50;'>Ask your question:</h3>", unsafe_allow_html=True)
    # Add custom CSS to fix the input box at the bottom
    st.markdown("""
    <style>
        .fixed-bottom-input {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: white;
            padding: 10px;
            box-shadow: 0px -2px 5px rgba(0,0,0,0.1);
        }
        .fixed-bottom-input form {
            display: flex;
            justify-content: space-between;
            width: 100%;
        }
        .fixed-bottom-input input[type="text"] {
            flex-grow: 1;
            margin-right: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            st.markdown(f"**You:** {chat['question']}")
            st.markdown(f"**AI Chatbot:** {chat['response']}")

    # Form for user input at the bottom
    st.markdown('<div class="fixed-bottom-input">', unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        input_text = st.text_input("", key="input", placeholder="Type your question here...", help="Enter the question you want to ask Gemini")
        submit = st.form_submit_button("Ask Question")
    st.markdown('</div>', unsafe_allow_html=True)

    if submit and input_text:
        with st.spinner("Generating response..."):
            response = get_gemini_response(input_text)
        st.session_state.chat_history.append({"question": input_text, "response": response})

        # Clear chat container and re-display updated chat history
        chat_container.empty()
        with chat_container:
            for chat in st.session_state.chat_history:
                st.markdown(f"**You:** {chat['question']}")
                st.markdown(f"**AI Chatbot:** {chat['response']}")

with tab2:
    st.markdown("<h3 style='color: #4CAF50;'>Skill gap finder:</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)...", type=["pdf"], help="Please upload the PDF")
    skill = st.text_input("Enter Job title", key="skill", placeholder="Enter the Job title you wish to join...", help="Enter the skill you want to search for jobs")
    location = st.text_input("Location", key="location", placeholder="Enter the location for job...", help="Enter the location for job search")
    if uploaded_file:
        st.write("PDF Uploaded Successfully")
    submit = st.button("Submit")
    if submit:
        if uploaded_file:
            text = input_pdf_text(uploaded_file)
            if skill and location:
                with st.spinner("Fetching job data..."):
                    job_data = fetch_jobs(skill_name=skill, location=location)
                    if job_data:
                        job_descriptions = "\n\n".join([job['Description'] for job in job_data])
                        response = get_gemini_response(input_prompt.format(text=text, jd=job_descriptions))
                        response_data = json.loads(response)
                        missing_keywords = response_data.get("MissingKeywords", [])
                        if missing_keywords:
                            coursera_urls = [f"https://www.coursera.org/search?query={urllib.parse.quote_plus(keyword)}" for keyword in missing_keywords]
                            udemy_urls = [f"https://www.udemy.com/courses/search/?src=ukw&q={urllib.parse.quote_plus(keyword)}" for keyword in missing_keywords]
                            st.subheader("The response is")
                            st.write(response)
                            st.subheader("To learn a missing skill")  
                            for i in range(len(missing_keywords)):
                                st.write(f"Coursera: {coursera_urls[i]}")
                                st.write(f"Udemy: {udemy_urls[i]}")
                        else:
                            st.write("No missing keywords found.")
                    else:
                        st.write("No job data found matching the criteria.")
            else:
                st.write("Please enter the skill and location for job search")
        else:
            st.write("Please upload the resume")

with tab3:
    st.markdown("<h3 style='color: #4CAF50;'>Job Recommendation:</h3>", unsafe_allow_html=True)
    uploaded_resume = st.file_uploader("Upload Your Resume for Job Matching (PDF)...", type=["pdf"], key="resume_upload", help="Please upload the PDF")
    if uploaded_resume:
        st.write("PDF Uploaded Successfully")
        submit_recommendation = st.button("Get Job Recommendations")
        if submit_recommendation:
            with st.spinner("Extracting text and matching skills..."):
                extracted_text = extract_text_from_pdf(uploaded_resume)
                client = connect_db()
                if client:
                    try:
                        db1 = client['ESCO_Skills']
                        db2 = client['job_database']
                        skills_collection = db1['Skills']
                        skills_cursor = skills_collection.find({})
                        skills = [doc['preferredLabel'] for doc in skills_cursor]

                        matched_keywords = match_keywords(extracted_text, skills)
                        if not matched_keywords:
                            st.write("No matching keywords found in the resume.")
                        else:
                            resume_text = ' '.join(matched_keywords)
                            jobs_collection = db2['Job_Listings']
                            job_listings_cursor = jobs_collection.find({})
                            job_listings = pd.DataFrame(list(job_listings_cursor))
                            job_descriptions = job_listings['Description'].tolist()
                            texts = [resume_text] + job_descriptions
                            vectorizer = TfidfVectorizer()
                            tfidf_matrix = vectorizer.fit_transform(texts)
                            cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                            job_listings['similarity'] = cosine_similarities
                            top_matches = job_listings.sort_values(by='similarity', ascending=False).head(5)
                            # Make links clickable
                            top_matches['Link'] = top_matches['Link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
                            st.write(top_matches[['Job ID', 'Job Title', 'Company', 'Link']].to_html(escape=False, index=False), unsafe_allow_html=True)
                    except errors.PyMongoError as e:
                        st.error(f"Error fetching job data: {e}")
                    except Exception as e:
                        st.error(f"Unexpected Error: {e}")
                else:
                    st.write("Failed to connect to the database")

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
