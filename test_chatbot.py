#!/usr/bin/env python3
"""
Simple test script for the Zambian Farmer Chatbot
Run this to test the chatbot functionality
"""

from chatbot import ZambianFarmerChatbot

def test_chatbot():
    """Test the chatbot with various inputs"""
    print("🌱 Testing Zambian Farmer Chatbot\n")
    
    # Initialize chatbot
    chatbot = ZambianFarmerChatbot()
    
    # Test cases
    test_cases = [
        ("Hello", "greeting"),
        ("What's the weather like?", "weather"),
        ("Tell me about maize", "crop"),
        ("How do I plant cassava?", "crop"),
        ("What pests affect groundnuts?", "pest"),
        ("What are the market prices?", "market"),
        ("When should I harvest?", "general"),
        ("How much fertilizer do I need?", "general")
    ]
    
    for message, expected_type in test_cases:
        print(f"🤔 User: {message}")
        response = chatbot.get_response(message)
        print(f"🤖 Bot: {response}")
        print("-" * 50)
    
    # Test specific crop information
    print("\n🌾 Testing Crop Information:")
    maize_info = chatbot.get_crop_information("maize")
    print(f"Maize Info: {maize_info}")
    
    # Test market prices
    print("\n📊 Testing Market Prices:")
    prices = chatbot.get_market_prices()
    print(f"Market Prices: {prices}")
    
    # Test weather info
    print("\n🌤️ Testing Weather Info:")
    weather = chatbot.get_weather_info("Lusaka")
    print(f"Weather in Lusaka: {weather}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_chatbot() 