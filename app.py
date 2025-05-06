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

# Load custom CSS from external file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# You can add checks for API keys here if you didn't add them to the utility files,
# but adding them to the utils is cleaner as those functions rely on them.
# Let's assume the utility functions handle reporting missing keys upon call.

# --- Streamlit App ---

# Display the logo and title in a header container
#st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown(logo_html, unsafe_allow_html=True)
st.markdown('<h2 class="main-title">Transform Your Menu with AI</h2>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload a restaurant menu photo using the panel on the left, then watch as AI brings your dishes to life with stunning visualizations!</p>', unsafe_allow_html=True)
#st.markdown('</div>', unsafe_allow_html=True)

# Create two columns for the main layout with improved ratio
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<h3 class="card-title">📷 Upload Menu Photo</h3>', unsafe_allow_html=True)
    st.markdown('<p class="card-description">Upload a clear photo of a restaurant menu to get started.</p>', unsafe_allow_html=True)

    # Enhanced file uploader with custom styling
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="menu_upload")

    if uploaded_file:
        # Use a unique identifier for the upload session
        session_id = uuid.uuid4()
        original_filename = uploaded_file.name
        # Create a unique filename for Supabase
        supabase_filename = f"menu_uploads/{session_id}_{original_filename}"

        # Display the uploaded image with improved styling
        st.markdown('<div class="uploaded-image-container">', unsafe_allow_html=True)
        st.image(uploaded_file, caption="Uploaded Menu", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Add a process button with enhanced styling
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        process_button = st.button("🔍 Process Menu", type="primary", key="process_button")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Show drag and drop instructions with camera icon when no file is uploaded
        st.markdown('''
        <div class="upload-instructions">
            <div class="camera-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="24" height="24" rx="12" fill="#F3F4F6"/>
                    <path d="M8.5 11C8.5 9.61929 9.61929 8.5 11 8.5H13C14.3807 8.5 15.5 9.61929 15.5 11V15.5H8.5V11Z" fill="#9CA3AF"/>
                    <rect x="6" y="5" width="12" height="10" rx="2" stroke="#4B5563" stroke-width="1.5"/>
                    <path d="M6 14H18V16C18 17.1046 17.1046 18 16 18H8C6.89543 18 6 17.1046 6 16V14Z" fill="#4B5563"/>
                    <circle cx="12" cy="10" r="2" fill="#FF4B4B"/>
                </svg>
            </div>
            <p>Drag and drop menu photo here</p>
            <p>or click to browse files</p>
            <p class="upload-subtitle">Limit 200MB per file • JPG, JPEG, PNG</p>
        </div>
        ''', unsafe_allow_html=True)

    # Add some helpful tips with improved styling
    with st.expander("💡 Tips for Best Results", expanded=False):
        st.markdown('''
        <ul class="tips-list">
            <li><strong>Quality:</strong> Upload a clear, well-lit photo of the menu</li>
            <li><strong>Readability:</strong> Ensure text is readable and not blurry</li>
            <li><strong>Framing:</strong> Crop out unnecessary parts of the image</li>
            <li><strong>Lighting:</strong> Avoid glare or shadows on the menu</li>
        </ul>
        ''', unsafe_allow_html=True)

    # Add a footer with improved styling
    st.markdown('<div class="footer">© 2025 MenuViz | Powered by AI</div>', unsafe_allow_html=True)

with col2:
    if uploaded_file and 'process_button' in locals() and process_button:
        # Read the file bytes
        image_bytes = uploaded_file.getvalue()

        # Create a container for the processing section
        with st.container():
            st.markdown('<div class="menu-card results-card">', unsafe_allow_html=True)
            st.markdown('<h3 class="card-title">🔄 Processing Menu</h3>', unsafe_allow_html=True)

            # Create a progress bar with custom styling
            progress_container = st.container()
            with progress_container:
                st.markdown('<div class="progress-container">', unsafe_allow_html=True)
                progress_placeholder = st.empty()
                status_text = st.empty()

                # Initialize progress
                progress = progress_placeholder.progress(0)
                status_text.markdown('<p class="loading-animation">Initializing...</p>', unsafe_allow_html=True)
                time.sleep(0.5)  # Small delay for better UX

                # Step 1: Upload to Supabase
                progress.progress(10)
                status_text.markdown('<p class="loading-animation">Uploading menu image...</p>', unsafe_allow_html=True)

                # Check if S3 API should be used
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
                st.markdown('</div>', unsafe_allow_html=True)
                progress_placeholder.empty()
                status_text.empty()

            # Show results
            if structured_menu_items:
                # Filter out invalid items first for accurate count
                valid_items = [item for item in structured_menu_items if item.get("name") and item.get("name") != "Dish Name"]

                # Create a compact header
                st.markdown('<div class="results-header">', unsafe_allow_html=True)
                st.markdown('<h3 style="margin:0; font-size:1.1rem; line-height:1.1;">🍽️ Discovered Menu Items</h3>', unsafe_allow_html=True)
                st.markdown(f'<p class="results-count">Found <span class="highlight">{len(valid_items)}</span> items on the menu</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Create a container for the menu items with minimal spacing
                menu_items_container = st.container()

                with menu_items_container:
                    # Display items in a grid
                    num_cols = 2  # Adjust based on screen size

                    # Filter out invalid items first
                    valid_items = [item for item in structured_menu_items if item.get("name") and item.get("name") != "Dish Name"]

                    # Create rows for the grid layout
                    rows = [valid_items[i:i + num_cols] for i in range(0, len(valid_items), num_cols)]

                    # Add a container for better grid styling
                    st.markdown('<div class="menu-grid">', unsafe_allow_html=True)

                    for row in rows:
                        cols = st.columns(num_cols)
                        # Add a custom class to remove vertical spacing
                        st.markdown('<style>.dish-row { margin: 0 !important; padding: 0 !important; }</style>', unsafe_allow_html=True)
                        st.markdown('<div class="dish-row">', unsafe_allow_html=True)
                        for i, item in enumerate(row):
                            name = item.get("name", "N/A")
                            description = item.get("description", "No description provided.")

                            with cols[i]:
                                # Generate image silently without showing loading message
                                img_url = generate_dish_image(name, description)

                                # Create a fixed-height card with proper spacing
                                st.markdown('<div class="dish-card">', unsafe_allow_html=True)

                                if img_url:
                                    # Image container at the top of the card
                                    st.markdown('<div class="dish-image-container">', unsafe_allow_html=True)
                                    st.image(img_url, use_container_width=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div class="image-error">Could not generate image</div>', unsafe_allow_html=True)

                                # Content container for title and description
                                st.markdown('<div class="dish-content">', unsafe_allow_html=True)

                                # Display dish name
                                st.markdown(f'<h4 class="dish-name">{name}</h4>', unsafe_allow_html=True)

                                # Display dish description
                                st.markdown(f'<p class="dish-description">{description}</p>', unsafe_allow_html=True)

                                st.markdown('</div>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)

                        # Close the dish-row div
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Close the menu grid container
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                if extracted_text:
                    st.markdown('<div class="warning-container">', unsafe_allow_html=True)
                    st.warning("Could not extract structured menu items. Here's the raw text:")
                    st.markdown('</div>', unsafe_allow_html=True)

                    with st.expander("Extracted Text", expanded=True):
                        st.markdown('<div class="extracted-text">', unsafe_allow_html=True)
                        st.text(extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-container">', unsafe_allow_html=True)
                    st.error("Could not process the menu image. Please try a clearer photo.")
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Show a placeholder when no file is uploaded
        # Display an illustration or placeholder image
        st.markdown('''
        <div class="placeholder-image">
            <img src="https://img.icons8.com/fluency/240/000000/food.png" alt="Food illustration" style="max-width: 180px; margin: 20px auto; display: block;">
            <p class="placeholder-text">Upload a menu to see AI-generated dish visualizations</p>
        </div>
        ''', unsafe_allow_html=True)


# Sidebar content
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.markdown('<h1 class="sidebar-title">MenuViz</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-subtitle">AI-Powered Menu Visualization</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # About section with improved styling
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="sidebar-section-title">📖 About</h2>', unsafe_allow_html=True)
    st.markdown('''
    <p class="sidebar-text">MenuViz uses advanced AI to transform restaurant menu photos into visual experiences:</p>

    <div class="sidebar-process">
        <div class="process-step">
            <div class="process-number">1</div>
            <div class="process-text"><strong>Extract</strong> dish information from menu images</div>
        </div>
        <div class="process-step">
            <div class="process-number">2</div>
            <div class="process-text"><strong>Process</strong> the data with Llama 4 AI</div>
        </div>
        <div class="process-step">
            <div class="process-number">3</div>
            <div class="process-text"><strong>Generate</strong> realistic dish visualizations</div>
        </div>
        <div class="process-step">
            <div class="process-number">4</div>
            <div class="process-text"><strong>Display</strong> the results in an organized gallery</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Technology stack with improved styling
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="sidebar-section-title">⚙️ Powered By</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="tech-category">', unsafe_allow_html=True)
        st.markdown('<p class="tech-title">Frontend</p>', unsafe_allow_html=True)
        st.markdown('<p class="tech-item">• Streamlit</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="tech-category">', unsafe_allow_html=True)
        st.markdown('<p class="tech-title">Storage</p>', unsafe_allow_html=True)
        st.markdown('<p class="tech-item">• Supabase</p>', unsafe_allow_html=True)
        st.markdown('<p class="tech-item">• S3 API</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="tech-category">', unsafe_allow_html=True)
        st.markdown('<p class="tech-title">AI Models</p>', unsafe_allow_html=True)
        st.markdown('<p class="tech-item">• Llama 4 (Groq)</p>', unsafe_allow_html=True)
        st.markdown('<p class="tech-item">• Flux (Together)</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Add version and GitHub link with improved styling
    st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
    st.markdown('<hr class="footer-divider">', unsafe_allow_html=True)
    st.markdown('<p class="version-text">v1.0.0 | <a href="https://github.com/yourusername/menuviz" target="_blank" class="github-link">GitHub</a></p>', unsafe_allow_html=True)

    # Current date/time
    now = datetime.now()
    st.markdown(f'<p class="update-text">Last updated: {now.strftime("%b %d, %Y")}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- End of app.py ---