# ClarifAI - Bringing Clarity Through AI Innovation

## Project Overview

ClarifAI is an innovative web application developed to combat the pervasive issue of misinformation on social media. It provides users with real-time verification of news headlines and statements by leveraging advanced fact-checking capabilities and sentiment analysis, promoting a more informed digital environment. Born from the Amdocs GenAI Graduate Hackathon 2024, ClarifAI aims to bring clarity through AI innovation.

Misinformation Detection and Fact-Checking on Social Media.🔍

## Features

* **Real-time Fact-Checking:** Instantly verify news headlines and statements against a comprehensive database of fact-checked claims via the Google Fact-Check API.
* **Dynamic Verdict System:** Provides a nuanced "Overall Verdict" by synthesizing individual claim verdicts, content severity, and source credibility, offering clear insights (e.g., "Highly Misleading," "Mostly Accurate").
* **Sentiment Analysis:** Analyzes the sentiment (positive, neutral, negative) of entered statements using TextBlob, adding another layer of context.
* **Content Severity Scoring:** Implements a keyword-based system to assign severity scores, indicating the potential impact of a claim.
* **Secure User Authentication:** Features a robust user registration and login system with password hashing (bcrypt) and persistent sessions.
* **User Feedback System:** Allows users to submit feedback on accuracy and overall experience, enabling continuous improvement and iterative development.
* **Word Cloud Generation:** Visualizes key terms from fact-checked results for quick insights.

## Tech Stack

ClarifAI is built using a modern and efficient tech stack:

* **Frontend & Framework:** `Streamlit` 🌐 (for rapid web application development and interactive UI)
* **Backend & Logic:** `Python` 🐍
* **Database:** `MongoDB Atlas` 🍃 (cloud-hosted NoSQL database for user data and feedback storage)
* **Core API:** `Google Fact-Check API` 🔑 (for fetching real-time fact-check data)
* **Authentication:** `bcrypt` 🛡️ (for secure password hashing)
* **Sentiment Analysis:** `TextBlob` 📖 (for natural language processing and sentiment scoring)
* **Session Management:** `streamlit_cookies_manager` 🍪 (for persistent user sessions)
* **Data Visualization:** `WordCloud` 📝 (for generating word cloud images from text)

## Instructions to Run the Project:

### Clone the Repository:

Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/VedikaSawant/ClarifAI-Social_Media_Misinformation_Detection.git
````

### Navigate to the Project Directory:

```bash
cd clarifai_streamlit
```

### Install Dependencies:

Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
```

For macOS/Linux:

```bash
source venv/bin/activate
```

For Windows:

```bash
venv\Scripts\activate
```

Install required libraries:

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables:

Create a `.env` file in the project directory and add the following variables:

```
MONGO_URI="your_mongodb_atlas_connection_string"
API_KEY="your_google_fact_check_api_key"
```

  * **Obtaining MONGO\_URI:**
     To get this, you must first have a MongoDB Atlas account and a deployed cluster.
   
     **Prerequisites:**
     
     1. Create a MongoDB Atlas account.
     
     2. Deploy a new cluster (a Free Tier cluster is sufficient for testing).
     
     **Steps to Get the URI:**
     
     1. Log in to MongoDB Atlas and go to your Clusters dashboard.
     
     2. Locate your cluster and click the "Connect" button.
     
     3. Select "Connect your application."
     
     4. Copy the connection string (the MONGO_URI).
     
     *Important: Replace the <password> placeholder in the copied URI with the actual password for the database user you created during setup.*


  * **Obtaining API\_KEY🗝️ (Google Fact-Check API):**
     This requires a Google Cloud project with the necessary API enabled.
     
     **Prerequisites:**
     
     1. Create a Google Cloud Project in the Google Cloud Console.
     
     2. Enable the Fact Check API for that project.
     
     **Steps to Get the Key:**
     1. In the Google Cloud Console, navigate to "APIs & Services" $\rightarrow$ "Credentials.
     
     2. "Click "+ CREATE CREDENTIALS" and choose "API key"
     
     3. Copy the generated API Key.
     
     *Best Practice: Edit the key to add an API restriction, selecting only the Fact Check API to ensure security.*


### Run the Streamlit Application:

To start the app, run:

```bash
streamlit run app.py
```

Open a web browser and visit `http://localhost:[port]` (usually `8501`) given in the output to access the app.🚀

## Usage

### Authentication:

  * **Sign Up:** Create a new user account with your username, email, and password.
  * **Login:** Use your email and password to log in to the app.

### Fact-Check:

  * Enter a news headline or statement in the "FactCheck News" section to verify if it's true or fake.🧐

### Feedback:

  * After using the app, you can provide feedback on the results and experience in the "Feedback" section.⭐

## Demo / Preview

  * [**Live Demo**](https://clarifai-social-media-misinformation-detection.streamlit.app/)🌐
  * [**Demo on Youtube**](https://youtu.be/EcwSyNZv2Zw)📺

## Contributing

Contributions are welcome🤝\! If you have suggestions or want to improve the project, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

## Acknowledgements

  * Developed as a semifinalist project in the **Amdocs GenAI Graduate Hackathon 2024**.
  * Powered by the [Google Fact-Check API](https://www.google.com/search?q=https://developers.google.com/fact-check/api).

<!-- end list -->
