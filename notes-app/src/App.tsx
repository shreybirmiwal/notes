import React, { useState, useEffect } from 'react';
import './App.css';
import NotesColumn from './components/NotesColumn';

const classes = [
  { id: 'data-structures', name: 'Data Structures' },
  { id: 'discrete-math', name: 'Discrete Math' },
  { id: 'calculus', name: 'Calculus' },
  { id: 'ugs', name: 'UGS' },
  { id: 'misc', name: 'Misc' }
];

function App() {
  const [notes, setNotes] = useState<{ [key: string]: any[] }>({
    'data-structures': [],
    'discrete-math': [],
    'calculus': [],
    'ugs': [],
    'misc': []
  });

  return (
    <div className="App">
      <header className="App-header">
        <h1>My Notes</h1>
      </header>
      <main className="notes-container">
        {classes.map((classInfo) => (
          <NotesColumn
            key={classInfo.id}
            classId={classInfo.id}
            className={classInfo.name}
            notes={notes[classInfo.id] || []}
            setNotes={setNotes}
          />
        ))}
      </main>
    </div>
  );
}

export default App;
