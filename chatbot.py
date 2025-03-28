import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
import sqlite3

# Initialize OpenAI model
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, openai_api_key="your-api-key-here")


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

def get_user_preferences():
    """Collects user preferences for language learning."""
    target_language = input("What language do you want to learn? ")
    native_language = input("What is your native language? ")
    proficiency = input("What is your current level in the target language? (Beginner/Intermediate/Advanced) ")
    return target_language, native_language, proficiency

def generate_conversation_scene(target_language, native_language, proficiency):
    """Generates a conversational scene based on user preferences."""
    prompt = f"""
    You are a language tutor. Create a conversational scene in {target_language} for a student whose native language is {native_language} and is at {proficiency} level. 
    The scene should be engaging and relevant to their skill level.
    """
    response = llm.invoke([SystemMessage(content=prompt)])
    return response.content

def chat_with_user():
    """Handles the chatbot interaction."""
    target_language, native_language, proficiency = get_user_preferences()
    scene = generate_conversation_scene(target_language, native_language, proficiency)
    print(f"Chatbot: {scene}")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        response = llm.invoke([HumanMessage(content=user_input)])
        print(f"Chatbot: {response.content}")
        
        # TODO: Implement mistake detection and store in database

def main():
    setup_database()
    chat_with_user()

if __name__ == "__main__":
    main()
