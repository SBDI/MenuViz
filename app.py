import streamlit as st
# Optional: Load environment variables from .env file for local development
from dotenv import load_dotenv
load_dotenv()

import uuid # To create unique identifiers for uploads

# Import our utility functions
from supabase_utils import upload_image_to_supabase
from ai_utils import extract_menu_text, generate_dish_image

# --- Configuration and Setup Checks ---

# You can add checks for API keys here if you didn't add them to the utility files,
# but adding them to the utils is cleaner as those functions rely on them.
# Let's assume the utility functions handle reporting missing keys upon call.

# --- Streamlit App ---

st.set_page_config(layout="wide", page_title="MenuViz")
st.title("🍽️ MenuViz: See Your Menu Come Alive")

st.markdown("""
Upload a clear photo of a restaurant menu. MenuViz will attempt to extract the dish names and descriptions
and generate a visual representation for each item using AI.
""")

uploaded_file = st.file_uploader("Upload a photo of the menu", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Use a unique identifier for the upload session to avoid naming conflicts in storage
    session_id = uuid.uuid4()
    original_filename = uploaded_file.name
    # Create a unique filename for Supabase
    supabase_filename = f"menu_uploads/{session_id}_{original_filename}" # Organize uploads

    st.subheader("Uploaded Menu:")
    st.image(uploaded_file, caption=original_filename, use_container_width=True)

    # Read the file bytes once
    image_bytes = uploaded_file.getvalue()

    # --- Process the Image ---

    # Process the uploaded image
    if image_bytes: # Process automatically on file upload
        # Create a progress bar for the overall process
        overall_progress = st.progress(0)

        # Step 1: Upload to Supabase (25% of progress)
        public_url = upload_image_to_supabase(image_bytes, supabase_filename)
        overall_progress.progress(25)

        # Step 2: Extract menu items using Llama 4 (75% of progress)
        extracted_text, structured_menu_items = extract_menu_text(image_bytes)
        overall_progress.progress(100)

        # Clear the progress bar when done
        overall_progress.empty()

        # Display the raw extracted text in a collapsible section
        if extracted_text and not structured_menu_items:
            with st.expander("Raw Extracted Text", expanded=True):
                st.text(extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text)

        if structured_menu_items:
            st.subheader("Menu Items")

            # Display items and generate images in columns
            cols = st.columns(3) # Adjust number of columns (e.g., 2, 3, 4)

            # Use st.progress for overall generation status (optional)
            # total_items = len(structured_menu_items)
            # progress_bar = st.progress(0)

            for index, item in enumerate(structured_menu_items):
                name = item.get("name", "N/A")
                description = item.get("description", "No description provided.")

                # Ensure name is not empty or placeholder before generating
                if not name or name == "Dish Name":
                     st.warning(f"Skipping item {index + 1} due to invalid name: '{name}'")
                     continue # Skip to the next item

                # Generate image for each item
                # The generate_dish_image function has st.info/success/error messages inside
                img_url = generate_dish_image(name, description)

                # Display in the current column
                with cols[index % len(cols)]: # Cycle through columns
                     st.markdown(f"**{name}**")
                     st.caption(description)
                     if img_url:
                        st.image(img_url, caption=f"Visualisation of {name}", use_container_width=True)
                     else:
                        st.warning(f"Could not generate image for '{name}'.")
                     st.markdown("---") # Separator

                # Update progress bar (optional)
                # progress_bar.progress((index + 1) / total_items)

            # End of menu item processing

        else:
            st.warning("No menu items could be extracted. Please try a clearer image.")


st.sidebar.header("About")
st.sidebar.info("""
MenuViz is an experimental app that uses AI to extract menu items from an image
 and generate visualisations for each dish.

 Built with:
 - Streamlit (UI)
 - Supabase Storage (Image Upload)
 - Groq API (for Llama 4 Image & Text Processing)
 - Together AI (for Flux Image Generation)
""")

st.sidebar.header("Instructions")
st.sidebar.markdown("""
1.  **Install Dependencies:** `pip install -r requirements.txt`
2.  **Set API Keys:** Use environment variables (SUPABASE_URL, SUPABASE_ANON_KEY, GROQ_API_KEY, TOGETHER_API_KEY) or a `.env` file.
3.  **Setup Supabase:** Create a bucket named `menuviz` and ensure it's public.
4.  **Run App:** `streamlit run app.py`
5.  Upload a clear menu photo.
""")

# --- End of app.py ---