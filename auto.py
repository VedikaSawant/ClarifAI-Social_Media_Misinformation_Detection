import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 🔹 Retrieve the API Key from environment variable
API_KEY = os.getenv("API_KEY")  # This retrieves the API key from the environment variable

if API_KEY is None:
    print("❌ API Key not set!")
    exit()

# 🔹 Define the API endpoint
URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

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

# 🔹 Function to check news credibility
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
            for claim in data["claims"]:
                print(f"\n🔹 Claim: {claim['text']}")
                for review in claim.get("claimReview", []):
                    print(f"✅ Fact-Checker: {review['publisher']['name']}")
                    print(f"🧐 Verdict: {review['textualRating']}")
                    print(f"🔗 URL: {review['url']}")
                    print(f"⚖️ Severity Score: {severity_score}/10")

                    # Safely handle missing reviewDate field
                    review_date = review.get("reviewDate", "N/A")
                    print(f"📅 Review Date: {review_date}\n")
        else:
            print("❌ No fact-check results found.")
    else:
        print("❌ Error:", response.status_code, response.json())

# Test with multiple claims
claims = [
    "Drinking bleach can cure COVID-19.",
    "Vaccines cause autism in children.",
    "You should never use seat belts in a car because they’re dangerous.",
    "Microwaving plastic containers can release toxic chemicals.",
    "Climate change is a hoax invented by scientists.",
    "Plastic waste doesn't harm the environment if it's recycled properly.",
    "The 2020 US Presidential Election was rigged and stolen.",
    "Immigrants are taking all the jobs in the United States.",
    "The moon landing was faked by NASA.",
    "Aliens are controlling our government from the White House.",
    "Cryptocurrency is a guaranteed way to get rich quickly.",
    "The stock market will crash if we raise the minimum wage.",
    "You don’t need a high school diploma to get a good job.",
    "Student loans are completely forgivable if you claim bankruptcy.",
    "Tom Hanks was arrested for child trafficking.",
    "Beyoncé secretly ran a pyramid scheme."
]


# Iterate through the claims and check them
for claim in claims:
    check_fake_news(claim)