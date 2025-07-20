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
* **Environment Management:** `python-dotenv` ⚙️ (for secure handling of environment variables)
* **Data Visualization:** `WordCloud` 📝 (for generating word cloud images from text)

## Instructions to Run the Project:

### Clone the Repository:

Clone the repository to your local machine using the following command:

```bash
git clone [repository_link]
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

  * **MONGO\_URI:** Obtain this from your MongoDB Atlas cluster.
  * **API\_KEY:** Get this from the Google Cloud Console for the Fact-Check API.🗝️

### Run the Streamlit Application:

To start the app, run:

```bash
streamlit run app.py
```

Open a web browser and visit `http://localhost:[port]` (usually `8501`) to access the app.🚀

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
