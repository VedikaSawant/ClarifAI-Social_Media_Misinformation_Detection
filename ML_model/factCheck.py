import streamlit as st
import requests

st.set_page_config(page_title="ClarifAI - Misinformation Detection", layout="centered")

def get_prediction_from_api(text):
    url = "http://127.0.0.1:5000/api/fact-check"  # Your API URL
    data = {'content': text}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}")  # Display error in Streamlit
        return None  # Return None to indicate failure


page = st.sidebar.selectbox("Navigate", ["Fact Check", "Results"])

if page == "Fact Check":
    st.header("FACTCHECK")
    text_input = st.text_area("TEXT", "Enter textual input")
    if st.button("SUBMIT"):
      if not text_input:
        st.warning("Please enter text to check")
      else:
        result = get_prediction_from_api(text_input)
        if result: # Check if the API call was successful
            prediction = result.get('verdict')
            source = result.get('source')

            if prediction:
                st.session_state["results"] = {"prediction": prediction, "source": source}
                st.success(f"Analysis completed! (Source: {source.upper()}). Navigate to Results.")
            else:
                st.error(result.get("error", "An error occurred."))
        

elif page == "Results":
    st.header("RESULTS")
    if "results" in st.session_state:
        results = st.session_state["results"]
        st.subheader("Prediction")
        st.write(f"{results['prediction']} News (Source: {results['source'].upper()}")
    else:
        st.warning("No results available. Please perform a Fact Check first.")
