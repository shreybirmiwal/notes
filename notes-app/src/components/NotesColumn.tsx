import React, { useState } from 'react';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { doc, setDoc, collection, addDoc } from 'firebase/firestore';
import { storage, db } from '../App';
import './NotesColumn.css';

interface Note {
  id: string;
  title: string;
  url: string;
  timestamp: Date;
}

interface NotesColumnProps {
  classId: string;
  className: string;
  notes: Note[];
  setNotes: React.Dispatch<React.SetStateAction<{[key: string]: Note[]}>>;
}

const NotesColumn: React.FC<NotesColumnProps> = ({ 
  classId, 
  className, 
  notes, 
  setNotes 
}) => {
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.includes('pdf')) {
      alert('Please upload a PDF file');
      return;
    }

    setIsUploading(true);
    try {
      // Upload to Firebase Storage
      const storageRef = ref(storage, `notes/${classId}/${file.name}`);
      const snapshot = await uploadBytes(storageRef, file);
      const downloadURL = await getDownloadURL(snapshot.ref);

      // Create note object
      const newNote: Note = {
        id: Date.now().toString(),
        title: file.name.replace('.pdf', ''),
        url: downloadURL,
        timestamp: new Date()
      };

      // Save to Firestore
      await addDoc(collection(db, 'notes'), {
        classId,
        ...newNote,
        timestamp: newNote.timestamp.toISOString()
      });

      // Update local state
      setNotes(prev => ({
        ...prev,
        [classId]: [...(prev[classId] || []), newNote]
      }));

    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleNoteClick = (note: Note) => {
    window.open(note.url, '_blank');
  };

  return (
    <div className="notes-column">
      <div className="column-header">
        <h2>{className}</h2>
        <div className="upload-section">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            id={`file-upload-${classId}`}
            style={{ display: 'none' }}
          />
          <label 
            htmlFor={`file-upload-${classId}`}
            className="upload-button"
          >
            {isUploading ? 'Uploading...' : 'Upload Notes'}
          </label>
        </div>
      </div>
      
      <div className="notes-list">
        {notes.length === 0 ? (
          <p className="no-notes">No notes yet</p>
        ) : (
          notes.map((note) => (
            <div 
              key={note.id} 
              className="note-item"
              onClick={() => handleNoteClick(note)}
            >
              <h3>{note.title}</h3>
              <p>{note.timestamp.toLocaleDateString()}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default NotesColumn;
