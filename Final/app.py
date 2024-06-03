import re
from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import os

# Configure the API key
genai.configure(api_key="AIzaSyCLZMT3xhqG9r3MVQxcRf2nKrm2j8XBJAk")

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)


def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


def save_text_to_file(text, file_path):
    with open(file_path, 'w') as file:
        file.write(text)


def extract_contact_number_from_resume(text):
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    return match.group() if match else None


def extract_email_from_resume(text):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    return match.group() if match else None


def extract_skills_from_resume(text, skills_list):
    return [skill for skill in skills_list if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE)]


def extract_education_from_resume(text):
    pattern = r"(?i)(?:Bsc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bMaster(?:'s)?|\bPh\.D)\s(?:\w+\s)*\w+"
    return [match.strip() for match in re.findall(pattern, text)]


def extract_name(resume_text):
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    patterns = [
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}],
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]
    ]
    for pattern in patterns:
        matcher.add('NAME', [pattern])
    doc = nlp(resume_text)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text
    return None


def generate_suggestions(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return str(e)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify(error="No file part"), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify(error="No selected file"), 400
    if file:
        file_path = os.path.join('/tmp', file.filename)
        file.save(file_path)

        try:
            text = extract_text_from_pdf(file_path)
            text_file_path = file_path.replace('.pdf', '.txt')
            save_text_to_file(text, text_file_path)
        except Exception as e:
            return jsonify(error=f"Error extracting text from PDF: {e}"), 500

        name = extract_name(text) or "N/A"
        contact_number = extract_contact_number_from_resume(text) or "N/A"
        email = extract_email_from_resume(text) or "N/A"

        skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management',
                       'Deep Learning', 'SQL', 'Tableau']
        extracted_skills = extract_skills_from_resume(text, skills_list)

        extracted_education = extract_education_from_resume(text)

        prompt = f"I have parsed the resume and extracted the following information:\n" \
                 f"Name: {name}\n" \
                 f"Contact Number: {contact_number}\n" \
                 f"Email: {email}\n" \
                 f"Skills: {', '.join(extracted_skills)}\n" \
                 f"Education: {', '.join(extracted_education)}\n" \
                 f"What suggestions do you have for the candidate? Answer in 150 words only"

        suggestion = generate_suggestions(prompt)

        response = {
            'name': name,
            'contact_number': contact_number,
            'email': email,
            'skills': extracted_skills,
            'education': extracted_education,
            'suggestion': suggestion,
            'text_file': text_file_path
        }

        return jsonify(response)


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('/tmp', filename)


@app.route('/')
def serve_index():
    return send_from_directory('', 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
