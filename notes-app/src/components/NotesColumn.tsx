import React, { useState } from 'react';
import { supabase } from '../supabase-config';
import './NotesColumn.css';
import UploadModal from './UploadModal';

interface Note {
  id: string;
  title: string;
  summary: string;
  tags: string;
  url: string;
  timestamp: Date;
}

interface NotesColumnProps {
  classId: string;
  className: string;
  notes: Note[];
  setNotes: React.Dispatch<React.SetStateAction<{ [key: string]: Note[] }>>;
}

const NotesColumn: React.FC<NotesColumnProps> = ({
  classId,
  className,
  notes,
  setNotes
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.includes('pdf')) {
      alert('Please upload a PDF file');
      return;
    }

    setSelectedFile(file);
    setIsModalOpen(true);
  };

  const handleUpload = async (title: string, summary: string, tags: string) => {
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      console.log('Starting upload to Supabase...');

      // Upload file to Supabase Storage
      const fileName = `${Date.now()}_${selectedFile.name}`;
      console.log('Uploading file:', fileName, 'to bucket: notes');

      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('notes')
        .upload(`${classId}/${fileName}`, selectedFile);

      if (uploadError) {
        console.error('Upload error:', uploadError);
        throw uploadError;
      }

      console.log('Upload successful:', uploadData);

      // Get the public URL
      const { data: urlData } = supabase.storage
        .from('notes')
        .getPublicUrl(`${classId}/${fileName}`);

      // Create note object
      const newNote: Note = {
        id: Date.now().toString(),
        title,
        summary,
        tags,
        url: urlData.publicUrl,
        timestamp: new Date()
      };

      // Save to Supabase Database
      const { error: dbError } = await supabase
        .from('notes')
        .insert({
          class_id: classId,
          title,
          summary,
          tags,
          file_path: `${classId}/${fileName}`,
          created_at: new Date().toISOString()
        });

      if (dbError) {
        throw dbError;
      }

      // Update local state
      setNotes(prev => ({
        ...prev,
        [classId]: [...(prev[classId] || []), newNote]
      }));

      // Reset state
      setSelectedFile(null);
      setIsModalOpen(false);

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
    <>
      <div className="notes-column">
        <div className="column-header">
          <h2>{className}</h2>
          <div className="upload-section">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
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
                {note.summary && <p className="note-summary">{note.summary}</p>}
                {note.tags && <p className="note-tags">{note.tags}</p>}
                <p className="note-date">{note.timestamp.toLocaleDateString()}</p>
              </div>
            ))
          )}
        </div>
      </div>

      <UploadModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedFile(null);
        }}
        onUpload={handleUpload}
        fileName={selectedFile?.name || ''}
      />
    </>
  );
};

export default NotesColumn;
