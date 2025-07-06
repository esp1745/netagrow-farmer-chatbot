from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from chatbot import ZambianFarmerChatbot
import json
import requests  # Add this import at the top with others
import jwt

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the chatbot
chatbot = ZambianFarmerChatbot()

SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SUPABASE_USER_LOOKUP_URL = "https://eobkhsunhiqtfkgkaovv.supabase.co/functions/v1/user-lookup"

def get_user_info(email=None, phone=None):
    headers = {
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    params = {}
    if email:
        params["email"] = email
    if phone:
        params["phone"] = phone
    params["include"] = "basic,farms,crops"
    try:
        response = requests.get(SUPABASE_USER_LOOKUP_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def get_farm_info_from_db(email):
    url = "https://eobkhsunhiqtfkgkaovv.supabase.co/functions/v1/marketing-data"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
    }
    payload = {"email": email}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'farm_name': data.get('farm_name'),
                'location': data.get('location'),
                'size': data.get('size'),
                'crops': data.get('crops')
            }
        else:
            return None
    except Exception as e:
        print(f"Error calling Supabase Edge Function: {e}")
        return None

def get_user_id_from_token():
    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return decoded.get('sub')  # 'sub' is the user ID in Supabase
    except Exception as e:
        print(f"JWT decode error: {e}")
        return None

def get_farm_info_from_user_lookup(search_value, search_type):
    headers = {
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    params = {search_type: search_value, "include": "basic,farms,crops"}
    try:
        response = requests.get(SUPABASE_USER_LOOKUP_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                return data["data"]
            else:
                return None
        else:
            print(f"User lookup failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Error calling User Lookup API: {e}")
        return None

@app.route('/')
def home():
    return "Zambian Farmer Chatbot API is running."

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        language = data.get('language', 'english')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get response from chatbot
        response = chatbot.get_response(user_message, language)
        
        return jsonify({
            'response': response,
            'language': language
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<location>')
def get_weather(location):
    """Get weather information for a specific location"""
    try:
        weather_info = chatbot.get_weather_info(location)
        return jsonify(weather_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-prices')
def get_market_prices():
    """Get current market prices for common crops"""
    try:
        prices = chatbot.get_market_prices()
        return jsonify(prices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crop-info/<crop_name>')
def get_crop_info(crop_name):
    """Get detailed information about a specific crop"""
    try:
        crop_info = chatbot.get_crop_information(crop_name)
        return jsonify(crop_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pest-disease/<query>')
def identify_pest_disease(query):
    """Identify pests or diseases based on symptoms"""
    try:
        identification = chatbot.identify_pest_disease(query)
        return jsonify(identification)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/languages')
def get_supported_languages():
    """Get list of supported languages"""
    languages = [
        {'code': 'english', 'name': 'English'},
        {'code': 'bemba', 'name': 'Bemba'},
        {'code': 'njanja', 'name': 'Nyanja'},
        {'code': 'tonga', 'name': 'Tonga'},
        {'code': 'lozi', 'name': 'Lozi'}
    ]
    return jsonify(languages)

@app.route('/api/ask', methods=['POST'])
def ask_chatbot():
    data = request.get_json()
    user_message = data.get('message', '')
    language = data.get('language', 'english')
    email = data.get('email')
    phone = data.get('phone')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    user_info = get_user_info(email=email, phone=phone)
    if not user_info or not user_info.get("data"):
        return jsonify({"response": "Sorry, I couldn't find your farm information in the database."})
    
    # Extract farm information for context
    user_data = user_info['data']
    farms = user_data.get('farms', [])
    
    # Build farm context
    farm_context = ""
    if farms:
        farm_context = f"Farmer: {user_data.get('full_name', 'Unknown')}\n"
        farm_context += f"Location: {user_data.get('farmer_profile', {}).get('location', 'Not specified')}\n"
        farm_context += f"Total Farms: {len(farms)}\n"
        
        for i, farm in enumerate(farms, 1):
            farm_context += f"\nFarm {i}: {farm.get('name', 'Unknown Farm')}\n"
            farm_context += f"  Size: {farm.get('size', 0)} hectares\n"
            farm_context += f"  Location: {farm.get('location', 'Not specified')}\n"
            
            fields = farm.get('fields', [])
            if fields:
                farm_context += f"  Fields: {len(fields)}\n"
                for field in fields:
                    farm_context += f"    - {field.get('name', 'Unknown Field')} ({field.get('size', 0)} ha, {field.get('soil_type', 'unknown soil')})\n"
                    
                    crops = field.get('crops', [])
                    if crops:
                        farm_context += f"      Crops:\n"
                        for crop in crops:
                            status = crop.get('status', 'unknown')
                            variety = crop.get('variety', '')
                            planting_date = crop.get('planting_date', '')
                            harvest_date = crop.get('expected_harvest_date', '')
                            
                            crop_info = f"        • {crop.get('name', 'Unknown')}"
                            if variety:
                                crop_info += f" ({variety})"
                            if status:
                                crop_info += f" - Status: {status}"
                            if planting_date:
                                crop_info += f" - Planted: {planting_date}"
                            if harvest_date:
                                crop_info += f" - Expected Harvest: {harvest_date}"
                            
                            farm_context += crop_info + "\n"
    else:
        farm_context = f"Farmer: {user_data.get('full_name', 'Unknown')}\nNo farm data available yet."
    
    # Create AI context
    ai_context = f"""You are a helpful Zambian farming assistant. Here is the farmer's information:

{farm_context}

Farmer's Question: {user_message}

Please provide a friendly, helpful response in {language} that:
1. Addresses their specific question
2. Uses their farm information when relevant
3. Provides practical farming advice
4. Is encouraging and supportive
5. Uses simple, clear language suitable for farmers

Keep your response conversational and under 200 words."""

    # Generate AI response
    try:
        ai_response = chatbot._get_openai_response(ai_context, language)
        return jsonify({
            "response": ai_response
        })
    except Exception as e:
        # Fallback response if AI fails
        return jsonify({
            "response": f"Hello {user_data.get('full_name', 'farmer')}! I can see you have {len(farms)} farm(s). How can I help you with your farming today?"
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port) 