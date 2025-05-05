import streamlit as st
import os
from dotenv import load_dotenv
import s3_utils
import json

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Supabase S3 Connection Example",
    page_icon="🪣",
    layout="wide"
)

# Title and description
st.title("Supabase S3 Connection Example")
st.markdown("""
This example demonstrates how to use Supabase's S3-compatible connection protocol.
You can use this to interact with Supabase Storage using the AWS S3 API.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Authentication Method")
    auth_method = st.radio(
        "Choose authentication method:",
        ["S3 Access Keys", "Session Token (JWT)"]
    )
    
    # Input fields based on authentication method
    if auth_method == "S3 Access Keys":
        st.info("S3 access keys provide full access to all S3 operations across all buckets and bypass RLS policies. These are meant to be used only on the server.")
        
        # Get S3 access keys
        access_key_id = st.text_input("Access Key ID", type="password")
        secret_access_key = st.text_input("Secret Access Key", type="password")
        
        # Create client button
        create_client_button = st.button("Create S3 Client")
        
        if create_client_button:
            if access_key_id and secret_access_key:
                s3_client = s3_utils.create_s3_client_with_access_keys(
                    access_key_id=access_key_id,
                    secret_access_key=secret_access_key
                )
                
                if s3_client:
                    st.session_state.s3_client = s3_client
                    st.session_state.auth_method = "access_keys"
                    st.success("S3 client created successfully!")
            else:
                st.error("Please provide both Access Key ID and Secret Access Key")
    
    else:  # Session Token
        st.info("Session token authentication uses a JWT token to provide limited access via RLS to all S3 operations.")
        
        # Get JWT token
        jwt_token = st.text_input("JWT Token", type="password")
        
        # Create client button
        create_client_button = st.button("Create S3 Client")
        
        if create_client_button:
            if jwt_token:
                s3_client = s3_utils.create_s3_client_with_session_token(
                    jwt_token=jwt_token
                )
                
                if s3_client:
                    st.session_state.s3_client = s3_client
                    st.session_state.auth_method = "session_token"
                    st.success("S3 client created successfully!")
            else:
                st.error("Please provide a JWT token")

# Main content
st.header("S3 Operations")

# Check if S3 client exists in session state
if "s3_client" not in st.session_state:
    st.warning("Please create an S3 client using the sidebar first")
else:
    # Tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["Upload", "List", "Download", "Delete"])
    
    # Upload tab
    with tab1:
        st.subheader("Upload File")
        
        # Bucket name
        bucket_name = st.text_input("Bucket Name", value="menuviz")
        
        # File uploader
        uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf", "txt"])
        
        # Object name (path in bucket)
        object_name = st.text_input("Object Name (path in bucket)", value="example/file.jpg")
        
        # Upload button
        if uploaded_file is not None:
            if st.button("Upload File"):
                # Get file content
                file_content = uploaded_file.getvalue()
                
                # Determine content type
                content_type = uploaded_file.type
                
                # Upload file
                public_url = s3_utils.upload_file(
                    file_data=file_content,
                    object_name=object_name,
                    bucket_name=bucket_name,
                    s3_client=st.session_state.s3_client,
                    content_type=content_type
                )
                
                if public_url:
                    st.success(f"File uploaded successfully!")
                    st.markdown(f"Public URL: [{public_url}]({public_url})")
    
    # List tab
    with tab2:
        st.subheader("List Files")
        
        # Bucket name
        bucket_name = st.text_input("Bucket Name", value="menuviz", key="list_bucket")
        
        # Prefix (optional)
        prefix = st.text_input("Prefix (optional)", value="")
        
        # List button
        if st.button("List Files"):
            files = s3_utils.list_files(
                bucket_name=bucket_name,
                prefix=prefix,
                s3_client=st.session_state.s3_client
            )
            
            if files is not None:
                if len(files) > 0:
                    st.success(f"Found {len(files)} files")
                    
                    # Display files in a table
                    file_data = []
                    for file in files:
                        file_data.append({
                            "Key": file.get("Key", ""),
                            "Size (bytes)": file.get("Size", 0),
                            "Last Modified": file.get("LastModified", "").strftime("%Y-%m-%d %H:%M:%S") if file.get("LastModified") else ""
                        })
                    
                    st.table(file_data)
                else:
                    st.info("No files found")
    
    # Download tab
    with tab3:
        st.subheader("Download File")
        
        # Bucket name
        bucket_name = st.text_input("Bucket Name", value="menuviz", key="download_bucket")
        
        # Object name
        object_name = st.text_input("Object Name", value="", key="download_object")
        
        # Download button
        if st.button("Download File"):
            if object_name:
                file_content = s3_utils.download_file(
                    object_name=object_name,
                    bucket_name=bucket_name,
                    s3_client=st.session_state.s3_client
                )
                
                if file_content:
                    st.success(f"File downloaded successfully!")
                    
                    # Determine file type and display accordingly
                    if object_name.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                        st.image(file_content, caption=object_name)
                    elif object_name.lower().endswith((".txt", ".csv", ".json")):
                        st.text(file_content.decode("utf-8"))
                    else:
                        # Create download button
                        st.download_button(
                            label="Download File",
                            data=file_content,
                            file_name=object_name.split("/")[-1],
                            mime="application/octet-stream"
                        )
            else:
                st.error("Please provide an object name")
    
    # Delete tab
    with tab4:
        st.subheader("Delete File")
        
        # Bucket name
        bucket_name = st.text_input("Bucket Name", value="menuviz", key="delete_bucket")
        
        # Object name
        object_name = st.text_input("Object Name", value="", key="delete_object")
        
        # Delete button with confirmation
        if object_name:
            if st.button("Delete File", type="primary"):
                success = s3_utils.delete_file(
                    object_name=object_name,
                    bucket_name=bucket_name,
                    s3_client=st.session_state.s3_client
                )
                
                if success:
                    st.success(f"File deleted successfully!")
                else:
                    st.error("Failed to delete file")
        else:
            st.error("Please provide an object name")

# Footer
st.markdown("---")
st.markdown("For more information, see the [Supabase S3 Authentication Documentation](https://supabase.com/docs/guides/storage/s3/authentication)")
