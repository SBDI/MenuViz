# MenuViz

MenuViz is an AI-powered application that brings restaurant menus to life by extracting dish information from menu images and generating visual representations for each dish.

![MenuViz Demo](https://via.placeholder.com/800x400?text=MenuViz+Demo)

## Features

- **Menu Image Processing**: Upload a photo of a restaurant menu and extract dish names and descriptions using Llama 4's multimodal capabilities.
- **Dish Visualization**: Generate realistic images of each dish using Together AI's Flux image generation model.
- **Cloud Storage**: Store uploaded menu images in Supabase for easy access and sharing.
- **Clean UI**: Enjoy a frictionless user experience with progress indicators and minimal clutter.

## Technology Stack

- **Frontend**: Streamlit
- **Image Processing**: Llama 4 via Groq API
- **Image Generation**: Flux via Together AI
- **Storage**: Supabase Storage

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

## API Keys Setup

You'll need to obtain API keys from the following services:

1. **Supabase**: Create an account at [supabase.com](https://supabase.com) and create a new project. Get your project URL and anon key from the API settings.

2. **Groq**: Sign up at [groq.com](https://console.groq.com) to get an API key for accessing Llama 4.

3. **Together AI**: Register at [together.ai](https://together.ai) to get an API key for the Flux image generation model.

## Supabase Setup

1. Create a new bucket named `menuviz` in your Supabase project.
2. Make sure the bucket is set to public access.

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. Upload a clear photo of a restaurant menu.

3. The application will:
   - Extract dish names and descriptions from the menu
   - Generate visual representations for each dish
   - Display the results in a clean, organized layout

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web application framework
- [Groq](https://groq.com/) for the Llama 4 API
- [Together AI](https://together.ai/) for the Flux image generation model
- [Supabase](https://supabase.com/) for storage solutions
