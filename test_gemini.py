"""
Test Gemini API connection
"""
import os

# Set the API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyA9oQw2haRe86sFC_Yo9KGUWsFvaQmY1wY'

try:
    import google.generativeai as genai
    
    # Configure
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    
    # Test with a simple prompt
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Gemini connected successfully!' in one sentence.")
    
    print("SUCCESS! GEMINI CONNECTION WORKS!")
    print(f"Response: {response.text}")
    print("La chiave Gemini funziona perfettamente!")
    
except ImportError:
    print("❌ Libreria google-generativeai non installata")
    print("Run: pip install google-generativeai")
except Exception as e:
    print(f"❌ GEMINI CONNECTION FAILED: {e}")

