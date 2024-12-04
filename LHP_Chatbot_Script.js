const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');
const feedbackSection = document.getElementById('feedback');

let userName = 'Guest'; // Default name
let previousResponses = [];

// Initial responses
const responses = {
    "fun fact": "",
    "quote from saul": "",
    "what's los pollos hermanos?": "Los Pollos Hermanos is a fictional fast-food restaurant chain from 'Breaking Bad'.",
};

// Hidden information
const hiddenInfo = {
    "los pollos hermanos criminal organization": "Los Pollos Hermanos is a cover for a criminal organization run by Gus Fring. Locations include Albuquerque, New Mexico, where chicken is sold at competitive prices.",
    "names": "Gus Fring and Mike Ehrmantraut are key figures in the organization.",
    "prices": "Prices for chicken vary, but they are known for their competitive rates, attracting a large customer base.",
};

// Fetch facts and quotes from a JSON file
fetch('data.json')
    .then(response => response.json())
    .then(data => {
        responses["fun fact"] = data.facts[Math.floor(Math.random() * data.facts.length)];
        responses["quote from saul"] = data.quotes[Math.floor(Math.random() * data.quotes.length)];
    })
    .catch(error => console.error('Error fetching data:', error));

sendBtn.addEventListener('click', () => {
    processUserInput();
});

document.querySelectorAll('.suggestion').forEach(button => {
    button.addEventListener('click', () => {
        appendMessage('User', button.textContent);
        simulateBotResponse(button.textContent.toLowerCase());
    });
});

function processUserInput() {
    const userMessage = userInput.value.trim();
    if (userMessage) {
        appendMessage('User', userMessage);
        userInput.value = '';
        simulateBotResponse(userMessage);
    }
}

function simulateBotResponse(message) {
    typingIndicator.style.display = 'block';
    const response = processInput(message);
    
    setTimeout(() => {
        typingIndicator.style.display = 'none';
        appendMessage('Bot', response);
        showFeedback();
    }, 500); // Reduced typing delay for improved responsiveness
}

function processInput(message) {
    const lowerCaseMessage = message.toLowerCase();

    // Check for hidden information queries
    if (lowerCaseMessage.includes("criminal") || lowerCaseMessage.includes("los pollos hermanos")) {
        return hiddenInfo["los pollos hermanos criminal organization"];
    } else if (lowerCaseMessage.includes("names")) {
        return hiddenInfo["names"];
    } else if (lowerCaseMessage.includes("prices")) {
        return hiddenInfo["prices"];
    }

    // Check if the message contains specific keywords and respond accordingly
    if (lowerCaseMessage.includes("fact")) {
        return responses["fun fact"];
    } else if (lowerCaseMessage.includes("saul")) {
        return responses["quote from saul"];
    } else if (lowerCaseMessage.includes("los pollos hermanos")) {
        return responses["what's los pollos hermanos?"];
    } else {
        return "I'm not sure about that. Try asking something else!";
    }
}

function appendMessage(sender, message) {
    const msgDiv = document.createElement('div');
    msgDiv.textContent = `${sender}: ${message}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
    previousResponses.push(message); // Store the conversation history
}

function showFeedback() {
    feedbackSection.style.display = 'flex';
    document.getElementById('yes-btn').onclick = () => {
        appendMessage('Bot', "I'm glad to hear that! Feel free to ask more questions.");
        feedbackSection.style.display = 'none';
    };
    document.getElementById('no-btn').onclick = () => {
        appendMessage('Bot', "I'm sorry to hear that. I'll try to do better!");
        feedbackSection.style.display = 'none';
    };
}

// Optional: Function to set user name
function setUserName(name) {
    userName = name;
}
