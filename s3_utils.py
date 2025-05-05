import os
import json
import boto3
from botocore.client import Config
import streamlit as st
from typing import Optional, Dict, List, Union, BinaryIO
import io

# --- Configuration ---
# Access keys from environment variables or Streamlit secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY", "")
SUPABASE_BUCKET_NAME = "menuviz"  # Default bucket name

# Extract project reference from Supabase URL
# Example: https://bxtluxytxmydgmztplrt.supabase.co -> bxtluxytxmydgmztplrt
def get_project_ref() -> str:
    """Extract project reference from Supabase URL."""
    if not SUPABASE_URL:
        return ""

    # Extract the subdomain from the URL
    try:
        # Remove https:// and split by dots
        parts = SUPABASE_URL.replace("https://", "").split(".")
        return parts[0]
    except Exception:
        return ""

PROJECT_REF = get_project_ref()

# Get S3 endpoint and region from environment variables or construct from Supabase URL
S3_ENDPOINT = os.environ.get("S3_ENDPOINT") or st.secrets.get("S3_ENDPOINT", f"https://{PROJECT_REF}.supabase.co/storage/v1/s3")
REGION = os.environ.get("S3_REGION") or st.secrets.get("S3_REGION", "us-east-1")  # Default region

# --- S3 Client Creation Functions ---

def create_s3_client_with_access_keys(access_key_id: str, secret_access_key: str) -> Optional[boto3.client]:
    """
    Create an S3 client using Supabase S3 access keys (server-side use only).

    Args:
        access_key_id: The S3 access key ID from Supabase
        secret_access_key: The S3 secret access key from Supabase

    Returns:
        An S3 client or None if creation fails
    """
    if not access_key_id or not secret_access_key:
        st.error("S3 access keys not provided")
        return None

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=REGION,
            config=Config(s3={'addressing_style': 'path'})
        )
        return s3_client
    except Exception as e:
        st.error(f"Error creating S3 client with access keys: {e}")
        return None

def create_s3_client_with_session_token(jwt_token: str) -> Optional[boto3.client]:
    """
    Create an S3 client using a JWT token for user-authenticated access.
    This respects RLS policies set in Supabase.

    Args:
        jwt_token: A valid JWT token from Supabase auth

    Returns:
        An S3 client or None if creation fails
    """
    if not PROJECT_REF or not SUPABASE_KEY or not jwt_token:
        st.error("Missing required credentials for S3 session token authentication")
        return None

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=PROJECT_REF,
            aws_secret_access_key=SUPABASE_KEY,
            aws_session_token=jwt_token,
            region_name=REGION,
            config=Config(s3={'addressing_style': 'path'})
        )
        return s3_client
    except Exception as e:
        st.error(f"Error creating S3 client with session token: {e}")
        return None

# --- S3 Operations ---

def upload_file(
    file_data: Union[bytes, BinaryIO, str],
    object_name: str,
    bucket_name: str = SUPABASE_BUCKET_NAME,
    s3_client: Optional[boto3.client] = None,
    content_type: str = "application/octet-stream",
    access_key_id: str = "",
    secret_access_key: str = "",
    jwt_token: str = ""
) -> Optional[str]:
    """
    Upload a file to Supabase Storage using S3 API.

    Args:
        file_data: The file data as bytes, file-like object, or path to file
        object_name: The name to give the object in the bucket
        bucket_name: The name of the bucket to upload to
        s3_client: An existing S3 client (optional)
        content_type: The content type of the file
        access_key_id: S3 access key ID (if s3_client not provided)
        secret_access_key: S3 secret access key (if s3_client not provided)
        jwt_token: JWT token for user authentication (if s3_client not provided)

    Returns:
        The public URL of the uploaded file or None if upload fails
    """
    # Create a progress bar
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    status_placeholder.info("Preparing to upload file...")

    try:
        # Create S3 client if not provided
        if s3_client is None:
            if jwt_token:
                s3_client = create_s3_client_with_session_token(jwt_token)
            elif access_key_id and secret_access_key:
                s3_client = create_s3_client_with_access_keys(access_key_id, secret_access_key)
            else:
                status_placeholder.error("No authentication method provided")
                progress_bar.empty()
                return None

        if s3_client is None:
            status_placeholder.error("Failed to create S3 client")
            progress_bar.empty()
            return None

        # Update progress
        progress_bar.progress(25)
        status_placeholder.info("Preparing file data...")

        # Handle different file_data types
        if isinstance(file_data, str):
            # Assume it's a file path
            with open(file_data, 'rb') as f:
                file_bytes = f.read()
        elif isinstance(file_data, bytes):
            file_bytes = file_data
        else:
            # Assume it's a file-like object
            file_bytes = file_data.read()

        # Update progress
        progress_bar.progress(50)
        status_placeholder.info(f"Uploading to {bucket_name}/{object_name}...")

        # Upload the file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=file_bytes,
            ContentType=content_type
        )

        # Update progress
        progress_bar.progress(75)
        status_placeholder.info("Generating public URL...")

        # Generate the public URL
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{object_name}"

        # Update progress and clear status
        progress_bar.progress(100)
        status_placeholder.empty()
        progress_bar.empty()

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

def list_files(
    bucket_name: str = SUPABASE_BUCKET_NAME,
    prefix: str = "",
    s3_client: Optional[boto3.client] = None,
    access_key_id: str = "",
    secret_access_key: str = "",
    jwt_token: str = ""
) -> Optional[List[Dict]]:
    """
    List files in a Supabase Storage bucket using S3 API.

    Args:
        bucket_name: The name of the bucket to list files from
        prefix: Filter results to objects with this prefix
        s3_client: An existing S3 client (optional)
        access_key_id: S3 access key ID (if s3_client not provided)
        secret_access_key: S3 secret access key (if s3_client not provided)
        jwt_token: JWT token for user authentication (if s3_client not provided)

    Returns:
        A list of objects or None if operation fails
    """
    try:
        # Create S3 client if not provided
        if s3_client is None:
            if jwt_token:
                s3_client = create_s3_client_with_session_token(jwt_token)
            elif access_key_id and secret_access_key:
                s3_client = create_s3_client_with_access_keys(access_key_id, secret_access_key)
            else:
                st.error("No authentication method provided")
                return None

        if s3_client is None:
            st.error("Failed to create S3 client")
            return None

        # List objects
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )

        # Extract and return the objects
        if 'Contents' in response:
            return response['Contents']
        else:
            return []

    except Exception as e:
        st.error(f"Error listing files: {e}")
        return None

def download_file(
    object_name: str,
    bucket_name: str = SUPABASE_BUCKET_NAME,
    s3_client: Optional[boto3.client] = None,
    access_key_id: str = "",
    secret_access_key: str = "",
    jwt_token: str = ""
) -> Optional[bytes]:
    """
    Download a file from Supabase Storage using S3 API.

    Args:
        object_name: The name of the object to download
        bucket_name: The name of the bucket containing the object
        s3_client: An existing S3 client (optional)
        access_key_id: S3 access key ID (if s3_client not provided)
        secret_access_key: S3 secret access key (if s3_client not provided)
        jwt_token: JWT token for user authentication (if s3_client not provided)

    Returns:
        The file content as bytes or None if download fails
    """
    try:
        # Create S3 client if not provided
        if s3_client is None:
            if jwt_token:
                s3_client = create_s3_client_with_session_token(jwt_token)
            elif access_key_id and secret_access_key:
                s3_client = create_s3_client_with_access_keys(access_key_id, secret_access_key)
            else:
                st.error("No authentication method provided")
                return None

        if s3_client is None:
            st.error("Failed to create S3 client")
            return None

        # Download the file
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_name
        )

        # Read and return the file content
        return response['Body'].read()

    except Exception as e:
        st.error(f"Error downloading file: {e}")
        return None

def delete_file(
    object_name: str,
    bucket_name: str = SUPABASE_BUCKET_NAME,
    s3_client: Optional[boto3.client] = None,
    access_key_id: str = "",
    secret_access_key: str = "",
    jwt_token: str = ""
) -> bool:
    """
    Delete a file from Supabase Storage using S3 API.

    Args:
        object_name: The name of the object to delete
        bucket_name: The name of the bucket containing the object
        s3_client: An existing S3 client (optional)
        access_key_id: S3 access key ID (if s3_client not provided)
        secret_access_key: S3 secret access key (if s3_client not provided)
        jwt_token: JWT token for user authentication (if s3_client not provided)

    Returns:
        True if deletion succeeds, False otherwise
    """
    try:
        # Create S3 client if not provided
        if s3_client is None:
            if jwt_token:
                s3_client = create_s3_client_with_session_token(jwt_token)
            elif access_key_id and secret_access_key:
                s3_client = create_s3_client_with_access_keys(access_key_id, secret_access_key)
            else:
                st.error("No authentication method provided")
                return False

        if s3_client is None:
            st.error("Failed to create S3 client")
            return False

        # Delete the file
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=object_name
        )

        return True

    except Exception as e:
        st.error(f"Error deleting file: {e}")
        return False

# --- Helper Functions ---

def check_bucket_exists(
    bucket_name: str = SUPABASE_BUCKET_NAME,
    s3_client: Optional[boto3.client] = None,
    access_key_id: str = "",
    secret_access_key: str = "",
    jwt_token: str = ""
) -> bool:
    """
    Check if a bucket exists in Supabase Storage using S3 API.

    Args:
        bucket_name: The name of the bucket to check
        s3_client: An existing S3 client (optional)
        access_key_id: S3 access key ID (if s3_client not provided)
        secret_access_key: S3 secret access key (if s3_client not provided)
        jwt_token: JWT token for user authentication (if s3_client not provided)

    Returns:
        True if the bucket exists, False otherwise
    """
    try:
        # Create S3 client if not provided
        if s3_client is None:
            if jwt_token:
                s3_client = create_s3_client_with_session_token(jwt_token)
            elif access_key_id and secret_access_key:
                s3_client = create_s3_client_with_access_keys(access_key_id, secret_access_key)
            else:
                st.error("No authentication method provided")
                return False

        if s3_client is None:
            st.error("Failed to create S3 client")
            return False

        # List buckets
        response = s3_client.list_buckets()

        # Check if the bucket exists
        for bucket in response['Buckets']:
            if bucket['Name'] == bucket_name:
                return True

        return False

    except Exception as e:
        st.error(f"Error checking if bucket exists: {e}")
        return False

def create_bucket(
    bucket_name: str,
    s3_client: Optional[boto3.client] = None,
    access_key_id: str = "",
    secret_access_key: str = "",
    public: bool = True
) -> bool:
    """
    Create a bucket in Supabase Storage using S3 API.
    Note: This requires S3 access keys, not a session token.

    Args:
        bucket_name: The name of the bucket to create
        s3_client: An existing S3 client (optional)
        access_key_id: S3 access key ID (if s3_client not provided)
        secret_access_key: S3 secret access key (if s3_client not provided)
        public: Whether the bucket should be public

    Returns:
        True if creation succeeds, False otherwise
    """
    try:
        # Create S3 client if not provided
        if s3_client is None:
            if access_key_id and secret_access_key:
                s3_client = create_s3_client_with_access_keys(access_key_id, secret_access_key)
            else:
                st.error("S3 access keys required to create a bucket")
                return False

        if s3_client is None:
            st.error("Failed to create S3 client")
            return False

        # Create the bucket
        s3_client.create_bucket(Bucket=bucket_name)

        # Set bucket policy if public
        if public:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }

            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy)
            )

        return True

    except Exception as e:
        st.error(f"Error creating bucket: {e}")
        return False
