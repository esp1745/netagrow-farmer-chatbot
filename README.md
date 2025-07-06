# Zambian Farmer Assistant Chatbot 🌱

A comprehensive AI-powered chatbot designed specifically for farmers in Zambia, providing agricultural advice, weather information, market prices, and crop management guidance.

## Features

### 🌾 Agricultural Knowledge
- **Crop Information**: Detailed guides for maize, cassava, groundnuts, and other Zambian crops
- **Planting Seasons**: Optimal planting times for different crops
- **Harvesting Advice**: When and how to harvest various crops
- **Soil Management**: Soil type recommendations and fertilizer guidance

### 🌤️ Weather & Climate
- **Seasonal Patterns**: Rainy and dry season information
- **Climate Data**: Average rainfall and temperature patterns
- **Weather Forecasts**: Location-specific weather information

### 🐛 Pest & Disease Management
- **Pest Identification**: Common pests in Zambian agriculture
- **Disease Prevention**: Tips for preventing crop diseases
- **Treatment Advice**: Recommended solutions for pest and disease issues

### 📊 Market Information
- **Price Updates**: Current market prices for major crops
- **Price Trends**: Market price analysis and predictions
- **Trading Advice**: Best times to sell crops

### 🌍 Multi-Language Support
- **English**: Primary language support
- **Bemba**: Local language support
- **Nyanja**: Local language support
- **Tonga**: Local language support
- **Lozi**: Local language support

### 🎯 Quick Actions
- **Voice Input**: Speech-to-text functionality
- **Image Upload**: Upload photos for pest/disease identification
- **Quick Buttons**: One-click access to common queries

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI/ML**: Natural Language Processing
- **APIs**: Weather API, Market Data API
- **Styling**: Modern CSS with responsive design

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd netagrow-chatboat
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Variables
Create a `.env` file in the root directory:
```env
# Optional: Weather API key for enhanced weather features
WEATHER_API_KEY=your_weather_api_key_here

# Optional: OpenAI API key for advanced AI features
OPENAI_API_KEY=your_openai_api_key_here

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:8000`

## Usage Guide

### For Farmers

1. **Getting Started**
   - Open the chatbot in your web browser
   - Select your preferred language from the dropdown
   - Start by asking about your specific farming needs

2. **Asking Questions**
   - Type your question in the chat input
   - Use natural language (e.g., "When should I plant maize?")
   - Click the send button or press Enter

3. **Quick Actions**
   - Use the quick action buttons for common queries
   - Weather: Get current weather and forecast
   - Crops: Information about crop management
   - Pests: Pest and disease identification
   - Market: Current market prices

4. **Voice Input**
   - Click the microphone button
   - Speak your question clearly
   - The chatbot will transcribe and respond

5. **Image Upload**
   - Click the camera button
   - Upload a photo of your crop issue
   - Get AI-powered identification and advice

### For Developers

#### Project Structure
```
netagrow-chatboat/
├── app.py                 # Main Flask application
├── chatbot.py            # Core chatbot logic
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .env                 # Environment variables
├── templates/
│   └── index.html       # Main HTML template
└── static/
    ├── css/
    │   └── style.css    # Styling
    └── js/
        └── chat.js      # Frontend JavaScript
```

#### API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send chat message
- `GET /api/weather/<location>` - Get weather information
- `GET /api/market-prices` - Get current market prices
- `GET /api/crop-info/<crop_name>` - Get crop information
- `GET /api/pest-disease/<query>` - Identify pests/diseases
- `GET /api/languages` - Get supported languages

#### Extending the Chatbot

1. **Adding New Crops**
   - Update the `zambian_crops` list in `chatbot.py`
   - Add crop information to the knowledge base

2. **Adding New Languages**
   - Add language options to the HTML template
   - Implement translations in the chatbot logic

3. **Integrating External APIs**
   - Add API keys to the `.env` file
   - Implement API calls in the chatbot methods

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Using Docker (if Dockerfile is provided)
docker build -t zambian-farmer-chatbot .
docker run -p 8000:8000 zambian-farmer-chatbot
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] **Mobile App**: Native mobile application
- [ ] **SMS Integration**: Text message support for farmers without smartphones
- [ ] **Offline Mode**: Basic functionality without internet
- [ ] **Community Features**: Farmer-to-farmer communication
- [ ] **Advanced AI**: Machine learning for better crop recommendations
- [ ] **Satellite Integration**: Real-time crop monitoring
- [ ] **Financial Services**: Micro-loans and insurance information

## Support

For support and questions:
- Email: support@zambianfarmerassistant.com
- Phone: +260 211 123456
- WhatsApp: +260 955 123456

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Zambian Ministry of Agriculture
- Local farming communities
- Agricultural extension officers
- Open source community contributors

---

**Built with ❤️ for Zambian Farmers** 