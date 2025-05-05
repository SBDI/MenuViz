import os
from supabase import create_client, Client
import streamlit as st # Using st for error display in this utility
import io

# Optional: Import S3 utilities if available
try:
    import s3_utils
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

# --- Configuration ---
# Access keys from environment variables
# Use st.secrets for Streamlit cloud deployment, os.environ for local
SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
SUPABASE_BUCKET_NAME = "menuviz" # Make sure this bucket exists in Supabase

# S3 access keys (optional)
S3_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY_ID") or st.secrets.get("S3_ACCESS_KEY_ID", "")
S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY") or st.secrets.get("S3_SECRET_ACCESS_KEY", "")

# Check if keys are set and initialize client
supabase: Client = None
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase URL or Key not set. Please provide them via environment variables or st.secrets.")
else:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error initializing Supabase client: {e}")
        supabase = None # Ensure supabase is None if initialization fails

# Initialize S3 client if credentials are available
s3_client = None
if S3_AVAILABLE and S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY:
    try:
        s3_client = s3_utils.create_s3_client_with_access_keys(
            access_key_id=S3_ACCESS_KEY_ID,
            secret_access_key=S3_SECRET_ACCESS_KEY
        )
    except Exception as e:
        st.error(f"Error initializing S3 client: {e}")
        s3_client = None

# --- Functions ---

def upload_image_to_supabase(image_bytes: bytes, filename: str, bucket_name: str = SUPABASE_BUCKET_NAME, use_s3: bool = False) -> str | None:
    """
    Uploads image data (bytes) to Supabase storage.

    Args:
        image_bytes: The image data as bytes.
        filename: The desired filename in the bucket.
        bucket_name: The name of the Supabase bucket.
        use_s3: Whether to use the S3 API instead of the Supabase API.

    Returns:
        The public URL of the uploaded image, or None if upload failed.
    """
    # Create a progress bar
    progress_bar = st.progress(0)
    status_placeholder = st.empty()

    try:
        # Update progress
        progress_bar.progress(10)
        status_placeholder.info(f"Checking storage bucket...")

        # Determine which method to use
        if use_s3 and S3_AVAILABLE and s3_client:
            # Use S3 API
            status_placeholder.info(f"Using S3 API for upload...")

            # Check if bucket exists using S3 API
            if not s3_utils.check_bucket_exists(bucket_name, s3_client=s3_client):
                progress_bar.empty()
                status_placeholder.error(f"Bucket '{bucket_name}' not found. Please create it in your Supabase dashboard.")
                return None

            # Update progress
            progress_bar.progress(25)
            status_placeholder.info(f"Uploading menu image via S3 API...")

            # Upload using S3 API
            public_url = s3_utils.upload_file(
                file_data=image_bytes,
                object_name=filename,
                bucket_name=bucket_name,
                s3_client=s3_client,
                content_type="image/jpeg"
            )

            # Update progress and clear status
            progress_bar.progress(100)
            status_placeholder.empty()

            return public_url

        else:
            # Use standard Supabase API
            if supabase is None:
                progress_bar.empty()
                status_placeholder.error("Supabase client not initialized. Check your API keys.")
                return None

            # First check if the bucket exists
            if not check_bucket_exists(bucket_name):
                progress_bar.empty()
                status_placeholder.error(f"Bucket '{bucket_name}' not found. Please create it in your Supabase dashboard.")
                return None

            # Update progress
            progress_bar.progress(25)
            status_placeholder.info(f"Uploading menu image...")

            # Create a file-like object from bytes
            file = io.BytesIO(image_bytes)
            file.seek(0)  # Reset file pointer to beginning

            # Try with file-like object
            try:
                result = supabase.storage.from_(bucket_name).upload(
                    path=filename,
                    file=file,
                    file_options={"content-type": "image/jpeg"}
                )
            except Exception as upload_error:
                # If that fails, try with raw bytes
                with st.expander("First upload attempt failed", expanded=False):
                    st.error(f"First upload attempt error: {str(upload_error)}")

                result = supabase.storage.from_(bucket_name).upload(
                    path=filename,
                    file=image_bytes,
                    file_options={"content-type": "image/jpeg"}
                )

            # Debug output (hidden in production)
            with st.expander("Debug Info", expanded=False):
                st.write(f"Upload result: {result}")

            # Update progress
            progress_bar.progress(75)

            # If successful, get the public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(filename)

            # Update progress and clear status
            progress_bar.progress(100)
            status_placeholder.empty()

            return public_url

    except Exception as e:
        # Handle error and update UI
        progress_bar.empty()
        error_msg = str(e)
        status_placeholder.error(f"Upload failed: {error_msg}")

        # Debug output
        with st.expander("Error Details", expanded=False):
            st.error(f"Error type: {type(e).__name__}")
            st.error(f"Error message: {error_msg}")

        return None

# Function to check if the bucket exists
def check_bucket_exists(bucket_name: str = SUPABASE_BUCKET_NAME) -> bool:
    """
    Checks if the specified bucket exists in Supabase storage.

    Args:
        bucket_name: The name of the bucket to check.

    Returns:
        True if the bucket exists, False otherwise.
    """
    if supabase is None:
        st.error("Supabase client not initialized. Check your API keys.")
        return False

    try:
        # List all buckets
        buckets = supabase.storage.list_buckets()

        # Debug output
        with st.expander("Supabase Buckets", expanded=False):
            st.write(buckets)

        # Check if our bucket exists
        bucket_exists = any(bucket.get('name') == bucket_name for bucket in buckets)

        if not bucket_exists:
            # Try to create the bucket
            if create_bucket(bucket_name):
                return True
            else:
                st.error(f"Bucket '{bucket_name}' not found and could not be created.")
                return False

        return bucket_exists

    except Exception as e:
        st.error(f"Error checking buckets: {str(e)}")
        return False

# Function to create a bucket
def create_bucket(bucket_name: str) -> bool:
    """
    Creates a new bucket in Supabase storage.

    Args:
        bucket_name: The name of the bucket to create.

    Returns:
        True if the bucket was created successfully, False otherwise.
    """
    if supabase is None:
        st.error("Supabase client not initialized. Check your API keys.")
        return False

    try:
        # Create the bucket
        result = supabase.storage.create_bucket(
            id=bucket_name,
            options={
                "public": True  # Make the bucket public
            }
        )

        # Debug output
        with st.expander("Bucket Creation Result", expanded=False):
            st.write(result)

        st.success(f"Bucket '{bucket_name}' created successfully.")
        return True

    except Exception as e:
        st.error(f"Error creating bucket: {str(e)}")
        return False