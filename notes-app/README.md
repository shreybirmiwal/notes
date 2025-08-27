# Simple Notes App

A minimalistic React app for organizing handwritten notes by class. Upload PDF scans of your notes and access them easily.

## Features

- 4 columns for different classes
- Upload PDF notes with a simple button
- Click on notes to view them in a new tab
- Secure storage using Firebase
- Clean, minimalistic black and white design

## Setup

### 1. Install dependencies
```bash
npm install
```

### 2. Configure Supabase

Follow the setup guide in `supabase-setup.md` to:
1. Create a storage bucket named `notes`
2. Create the database table
3. Set up storage policies

### 3. Run the app
```bash
npm start
```

## Usage

1. Click "Upload Notes" in any class column
2. Select a PDF file of your handwritten notes
3. The note will appear in the column with the filename as the title
4. Click on any note to view it in a new tab

## Security

- All notes are stored securely in Supabase Storage
- Metadata is stored in Supabase Database
- Files are organized by class for easy management
