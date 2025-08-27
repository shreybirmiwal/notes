#!/usr/bin/env python3
"""
SB Notes - Personal Note Management System
A terminal-based tool for uploading, analyzing, and organizing PDF notes with AI assistance.
"""

import os
import json
import shutil
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import anthropic
from dotenv import load_dotenv
import fpdf
from dateutil import parser

# Load environment variables
load_dotenv()

class NoteManager:
    def __init__(self):
        self.console = Console()
        self.data_dir = Path("data")
        self.uploads_dir = Path("uploads")
        self.generated_dir = Path("generated_pdfs")
        self.notes_file = self.data_dir / "notes.json"
        
        # Initialize directories
        self._init_directories()
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.console.print("[red]Error: ANTHROPIC_API_KEY not found in environment variables[/red]")
            exit(1)
        
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
                self.console.print("[yellow]Warning: Corrupted notes file, starting fresh[/yellow]")
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
            self.console.print("[yellow]Traditional text extraction failed. Using AI vision to read scanned notes...[/yellow]")
            return self._extract_text_with_vision(pdf_path)
            
        except Exception as e:
            self.console.print(f"[red]Error with traditional extraction: {e}[/red]")
            self.console.print("[yellow]Falling back to AI vision OCR...[/yellow]")
            return self._extract_text_with_vision(pdf_path)
    
    def _extract_text_with_vision(self, pdf_path: Path) -> str:
        """Extract text from scanned PDF using Claude's PDF document support."""
        try:
            self.console.print("[yellow]Uploading PDF directly to Claude for analysis...[/yellow]")
            
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
            self.console.print(f"[red]Error with PDF document processing: {e}[/red]")
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
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
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
            self.console.print(f"[red]Error analyzing notes with AI: {e}[/red]")
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
        self.console.print(Panel.fit("📚 Upload New Notes", style="bold blue"))
        
        # Get PDF file path
        pdf_path = Prompt.ask("Enter the path to your PDF file")
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            self.console.print("[red]Error: File not found[/red]")
            return
        
        if pdf_path.suffix.lower() != '.pdf':
            self.console.print("[red]Error: File must be a PDF[/red]")
            return
        
        # Get class information
        class_name = Prompt.ask("Enter the class name")
        note_type = Prompt.ask(
            "Select note type",
            choices=["Notes", "Homework", "Study Prep", "Exam", "Other"]
        )
        
        # Extract text from PDF
        self.console.print("[yellow]Extracting text from PDF...[/yellow]")
        text = self._extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            self.console.print("[red]Error: Could not extract text from PDF[/red]")
            return
        
        # Analyze with AI
        self.console.print("[yellow]Analyzing notes with AI...[/yellow]")
        analysis = self._analyze_notes_with_ai(text, note_type, class_name)
        
        # Create note entry
        timestamp = datetime.now().isoformat()
        note_id = f"{class_name}_{timestamp}"
        
        # Copy PDF to uploads directory
        upload_path = self.uploads_dir / f"{note_id}.pdf"
        shutil.copy2(pdf_path, upload_path)
        
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
        
        self.console.print(f"[green]✅ Successfully uploaded notes for {class_name}[/green]")
        self.console.print(f"[blue]Summary: {analysis.get('summary', 'No summary available')}[/blue]")
    
    def search_notes(self):
        """Search through notes."""
        self.console.print(Panel.fit("🔍 Search Notes", style="bold green"))
        
        search_term = Prompt.ask("Enter search term")
        
        # Search in class names, note types, and AI analysis
        results = []
        for note in self.notes["notes"]:
            searchable_text = f"{note['class_name']} {note['note_type']} {note['analysis'].get('summary', '')} {note['analysis'].get('key_topics', [])}"
            
            if search_term.lower() in searchable_text.lower():
                results.append(note)
        
        if not results:
            self.console.print("[yellow]No notes found matching your search[/yellow]")
            return
        
        # Display results
        table = Table(title=f"Search Results for '{search_term}'")
        table.add_column("Class", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Date", style="green")
        table.add_column("Summary", style="white")
        
        for note in results[:10]:  # Limit to 10 results
            date = datetime.fromisoformat(note["upload_date"]).strftime("%Y-%m-%d %H:%M")
            summary = note["analysis"].get("summary", "No summary")[:100] + "..."
            table.add_row(note["class_name"], note["note_type"], date, summary)
        
        self.console.print(table)
    
    def view_notes(self):
        """View all notes with filtering options."""
        self.console.print(Panel.fit("📖 View Notes", style="bold yellow"))
        
        if not self.notes["notes"]:
            self.console.print("[yellow]No notes uploaded yet[/yellow]")
            return
        
        # Show class overview
        table = Table(title="Classes Overview")
        table.add_column("Class", style="cyan")
        table.add_column("Total Notes", style="magenta")
        table.add_column("Note Types", style="green")
        table.add_column("Last Updated", style="white")
        
        for class_name, class_info in self.notes["classes"].items():
            note_types = ", ".join([f"{t}: {c}" for t, c in class_info["note_types"].items()])
            last_updated = datetime.fromisoformat(class_info["last_updated"]).strftime("%Y-%m-%d")
            table.add_row(class_name, str(class_info["total_notes"]), note_types, last_updated)
        
        self.console.print(table)
        
        # Ask for specific class to view
        class_name = Prompt.ask("Enter class name to view detailed notes (or press Enter to skip)")
        
        if class_name and class_name in self.notes["classes"]:
            self._view_class_notes(class_name)
    
    def _view_class_notes(self, class_name: str):
        """View detailed notes for a specific class."""
        class_notes = [note for note in self.notes["notes"] if note["class_name"] == class_name]
        
        table = Table(title=f"Notes for {class_name}")
        table.add_column("Type", style="cyan")
        table.add_column("Date", style="magenta")
        table.add_column("Summary", style="green")
        table.add_column("Difficulty", style="yellow")
        table.add_column("Study Time", style="white")
        table.add_column("Quality", style="blue")
        
        for note in sorted(class_notes, key=lambda x: x["upload_date"], reverse=True):
            date = datetime.fromisoformat(note["upload_date"]).strftime("%Y-%m-%d %H:%M")
            summary = note["analysis"].get("summary", "No summary")[:80] + "..."
            difficulty = note["analysis"].get("difficulty_level", "Unknown")
            study_time = note["analysis"].get("estimated_study_time", "Unknown")
            quality = note["analysis"].get("transcription_quality", "Unknown")
            
            table.add_row(note["note_type"], date, summary, difficulty, study_time, quality)
        
        self.console.print(table)
    
    def generate_class_pdf(self):
        """Generate a combined PDF for a class with page dividers."""
        self.console.print(Panel.fit("📄 Generate Class PDF", style="bold purple"))
        
        if not self.notes["classes"]:
            self.console.print("[yellow]No classes available[/yellow]")
            return
        
        # Show available classes
        classes = list(self.notes["classes"].keys())
        for i, class_name in enumerate(classes, 1):
            self.console.print(f"{i}. {class_name}")
        
        try:
            choice = int(Prompt.ask("Select class number")) - 1
            if 0 <= choice < len(classes):
                class_name = classes[choice]
                self._create_class_pdf(class_name)
            else:
                self.console.print("[red]Invalid selection[/red]")
        except ValueError:
            self.console.print("[red]Please enter a valid number[/red]")
    
    def _create_class_pdf(self, class_name: str):
        """Create a combined PDF for a specific class."""
        class_notes = [note for note in self.notes["notes"] if note["class_name"] == class_name]
        
        if not class_notes:
            self.console.print(f"[yellow]No notes found for {class_name}[/yellow]")
            return
        
        # Sort notes by date
        class_notes.sort(key=lambda x: x["upload_date"])
        
        # Create combined PDF
        output_path = self.generated_dir / f"{class_name}_combined_notes.pdf"
        
        try:
            # Use PyPDF2 to combine PDFs
            merger = PyPDF2.PdfMerger()
            
            for i, note in enumerate(class_notes):
                # Add divider page
                divider_pdf = self._create_divider_page(note, i + 1)
                merger.append(divider_pdf)
                
                # Add actual note PDF
                if Path(note["file_path"]).exists():
                    merger.append(note["file_path"])
                else:
                    self.console.print(f"[yellow]Warning: Original PDF not found for {note['id']}[/yellow]")
            
            # Write combined PDF
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            self.console.print(f"[green]✅ Generated combined PDF: {output_path}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error generating PDF: {e}[/red]")
    
    def _create_divider_page(self, note: Dict, day_number: int) -> str:
        """Create a divider page for the combined PDF."""
        # Create a temporary PDF with divider content
        divider_path = self.generated_dir / f"divider_{note['id']}.pdf"
        
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 16)
        
        # Title
        pdf.cell(0, 20, f"Day {day_number} Notes: {note['class_name']}", new_x=fpdf.XPos.LMARGIN, new_y=fpdf.YPos.NEXT, align='C')
        pdf.ln(10)
        
        # Note type and date
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0, 10, f"Type: {note['note_type']}", new_x=fpdf.XPos.LMARGIN, new_y=fpdf.YPos.NEXT)
        pdf.cell(0, 10, f"Date: {datetime.fromisoformat(note['upload_date']).strftime('%Y-%m-%d %H:%M')}", new_x=fpdf.XPos.LMARGIN, new_y=fpdf.YPos.NEXT)
        pdf.ln(10)
        
        # AI analysis summary
        analysis = note['analysis']
        pdf.cell(0, 10, "AI Analysis Summary:", new_x=fpdf.XPos.LMARGIN, new_y=fpdf.YPos.NEXT)
        pdf.set_font('helvetica', '', 10)
        
        summary = analysis.get('summary', 'No summary available')
        # Wrap text to fit page width
        for line in [summary[i:i+80] for i in range(0, len(summary), 80)]:
            pdf.cell(0, 8, line, new_x=fpdf.XPos.LMARGIN, new_y=fpdf.YPos.NEXT)
        
        pdf.ln(10)
        
        # Key topics
        if analysis.get('key_topics'):
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(0, 10, "Key Topics:", new_x=fpdf.XPos.LMARGIN, new_y=fpdf.YPos.NEXT)
            pdf.set_font('helvetica', '', 10)
            for topic in analysis['key_topics'][:5]:  # Limit to 5 topics
                pdf.cell(0, 8, f"- {topic}", new_x=fpdf.XPos.LMARGIN, new_y=fpdf.YPos.NEXT)
        
        pdf.output(str(divider_path))
        return str(divider_path)
    
    def run(self):
        """Main application loop."""
        while True:
            self.console.print("\n" + "="*60)
            self.console.print(Panel.fit("📚 SB Notes - Personal Note Management", style="bold blue"))
            self.console.print("="*60)
            
            self.console.print("1. 📤 Upload New Notes")
            self.console.print("2. 🔍 Search Notes")
            self.console.print("3. 📖 View Notes")
            self.console.print("4. 📄 Generate Class PDF")
            self.console.print("5. ❌ Exit")
            
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.upload_notes()
            elif choice == "2":
                self.search_notes()
            elif choice == "3":
                self.view_notes()
            elif choice == "4":
                self.generate_class_pdf()
            elif choice == "5":
                self.console.print("[green]Goodbye! 👋[/green]")
                break

if __name__ == "__main__":
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your Anthropic API key:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
        print("\nOr run: python3 setup.py")
        exit(1)
    
    note_manager = NoteManager()
    note_manager.run()
