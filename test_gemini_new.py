"""
Test Gemini API with NEW library
"""
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyA9oQw2haRe86sFC_Yo9KGUWsFvaQmY1wY'

try:
    from google import genai
    
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents='Say "Gemini connected successfully!" in one sentence.'
    )
    
    print("SUCCESS! GEMINI CONNECTION WORKS!")
    print(f"Response: {response.text}")
    print("\nLa chiave Gemini funziona perfettamente!")
    print("Modello: gemini-2.0-flash-exp")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("\nProvo con modello alternativo...")
    try:
        from google import genai
        client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents='Test connection'
        )
        print("SUCCESS with gemini-1.5-flash!")
        print(f"Response: {response.text}")
    except Exception as e2:
        print(f"ERROR anche con 1.5-flash: {e2}")

