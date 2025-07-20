import streamlit as st
import os
import requests
from dotenv import load_dotenv
import pymongo
import bcrypt
from wordcloud import WordCloud
import io
from PIL import Image
from textblob import TextBlob

# --- Initialize session state ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- Load env and MongoDB connection ---
load_dotenv()
MONGO_URI = st.secrets["MONGO_URI"]
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database()
users_collection = db.get_collection("user_data")

# --- Auth helpers ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_password)

def login():
    st.title("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted and email and password:
            user = users_collection.find_one({"email": email})
            if user and verify_password(user["password"], password):
                st.session_state.update({'authenticated': True, 'user': email, 'page': "FactCheck"})
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid email or password")
        elif submitted:
            st.error("Please fill in all fields.")

def signup():
    st.title("Create New Account")
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign Up")

        if submitted and username and email and password:
            if users_collection.find_one({"email": email}):
                st.error("Email is already in use")
            else:
                users_collection.insert_one({"username": username, "email": email, "password": hash_password(password)})
                st.session_state.update({'authenticated': True, 'user': email, 'page': "FactCheck"})
                st.success("Account created! Logging in...")
                st.rerun()
        elif submitted:
            st.error("Please fill in all fields.")

# --- FactCheck API Setup ---
API_KEY = st.secrets["API_KEY"]
URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# --- Verdict classification ---
def classify_verdict(verdict_text):
    verdict_text = verdict_text.lower()
    if any(x in verdict_text for x in ["false", "misleading", "incorrect"]):
        return "❌ False"
    elif any(x in verdict_text for x in ["true", "accurate", "correct"]):
        return "✅ True"
    else:
        return "⚠️ Unclear"

# --- Severity logic ---
def assign_severity(claim):
    claim = claim.lower()
    keywords = {
        10: ["vaccine", "covid-19", "health"],
        9: ["explosion", "hazard"],
        8: ["climate change", "pollution"],
        7: ["election", "fraud", "corruption"],
        6: ["technology", "robot", "science"],
        5: ["celebrity", "sports"],
        4: []  # fallback
    }
    for score, words in keywords.items():
        if any(word in claim for word in words):
            return score
    return 4

# --- Core logic ---
def check_fake_news(query):
    response = requests.get(URL, params={"query": query, "key": API_KEY})
    if response.status_code != 200:
        st.error(f"❌ API Error {response.status_code}")
        return []

    data = response.json()
    if "claims" not in data:
        return []

    results = []
    for claim in data["claims"]:
        for review in claim.get("claimReview", []):
            results.append({
                "claim": claim['text'],
                "fact_checker": review['publisher']['name'],
                "verdict": review['textualRating'],
                "verdict_label": classify_verdict(review['textualRating']),
                "url": review['url'],
                "severity_score": assign_severity(claim['text'])
            })
    return results

# --- Visualization tools ---
def generate_word_cloud(claims):
    text = " ".join([f"{c['claim']} {c['verdict']}" for c in claims])
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    return img

def analyze_sentiment(text):
    score = TextBlob(text).sentiment.polarity
    return {
        "positive": 80 if score > 0.1 else 10 if score < -0.1 else 20,
        "neutral": 10 if score > 0.1 else 20 if score < -0.1 else 60,
        "negative": 10 if score > 0.1 else 70 if score < -0.1 else 20
    }

def calculate_average_severity(results):
    return sum(r['severity_score'] for r in results) / len(results) if results else 0

# --- UI Logic ---
def factcheck_input():
    st.title("FactCheck News")
    with st.form("factcheck_form"):
        text_input = st.text_area("Enter a news headline or statement", placeholder="e.g. The Earth is flat")
        submitted = st.form_submit_button("Check Fact")

        if submitted and text_input.strip():
            results = check_fake_news(text_input)
            if not results:
                st.error("No results found for the claim.")
                return

            st.subheader("Prediction Result")
            avg_severity = calculate_average_severity(results)

            for r in results:
                st.markdown(f"**Claim:** {r['claim']}")
                st.markdown(f"**Fact-Checker:** {r['fact_checker']}")
                st.markdown(f"**Verdict:** {r['verdict_label']} ({r['verdict']})")
                st.markdown(f"**Severity Score:** {r['severity_score']}/10")
                st.markdown(f"**URL:** {r['url']}")

            st.subheader("Word Cloud")
            st.image(generate_word_cloud(results), use_container_width=True)

            st.subheader("Content Severity Rating")
            st.progress(avg_severity / 10)
            st.text(f"{avg_severity:.1f}: {'MISLEADING' if avg_severity >= 5 else 'LOW IMPACT'}")

            credibility_score = len(results)
            st.subheader("Source Credibility Score")
            st.progress(min(credibility_score / 10, 1.0))
            st.text("Reliable" if credibility_score >= 5 else "Partially Reliable")

            sentiment = analyze_sentiment(text_input)
            st.subheader("Sentiment Distribution")
            st.text(f"Positive: {sentiment['positive']}%\nNeutral: {sentiment['neutral']}%\nNegative: {sentiment['negative']}%")
        elif submitted:
            st.error("Please enter a valid input.")

def feedback_section():
    st.title("Feedback")
    with st.form("feedback_form"):
        accuracy = st.select_slider("Accuracy of results?", options=[1, 2, 3, 4, 5], value=3)
        comments = st.text_area("Any comments?")
        experience = st.select_slider("Overall experience?", options=[1, 2, 3, 4, 5], value=4)
        submitted = st.form_submit_button("Submit")
        if submitted:
            if 'user' in st.session_state:
                users_collection.update_one(
                    {"email": st.session_state['user']},
                    {"$push": {"feedback": {
                        "accuracy": accuracy,
                        "experience": experience,
                        "comments": comments
                    }}}
                )
            st.success("Thank you for your feedback!")

def main():
    st.set_page_config(page_title="FactCheck App", layout="wide")
    st.sidebar.title("📂 Navigation")
    st.sidebar.markdown("---")

    if st.session_state['authenticated']:
        st.sidebar.markdown("**Welcome:** " + st.session_state['user'])
        st.sidebar.markdown("### Pages")
        pages = {"📰 FactCheck": "FactCheck", "💬 Feedback": "Feedback"}
    else:
        st.sidebar.markdown("### Auth")
        pages = {"🔐 Login": "Login", "📝 Sign Up": "Sign Up"}

    selected_page = st.session_state.get('page', list(pages.values())[0])

for label, target in pages.items():
    if st.sidebar.button(label):
        selected_page = target

if selected_page != st.session_state.get('page'):
    st.session_state['page'] = selected_page
    st.experimental_rerun()

    page = st.session_state.get('page', list(pages.values())[0])

    if page == "Login": login()
    elif page == "Sign Up": signup()
    elif page == "FactCheck": factcheck_input()
    elif page == "Feedback": feedback_section()

if __name__ == "__main__":
    main()
