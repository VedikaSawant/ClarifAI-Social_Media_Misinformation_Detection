import streamlit as st
import os
import requests
from dotenv import load_dotenv
import pymongo
import bcrypt
from wordcloud import WordCloud
import io
from PIL import Image
from collections import Counter
from textblob import TextBlob  # For sentiment analysis

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Load environment variables from .env file
load_dotenv()

# MongoDB setup
MONGO_URI = st.secrets["MONGO_URI"]  # Access MongoDB URI from Streamlit secrets
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database('users')
users_collection = db.get_collection("user_data")

# Function to hash the password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify password
def verify_password(stored_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_password)

# Function for login
def login():
    st.title("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if email and password:
                user = users_collection.find_one({"email": email})
                if user and verify_password(user["password"], password):
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = user['email']
                    st.success("Successfully logged in!")
                    st.session_state['page'] = "FactCheck"  # Redirect to FactCheck page
                    st.rerun()  # Force rerun to update the page
                else:
                    st.error("Invalid email or password")
            else:
                st.error("Please fill in all fields.")

# Function for sign-up
def signup():
    st.title("Create New Account")
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if username and email and password:
                # Check if user already exists
                if users_collection.find_one({"email": email}):
                    st.error("Email is already in use")
                else:
                    hashed_password = hash_password(password)
                    users_collection.insert_one({
                        "username": username,
                        "email": email,
                        "password": hashed_password
                    })
                    st.success("Account created successfully! You can now log in.")
                    
                    # Set session state for authentication and page redirection
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = email  # Set the user info in session
                    st.session_state['page'] = "FactCheck"  # Redirect to FactCheck page
                    
                    # Rerun to update the page
                    st.rerun()
            else:
                st.error("Please fill in all fields.")

# Retrieve the API Key from environment variable
API_KEY = st.secrets["API_KEY"]

if API_KEY is None:
    st.error("❌ API Key not set!")
    st.stop()

# Define the API endpoint
URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# Define the severity assignment function based on keywords in claims
def assign_severity(claim):
    claim = claim.lower()

    # Health-related misinformation (high severity)
    if any(keyword in claim for keyword in ["vaccine", "covid-19", "health", "medication", "pandemic", "disease"]):
        return 10  # High severity, potential for significant harm
    
    # Safety-related misinformation (high severity)
    elif any(keyword in claim for keyword in ["fire", "explosion", "danger", "safety", "hazard", "chemical"]):
        return 9  # High severity, immediate safety concerns
    
    # Environmental misinformation (moderate to high severity)
    elif any(keyword in claim for keyword in ["climate change", "global warming", "pollution", "deforestation", "ozone"]):
        return 8  # Moderate to high impact but longer-term consequences
    
    # Misinformation about social issues or politics (moderate severity)
    elif any(keyword in claim for keyword in ["election", "conspiracy", "fraud", "government", "corruption", "immigration", "racism", "gender inequality"]):
        return 7  # Moderate severity, can influence political views or lead to social division
    
    # Science and technology misinformation (medium severity)
    elif any(keyword in claim for keyword in ["alien", "technology", "space", "robot", "science", "scientific research"]):
        return 6  # Medium severity, speculative or misleading but less harmful
    
    # Financial misinformation (medium to high severity)
    elif any(keyword in claim for keyword in ["stock market", "cryptocurrency", "scam", "investment", "bitcoin", "ponzi"]):
        return 7  # Medium to high severity, financial harm or misdirection
    
    # Misinformation related to education (medium severity)
    elif any(keyword in claim for keyword in ["university", "degree", "school", "curriculum", "education", "student loan"]):
        return 6  # Can mislead individuals but not as immediate harm as health or safety misinformation
    
    # Misinformation related to public figures or celebrities (medium severity)
    elif any(keyword in claim for keyword in ["celebrity", "actor", "singer", "sports", "scandal"]):
        return 5  # Can cause confusion or harm reputations, but generally less impactful
    
    # Minor misleading claims or non-urgent information (low severity)
    else:
        return 4  # Lower severity for claims that are not urgent or harmful but still misleading

# Function to check news credibility
def check_fake_news(query):
    params = {
        "query": query,
        "key": API_KEY
    }
    response = requests.get(URL, params=params)
    severity_score = assign_severity(query)
    
    if response.status_code == 200:
        data = response.json()
        if "claims" in data and data["claims"]:
            result = []
            for claim in data["claims"]:
                claim_text = claim['text']
                for review in claim.get("claimReview", []):
                    result.append({
                        "claim": claim_text,
                        "fact_checker": review['publisher']['name'],
                        "verdict": review['textualRating'],
                        "url": review['url'],
                        "severity_score": severity_score
                    })
            return result
        else:
            return [{"claim": query, "fact_checker": "N/A", "verdict": "N/A", "url": "N/A", "severity_score": severity_score}]
    else:
        st.error(f"❌ Error: {response.status_code} - {response.json()}")
        return []

# Calculate the average verdict severity
def calculate_average_severity(results):
    # Calculate average severity score from all reviews
    severities = [result['severity_score'] for result in results]
    average_severity = sum(severities) / len(severities) if severities else 0
    return average_severity

# Generate Word Cloud based on claims and verdicts
def generate_word_cloud(claims):
    # Check if claims is a list and handle it appropriately
    if isinstance(claims, list) and len(claims) > 0:
        text = " ".join([claim['claim'] + " " + claim['verdict'] for claim in claims])
    else:
        # If only a single claim is entered, treat it as a dictionary
        text = claims['claim'] + " " + claims['verdict']

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    
    # Save to a BytesIO object
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)

    return img

# Function to analyze sentiment distribution
def analyze_sentiment(claim):
    blob = TextBlob(claim)
    sentiment = blob.sentiment.polarity  # Sentiment score: -1 (negative) to 1 (positive)
    
    if sentiment > 0.1:
        return {"positive": 80, "neutral": 10, "negative": 10}
    elif sentiment < -0.1:
        return {"positive": 10, "neutral": 20, "negative": 70}
    else:
        return {"positive": 20, "neutral": 60, "negative": 20}

# Function for FactCheck Input
def factcheck_input():
    st.title("FactCheck News")

    st.markdown("""
    <style>
    .title {
        color: #3E8E41;
        font-size: 30px;
    }
    .subheader {
        font-size: 24px;
        color: #4B0082;
    }
    .text {
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.form("factcheck_form"):
        text_input = st.text_area("Enter a news headline or statement")
        submitted = st.form_submit_button("Check Fact")

        if submitted:
            if text_input.strip():  # Ensure input is not empty
                results = check_fake_news(text_input)  # Call the FactCheck API
                if results:
                    st.subheader("Prediction Result")
                    # Calculate the average severity score for the results
                    avg_severity = calculate_average_severity(results)

                    for result in results:
                        st.write(f"**Claim:** {result['claim']}")
                        st.write(f"**Fact-Checker:** {result['fact_checker']}")
                        st.write(f"**Verdict:** {result['verdict']}")
                        st.write(f"**Severity Score:** {avg_severity}/10")
                        st.write(f"**URL:** {result['url']}")
                    
                    # Generate the word cloud image based on the result
                    wordcloud_img = generate_word_cloud(results[0])  # Only pass the first claim

                    # Display the word cloud
                    st.image(wordcloud_img, caption="Word Cloud", use_column_width=True)

                    # Display Content Severity Rating, Source Credibility Score, and Sentiment Distribution
                    st.subheader("Content Severity Rating")
                    # Make sure avg_severity is between 0 and 1 for the progress bar
                    normalized_severity = avg_severity / 10.0

                    # Pass the normalized value to the progress bar
                    st.progress(normalized_severity)

                    st.text(f"{avg_severity}: MISLEADING")

                    # Dynamic Source Credibility Score (based on the number of reviews)
                    credibility_score = len(results)  # Directly use the number of reviews as the credibility score

                    # Normalize the score to fit the 0.0 - 1.0 range (assuming 10 reviews is the max credibility)
                    normalized_credibility = min(credibility_score / 10.0, 1.0)  # Normalize to a value between 0 and 1

                    # Display Source Credibility Score
                    st.subheader("Source Credibility Score")
                    st.progress(normalized_credibility)

                    # Display credibility description
                    if credibility_score < 5:
                        st.text("Partially Reliable")
                    else:
                        st.text("Reliable")

                    # Dynamic Sentiment Distribution (analyzing the claim text)
                    sentiment = analyze_sentiment(text_input)
                    st.subheader("Sentiment Distribution")
                    st.text(f"Positive: {sentiment['positive']}% \nNeutral: {sentiment['neutral']}% \nNegative: {sentiment['negative']}%")
                else:
                    st.error("No results found for the claim.")
            else:
                st.error("Please enter a valid text input.")

# Main function to manage pages
def main():
    st.set_page_config(page_title="FactCheck App", layout="wide")
    pages = ["Login", "Sign Up", "FactCheck", "Feedback"]

    pages = ["FactCheck", "Feedback"]
    if st.session_state['authenticated']:
        page = st.sidebar.selectbox("Navigate", pages)  # Show all pages for authenticated users
    else:
        page = st.sidebar.selectbox("Navigate", ["Login", "Sign Up"])  # Only show Login and Sign Up

    # Render pages based on authentication state
    if page == "Login":
        login()
    elif page == "Sign Up":
        signup()
    elif page == "FactCheck":
        factcheck_input()
    elif page == "Feedback":
        feedback_section()
    else:
        st.error("You need to log in to access this page.")

def feedback_section():
    st.title("Feedback")
    with st.form("feedback_form"):
        accuracy = st.select_slider("How accurate were the results provided?", options=[1, 2, 3, 4, 5], value=3)
        comments = st.text_area("Additional Comments on Results")
        experience = st.select_slider("How would you rate the experience of using this app?", options=[1, 2, 3, 4, 5], value=4)
        submitted = st.form_submit_button("Submit")

        if submitted:
            st.success("Thank you for your feedback!")

if __name__ == "__main__":
    main()
