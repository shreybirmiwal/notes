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
