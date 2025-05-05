# MenuViz

MenuViz is an AI-powered application that brings restaurant menus to life by extracting dish information from menu images and generating visual representations for each dish. It leverages cutting-edge AI models to transform static menu photos into an interactive visual experience.

![MenuViz Demo](https://via.placeholder.com/800x400?text=MenuViz+Demo)

## Features

- **Menu Image Processing**: Upload a photo of a restaurant menu and extract dish names and descriptions using Llama 4's multimodal capabilities, eliminating the need for manual OCR.
- **Dish Visualization**: Generate realistic images of each dish using Together AI's Flux image generation model, helping customers visualize menu items.
- **Cloud Storage**: Store uploaded menu images in Supabase with both standard API and S3-compatible API options for flexible storage solutions.
- **Clean UI**: Enjoy a frictionless user experience with progress indicators, minimal clutter, and responsive design.
- **Real-time Processing**: Watch as the AI analyzes your menu and generates images in real-time with visual feedback.
- **Error Handling**: Robust error handling ensures the application gracefully manages issues with image uploads or AI processing.

## Technology Stack

- **Frontend**:
  - Streamlit for the web interface
  - Custom CSS for styling without external dependencies

- **AI Models**:
  - **Image Processing**: Llama 4 (via Groq API) for multimodal menu analysis
  - **Image Generation**: Flux (via Together AI) for photorealistic dish visualization

- **Storage**:
  - **Primary**: Supabase Storage for cloud-based file management
  - **Alternative**: S3-compatible API for advanced storage operations

- **Backend**:
  - Python 3.9+ for core application logic
  - Boto3 for S3 API integration
  - Environment variable management for secure configuration

## System Requirements

- Python 3.9 or higher
- Internet connection for API access
- 2GB+ RAM recommended for processing larger menu images
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/menuviz.git
   cd menuviz
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the `.env.example` template and add your API keys:
   ```bash
   cp .env.example .env
   # Edit the .env file with your API keys
   ```

5. (Optional) For Streamlit Cloud deployment, add the same environment variables to your Streamlit secrets.

## API Keys Setup

You'll need to obtain API keys from the following services:

1. **Supabase**:
   - Create an account at [supabase.com](https://supabase.com) and create a new project
   - Get your project URL and anon key from the API settings page
   - These keys are used for basic storage operations

2. **Groq**:
   - Sign up at [groq.com](https://console.groq.com) to get an API key
   - This key provides access to Llama 4, which powers the menu text extraction
   - Groq offers high-performance inference for large language models

3. **Together AI**:
   - Register at [together.ai](https://together.ai) to get an API key
   - This key enables access to the Flux image generation model
   - Together AI provides state-of-the-art image generation capabilities

## Supabase Setup

### Basic Storage Setup

1. Create a new bucket named `menuviz` in your Supabase project:
   - Go to Storage in your Supabase dashboard
   - Click "Create new bucket"
   - Name it `menuviz`
   - Enable public access for the bucket

2. Configure RLS (Row Level Security) policies if needed:
   - By default, the application uses the anon key which has limited permissions
   - You can customize access control through Supabase's RLS policies

### Using Supabase S3 API (Optional)

MenuViz supports using Supabase's S3-compatible API for storage operations. This provides several advantages:

- **Compatibility**: Use standard S3 tools and libraries with your Supabase storage
- **Advanced Operations**: Access to more sophisticated storage operations not available in the standard API
- **Performance**: Potentially better performance for large file operations
- **Flexibility**: More control over storage configuration

To use the S3 API:

1. Generate S3 access keys from your Supabase project settings:
   - Navigate to Storage > S3 Access Keys in your Supabase dashboard
   - Create a new key pair
   - Copy both the Access Key ID and Secret Access Key

2. Add the keys to your `.env` file or Streamlit secrets:
   ```
   S3_ACCESS_KEY_ID="your-s3-access-key-id"
   S3_SECRET_ACCESS_KEY="your-s3-secret-access-key"
   USE_SUPABASE_S3="true"
   ```

3. (Optional) Configure additional S3 settings:
   ```
   S3_ENDPOINT="https://your-project-ref.supabase.co/storage/v1/s3"
   S3_REGION="your-preferred-region"
   ```

4. The application will automatically use the S3 API for storage operations when these keys are provided.

### Testing S3 Connection

You can test your S3 connection using the included example application:

```bash
streamlit run s3_example.py
```

This tool provides a simple interface to:
- Test authentication with both access keys and session tokens
- Upload files to your Supabase bucket
- List files in your bucket
- Download files from your bucket
- Delete files from your bucket

## Usage

### Running the Application

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. The application will open in your default web browser at `http://localhost:8501`

### Processing a Menu

1. **Upload a Menu Image**:
   - Use the file uploader in the left panel
   - Select a clear, well-lit photo of a restaurant menu
   - Supported formats: JPG, JPEG, PNG

2. **Process the Menu**:
   - Click the "Process Menu" button
   - Watch the progress indicators as the application:
     - Uploads the image to Supabase storage
     - Analyzes the menu text using Llama 4
     - Extracts dish names and descriptions
     - Generates visual representations for each dish

3. **View Results**:
   - Extracted menu items appear in a grid layout
   - Each item includes:
     - Dish name
     - Description
     - AI-generated visual representation
   - If extraction fails, the raw text will be displayed

### Tips for Best Results

- Use clear, well-lit photos of menus
- Ensure text is readable and not blurry
- Crop out unnecessary parts of the image
- Avoid glare or shadows on the menu
- For complex menus, consider processing sections separately

## Advanced Usage

### S3 API Integration

The application supports both standard Supabase storage API and S3-compatible API. To switch between them:

1. **Standard API** (default):
   - No additional configuration needed
   - Uses the Supabase client for storage operations

2. **S3 API**:
   - Set `USE_SUPABASE_S3="true"` in your environment variables
   - Requires S3 access keys to be configured
   - Uses boto3 for S3-compatible operations

### Customization

You can customize the application by modifying:

- **CSS Styles**: Edit the CSS in `app.py` to change the appearance
- **Bucket Name**: Change the `SUPABASE_BUCKET_NAME` in `supabase_utils.py`
- **AI Parameters**: Adjust model parameters in `ai_utils.py` for different results

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure all API keys are correctly set in your `.env` file
   - Check that the keys have not expired or been revoked

2. **Storage Issues**:
   - Verify the Supabase bucket exists and is publicly accessible
   - Check that your Supabase project is active

3. **Image Processing Failures**:
   - Try using a clearer image of the menu
   - Ensure the menu text is legible in the uploaded image

### Getting Help

If you encounter issues not covered here:
- Check the Streamlit, Supabase, Groq, or Together AI documentation
- Open an issue in the GitHub repository
- Consult the error messages in the application for specific guidance

## Contributing

Contributions are welcome! Here's how you can contribute:

1. **Report Bugs**: Open an issue describing the bug and steps to reproduce
2. **Suggest Features**: Submit feature requests through GitHub issues
3. **Submit Pull Requests**: Fork the repository, make changes, and submit a PR
4. **Improve Documentation**: Help clarify or expand the documentation

Please follow the existing code style and include appropriate tests for new features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the intuitive web application framework
- [Groq](https://groq.com/) for the high-performance Llama 4 API
- [Together AI](https://together.ai/) for the powerful Flux image generation model
- [Supabase](https://supabase.com/) for flexible storage solutions and S3-compatible API
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for S3 API integration
