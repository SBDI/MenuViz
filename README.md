# MenuViz 🍽️

> AI-powered menu visualization tool that brings restaurant menus to life.

![MenuViz Demo](https://via.placeholder.com/800x400?text=MenuViz+Demo)

## ✨ Features

- **Menu Analysis** - Extract dish info from menu photos using Llama 4
- **Dish Visualization** - Generate realistic dish images with Flux AI
- **Cloud Storage** - Store images with Supabase (standard or S3 API)
- **Clean UI** - Intuitive interface with real-time progress indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- API keys for [Supabase](https://supabase.com), [Groq](https://console.groq.com), and [Together AI](https://together.ai)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/menuviz.git
cd menuviz

# Set up environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```bash
streamlit run app.py
```

1. Upload a clear menu photo (JPG/PNG)
2. Click "Process Menu"
3. View extracted dishes with AI-generated visuals

## 🔧 Supabase Setup

### Basic Setup

1. Create a bucket named `menuviz` in your Supabase dashboard
2. Make it publicly accessible

### S3 API Integration (Optional)

For advanced storage operations:

1. Get S3 access keys from Supabase (Storage > S3 Access Keys)
2. Add to your `.env` file:
   ```
   S3_ACCESS_KEY_ID="your-key"
   S3_SECRET_ACCESS_KEY="your-secret"
   USE_SUPABASE_S3="true"
   ```

Test your S3 connection:
```bash
streamlit run s3_example.py
```

## 💡 Tips for Best Results

- Use clear, well-lit menu photos
- Ensure text is readable without glare or shadows
- For large menus, process sections separately

## 🛠️ Customization

- **CSS**: Edit styles directly in `app.py`
- **Storage**: Configure bucket in `supabase_utils.py`
- **AI Parameters**: Adjust settings in `ai_utils.py`

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) - Web framework
- [Groq](https://groq.com/) - Llama 4 API
- [Together AI](https://together.ai/) - Flux image generation
- [Supabase](https://supabase.com/) - Storage solution
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - S3 integration
