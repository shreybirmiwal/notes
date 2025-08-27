#!/usr/bin/env python3
"""
SB Notes Web Interface
A beautiful Streamlit web app for uploading, analyzing, and organizing PDF notes with AI assistance.
"""

import os
import json
import shutil
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
import streamlit as st
import anthropic
from dotenv import load_dotenv
import fpdf
from dateutil import parser

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SB Notes - Personal Note Management",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class SBNotesWeb:
    def __init__(self):
        self.data_dir = Path("data")
        self.uploads_dir = Path("uploads")
        self.generated_dir = Path("generated_pdfs")
        self.notes_file = self.data_dir / "notes.json"
        
        # Initialize directories
        self._init_directories()
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("❌ ANTHROPIC_API_KEY not found in environment variables")
            st.stop()
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Load existing notes
        self.notes = self._load_notes()
    
    def _init_directories(self):
        """Initialize necessary directories."""
        self.data_dir.mkdir(exist_ok=True)
        self.uploads_dir.mkdir(exist_ok=True)
        self.generated_dir.mkdir(exist_ok=True)
    
    def _load_notes(self) -> Dict:
        """Load existing notes from JSON file."""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                st.warning("⚠️ Corrupted notes file, starting fresh")
        return {"notes": [], "classes": {}}
    
    def _save_notes(self):
        """Save notes to JSON file."""
        with open(self.notes_file, 'w') as f:
            json.dump(self.notes, f, indent=2)
    
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file using OCR with vision capabilities."""
        try:
            # First try traditional text extraction
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += page_text + "\n"
                
                # If we got substantial text, return it
                if len(text.strip()) > 50:
                    return text
            
            # If traditional extraction failed or got minimal text, use vision OCR
            st.info("🔄 Traditional text extraction failed. Using AI vision to read scanned notes...")
            return self._extract_text_with_vision(pdf_path)
            
        except Exception as e:
            st.error(f"❌ Error with traditional extraction: {e}")
            st.info("🔄 Falling back to AI vision OCR...")
            return self._extract_text_with_vision(pdf_path)
    
    def _extract_text_with_vision(self, pdf_path: Path) -> str:
        """Extract text from scanned PDF using Claude's PDF document support."""
        try:
            with st.spinner("📤 Uploading PDF to Claude for analysis..."):
                # Read the PDF file and convert to base64
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()
                    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                
                # Use Claude's PDF document support to read the entire PDF
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": pdf_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": "Please read and transcribe all the text content from this PDF. This appears to be handwritten or scanned notes. Extract all text, mathematical formulas, diagrams descriptions, and any other written content from all pages. Be thorough and accurate in your transcription. Organize the content by pages if possible."
                                }
                            ]
                        }
                    ]
                )
                
                return message.content[0].text
                
        except Exception as e:
            st.error(f"❌ Error with PDF document processing: {e}")
            return f"PDF document processing failed: {str(e)}"
    
    def _analyze_notes_with_ai(self, text: str, note_type: str, class_name: str) -> Dict:
        """Analyze notes using Anthropic Claude."""
        prompt = f"""
        Analyze the following {note_type} for {class_name}. This content was extracted from scanned/handwritten notes using AI vision, so it may contain transcription artifacts.
        
        Please provide:
        1. A concise summary (2-3 sentences)
        2. Key topics/concepts covered
        3. Important formulas, definitions, or concepts
        4. Difficulty level (Beginner/Intermediate/Advanced)
        5. Estimated study time needed
        6. Related topics that might be connected
        7. Content quality assessment (how well the notes were transcribed)
        
        Notes content:
        {text[:8000]}  # Limit to avoid token limits
        
        Please format your response as JSON with these keys:
        - summary
        - key_topics
        - important_concepts
        - difficulty_level
        - estimated_study_time
        - related_topics
        - transcription_quality
        """
        
        try:
            with st.spinner("🤖 Analyzing notes with AI..."):
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Try to parse JSON response
                try:
                    response_text = message.content[0].text.strip()
                    # Remove code block markers if present
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    response_text = response_text.strip()
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    # If JSON parsing fails, create a structured response
                    return {
                        "summary": message.content[0].text[:200] + "...",
                        "key_topics": ["Extracted from AI analysis"],
                        "important_concepts": ["See full analysis"],
                        "difficulty_level": "Unknown",
                        "estimated_study_time": "Unknown",
                        "related_topics": [],
                        "transcription_quality": "Unknown"
                    }
                    
        except Exception as e:
            st.error(f"❌ Error analyzing notes with AI: {e}")
            return {
                "summary": "AI analysis failed",
                "key_topics": [],
                "important_concepts": [],
                "difficulty_level": "Unknown",
                "estimated_study_time": "Unknown",
                "related_topics": [],
                "transcription_quality": "Failed"
            }
    
    def upload_notes(self):
        """Upload and process a new PDF note."""
        st.markdown("## 📤 Upload New Notes")
        
        with st.container():
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            
            # File upload
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Upload your scanned or handwritten notes"
            )
            
            if uploaded_file is not None:
                # Display file info
                file_details = {
                    "Filename": uploaded_file.name,
                    "File size": f"{uploaded_file.size / 1024:.1f} KB",
                    "File type": uploaded_file.type
                }
                st.json(file_details)
                
                # Class and type selection
                col1, col2 = st.columns(2)
                with col1:
                    class_name = st.text_input("Class Name", placeholder="e.g., Calculus, Physics")
                with col2:
                    note_type = st.selectbox(
                        "Note Type",
                        ["Notes", "Homework", "Study Prep", "Exam", "Other"]
                    )
                
                # Upload button
                if st.button("🚀 Upload & Analyze", type="primary"):
                    if not class_name:
                        st.error("❌ Please enter a class name")
                        return
                    
                    # Save uploaded file
                    timestamp = datetime.now().isoformat()
                    note_id = f"{class_name}_{timestamp}"
                    upload_path = self.uploads_dir / f"{note_id}.pdf"
                    
                    with open(upload_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Extract text
                    with st.spinner("📖 Extracting text from PDF..."):
                        text = self._extract_text_from_pdf(upload_path)
                    
                    if not text.strip():
                        st.error("❌ Could not extract text from PDF")
                        return
                    
                    # Analyze with AI
                    analysis = self._analyze_notes_with_ai(text, note_type, class_name)
                    
                    # Create note entry
                    note_entry = {
                        "id": note_id,
                        "class_name": class_name,
                        "note_type": note_type,
                        "upload_date": timestamp,
                        "file_path": str(upload_path),
                        "analysis": analysis,
                        "text_preview": text[:500] + "..." if len(text) > 500 else text
                    }
                    
                    # Add to notes list
                    self.notes["notes"].append(note_entry)
                    
                    # Update class information
                    if class_name not in self.notes["classes"]:
                        self.notes["classes"][class_name] = {
                            "total_notes": 0,
                            "note_types": {},
                            "last_updated": timestamp
                        }
                    
                    self.notes["classes"][class_name]["total_notes"] += 1
                    self.notes["classes"][class_name]["note_types"][note_type] = \
                        self.notes["classes"][class_name]["note_types"].get(note_type, 0) + 1
                    self.notes["classes"][class_name]["last_updated"] = timestamp
                    
                    # Save notes
                    self._save_notes()
                    
                    # Success message
                    st.success("✅ Successfully uploaded and analyzed notes!")
                    
                    # Display analysis results
                    st.markdown("### 📊 Analysis Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Summary:**")
                        st.write(analysis.get('summary', 'No summary available'))
                        
                        st.markdown("**Difficulty Level:**")
                        st.info(analysis.get('difficulty_level', 'Unknown'))
                        
                        st.markdown("**Study Time:**")
                        st.info(analysis.get('estimated_study_time', 'Unknown'))
                    
                    with col2:
                        st.markdown("**Key Topics:**")
                        topics = analysis.get('key_topics', [])
                        if topics:
                            for topic in topics[:5]:
                                st.write(f"• {topic}")
                        else:
                            st.write("No topics identified")
                        
                        st.markdown("**Transcription Quality:**")
                        quality = analysis.get('transcription_quality', 'Unknown')
                        if 'good' in quality.lower() or 'excellent' in quality.lower():
                            st.success(quality)
                        elif 'failed' in quality.lower():
                            st.error(quality)
                        else:
                            st.info(quality)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def view_notes(self):
        """View all notes with filtering options."""
        st.markdown("## 📖 View Notes")
        
        if not self.notes["notes"]:
            st.info("📝 No notes uploaded yet. Upload your first note to get started!")
            return
        
        # Statistics
        total_notes = len(self.notes["notes"])
        total_classes = len(self.notes["classes"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Notes", total_notes)
        with col2:
            st.metric("Classes", total_classes)
        with col3:
            latest_note = max(self.notes["notes"], key=lambda x: x["upload_date"])
            latest_date = datetime.fromisoformat(latest_note["upload_date"]).strftime("%Y-%m-%d")
            st.metric("Latest Upload", latest_date)
        
        # Filter options
        st.markdown("### 🔍 Filter Notes")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            class_filter = st.selectbox(
                "Filter by Class",
                ["All Classes"] + list(self.notes["classes"].keys())
            )
        
        with col2:
            type_filter = st.selectbox(
                "Filter by Type",
                ["All Types", "Notes", "Homework", "Study Prep", "Exam", "Other"]
            )
        
        with col3:
            search_term = st.text_input("Search in content", placeholder="Enter keywords...")
        
        # Filter notes
        filtered_notes = self.notes["notes"]
        
        if class_filter != "All Classes":
            filtered_notes = [note for note in filtered_notes if note["class_name"] == class_filter]
        
        if type_filter != "All Types":
            filtered_notes = [note for note in filtered_notes if note["note_type"] == type_filter]
        
        if search_term:
            filtered_notes = [
                note for note in filtered_notes
                if search_term.lower() in note["class_name"].lower() or
                   search_term.lower() in note["note_type"].lower() or
                   search_term.lower() in note["analysis"].get("summary", "").lower()
            ]
        
        # Display notes
        st.markdown(f"### 📋 Notes ({len(filtered_notes)} found)")
        
        for note in filtered_notes:
            with st.expander(f"📚 {note['class_name']} - {note['note_type']} ({datetime.fromisoformat(note['upload_date']).strftime('%Y-%m-%d %H:%M')})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Summary:**")
                    st.write(note["analysis"].get("summary", "No summary available"))
                    
                    st.markdown("**Key Topics:**")
                    topics = note["analysis"].get("key_topics", [])
                    if topics:
                        for topic in topics[:3]:
                            st.write(f"• {topic}")
                    
                    st.markdown("**Text Preview:**")
                    st.text(note["text_preview"][:200] + "...")
                
                with col2:
                    st.markdown("**Details:**")
                    st.write(f"**Class:** {note['class_name']}")
                    st.write(f"**Type:** {note['note_type']}")
                    st.write(f"**Difficulty:** {note['analysis'].get('difficulty_level', 'Unknown')}")
                    st.write(f"**Study Time:** {note['analysis'].get('estimated_study_time', 'Unknown')}")
                    st.write(f"**Quality:** {note['analysis'].get('transcription_quality', 'Unknown')}")
    
    def generate_pdf(self):
        """Generate combined PDFs for classes."""
        st.markdown("## 📄 Generate Class PDFs")
        
        if not self.notes["classes"]:
            st.info("📝 No classes available. Upload some notes first!")
            return
        
        # Class selection
        selected_class = st.selectbox(
            "Select a class to generate PDF",
            list(self.notes["classes"].keys())
        )
        
        if selected_class:
            class_notes = [note for note in self.notes["notes"] if note["class_name"] == selected_class]
            
            st.markdown(f"### 📚 {selected_class} Notes")
            st.write(f"Found {len(class_notes)} notes for this class")
            
            # Show notes that will be included
            for note in class_notes:
                st.write(f"• {note['note_type']} - {datetime.fromisoformat(note['upload_date']).strftime('%Y-%m-%d')}")
            
            if st.button("📄 Generate Combined PDF", type="primary"):
                with st.spinner("🔄 Generating PDF..."):
                    # Create combined PDF
                    output_path = self.generated_dir / f"{selected_class}_combined_notes.pdf"
                    
                    try:
                        # Use PyPDF2 to combine PDFs
                        merger = PyPDF2.PdfMerger()
                        
                        for i, note in enumerate(class_notes):
                            # Add actual note PDF
                            if Path(note["file_path"]).exists():
                                merger.append(note["file_path"])
                            else:
                                st.warning(f"⚠️ Original PDF not found for {note['id']}")
                        
                        # Write combined PDF
                        with open(output_path, 'wb') as output_file:
                            merger.write(output_file)
                        
                        st.success(f"✅ Generated combined PDF: {output_path}")
                        
                        # Provide download link
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="📥 Download Combined PDF",
                                data=f.read(),
                                file_name=f"{selected_class}_combined_notes.pdf",
                                mime="application/pdf"
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {e}")

def main():
    # Header
    st.markdown('<h1 class="main-header">📚 SB Notes</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Personal Note Management with AI</p>', unsafe_allow_html=True)
    
    # Initialize app
    app = SBNotesWeb()
    
    # Sidebar navigation
    st.sidebar.markdown("## 🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📤 Upload Notes", "📖 View Notes", "📄 Generate PDFs"]
    )
    
    # Sidebar stats
    st.sidebar.markdown("## 📊 Statistics")
    total_notes = len(app.notes["notes"])
    total_classes = len(app.notes["classes"])
    
    st.sidebar.metric("Total Notes", total_notes)
    st.sidebar.metric("Classes", total_classes)
    
    if total_notes > 0:
        latest_note = max(app.notes["notes"], key=lambda x: x["upload_date"])
        latest_date = datetime.fromisoformat(latest_note["upload_date"]).strftime("%Y-%m-%d")
        st.sidebar.metric("Latest Upload", latest_date)
    
    # Page routing
    if page == "📤 Upload Notes":
        app.upload_notes()
    elif page == "📖 View Notes":
        app.view_notes()
    elif page == "📄 Generate PDFs":
        app.generate_pdf()

if __name__ == "__main__":
    main()
