# 📚 SB Notes - Personal Note Management System

A powerful terminal-based tool for uploading, analyzing, and organizing PDF notes with AI assistance using Anthropic's Claude. Personalized for SB's note-taking workflow.

## ✨ Features

- **📤 Easy PDF Upload**: Simply provide the path to your PDF and the system handles the rest
- **👁️ AI Vision OCR**: Automatically reads scanned/handwritten notes by uploading PDFs directly to Claude Vision
- **🤖 AI-Powered Analysis**: Uses Claude to automatically analyze and summarize your notes
- **📊 Smart Organization**: Categorize notes by class and type (Notes, Homework, Study Prep, etc.)
- **🔍 Advanced Search**: Search through all your notes using AI-generated summaries and content
- **📄 Combined PDFs**: Generate organized PDFs per class with AI-generated page dividers
- **💾 Safe Storage**: Original PDFs are preserved in organized directories
- **🎨 Beautiful Terminal UI**: Rich, colorful interface with tables and panels

## 🚀 Quick Start

### 1. Setup

```bash
# Clone or download the project
cd notes

# Run the setup script
python setup.py
```

### 2. Run the Application

```bash
python sbnotes.py
```

Or make it executable:
```bash
chmod +x sbnotes.py
./sbnotes.py
```

## 📖 How to Use

### Uploading Notes

1. Select "Upload New Notes" from the main menu
2. Enter the path to your PDF file
3. Specify the class name (e.g., "Calculus", "Physics")
4. Choose the note type:
   - **Notes**: Regular class notes
   - **Homework**: Assignments and problem sets
   - **Study Prep**: Exam preparation materials
   - **Exam**: Test materials
   - **Other**: Miscellaneous materials

The system will:
- Extract text from your PDF (or upload directly to Claude Vision for scanned/handwritten notes)
- Analyze it with Claude AI
- Generate a summary and key topics
- Store the original PDF safely
- Create a searchable database entry

### Searching Notes

- Use the search function to find notes by:
  - Class name
  - Note type
  - Content keywords
  - AI-generated summaries

### Viewing Notes

- See an overview of all your classes
- View detailed information for each class
- Browse notes by date, type, and difficulty level

### Generating Combined PDFs

- Create organized PDFs for each class
- Each PDF includes:
  - AI-generated page dividers
  - Original note PDFs
  - Summaries and key topics
  - Date and type information

## 🏗️ Project Structure

```
sbnotes/
├── sbnotes.py         # Main application
├── setup.py           # Setup script
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (auto-created)
├── .gitignore        # Git ignore rules
├── README.md         # This file
├── data/             # Application data
│   └── notes.json    # Notes database
├── uploads/          # Original PDF uploads
└── generated_pdfs/   # Combined PDF outputs
```

## 🔧 Configuration

The system uses a `.env` file for configuration:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

The setup script will create this file automatically with your provided API key.

## 📦 Dependencies

- **anthropic**: AI analysis with Claude
- **PyPDF2**: PDF text extraction and manipulation
- **rich**: Beautiful terminal UI
- **python-dotenv**: Environment variable management
- **fpdf2**: PDF generation for dividers
- **python-dateutil**: Date parsing utilities
- **Anthropic Claude**: Direct PDF processing and AI analysis

## 🛡️ Safety Features

- **Original PDF Preservation**: All uploaded PDFs are safely stored in the `uploads/` directory
- **Data Backup**: Notes database is stored in JSON format for easy backup
- **Error Handling**: Comprehensive error handling prevents data loss
- **Git Integration**: Project is ready for version control

## 🎯 AI Analysis Features

Each uploaded note is analyzed by Claude to provide:

- **Summary**: 2-3 sentence overview
- **Key Topics**: Main concepts covered
- **Important Concepts**: Formulas, definitions, key points
- **Difficulty Level**: Beginner/Intermediate/Advanced
- **Study Time**: Estimated time needed to review
- **Related Topics**: Connected subjects for cross-reference

## 🔍 Search Capabilities

Search through:
- Class names
- Note types
- AI-generated summaries
- Key topics and concepts
- Upload dates

## 📄 PDF Generation

The system creates organized PDFs with:
- Professional page dividers
- AI-generated summaries
- Key topics and concepts
- Date and type information
- Original note content

## 🚨 Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your `.env` file contains the correct Anthropic API key
2. **PDF Text Extraction**: Some PDFs may not extract text properly if they're image-based
3. **File Permissions**: Ensure the script has permission to create directories and files

### Getting Help

- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your API key is correct in the `.env` file
- Ensure PDF files are readable and contain extractable text
- For scanned notes, the AI vision will automatically handle OCR

## 🎉 Features in Action

1. **Upload**: Drag and drop PDFs or provide file paths
2. **Analyze**: AI automatically categorizes and summarizes content
3. **Organize**: Notes are sorted by class, type, and date
4. **Search**: Find specific content across all your notes
5. **Generate**: Create professional combined PDFs for each class

## 🔄 Git Integration

The project is designed for version control:
- `.gitignore` excludes sensitive files and generated content
- Original PDFs are preserved in organized directories
- Database is stored in human-readable JSON format

---

**Happy Note Taking, SB! 📝✨**
