import streamlit as st
import os
import time
from datetime import datetime
# Optional: Load environment variables from .env file for local development
from dotenv import load_dotenv
load_dotenv()

import uuid # To create unique identifiers for uploads

# Import our utility functions
from supabase_utils import upload_image_to_supabase
from ai_utils import extract_menu_text, generate_dish_image
from logo import logo_html

# --- Configuration and Setup Checks ---

# Set page configuration
st.set_page_config(
    page_title="MenuViz - Visualize Your Menu",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define custom CSS directly in the code
st.markdown("""
<style>
/* General styling */
.stApp {
    font-family: 'Inter', sans-serif;
}

/* Menu card styling */
.menu-card {
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Dish name styling */
.dish-name {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 5px;
    color: #1E3A8A;
}

/* Dish description styling */
.dish-description {
    font-size: 0.9rem;
    color: #4B5563;
    margin-bottom: 15px;
}

/* Subtitle styling */
.subtitle {
    font-size: 1.2rem;
    color: #6B7280;
    margin-top: -10px;
    margin-bottom: 20px;
}

/* Footer styling */
.footer {
    font-size: 0.8rem;
    color: #9CA3AF;
    text-align: center;
    margin-top: 30px;
}

/* Loading animation */
.loading-animation {
    color: #2563EB;
    font-weight: 500;
}

/* Custom button styling */
.stButton > button {
    width: 100%;
    border-radius: 5px;
    font-weight: 500;
}

/* Custom file uploader */
.stFileUploader > div {
    padding: 10px;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# You can add checks for API keys here if you didn't add them to the utility files,
# but adding them to the utils is cleaner as those functions rely on them.
# Let's assume the utility functions handle reporting missing keys upon call.

# --- Streamlit App ---

# Display the logo and title
st.markdown(logo_html, unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload a menu photo and watch it come to life with AI-generated dish visualizations</p>', unsafe_allow_html=True)

# Create two columns for the main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.markdown("### Upload Menu Photo")
    st.markdown("Upload a clear photo of a restaurant menu to get started.")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="menu_upload")

    if uploaded_file:
        # Use a unique identifier for the upload session
        session_id = uuid.uuid4()
        original_filename = uploaded_file.name
        # Create a unique filename for Supabase
        supabase_filename = f"menu_uploads/{session_id}_{original_filename}"

        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Menu", use_container_width=True)

        # Add a process button for better UX
        process_button = st.button("Process Menu", type="primary", key="process_button")
    st.markdown('</div>', unsafe_allow_html=True)

    # Add some helpful tips
    with st.expander("Tips for Best Results", expanded=False):
        st.markdown("""
        - Upload a clear, well-lit photo of the menu
        - Ensure text is readable and not blurry
        - Crop out unnecessary parts of the image
        - Avoid glare or shadows on the menu
        """)

    # Add a footer
    st.markdown('<div class="footer">© 2025 MenuViz | Powered by AI</div>', unsafe_allow_html=True)

with col2:
    if uploaded_file and 'process_button' in locals() and process_button:
        # Read the file bytes
        image_bytes = uploaded_file.getvalue()

        # Create a container for the processing section
        with st.container():
            st.markdown('<div class="menu-card">', unsafe_allow_html=True)
            st.markdown("### Processing Menu")

            # Create a progress bar with custom styling
            progress_placeholder = st.empty()
            status_text = st.empty()

            # Initialize progress
            progress = progress_placeholder.progress(0)
            status_text.markdown('<p class="loading-animation">Initializing...</p>', unsafe_allow_html=True)
            time.sleep(0.5)  # Small delay for better UX

            # Step 1: Upload to Supabase
            progress.progress(10)
            status_text.markdown('<p class="loading-animation">Uploading menu image...</p>', unsafe_allow_html=True)

            # Check if S3 API should be used (can be controlled via environment variable or Streamlit secrets)
            use_s3_env = os.environ.get("USE_SUPABASE_S3", "").lower()
            use_s3_secret = st.secrets.get("USE_SUPABASE_S3", "").lower()
            use_s3 = use_s3_env == "true" or use_s3_secret == "true"

            if use_s3:
                status_text.markdown('<p class="loading-animation">Using Supabase S3 API for storage...</p>', unsafe_allow_html=True)

            # Upload the image
            public_url = upload_image_to_supabase(image_bytes, supabase_filename, use_s3=use_s3)
            progress.progress(30)

            # Step 2: Extract menu items
            status_text.markdown('<p class="loading-animation">Analyzing menu with AI...</p>', unsafe_allow_html=True)
            extracted_text, structured_menu_items = extract_menu_text(image_bytes)
            progress.progress(100)

            # Clear progress indicators
            time.sleep(0.5)  # Small delay for better UX
            progress_placeholder.empty()
            status_text.empty()

            # Show results
            if structured_menu_items:
                st.markdown("### Discovered Menu Items")
                st.markdown(f"Found **{len(structured_menu_items)}** items on the menu")

                # Create a container for the menu items
                menu_items_container = st.container()

                with menu_items_container:
                    # Display items in a grid
                    num_cols = 2  # Adjust based on screen size
                    rows = [structured_menu_items[i:i + num_cols] for i in range(0, len(structured_menu_items), num_cols)]

                    for row in rows:
                        cols = st.columns(num_cols)
                        for i, item in enumerate(row):
                            name = item.get("name", "N/A")
                            description = item.get("description", "No description provided.")

                            # Skip invalid items
                            if not name or name == "Dish Name":
                                continue

                            with cols[i]:
                                st.markdown('<div class="menu-card">', unsafe_allow_html=True)
                                st.markdown(f'<p class="dish-name">{name}</p>', unsafe_allow_html=True)
                                st.markdown(f'<p class="dish-description">{description}</p>', unsafe_allow_html=True)

                                # Generate and display image
                                with st.spinner(f"Generating image for {name}..."):
                                    img_url = generate_dish_image(name, description)

                                if img_url:
                                    st.image(img_url, use_container_width=True)
                                else:
                                    st.info("Could not generate image")

                                st.markdown('</div>', unsafe_allow_html=True)
            else:
                if extracted_text:
                    st.warning("Could not extract structured menu items. Here's the raw text:")
                    with st.expander("Extracted Text", expanded=True):
                        st.text(extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text)
                else:
                    st.error("Could not process the menu image. Please try a clearer photo.")

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Show a placeholder when no file is uploaded
        st.markdown('<div class="menu-card" style="min-height: 300px; display: flex; justify-content: center; align-items: center; text-align: center;">', unsafe_allow_html=True)
        st.markdown("""
        ### Upload a Menu to Get Started

        Select a menu photo using the uploader on the left panel, then click "Process Menu" to see the magic happen!

        MenuViz will:
        1. Extract dish names and descriptions
        2. Generate visual representations
        3. Display the results here
        """)
        st.markdown('</div>', unsafe_allow_html=True)


# Sidebar content
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown("# MenuViz")
    st.markdown("### AI-Powered Menu Visualization")
    st.markdown("</div>", unsafe_allow_html=True)

    # About section
    st.markdown("## About")
    st.markdown("""
    MenuViz uses advanced AI to transform restaurant menu photos into visual experiences:

    1. **Extract** dish information from menu images
    2. **Process** the data with Llama 4 AI
    3. **Generate** realistic dish visualizations
    4. **Display** the results in an organized gallery
    """)

    # Technology stack
    st.markdown("## Powered By")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Frontend**")
        st.markdown("• Streamlit")
        st.markdown("**Storage**")
        st.markdown("• Supabase")
    with col2:
        st.markdown("**AI Models**")
        st.markdown("• Llama 4 (Groq)")
        st.markdown("• Flux (Together)")

    # Add version and GitHub link
    st.markdown("---")
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.markdown("v1.0.0 | [GitHub](https://github.com/yourusername/menuviz)")

    # Current date/time
    now = datetime.now()
    st.markdown(f"Last updated: {now.strftime('%b %d, %Y')}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- End of app.py ---