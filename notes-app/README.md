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

### 2. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Go to Project Settings > General
4. Scroll down to "Your apps" section
5. Click on the web app or create a new one
6. Copy the config values from the provided code snippet
7. Replace the values in `src/firebase-config.ts`

### 3. Enable Firebase Services

In your Firebase project:
1. Go to Firestore Database and create a database
2. Go to Storage and create a storage bucket
3. Set up security rules for both services

### 4. Run the app
```bash
npm start
```

## Usage

1. Click "Upload Notes" in any class column
2. Select a PDF file of your handwritten notes
3. The note will appear in the column with the filename as the title
4. Click on any note to view it in a new tab

## Security

- All notes are stored securely in Firebase Storage
- Metadata is stored in Firestore Database
- Files are organized by class for easy management
