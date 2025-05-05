import os
import json
import requests # Needed for API calls
import base64
from typing import List, Dict, Tuple
import streamlit as st # Using st for error display and caching
from PIL import Image
import io

# LLM (Groq) Libraries
from groq import Groq

# --- Configuration ---
# Access keys from environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY") or st.secrets.get("TOGETHER_API_KEY")

# Groq client setup (using official Groq client)
if not GROQ_API_KEY:
    st.error("Groq API Key not set. Please provide it via environment variables or st.secrets.")
    groq_client = None
else:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        st.error(f"Error initializing Groq client: {e}")
        groq_client = None

# Function to encode image to base64
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- Functions ---

@st.cache_data(show_spinner="Analyzing menu...")
def extract_menu_text(image_bytes: bytes) -> Tuple[str | None, List[Dict] | None]:
    """
    Processes a menu image using Llama 4 via Groq API and extracts structured menu data.

    Args:
        image_bytes: The image data as bytes.

    Returns:
        A tuple containing the raw text (or None on error) and a list of dicts
        representing menu items (or None/empty list on error).
    """
    # Create a placeholder for status updates
    status_placeholder = st.empty()
    status_placeholder.info("Analyzing menu items...")

    if groq_client is None:
        status_placeholder.error("API connection error. Please try again.")
        return None, []

    try:
        # Encode the image to base64
        base64_image = encode_image(image_bytes)

        # Create the prompt for Llama 4
        prompt = """You are an expert at extracting structured data from restaurant menus.
        Look at this menu image and extract a clean list of dish names and short descriptions.

        Rules:
        1. Focus on distinct menu items like appetizers, main courses, and desserts.
        2. Ignore sections like "Drinks", "Wines", headers, footers, addresses, phone numbers.
        3. Exclude prices, numbering, or bullet points unless they are part of the actual dish name.
        4. If a dish has a clear description, use it.
        5. If a dish name is listed without a description immediately following it, provide a very brief, generic description based on the dish name if possible.
        6. Respond ONLY with a JSON array. Each element in the array should be an object with two keys: "name" (string) and "description" (string).
        7. Ensure the JSON is valid and correctly formatted.
        """

        # Call Llama 4 via Groq API with the image
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # Using Llama 4 Scout for multimodal capabilities
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from images."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            temperature=0.0,  # Keep it low for structured output
            response_format={"type": "json_object"}  # Request JSON format
        )

        # Extract the response content
        structured_menu_str = response.choices[0].message.content.strip()

        # Display a sample of the extracted text
        with st.expander("Extracted Menu Text", expanded=False):
            st.text(structured_menu_str[:1000] + "..." if len(structured_menu_str) > 1000 else structured_menu_str)

        # Parse the JSON response
        try:
            # Clean up potential markdown wrapping
            if structured_menu_str.startswith("```json"):
                structured_menu_str = structured_menu_str[len("```json"):].strip()
            if structured_menu_str.endswith("```"):
                structured_menu_str = structured_menu_str[:-len("```")].strip()

            items_data = json.loads(structured_menu_str)

            # Extract the items array from the JSON object
            if "items" in items_data:
                items = items_data["items"]
            elif "menu_items" in items_data:
                items = items_data["menu_items"]
            elif "dishes" in items_data:
                items = items_data["dishes"]
            elif isinstance(items_data, list):
                items = items_data
            else:
                # Try to find any array in the response
                for _, value in items_data.items():
                    if isinstance(value, list) and len(value) > 0:
                        items = value
                        break
                else:
                    items = []

            if not isinstance(items, list):
                if isinstance(items, dict):
                    items = [items]  # Wrap single dict in a list
                else:
                    items = []  # Return empty list

            # Validate the items
            valid_items = []
            for item in items:
                if isinstance(item, dict) and "name" in item and "description" in item:
                    valid_items.append(item)

            # Clear the status message if successful
            status_placeholder.empty()

            return structured_menu_str, valid_items

        except json.JSONDecodeError:
            status_placeholder.error("Could not process menu. Please try a clearer image.")
            return structured_menu_str, []  # Return empty list on parse error

    except Exception:
        status_placeholder.error("Could not process menu. Please try again.")
        return None, []  # Return empty list on API error

# Step 5 will add the image generation function here
# --- Functions (continued) ---

# @st.cache_data # Careful caching image generation calls, you might hit API limits or want fresh images
def generate_dish_image(dish_name: str, description: str) -> str | None:
    """
    Generates an image for a dish using Flux via Together AI.

    Args:
        dish_name: The name of the dish.
        description: A short description of the dish.

    Returns:
        The URL of the generated image, or None if generation failed.
    """
    if not TOGETHER_API_KEY:
         st.error("Together AI API Key not set.")
         return None

    # Create a placeholder for status updates
    status_placeholder = st.empty()
    status_placeholder.info(f"Generating image for '{dish_name}'...")

    prompt = f"A high-quality, photorealistic image of '{dish_name}', which is described as: {description}. Focus on the dish itself, beautifully presented on a plate. The style should be like a professional food photograph."

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Updated payload based on the TypeScript example
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell",  # Updated model name
        "prompt": prompt,
        "n": 1,  # Number of images to generate
        "steps": 5,  # Reduced steps for faster generation
        "height": 768,
        "width": 1024,
        "response_format": "url"  # Explicitly request URL format
    }

    api_url = "https://api.together.xyz/v1/images/generations"

    try:
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=60  # Add a timeout
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()

        # Expected structure: {'data': [{'url': '...', 'seed': ...}], 'created': ...}
        if result and 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
            if 'url' in result['data'][0]:
                img_url = result['data'][0]['url']
                status_placeholder.empty()  # Clear the status message
                return img_url
            elif 'b64_json' in result['data'][0]:
                # Handle base64 response if that's what we get
                b64_data = result['data'][0]['b64_json']
                img_url = f"data:image/jpeg;base64,{b64_data}"
                status_placeholder.empty()  # Clear the status message
                return img_url
            else:
                status_placeholder.error(f"Could not generate image for '{dish_name}'")
                return None
        else:
            status_placeholder.error(f"Could not generate image for '{dish_name}'")
            return None

    except requests.exceptions.Timeout:
        status_placeholder.error(f"Could not generate image for '{dish_name}'")
        return None
    except requests.exceptions.RequestException:
        status_placeholder.error(f"Could not generate image for '{dish_name}'")
        return None
    except Exception:
        status_placeholder.error(f"Could not generate image for '{dish_name}'")
        return None