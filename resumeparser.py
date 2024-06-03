import re
from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyCLZMT3xhqG9r3MVQxcRf2nKrm2j8XBJAk")

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


def extract_contact_number_from_resume(text):
    contact_number = None
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()
    return contact_number


def extract_email_from_resume(text):
    email = None
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()
    return email


def extract_skills_from_resume(text, skills_list):
    skills = []
    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills.append(skill)
    return skills


def extract_education_from_resume(text):
    education = []
    pattern = r"(?i)(?:Bsc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bMaster(?:'s)?|\bPh\.D)\s(?:\w+\s)*\w+"
    matches = re.findall(pattern, text)
    for match in matches:
        education.append(match.strip())
    return education


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
        suggestion = response.text.strip()
        return suggestion
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    resume_paths = [r"/Users/sydnum/Downloads/resume.pdf"]
    for resume_path in resume_paths:
        try:
            text = extract_text_from_pdf(resume_path)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            continue

        print("Resume:", resume_path)

        name = extract_name(text)
        if name:
            print("Name:", name)
        else:
            print("Name not found")

        contact_number = extract_contact_number_from_resume(text)
        if contact_number:
            print("Contact Number:", contact_number)
        else:
            print("Contact Number not found")

        email = extract_email_from_resume(text)
        if email:
            print("Email:", email)
        else:
            print("Email not found")

        skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management',
                       'Deep Learning', 'SQL', 'Tableau']
        extracted_skills = extract_skills_from_resume(text, skills_list)
        if extracted_skills:
            print("Skills:", extracted_skills)
        else:
            print("No skills found")

        extracted_education = extract_education_from_resume(text)
        if extracted_education:
            print("Education:", extracted_education)
        else:
            print("No education information found")

        prompt = f"I have parsed the resume and extracted the following information:\n" \
                 f"Name: {name}\n" \
                 f"Contact Number: {contact_number}\n" \
                 f"Email: {email}\n" \
                 f"Skills: {', '.join(extracted_skills)}\n" \
                 f"Education: {', '.join(extracted_education)}\n" \
                 f"What suggestions do you have for the candidate? Answer in 300 words only"

        suggestion = generate_suggestions(prompt)

        print("Suggestions for the candidate:")
        print(suggestion)