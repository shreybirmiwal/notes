import React, { useState, useEffect } from 'react';
import './App.css';
import NotesColumn from './components/NotesColumn';
import ToDoColumn from './components/ToDoColumn';
import { supabase } from './supabase-config';

const classes = [
  { id: 'data-structures', name: 'Data Structures' },
  { id: 'discrete-math', name: 'Discrete Math' },
  { id: 'calculus', name: 'Calculus' },
  { id: 'ugs', name: 'UGS' },
  { id: 'misc', name: 'Misc' }
];

function App() {
  const [activeTab, setActiveTab] = useState<'notes' | 'todos'>('notes');
  const [notes, setNotes] = useState<{ [key: string]: any[] }>({
    'data-structures': [],
    'discrete-math': [],
    'calculus': [],
    'ugs': [],
    'misc': []
  });
  const [todos, setTodos] = useState<{ [key: string]: any[] }>({
    'data-structures': [],
    'discrete-math': [],
    'calculus': [],
    'ugs': [],
    'misc': []
  });

  // Download function to export all data
  const downloadAllData = async () => {
    try {
      // Create a zip file using JSZip
      const JSZip = (await import('jszip')).default;
      const zip = new JSZip();
      
      // Add notes for each class
      for (const classId of Object.keys(notes)) {
        const className = classes.find(c => c.id === classId)?.name || classId;
        const classNotes = notes[classId] || [];
        
        if (classNotes.length > 0) {
          const notesFolder = zip.folder(`Notes/${className}`);
          
          for (let index = 0; index < classNotes.length; index++) {
            const note = classNotes[index];
            
            // Create text file with note metadata
            const noteContent = `Title: ${note.title}
Summary: ${note.summary}
Tags: ${note.tags}
Created: ${note.timestamp.toLocaleDateString()}
URL: ${note.url}

---`;
            
            notesFolder?.file(`${index + 1}_${note.title.replace(/[^a-zA-Z0-9]/g, '_')}.txt`, noteContent);
            
            // Download and add the actual PDF file if URL exists
            if (note.url) {
              try {
                const response = await fetch(note.url);
                if (response.ok) {
                  const pdfBlob = await response.blob();
                  const fileName = note.file_path || `${note.title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
                  notesFolder?.file(`${index + 1}_${fileName}`, pdfBlob);
                }
              } catch (error) {
                console.error(`Error downloading PDF for note ${note.title}:`, error);
                // Add a placeholder file indicating the PDF couldn't be downloaded
                notesFolder?.file(`${index + 1}_${note.title.replace(/[^a-zA-Z0-9]/g, '_')}_PDF_NOT_FOUND.txt`, 
                  `PDF file could not be downloaded from: ${note.url}`);
              }
            }
          }
        }
      }
      
      // Add todos for each class
      Object.keys(todos).forEach(classId => {
        const className = classes.find(c => c.id === classId)?.name || classId;
        const classTodos = todos[classId] || [];
        
        if (classTodos.length > 0) {
          const todosFolder = zip.folder(`Todos/${className}`);
          
          classTodos.forEach((todo, index) => {
            const todoContent = `Title: ${todo.title}
Description: ${todo.description}
Due Date: ${todo.dueDate}
Priority: ${todo.priority}
Completed: ${todo.completed ? 'Yes' : 'No'}
Created: ${todo.timestamp.toLocaleDateString()}

---`;
            
            todosFolder?.file(`${index + 1}_${todo.title.replace(/[^a-zA-Z0-9]/g, '_')}.txt`, todoContent);
          });
        }
      });
      
      // Add a summary file
      const summaryContent = `Notes and Todos Export
Generated: ${new Date().toLocaleString()}

Summary:
${Object.keys(notes).map(classId => {
  const className = classes.find(c => c.id === classId)?.name || classId;
  const noteCount = notes[classId]?.length || 0;
  const todoCount = todos[classId]?.length || 0;
  return `${className}: ${noteCount} notes, ${todoCount} todos`;
}).join('\n')}

Note: This export includes both text summaries and the actual PDF files where available.`;
      
      zip.file('README.txt', summaryContent);
      
      // Generate and download the zip file
      const content = await zip.generateAsync({ type: 'blob' });
      const url = window.URL.createObjectURL(content);
      const link = document.createElement('a');
      link.href = url;
      link.download = `notes-export-${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error downloading data:', error);
      alert('Error downloading data. Please try again.');
    }
  };

  // Load existing notes and todos from Supabase
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load notes
        const { data: notesData, error: notesError } = await supabase
          .from('notes')
          .select('*')
          .order('created_at', { ascending: false });

        if (notesError) {
          console.error('Error loading notes:', notesError);
        } else if (notesData) {
          const groupedNotes: { [key: string]: any[] } = {
            'data-structures': [],
            'discrete-math': [],
            'calculus': [],
            'ugs': [],
            'misc': []
          };

          notesData.forEach((note: any) => {
            if (groupedNotes[note.class_id]) {
              groupedNotes[note.class_id].push({
                id: note.id.toString(),
                title: note.title,
                summary: note.summary || '',
                tags: note.tags || '',
                file_path: note.file_path || '',
                url: note.file_path ? `https://pycjkqmdyenoiqlowghj.supabase.co/storage/v1/object/public/notes/${note.file_path}` : '',
                timestamp: new Date(note.created_at)
              });
            }
          });

          setNotes(groupedNotes);
        }

        // Load todos
        const { data: todosData, error: todosError } = await supabase
          .from('todos')
          .select('*')
          .order('created_at', { ascending: false });

        if (todosError) {
          console.error('Error loading todos:', todosError);
        } else if (todosData) {
          const groupedTodos: { [key: string]: any[] } = {
            'data-structures': [],
            'discrete-math': [],
            'calculus': [],
            'ugs': [],
            'misc': []
          };

          todosData.forEach((todo: any) => {
            if (groupedTodos[todo.class_id]) {
              groupedTodos[todo.class_id].push({
                id: todo.id.toString(),
                title: todo.title,
                description: todo.description || '',
                dueDate: todo.due_date || '',
                priority: todo.priority,
                completed: todo.completed,
                timestamp: new Date(todo.created_at)
              });
            }
          });

          setTodos(groupedTodos);
        }
      } catch (error) {
        console.error('Error loading data:', error);
      }
    };

    loadData();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>My Notes</h1>
        <div className="tab-navigation">
          <button
            className={`tab-button ${activeTab === 'notes' ? 'active' : ''}`}
            onClick={() => setActiveTab('notes')}
          >
            Notes
          </button>
          <button
            className={`tab-button ${activeTab === 'todos' ? 'active' : ''}`}
            onClick={() => setActiveTab('todos')}
          >
            To Do
          </button>
        </div>
        <button className="download-button" onClick={downloadAllData}>
          Download All Data
        </button>
      </header>
      <main className="notes-container">
        {activeTab === 'notes' ? (
          classes.map((classInfo) => (
            <NotesColumn
              key={classInfo.id}
              classId={classInfo.id}
              className={classInfo.name}
              notes={notes[classInfo.id] || []}
              setNotes={setNotes}
            />
          ))
        ) : (
          classes.map((classInfo) => (
            <ToDoColumn
              key={classInfo.id}
              classId={classInfo.id}
              className={classInfo.name}
              todos={todos[classInfo.id] || []}
              setTodos={setTodos}
            />
          ))
        )}
      </main>
    </div>
  );
}

export default App;
