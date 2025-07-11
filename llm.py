from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

result = model.invoke('What is the capital of India')

print(result.content)