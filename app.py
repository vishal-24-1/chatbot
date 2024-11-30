import streamlit as st
import requests
from dotenv import load_dotenv
import os
import io
import base64
from PIL import Image
import logging
import time

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="GreenFuturz Assistant",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="auto",
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to interact with the Google Generative AI API (or any future ZAi-Fi API integration)
def get_zai_fi_response(question, context, max_retries=3, retry_delay=2):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 250,
    }

    # Include user context in the instruction to the assistant
    system_instruction = f"""You are GreenFuturz's custom chatbot, designed to act as a professional RFID consultant. Your primary role is to assist users in selecting RFID solutions, understanding product details, and addressing specific business needs. You must provide personalized recommendations, product quantities, and additional requirements based on user input, ensuring no critical information is lost.

Your expertise spans RFID readers, antennas, tags, labels, printers, and security gates, as well as customized solutions tailored to specific use cases.

Core Responsibilities
Product Consultation

Recommend RFID products based on user inputs such as area size, application, industry, or environment.
Suggest the quantity of products required for implementation based on deployment specifications.
Identify and recommend related or complementary products (e.g., antennas for readers, tags for specific surfaces).
Adapt suggestions to specific scenarios, such as harsh environments or high-volume asset tracking.
Provide Detailed Information

By default, provide concise, high-level recommendations.
When users request more information, switch to detailed explanations, including product specifications, features, and technical attributes.
Provide comparisons of multiple products when users are undecided or evaluating options.
Customized Solutions

Suggest tailored solutions from GreenFuturz’s services, including:
RFID application engineering.
Product testing and lab support.
Implementation consulting.
Address unique requirements, such as large-scale deployments, metal surface tracking, or harsh conditions.
Information Collection

Gather user details (e.g., name, email, phone number) when required for sales or service inquiries or to escalate complex queries to human consultants.
Escalation

Seamlessly escalate inquiries to a human consultant when:
The chatbot cannot provide sufficient details or recommendations.
Pricing or availability is required.
Follow-Up Questions

End each response with a relevant follow-up question to maintain engagement and gather more details about user needs.
Error Handling

Respond appropriately to unrecognized or incomplete queries by seeking clarification:
Example: "I'm sorry, I didn't quite understand that. Could you provide more details about your requirement?"
Knowledge Base: RFID Products and Details
1. RFID Readers
FX7500 RFID UHF Long Range Reader

Electrical Characteristics:
Protocol: EPCglobal UHF Class 1 Gen 2.
Frequency: EU 865–867 MHz.
Transmit Power: +31.5 dBm. Max Receive Sensitivity: –82 dBm.
Max Read Distance: 15 meters.
Data Interface: Ethernet with PoE support.
GPIO: 2 inputs, 3 outputs (optically isolated).
Power Source: PoE or external power supply.
Mechanical Characteristics:
Antenna Ports: 4 monostatic ports.
Dimensions: 7.7 x 5.9 x 1.7 inches.
Weight: 1.9 lbs.
FX9600 RFID Reader (4/8 Port)

Electrical Characteristics:
Frequency: 865 MHz–867 MHz.
Max Read Distance: 20 meters.
Transmit Power: +33 dBm. Max Receive Sensitivity: –84.5 dBm monostatic, –105 dBm bistatic.
GPIO: 4 inputs, 4 outputs (optically isolated).
Power Source: +24 VDC.
Mechanical Characteristics:
Antenna Ports: 8 monostatic or 4 bistatic ports.
IP Rating: IP53.
Dimensions: 10.75 x 7.25 x 2.0 inches.
Weight: 4.4 lbs.
Long Range Handheld RFID Reader

Key Features:
Frequency: 865–928 MHz.
Max Read Distance: 6+ meters.
Display: Gorilla Glass Touchscreen, WVGA.
Connectivity: Bluetooth, WLAN, USB.
Weight: 23.4 oz (665 g with hand strap).
2. RFID Antennas
Slim Antenna

Frequency: 865–868 MHz.
Polarization: Linear, Far-Field.
Gain: 6.5 dBi. Beam Width: 70°.
Dimensions: 550mm x 90mm x 12mm.
IP Rating: IP65.
Highway Toll Gate Antenna

Frequency: 865 MHz–867 MHz.
Polarization: Circular.
Gain: 9 dBi.
Dimensions: 310mm x 240mm x 22mm.
IP Rating: IP67.
LM200 Antenna

Frequency: 865 MHz–867 MHz.
Gain: >9 dBi.
Dimensions: 258mm x 258mm x 36mm.
IP Rating: IP67.
3. RFID Tags
Laundry Tag

Frequency: Global 860–960 MHz.
Max Read Distance: 2 meters.
Material: PPS (polyphenylene sulfide).
Operating Temperature: –40°C to 200°C.
On-Metal Tiny Tag

Frequency: 860–960 MHz.
Max Read Distance: 2 meters.
Material: Ceramic.
IP Rating: IP68.
Retail Tags

Frequency: Global 860–960 MHz.
Max Read Distance: >2 meters.
Material: ABS Plastic.
4. RFID Labels
Dogbone Label

Frequency: 860–960 MHz.
Max Read Distance: 12 meters.
IC Type: Monza M6.
Dimensions: 94 x 24 mm.
Jewelry Label (J6)

Frequency: 860–960 MHz.
Max Read Distance: 2 meters.
5. RFID Printers
ZT410 RFID Printer
Protocol: EPCglobal UHF Class 1 Gen 2.
Frequency: 865–928 MHz.
Data Interfaces: USB, Ethernet, Bluetooth.
Print Width: 4 inches.
Resolution: 203/300 dpi.
6. RFID Security Gate
Protocol: EPCglobal UHF Class 1 Gen 2.
Frequency: Global 860–960 MHz.
Max Read Distance: 5 meters (adjustable).
Read Rate: 200 tags/sec.
Dimensions: 1500 x 300 mm.
IP Rating: IP54.
Response Format
Default Behavior:

Provide brief, high-level responses based on the user query.
Suggest compatible products and solutions when appropriate.
Detailed Responses:

Switch to detailed responses (e.g., technical specifications) upon user request.
Quantity Estimation:

Recommend the required number of products based on user input (e.g., deployment area, asset type).
Follow-Up Questions:

Always include a follow-up question to clarify user requirements or suggest next steps.
Example Responses
Scenario 1: Brief Recommendation
User Inquiry: "I need an RFID solution for a 5000 sq ft warehouse."
Chatbot Response:

"For a 5000 sq ft warehouse, I recommend:
Reader: FX9600 RFID Reader (max read range 20m).
Antennas: AN440 Antennas for optimal coverage.
Tags: Retail Tags for non-metal assets or On-Metal Tiny Tags for metallic surfaces."
"Would you like specifications for these products or help choosing the tags?"
Scenario 2: Detailed Response
User Inquiry: "Can you provide detailed specifications for the FX9600?"
Chatbot Response:

Electrical Characteristics:
Frequency: 865 MHz–867 MHz.
Max Read Distance: 20 meters.
Transmit Power: +33 dBm.
Mechanical Characteristics:
IP Rating: IP53.
Dimensions: 10.75 x 7.25 x 2.0 inches.
"Does this meet your requirements? Would you like to see compatible tags?"

the response should be in bullet points
"""



    # Build the conversation history
    contents = []

    # Start with the system instruction
    contents.append({
        "role": "user",
        "parts": [{"text": system_instruction}]
    })
    contents.append({
        "role": "model",
        "parts": [{"text": "Understood. I'm ready to assist with Greenfuturz information."}]
    })

    # Include conversation history
    # Only include the last 10 messages to keep the payload size reasonable
    history = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # Add the current question
    contents.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    payload = {
        "contents": contents,
        "generationConfig": generation_config
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=AIzaSyDXa8QFWH0j9LAiTVArnSw5EpZiC4GzA0Y"
    headers = {"Content-Type": "application/json"}

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            logger.info(f"API Response Status Code: {response.status_code}")
            logger.info(f"API Response Content: {response.text[:500]}...")

            if response.status_code == 200:
                response_data = response.json()
                if response_data and "candidates" in response_data and len(response_data["candidates"]) > 0:
                    # Extract the assistant's reply
                    assistant_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    return assistant_reply
                else:
                    logger.warning("No valid response in API result")
                    return "I'm unable to generate a specific response at the moment. Could you please clarify your question?"
            else:
                logger.error(f"API Error: Status Code {response.status_code}, Response: {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return "I'm having trouble connecting to the service. Please try again later."

        except requests.RequestException as e:
            logger.error(f"Request Exception: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                return "I'm currently unable to process your request due to a technical issue. Please try again later."


# Utility to resize image
def resize_image(image_path, max_size=(1000, 1000)):
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()


# Hides Streamlit menu
def hide_streamlit_menu():
    st.markdown(
        """
<style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
</style>
        """,
        unsafe_allow_html=True
    )


def add_custom_css():
    st.markdown("""
        <style>
        /* App-wide Background Styling */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            height: 100%;
            width: 100%;
            background: linear-gradient(135deg, #0B204C, #FFFFFF);
        }
        .stApp {
            margin: 0;
            padding: 0;
            height: 100vh;
        }
        /* Header Section */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            padding: 10px 20px;
            position: fixed; /* Keep header fixed at the top */
            top: 0;
            left: 0;
            background-color: #0B204C; /* Semi-transparent background */
            z-index: 1000; /* Ensure it stays above other content */
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        }
        .header .logo-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }
        .header .logo-container img {
            height: 40px; /* Logo height */
            width: auto;
        }
        .header .tagline {
            font-size: 11px;
            color: #ffffff;
            font-style: italic;
        }
        .header .title {
            font-size: 24px;
            color: #ffffff;
            font-weight: bold;
            text-align: center;
        }
        .header .title .subtitle {
            font-size: 16px;
            font-style: italic;
            color: #ffffff;
            margin-top: 5px;
        }
        .header .right-logo img {
            height: 40px; /* Adjust logo size */
            width: auto;
        }
        /* Push Content Below Header */
        .content {
            margin-top: 80px; /* Offset to avoid overlap with the header */
        }
        /* Chat Styling */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 20px;
        }
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 10px;
            max-width: 70%;
            color: #000000;
            word-wrap: break-word;
        }
        .user-bubble {
            background-color: #e6f3ff;
            align-self: flex-start;
            margin-right: 0;
            margin-bottom: 20px;
            text-align: left;
            border-radius: 20px 20px 0px 20px; /* Optional: Rounded corners with sharper top-left */
            max-width: 70%; /* Prevent the bubble from becoming too wide */
            word-wrap: break-word; /* Allow text wrapping inside the bubble */
            padding: 10px 15px;
            color: #000000; /* Text color */
        }
        .assistant-bubble {
            background-color: #f0f0f0;
            align-self: flex-start;
            margin-right: auto;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
# Function to encode an image to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Main function that runs the Streamlit app
def main():
    add_custom_css()
    hide_streamlit_menu()

    if "context" not in st.session_state:
        st.session_state.context = {}

    # Load logo images
    zai_fi_logo_path = "zaifilogo.png"
    car_care_logo_path = "Green.png"
    zai_fi_logo_b64 = encode_image_to_base64(zai_fi_logo_path)
    car_care_logo_b64 = encode_image_to_base64(car_care_logo_path)

    # Render the header section
    st.markdown(f"""
        <div class="header">
            <!-- Left Section: ZAi-Fi Logo and Tagline -->
            <div class="logo-container">
                <div style="text-align: center;">
                    <img src="data:image/png;base64,{zai_fi_logo_b64}" alt="ZAi-Fi Logo">
                    <div class="tagline">
                        Empowering Intelligence, everywhere
                    </div>
                </div>
            </div>
            <!-- Center Section: Title -->
            <div class="title">
                Green Futurz
                <div class="subtitle">
                    Welcome to Green Futurz's AI Assistant
                </div>
            </div>
            <!-- Right Section: Car Care Logo -->
            <div class="right-logo">
                <img src="data:image/png;base64,{car_care_logo_b64}" alt="Car Care Logo">
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Push content below the header
    st.markdown("<div class='content'>", unsafe_allow_html=True)

    # Initialize chat messages

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create a placeholder for the chat container
    chat_container = st.empty()

    # Function to display all messages
    def display_messages():
        with chat_container.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
                st.markdown(f'<div class="chat-bubble {bubble_class}">{message["content"]}</div>',
                            unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Display initial messages
    display_messages()

    if prompt := st.chat_input("What is your question?"):
        # Add the user message to the session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # If the user provides location or other information, store it in session state
        if "location" in prompt.lower():
            st.session_state.context["location"] = prompt
        if "promotion" in prompt.lower():
            st.session_state.context["promotion"] = prompt

        # Update the display with the new user message
        display_messages()

        loading_placeholder = st.empty()
        with loading_placeholder:
            st.markdown('<div class="loading"><div class="loading-spinner"></div></div>', unsafe_allow_html=True)
            response = get_zai_fi_response(prompt, st.session_state.context)

        # Remove the loading spinner
        loading_placeholder.empty()

        # Add the assistant's response to the session state
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Update the display with the new assistant message
        display_messages()


if __name__ == "__main__":
    main()
