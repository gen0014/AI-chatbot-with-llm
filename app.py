import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import sqlite3
import os
import streamlit as st # type: ignore
import matplotlib.pyplot as plt
import pandas as pd
import io

# Set OpenAI API key (Use environment variable for security)
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Initialize OpenAI model
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

def setup_database():
    """Creates an SQLite database to store user mistakes."""
    conn = sqlite3.connect("mistakes.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mistakes (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_input TEXT,
                      corrected_text TEXT,
                      mistake_type TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def detect_mistakes(user_input):
    """Uses OpenAI to analyze user input and detect mistakes."""
    prompt = f"Analyze the following sentence for grammar, spelling, and vocabulary mistakes. If there are errors, provide the corrected version and categorize the mistake.\n\nSentence: {user_input}"
    response = llm.invoke([SystemMessage(content=prompt)])
    return response.content

def store_mistake(user_input, corrected_text, mistake_type):
    """Stores mistakes in SQLite database."""
    conn = sqlite3.connect("mistakes.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mistakes (user_input, corrected_text, mistake_type) VALUES (?, ?, ?)",
                   (user_input, corrected_text, mistake_type))
    conn.commit()
    conn.close()

def generate_progress_chart():
    """Generates a progress chart showing mistake trends."""
    conn = sqlite3.connect("mistakes.db")
    df = pd.read_sql_query("SELECT mistake_type FROM mistakes", conn)
    conn.close()
    
    if df.empty:
        return "No data available for progress tracking."
    
    mistake_counts = df['mistake_type'].value_counts()
    
    plt.figure(figsize=(6,4))
    mistake_counts.plot(kind='bar', color=['red', 'blue', 'green'])
    plt.xlabel("Mistake Type")
    plt.ylabel("Frequency")
    plt.title("Mistake Analysis")
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    return buffer

def generate_summary():
    """Generates a summary of mistakes at the end of the session."""
    conn = sqlite3.connect("mistakes.db")
    df = pd.read_sql_query("SELECT mistake_type, COUNT(*) as count FROM mistakes GROUP BY mistake_type", conn)
    conn.close()
    
    if df.empty:
        return "No mistakes recorded this session. Great job!"
    
    summary = "### Summary of Mistakes\n\n"
    for index, row in df.iterrows():
        summary += f"- **{row['mistake_type']}**: {row['count']} occurrences\n"
    
    return summary

def main():
    setup_database()
    st.title("📚 AI-Powered Language Learning Chatbot")
    st.write("Improve your grammar and spelling with AI assistance!")
    
    user_input = st.text_area("Enter your sentence:")
    if st.button("Check Grammar"):
        if user_input:
            corrected_data = detect_mistakes(user_input)
            st.subheader("Correction")
            st.write(corrected_data)
            
            # Example parsing (custom parsing might be needed)
            corrected_text = "Corrected text here"
            mistake_type = "Mistake type here"
            store_mistake(user_input, corrected_text, mistake_type)
    
    st.subheader("📊 Progress Chart")
    if st.button("Show Progress"):
        buffer = generate_progress_chart()
        st.image(buffer, caption="Mistake Trends")

    st.subheader("📋 Session Summary")
    if st.button("Show Summary"):
        summary = generate_summary()
        st.markdown(summary)
    
if __name__ == "__main__":
    main()
