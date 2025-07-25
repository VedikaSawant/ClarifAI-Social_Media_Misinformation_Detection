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
from streamlit_cookies_manager import CookieManager

# --- Page Config (must be the first Streamlit command) ---
st.set_page_config(page_title="FactCheck App", layout="wide")

# Initialize Cookie Manager
cookies = CookieManager()

# --- IMPORTANT: Wait for cookies to be ready before proceeding with authentication logic ---
if not cookies.ready():
    st.warning("Loading cookies...")
    st.stop() # Stops the script execution until the cookies are ready
              # Streamlit will automatically rerun once the component is ready.

# --- Initialize session state from cookie ---
# Do this ONCE, at the very top of the script.
if 'authenticated' not in st.session_state:
    # Now, cookies are guaranteed to be ready here
    if cookies.get('username'):
        # If cookie exists, set session state from cookie
        st.session_state['authenticated'] = True
        st.session_state['username'] = cookies.get('username')
        st.session_state['user'] = cookies.get('user_email')
        st.session_state['page'] = 'FactCheck'
    else:
        # If no cookie, initialize session state as new
        st.session_state['authenticated'] = False
        st.session_state['page'] = 'Login'
        st.session_state['username'] = ''
        st.session_state['user'] = ''

# ... (the rest of your app.py code remains the same from the previous correction) ...

# --- Load env and MongoDB connection ---
load_dotenv()
MONGO_URI = st.secrets.get("MONGO_URI", os.getenv("MONGO_URI"))
API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY"))

client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("factcheck_db")
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

        if submitted:
            if email and password:
                user = users_collection.find_one({"email": email})
                if user and verify_password(user["password"], password):
                    st.session_state.authenticated = True
                    st.session_state.user = email
                    st.session_state.username = user.get('username', email)
                    st.session_state.page = "FactCheck"

                    # Set cookies
                    cookies['username'] = st.session_state.username
                    cookies['user_email'] = st.session_state.user
                    cookies.save()

                    st.success("Successfully logged in!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            else:
                st.error("Please fill in all fields.")

def signup():
    st.title("Create New Account")
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if username and email and password:
                if users_collection.find_one({"email": email}):
                    st.error("Email is already in use")
                else:
                    users_collection.insert_one({
                        "username": username,
                        "email": email,
                        "password": hash_password(password),
                        "feedback": []
                    })
                    st.session_state.authenticated = True
                    st.session_state.user = email
                    st.session_state.username = username
                    st.session_state.page = "FactCheck"

                    # Set cookies
                    cookies['username'] = st.session_state.username
                    cookies['user_email'] = st.session_state.user
                    cookies.save()

                    st.success("Account created! Logging in...")
                    st.rerun()
            else:
                st.error("Please fill in all fields.")

# --- FactCheck API Setup ---
URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# --- Verdict classification ---
def classify_verdict(verdict_text):
    verdict_text = verdict_text.lower()
    if any(x in verdict_text for x in ["false", "misleading", "incorrect", "untrue", "fake", "inaccurate", "not true"]):
        return "❌ False"
    elif any(x in verdict_text for x in ["true", "accurate", "correct", "mostly true"]):
        return "✅ True"
    else:
        return "⚠️ Unclear"

# --- Severity logic ---
def assign_severity(claim):
    claim = claim.lower()
    keywords = {
        10: ["vaccine", "covid-19", "health", "medical"],
        9: ["explosion", "hazard", "attack", "war"],
        8: ["climate change", "pollution", "disaster"],
        7: ["election", "fraud", "corruption", "government"],
        6: ["technology", "robot", "science", "AI", "radar"],
        5: ["celebrity", "sports", "entertainment"],
    }
    for score, words in keywords.items():
        if any(word in claim for word in words):
            return score
    return 4 # Fallback score

# --- Core logic ---
def check_fake_news(query):
    response = requests.get(URL, params={"query": query, "key": API_KEY})
    if response.status_code != 200:
        st.error(f"❌ API Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    if "claims" not in data or not data["claims"]:
        return []

    results = []
    for claim in data["claims"]:
        if "claimReview" in claim:
            for review in claim["claimReview"]:
                results.append({
                    "claim": claim.get('text', 'N/A'),
                    "fact_checker": review.get('publisher', {}).get('name', 'N/A'),
                    "verdict": review.get('textualRating', 'N/A'),
                    "verdict_label": classify_verdict(review.get('textualRating', '')),
                    "url": review.get('url', '#'),
                    "severity_score": assign_severity(claim.get('text', ''))
                })
    return results

# --- Visualization tools ---
def generate_word_cloud(claims):
    text = " ".join([f"{c['claim']} {c['verdict']}" for c in claims])
    if not text.strip():
        return None
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    return img

def analyze_sentiment(text):
    score = TextBlob(text).sentiment.polarity
    if score > 0.1:
        return {"positive": 80, "neutral": 10, "negative": 10}
    elif score < -0.1:
        return {"positive": 10, "neutral": 20, "negative": 70}
    else:
        return {"positive": 20, "neutral": 60, "negative": 20}

def calculate_average_severity(results):
    if not results:
        return 0
    return sum(r['severity_score'] for r in results) / len(results)

# --- UI Logic ---
def factcheck_input():
    st.title("FactCheck News 📰")
    with st.form("factcheck_form"):
        text_input = st.text_area("Enter a news headline or statement", placeholder="e.g. The Earth is flat")
        submitted = st.form_submit_button("Check Fact")

        if submitted and text_input.strip():
            with st.spinner("Analyzing claim..."):
                results = check_fake_news(text_input)

            if not results:
                st.error("No fact-check results found for this claim.")
                return

            st.subheader("Prediction Results")
            for r in sorted(results, key=lambda x: x['severity_score'], reverse=True):
                with st.container(border=True):
                    st.markdown(f"**Claim:** {r['claim']}")
                    st.markdown(f"**Fact-Checker:** {r['fact_checker']}")
                    st.markdown(f"**Verdict:** {r['verdict_label']} ({r['verdict']})")
                    st.markdown(f"**Severity Score:** `{r['severity_score']}/10`")
                    st.markdown(f"**Source:** [{r['url']}]({r['url']})")

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Content Severity Rating")
                avg_severity = calculate_average_severity(results)
                st.progress(avg_severity / 10)
                st.markdown(f"**Average Score: {avg_severity:.1f} / 10**")
                st.info('MISLEADING' if avg_severity >= 5 else 'LOW IMPACT')

            with col2:
                st.subheader("Source Credibility")
                credibility_score = len(results)
                st.progress(min(credibility_score / 10, 1.0))
                st.markdown(f"**Found {credibility_score} fact-check reviews.**")
                st.info("Reliable" if credibility_score >= 5 else "Partially Reliable")

            # Calculate false percentage for refined Overall Verdict
            false_count = sum(1 for r in results if r['verdict_label'] == "❌ False")
            total_claims = len(results)
            false_percentage = (false_count / total_claims) * 100 if total_claims > 0 else 0

            # OVERALL VERDICT
            st.subheader("Overall Verdict")
            if credibility_score < 5:
                st.info(f"❓ Overall Verdict: Verification is **LIMITED ({credibility_score} sources)**. The overall accuracy is unclear. Exercise caution and seek more information.")
            elif false_percentage >= 70:
                st.error(f"🚨 Overall Verdict: This claim is **HIGHLY MISLEADING** ({false_percentage:.0f}% false verdicts) and has been extensively debunked by reliable sources.")
            elif false_percentage >= 40:
                st.warning(f"⚠️ Overall Verdict: This claim is **PARTIALLY MISLEADING** ({false_percentage:.0f}% false verdicts). Exercise caution.")
            else: # false_percentage < 40 and credibility_score >= 5
                st.success(f"✅ Overall Verdict: This claim appears **MOSTLY ACCURATE** ({false_percentage:.0f}% false verdicts) or of low impact, supported by reliable fact-checking.")
            
            st.subheader("Sentiment & Word Cloud")
            col3, col4 = st.columns([1, 2])
            with col3:
                sentiment = analyze_sentiment(text_input)
                st.markdown("**Sentiment Distribution**")
                st.text(f"Positive: {sentiment['positive']}%\nNeutral:  {sentiment['neutral']}%\nNegative: {sentiment['negative']}%")
            with col4:
                st.markdown("**Key Terms**")
                wordcloud_img = generate_word_cloud(results)
                if wordcloud_img:
                    st.image(wordcloud_img, use_container_width=True)

        elif submitted:
            st.error("Please enter a valid input.")

def feedback_section():
    st.title("Feedback 💬")
    st.write("Help us improve! Let us know what you think.")
    with st.form("feedback_form"):
        accuracy = st.select_slider("How accurate were the results?", options=[1, 2, 3, 4, 5], value=3)
        experience = st.select_slider("Rate your overall experience:", options=[1, 2, 3, 4, 5], value=4)
        comments = st.text_area("Any comments or suggestions?")
        submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            if 'user' in st.session_state and st.session_state['user']:
                users_collection.update_one(
                    {"email": st.session_state['user']},
                    {"$push": {"feedback": {
                        "accuracy": accuracy,
                        "experience": experience,
                        "comments": comments
                    }}}
                )
                st.success("Thank you for your feedback! ✅")
            else:
                st.error("You must be logged in to submit feedback.")

# Main app logic
def main():
    st.sidebar.title("Page Selection")

    if st.session_state.authenticated:
        st.sidebar.markdown(f"**Welcome, {st.session_state.get('username', '')}!**")
        if st.sidebar.button("📰 FactCheck", use_container_width=True):
            st.session_state.page = "FactCheck"
            st.rerun()
        if st.sidebar.button("💬 Feedback", use_container_width=True):
            st.session_state.page = "Feedback"
            st.rerun()
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout", use_container_width=True):
            # Delete cookies
            del cookies['username']
            del cookies['user_email']
            cookies.save()
            
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.page = "Login"
            st.session_state.username = ''
            st.session_state.user = ''
            st.rerun()

    else: # Not authenticated
        if st.sidebar.button("🔐 Login", use_container_width=True):
            st.session_state.page = "Login"
            st.rerun()
        if st.sidebar.button("📝 Sign Up", use_container_width=True):
            st.session_state.page = "Sign Up"
            st.rerun()

    # --- Page Router ---
    if st.session_state.page == "Login":
        login()
    elif st.session_state.page == "Sign Up":
        signup()
    elif st.session_state.page == "FactCheck":
        factcheck_input()
    elif st.session_state.page == "Feedback":
        feedback_section()

if __name__ == "__main__":
    main()
