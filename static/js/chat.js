class ZambianFarmerChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.languageSelect = document.getElementById('languageSelect');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.floatingRobot = document.getElementById('floatingRobot');
        this.chatPopup = document.getElementById('chatPopup');
        this.closeChat = document.getElementById('closeChat');
        this.currentLanguage = 'english';
        
        this.initializeEventListeners();
        this.addWelcomeMessage();
    }

    initializeEventListeners() {
        // Floating robot click to open chat
        this.floatingRobot.addEventListener('click', () => this.openChat());
        
        // Close chat button
        this.closeChat.addEventListener('click', () => this.closeChatWindow());
        
        // Close chat when clicking outside (optional)
        document.addEventListener('click', (e) => {
            if (!this.chatPopup.contains(e.target) && 
                !this.floatingRobot.contains(e.target) && 
                this.chatPopup.classList.contains('active')) {
                this.closeChatWindow();
            }
        });

        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Language change
        this.languageSelect.addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            this.addSystemMessage(`Language changed to ${e.target.options[e.target.selectedIndex].text}`);
        });

        // Quick action buttons
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // Voice and image buttons
        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.handleVoiceInput();
        });

        document.getElementById('imageBtn').addEventListener('click', () => {
            this.handleImageInput();
        });

        // Focus input when chat opens
        this.chatPopup.addEventListener('animationend', () => {
            if (this.chatPopup.classList.contains('active')) {
                this.messageInput.focus();
            }
        });
    }

    openChat() {
        this.chatPopup.classList.add('active');
        this.floatingRobot.style.display = 'none';
        // Focus input after animation
        setTimeout(() => {
            this.messageInput.focus();
        }, 300);
    }

    closeChatWindow() {
        this.chatPopup.classList.remove('active');
        this.floatingRobot.style.display = 'block';
        // Clear input when closing
        this.messageInput.value = '';
    }

    addWelcomeMessage() {
        const welcomeMessage = {
            type: 'bot',
            content: `Hello! I'm your Zambian farming assistant. 🌱

I can help you with:
• Weather and climate information
• Crop planting and harvesting advice
• Pest and disease management
• Market prices and trends
• Soil and fertilizer recommendations

What would you like to know about farming in Zambia?`,
            timestamp: new Date()
        };
        this.addMessage(welcomeMessage);
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        const userMessage = {
            type: 'user',
            content: message,
            timestamp: new Date()
        };
        this.addMessage(userMessage);

        // Clear input
        this.messageInput.value = '';

        // Show loading
        this.showLoading();

        try {
            // Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    language: this.currentLanguage
                })
            });

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Add bot response
            const botMessage = {
                type: 'bot',
                content: data.response,
                timestamp: new Date()
            };
            this.addMessage(botMessage);

        } catch (error) {
            console.error('Error sending message:', error);
            this.addErrorMessage('Sorry, I encountered an error. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    handleQuickAction(action) {
        const actionMessages = {
            weather: "Tell me about the weather and climate for farming in Zambia",
            crops: "What crops are best to grow in Zambia and when should I plant them?",
            pests: "What are the common pests and diseases I should watch out for?",
            market: "What are the current market prices for crops in Zambia?"
        };

        const message = actionMessages[action];
        if (message) {
            this.messageInput.value = message;
            this.sendMessage();
        }
    }

    async handleVoiceInput() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.lang = this.getSpeechLanguage();
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = () => {
                this.addSystemMessage('Listening... Speak now.');
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.messageInput.value = transcript;
            };

            recognition.onerror = (event) => {
                this.addSystemMessage('Voice recognition error. Please try typing instead.');
            };

            recognition.start();
        } else {
            this.addSystemMessage('Voice input is not supported in your browser.');
        }
    }

    handleImageInput() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.addSystemMessage(`Image uploaded: ${file.name}. I can help identify pests, diseases, or crop issues from images.`);
                // Here you would typically upload the image to the server for analysis
            }
        };
        input.click();
    }

    getSpeechLanguage() {
        const languageMap = {
            'english': 'en-US',
            'bemba': 'en-US', // Fallback to English for now
            'njanja': 'en-US',
            'tonga': 'en-US',
            'lozi': 'en-US'
        };
        return languageMap[this.currentLanguage] || 'en-US';
    }

    addMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = message.type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = this.formatMessageContent(message.content);

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = this.formatTime(message.timestamp);

        content.appendChild(time);
        messageElement.appendChild(avatar);
        messageElement.appendChild(content);

        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }

    addSystemMessage(content) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message system';
        messageElement.innerHTML = `<div class="message-content system">${content}</div>`;
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }

    addErrorMessage(content) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message error';
        messageElement.innerHTML = `<div class="message-content error">❌ ${content}</div>`;
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }

    formatMessageContent(content) {
        // Convert line breaks to <br> tags
        content = content.replace(/\n/g, '<br>');
        
        // Highlight important information
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Add styling to bullet points
        content = content.replace(/• (.*?)(?=<br>|$)/g, '<span class="bullet-point">• $1</span>');
        
        return content;
    }

    formatTime(timestamp) {
        return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showLoading() {
        this.loadingIndicator.style.display = 'block';
        this.sendButton.disabled = true;
        this.sendButton.style.opacity = '0.5';
    }

    hideLoading() {
        this.loadingIndicator.style.display = 'none';
        this.sendButton.disabled = false;
        this.sendButton.style.opacity = '1';
    }

    // Utility methods for external API calls
    async getWeatherInfo(location) {
        try {
            const response = await fetch(`/api/weather/${encodeURIComponent(location)}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching weather:', error);
            return null;
        }
    }

    async getMarketPrices() {
        try {
            const response = await fetch('/api/market-prices');
            return await response.json();
        } catch (error) {
            console.error('Error fetching market prices:', error);
            return null;
        }
    }

    async getCropInfo(cropName) {
        try {
            const response = await fetch(`/api/crop-info/${encodeURIComponent(cropName)}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching crop info:', error);
            return null;
        }
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ZambianFarmerChatbot();
});

// Add some additional CSS for system and error messages
const additionalStyles = `
    .message.system .message-content {
        background: #e3f2fd;
        color: #1976d2;
        border: 1px solid #bbdefb;
        font-style: italic;
    }
    
    .message.error .message-content {
        background: #ffebee;
        color: #d32f2f;
        border: 1px solid #ffcdd2;
    }
    
    .bullet-point {
        display: block;
        margin: 5px 0;
        padding-left: 10px;
    }
    
    .message-content strong {
        color: #4CAF50;
        font-weight: 600;
    }
    
    .message-content em {
        color: #666;
        font-style: italic;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet); 