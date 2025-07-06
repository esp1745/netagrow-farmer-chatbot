import os
import json
import requests
from datetime import datetime
import re
from typing import Dict, List, Optional
from openai import OpenAI

class ZambianFarmerChatbot:
    def __init__(self):
        """Initialize the Zambian Farmer Chatbot with agricultural knowledge"""
        self.knowledge_base = self._load_knowledge_base()
        self.weather_api_key = os.getenv('WEATHER_API_KEY', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        
        # Initialize OpenAI client if API key is available
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.openai_available = True
                print("✅ OpenAI API configured successfully")
            except Exception as e:
                print(f"⚠️ OpenAI API configuration failed: {e}")
                self.openai_available = False
        else:
            print("⚠️ No OpenAI API key found - using rule-based responses")
            self.openai_available = False
        
        # Zambian agricultural context
        self.zambian_crops = [
            'maize', 'cassava', 'sweet potato', 'groundnuts', 'soybeans',
            'cotton', 'tobacco', 'sugarcane', 'coffee', 'tea', 'sunflower',
            'sorghum', 'millet', 'beans', 'cowpeas', 'pigeon peas'
        ]
        
        self.zambian_regions = [
            'Lusaka', 'Copperbelt', 'Central', 'Eastern', 'Western',
            'Southern', 'Northern', 'North-Western', 'Luapula', 'Muchinga'
        ]

    def _load_knowledge_base(self) -> Dict:
        """Load agricultural knowledge base"""
        knowledge = {
            'crops': {
                'maize': {
                    'planting_season': 'November to December',
                    'harvest_time': 'April to June',
                    'water_needs': 'Moderate to high',
                    'soil_type': 'Well-drained loamy soil',
                    'spacing': '75cm x 25cm',
                    'fertilizer': 'NPK 10-20-10 or 12-24-12',
                    'pests': ['Fall armyworm', 'Stem borers', 'Aphids'],
                    'diseases': ['Maize streak virus', 'Grey leaf spot', 'Rust']
                },
                'cassava': {
                    'planting_season': 'October to December',
                    'harvest_time': '8-18 months after planting',
                    'water_needs': 'Low to moderate',
                    'soil_type': 'Sandy loam to clay loam',
                    'spacing': '1m x 1m',
                    'fertilizer': 'NPK 12-24-12',
                    'pests': ['Cassava mealybug', 'Green mite'],
                    'diseases': ['Cassava mosaic virus', 'Bacterial blight']
                },
                'groundnuts': {
                    'planting_season': 'November to December',
                    'harvest_time': '4-5 months after planting',
                    'water_needs': 'Moderate',
                    'soil_type': 'Sandy loam',
                    'spacing': '60cm x 15cm',
                    'fertilizer': 'NPK 12-24-12',
                    'pests': ['Aphids', 'Thrips'],
                    'diseases': ['Groundnut rosette virus', 'Leaf spot']
                }
            },
            'weather_patterns': {
                'rainy_season': 'November to April',
                'dry_season': 'May to October',
                'average_rainfall': '800-1400mm annually'
            },
            'soil_types': {
                'sandy': 'Good for root crops like cassava',
                'clay': 'Good for rice and vegetables',
                'loamy': 'Best for most crops including maize'
            }
        }
        return knowledge

    def get_response(self, user_message: str, language: str = 'english') -> str:
        """Generate a response based on user input"""
        user_message_lower = user_message.lower().strip()
        
        # Check if this is a simple greeting first
        if self._is_greeting(user_message_lower):
            return self._get_greeting(language)
        
        # Hybrid: Weather queries use live data + AI summary
        if self._is_weather_query(user_message_lower):
            location = self._extract_location_from_message(user_message)
            if not location:
                return "Please specify a location (e.g., 'weather in Lusaka')."
            weather_data = self.get_weather_info(location)
            if 'error' in weather_data:
                return weather_data['error']
            # Compose a prompt for OpenAI
            if self.openai_available:
                weather_prompt = (
                    f"Here is the current weather for {weather_data['location']} in Zambia: "
                    f"Temperature: {weather_data['temperature']}, "
                    f"Condition: {weather_data['condition']}, "
                    f"Humidity: {weather_data['humidity']}. "
                    f"Forecast: {weather_data['forecast']}. "
                    f"Please summarize this weather for a Zambian farmer in {language}."
                )
                try:
                    ai_response = self._get_openai_response(weather_prompt, language)
                    if ai_response:
                        return ai_response
                except Exception as e:
                    print(f"OpenAI API error (weather): {e}")
            # Fallback: plain weather data
            return (
                f"Weather for {weather_data['location']}: "
                f"{weather_data['temperature']}, {weather_data['condition']}, "
                f"Humidity: {weather_data['humidity']}. Forecast: {weather_data['forecast']}"
            )
        
        # Try OpenAI API for all other queries if available
        if self.openai_available:
            try:
                ai_response = self._get_openai_response(user_message, language)
                if ai_response:
                    return ai_response
            except Exception as e:
                print(f"OpenAI API error: {e}")
                # Fall back to rule-based system
        
        # Fallback to rule-based system for specific query types
        return self._get_rule_based_response(user_message, language)

    def _get_openai_response(self, user_message: str, language: str) -> str:
        """Get response from OpenAI API"""
        try:
            # Create context for the AI
            context = f"""You are a helpful agricultural assistant for Zambian farmers. 
            You have expertise in Zambian farming practices, crops, weather patterns, and local conditions.
            
            Key Zambian crops: {', '.join(self.zambian_crops)}
            Zambian regions: {', '.join(self.zambian_regions)}
            
            Current knowledge base:
            - Rainy season: November to April
            - Dry season: May to October
            - Average rainfall: 800-1400mm annually
            
            Respond in {language} if requested, otherwise use English.
            Be helpful, practical, and specific to Zambian farming conditions.
            Keep responses concise but informative."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            return None

    def _get_rule_based_response(self, user_message: str, language: str) -> str:
        """Generate response using rule-based system"""
        # Check for specific queries
        if self._is_weather_query(user_message):
            return self._handle_weather_query(user_message, language)
        
        elif self._is_crop_query(user_message):
            return self._handle_crop_query(user_message, language)
        
        elif self._is_pest_disease_query(user_message):
            return self._handle_pest_disease_query(user_message, language)
        
        elif self._is_market_query(user_message):
            return self._handle_market_query(user_message, language)
        
        else:
            return self._get_general_advice(user_message, language)

    def _is_weather_query(self, message: str) -> bool:
        """Check if message is about weather"""
        weather_keywords = ['weather', 'rain', 'temperature', 'climate', 'forecast']
        return any(keyword in message for keyword in weather_keywords)

    def _is_crop_query(self, message: str) -> bool:
        """Check if message is about crops"""
        crop_keywords = ['plant', 'grow', 'harvest', 'fertilizer', 'soil']
        return any(keyword in message for keyword in crop_keywords) or \
               any(crop in message for crop in self.zambian_crops)

    def _is_pest_disease_query(self, message: str) -> bool:
        """Check if message is about pests or diseases"""
        pest_keywords = ['pest', 'disease', 'sick', 'damage', 'insect', 'fungus']
        return any(keyword in message for keyword in pest_keywords)

    def _is_market_query(self, message: str) -> bool:
        """Check if message is about market prices"""
        market_keywords = ['price', 'market', 'sell', 'buy', 'cost', 'kwacha']
        return any(keyword in message for keyword in market_keywords)

    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in message for greeting in greetings)

    def _handle_weather_query(self, message: str, language: str) -> str:
        """Handle weather-related queries"""
        if language == 'english':
            return ("In Zambia, the rainy season runs from November to April, "
                   "and the dry season from May to October. Average rainfall is "
                   "800-1400mm annually. For specific weather forecasts, please "
                   "provide your location.")
        else:
            return self._translate_to_local_language(
                "Weather information for Zambia", language
            )

    def _handle_crop_query(self, message: str, language: str) -> str:
        """Handle crop-related queries"""
        # Extract crop name from message
        for crop in self.zambian_crops:
            if crop in message:
                crop_info = self.knowledge_base['crops'].get(crop, {})
                if crop_info:
                    if language == 'english':
                        return self._format_crop_info(crop, crop_info)
                    else:
                        return self._translate_to_local_language(
                            f"Information about {crop}", language
                        )
        
        if language == 'english':
            return ("I can help you with information about maize, cassava, "
                   "groundnuts, and other crops grown in Zambia. What specific "
                   "crop would you like to know about?")
        else:
            return self._translate_to_local_language(
                "I can help with crop information", language
            )

    def _handle_pest_disease_query(self, message: str, language: str) -> str:
        """Handle pest and disease queries"""
        if language == 'english':
            return ("Common pests in Zambia include Fall Armyworm, Stem Borers, "
                   "and Aphids. For diseases, watch out for Maize Streak Virus, "
                   "Grey Leaf Spot, and Rust. Describe the symptoms you're seeing "
                   "for more specific advice.")
        else:
            return self._translate_to_local_language(
                "Pest and disease information", language
            )

    def _handle_market_query(self, message: str, language: str) -> str:
        """Handle market price queries"""
        if language == 'english':
            return ("Market prices vary by location and season. Current maize "
                   "prices range from K150-200 per 50kg bag. Cassava prices "
                   "are around K50-80 per kg. For the most current prices, "
                   "check with your local market.")
        else:
            return self._translate_to_local_language(
                "Market price information", language
            )

    def _get_greeting(self, language: str) -> str:
        """Get appropriate greeting based on language"""
        greetings = {
            'english': "Hello! I'm your Zambian farming assistant. How can I help you today?",
            'bemba': "Muli shani! Ndi mufyashi wenu wa Zambia. Nga ndesha ukusunga?",
            'njanja': "Moni! Ndine wothandiza a alimi a Zambia. Ndikuthandizeni bwanji?",
            'tonga': "Mwapona! Ndi mufyashi wenu wa Zambia. Nga ndesha ukusunga?",
            'lozi': "Lumela! Ndi mufyashi wenu wa Zambia. Nga ndesha ukusunga?"
        }
        return greetings.get(language, greetings['english'])

    def _get_general_advice(self, message: str, language: str) -> str:
        """Provide general farming advice"""
        if language == 'english':
            return ("I'm here to help with farming advice for Zambia. You can ask me about: "
                   "• Weather and climate information\n"
                   "• Crop planting and harvesting\n"
                   "• Pest and disease management\n"
                   "• Market prices\n"
                   "• Soil and fertilizer advice\n"
                   "What would you like to know?")
        else:
            return self._translate_to_local_language(
                "General farming advice", language
            )

    def _format_crop_info(self, crop: str, info: Dict) -> str:
        """Format crop information in a readable way"""
        return f"""Here's information about {crop}:

🌱 Planting Season: {info.get('planting_season', 'N/A')}
🌾 Harvest Time: {info.get('harvest_time', 'N/A')}
💧 Water Needs: {info.get('water_needs', 'N/A')}
🌍 Soil Type: {info.get('soil_type', 'N/A')}
📏 Spacing: {info.get('spacing', 'N/A')}
🌿 Fertilizer: {info.get('fertilizer', 'N/A')}

🐛 Common Pests: {', '.join(info.get('pests', []))}
🦠 Common Diseases: {', '.join(info.get('diseases', []))}"""

    def _translate_to_local_language(self, text: str, language: str) -> str:
        """Simple translation to local languages (basic implementation)"""
        translations = {
            'bemba': f"Bemba: {text}",
            'njanja': f"Nyanja: {text}",
            'tonga': f"Tonga: {text}",
            'lozi': f"Lozi: {text}"
        }
        return translations.get(language, text)

    def get_weather_info(self, location: str) -> Dict:
        """Get weather information for a location using WeatherAPI.com"""
        if not self.weather_api_key:
            return {'error': 'Weather API key not configured. Please contact support.'}
        try:
            url = f"http://api.weatherapi.com/v1/current.json?key={self.weather_api_key}&q={location}"
            resp = requests.get(url, timeout=8)
            data = resp.json()
            if resp.status_code != 200 or 'current' not in data:
                return {'error': f"Could not fetch weather for '{location}'. Please check the location name."}
            weather = data['current']['condition']['text']
            temp = data['current']['temp_c']
            humidity = data['current']['humidity']
            city = data['location']['name']
            forecast = weather
            return {
                'location': city,
                'temperature': f"{temp}°C",
                'condition': weather,
                'humidity': f"{humidity}%",
                'forecast': forecast
            }
        except Exception as e:
            return {'error': f"Weather service error: {str(e)}"}

    def get_market_prices(self) -> Dict:
        """Get current market prices"""
        return {
            'maize': {'price': 'K180/50kg', 'trend': 'stable'},
            'cassava': {'price': 'K65/kg', 'trend': 'rising'},
            'groundnuts': {'price': 'K120/kg', 'trend': 'stable'},
            'soybeans': {'price': 'K200/kg', 'trend': 'falling'}
        }

    def get_crop_information(self, crop_name: str) -> Dict:
        """Get detailed crop information"""
        return self.knowledge_base['crops'].get(crop_name.lower(), {})

    def identify_pest_disease(self, query: str) -> Dict:
        """Identify pests or diseases based on symptoms"""
        # This would use more sophisticated NLP/ML in a real implementation
        return {
            'query': query,
            'possible_issues': ['Check for common symptoms'],
            'recommendations': ['Contact local agricultural extension officer']
        }

    def _extract_location_from_message(self, message: str) -> str:
        """Extract location from user message for weather queries. Simple heuristic: look for 'in <location>' or last word."""
        import re
        match = re.search(r"in ([a-zA-Z\s]+)", message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Fallback: if message is like 'weather Lusaka'
        words = message.strip().split()
        for w in reversed(words):
            if w.lower() not in ['weather', 'in', 'the', 'for', 'forecast', 'temperature', 'climate']:
                return w
        return '' 