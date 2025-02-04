# ClarifAI-Bringing-clarity-through-AI-innovation.
Misinformation Detection and Fact-Checking on Social Media


Add this file in app and ML_model folders : 
https://drive.google.com/file/d/1WnzgkFwsQNzm0l29ZshIfJ9PKRCqEzI4/view?usp=sharing

<h2>Instructions to Run the Project:</h2>

<h3>Clone the Repository:</h3>
<p>Clone the repository to your local machine using the following command:</p>
<pre><code>git clone [repository_link]</code></pre>

<h3>Navigate to the Project Directory:</h3>
<pre><code>cd clarifai_streamlit</code></pre>

<h3>Install Dependencies:</h3>
<p>Create and activate a virtual environment (optional but recommended):</p>
<pre><code>python -m venv venv</code></pre>
<p>For macOS/Linux:</p>
<pre><code>source venv/bin/activate</code></pre>
<p>For Windows:</p>
<pre><code>venv\Scripts\activate</code></pre>

<p>Install required libraries:</p>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>Set Up Environment Variables:</h3>
<p>Create a <code>.env</code> file in the project directory and add the following variables:</p>
<pre><code>MONGO_URI=[your_mongo_uri]
API_KEY=[your_api_key]</code></pre>

<h3>Run the Streamlit Application:</h3>
<p>To start the app, run:</p>
<pre><code>streamlit run app.py</code></pre>
<p>Open a web browser and visit http://localhost:[port] to access the app.</p>

<h3>Authentication:</h3>
<ul>
    <li><strong>Sign Up:</strong> Create a new user account with your username, email, and password.</li>
    <li><strong>Login:</strong> Use your email and password to log in to the app.</li>
    <li><strong>Fact-Check:</strong> Enter a news headline or statement in the <strong>"FactCheck News"</strong> section to verify if it's true or fake.</li>
</ul>

<h3>Feedback:</h3>
<p>After using the app, you can provide feedback on the results and experience in the <strong>"Feedback"</strong> section.</p>
