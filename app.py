import streamlit as st
import os
from duckduckgo_search import DDGS
from google import genai

st.set_page_config(page_title="OmniSearch Agent", page_icon="🔍", layout="wide")

st.title("🔍 OmniSearch Agent")
st.markdown("**Autonomous Multi-Step Search & Reasoning AI Agent**")

st.sidebar.header("⚙️ Agent Settings")
user_api_key = st.sidebar.text_input(
    "Gemini API Key (Optional):", 
    type="password",
    help="Leave blank to use the app's default secret key."
)

raw_key = user_api_key.strip() if user_api_key else ""
api_key = raw_key or st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

query = st.text_input(
    "Enter your research prompt:", 
    placeholder="e.g., Which is the most popular street food in India?"
)

def fetch_web_results(search_query, num_results=5):
    """Fetches real-time web search results using DuckDuckGo."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(search_query, max_results=num_results):
            results.append(f"Title: {r.get('title')}\nLink: {r.get('href')}\nSummary: {r.get('body')}\n")
    return "\n---\n".join(results)

if st.button("Run OmniSearch Agent", type="primary"):
    if not query:
        st.warning("Please enter a research prompt.")
    elif not api_key:
        st.error("Missing Gemini API Key. Please enter a key in the sidebar or configure GEMINI_API_KEY in Streamlit Secrets.")
    else:
        with st.status("Agent processing query...", expanded=True) as status:
            st.write("📖 **1. Read:** Gathering live web data from search engines...")
            search_context = fetch_web_results(query)
            
            st.write("🧠 **2. Reason:** Synthesizing web context with Gemini 3.6 Flash...")
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                You are OmniSearch Agent, an autonomous research assistant powered by Gemini 3.6 Flash.
                User Prompt: {query}

                Live Web Context Retrieved:
                {search_context}

                Task:
                1. Analyze the web context.
                2. Produce a clear, highly accurate, and concise executive summary answering the user's prompt.
                3. Include key details and cite source URLs directly where relevant.
                """
                
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )
                
                st.write("⚙️ **3. Act:** Rendering executive research brief...")
                status.update(label="Research Complete!", state="complete", expanded=False)
                
                st.success("Analysis Complete!")
                st.subheader("Synthesized Executive Report")
                st.markdown(response.text)
                
                with st.expander("View Raw Web Context Retrieved"):
                    st.text(search_context)
                    
            except Exception as e:
                status.update(label="Execution Error", state="error", expanded=False)
                st.error(f"API Error: {str(e)}\n\nPlease ensure your Gemini API key is active and correctly configured.")
