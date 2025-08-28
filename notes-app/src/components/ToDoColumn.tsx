import React, { useState } from 'react';
import { supabase } from '../supabase-config';
import './ToDoColumn.css';

interface ToDoItem {
    id: string;
    title: string;
    description: string;
    dueDate: string;
    priority: 'low' | 'medium' | 'high';
    completed: boolean;
    timestamp: Date;
}

interface ToDoColumnProps {
    classId: string;
    className: string;
    todos: ToDoItem[];
    setTodos: React.Dispatch<React.SetStateAction<{ [key: string]: ToDoItem[] }>>;
}

const ToDoColumn: React.FC<ToDoColumnProps> = ({
    classId,
    className,
    todos,
    setTodos
}) => {
    const [isAdding, setIsAdding] = useState(false);
    const [newTodo, setNewTodo] = useState({
        title: '',
        description: '',
        dueDate: '',
        priority: 'medium' as const
    });

    const handleAddTodo = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newTodo.title.trim()) return;

        try {
            // Save to Supabase first
            const { data: insertData, error } = await supabase
                .from('todos')
                .insert({
                    class_id: classId,
                    title: newTodo.title,
                    description: newTodo.description,
                    due_date: newTodo.dueDate || null,
                    priority: newTodo.priority,
                    completed: false,
                    created_at: new Date().toISOString()
                })
                .select();

            if (error) throw error;

            // Create todo item with the actual ID from database
            const todoItem: ToDoItem = {
                id: insertData[0].id.toString(),
                title: newTodo.title,
                description: newTodo.description,
                dueDate: newTodo.dueDate,
                priority: newTodo.priority,
                completed: false,
                timestamp: new Date()
            };

            // Update local state - add new todo at the beginning to maintain newest-first order
            setTodos(prev => ({
                ...prev,
                [classId]: [todoItem, ...(prev[classId] || [])]
            }));

            // Reset form
            setNewTodo({ title: '', description: '', dueDate: '', priority: 'medium' });
            setIsAdding(false);

        } catch (error) {
            console.error('Error adding todo:', error);
            alert('Error adding todo. Please try again.');
        }
    };

    const toggleTodo = async (todoId: string) => {
        try {
            console.log('Toggling todo:', todoId);

            // Find the todo to toggle
            const todo = todos.find(t => t.id === todoId);
            if (!todo) {
                console.error('Todo not found:', todoId);
                return;
            }

            const newCompletedState = !todo.completed;
            console.log('New completed state:', newCompletedState);

            // Update in Supabase first
            const { error } = await supabase
                .from('todos')
                .update({ completed: newCompletedState })
                .eq('id', parseInt(todoId));

            if (error) {
                console.error('Supabase update error:', error);
                throw error;
            }

            console.log('Supabase update successful');

            // Update local state
            const updatedTodos = todos.map(todo =>
                todo.id === todoId ? { ...todo, completed: newCompletedState } : todo
            );

            setTodos(prev => ({
                ...prev,
                [classId]: updatedTodos
            }));

            console.log('Local state updated');

        } catch (error) {
            console.error('Error updating todo:', error);
            alert('Error updating todo. Please try again.');
        }
    };

    const deleteTodo = async (todoId: string) => {
        try {
            console.log('Deleting todo:', todoId);

            // Delete from Supabase
            const { error } = await supabase
                .from('todos')
                .delete()
                .eq('id', parseInt(todoId));

            if (error) {
                console.error('Supabase delete error:', error);
                throw error;
            }

            console.log('Supabase delete successful');

            // Update local state
            setTodos(prev => ({
                ...prev,
                [classId]: prev[classId].filter(todo => todo.id !== todoId)
            }));

            console.log('Local state updated');

        } catch (error) {
            console.error('Error deleting todo:', error);
            alert('Error deleting todo. Please try again.');
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return '#ff4444';
            case 'medium': return '#ffaa00';
            case 'low': return '#44aa44';
            default: return '#666';
        }
    };

    return (
        <div className="todo-column">
            <div className="column-header">
                <h2>{className}</h2>
                <div className="add-section">
                    {!isAdding ? (
                        <button
                            className="add-button"
                            onClick={() => setIsAdding(true)}
                        >
                            Add Todo
                        </button>
                    ) : (
                        <form onSubmit={handleAddTodo} className="add-form">
                            <input
                                type="text"
                                placeholder="Todo title"
                                value={newTodo.title}
                                onChange={(e) => setNewTodo(prev => ({ ...prev, title: e.target.value }))}
                                required
                                autoFocus
                            />
                            <textarea
                                placeholder="Description (optional)"
                                value={newTodo.description}
                                onChange={(e) => setNewTodo(prev => ({ ...prev, description: e.target.value }))}
                                rows={2}
                            />
                            <input
                                type="date"
                                value={newTodo.dueDate}
                                onChange={(e) => setNewTodo(prev => ({ ...prev, dueDate: e.target.value }))}
                            />
                            <select
                                value={newTodo.priority}
                                onChange={(e) => setNewTodo(prev => ({ ...prev, priority: e.target.value as any }))}
                            >
                                <option value="low">Low Priority</option>
                                <option value="medium">Medium Priority</option>
                                <option value="high">High Priority</option>
                            </select>
                            <div className="form-actions">
                                <button type="submit" className="save-button">Save</button>
                                <button
                                    type="button"
                                    className="cancel-button"
                                    onClick={() => setIsAdding(false)}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>

            <div className="todos-list">
                {todos.length === 0 ? (
                    <p className="no-todos">No todos yet</p>
                ) : (
                    todos.map((todo) => (
                        <div
                            key={todo.id}
                            className={`todo-item ${todo.completed ? 'completed' : ''}`}
                        >
                            <div className="todo-header">
                                <input
                                    type="checkbox"
                                    checked={todo.completed}
                                    onChange={() => toggleTodo(todo.id)}
                                    className="todo-checkbox"
                                />
                                <h3>{todo.title}</h3>
                                <button
                                    className="delete-button"
                                    onClick={() => deleteTodo(todo.id)}
                                >
                                    ×
                                </button>
                            </div>
                            {todo.description && <p className="todo-description">{todo.description}</p>}
                            <div className="todo-meta">
                                {todo.dueDate && (
                                    <span className="due-date">Due: {new Date(todo.dueDate).toLocaleDateString()}</span>
                                )}
                                <span
                                    className="priority"
                                    style={{ backgroundColor: getPriorityColor(todo.priority) }}
                                >
                                    {todo.priority}
                                </span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default ToDoColumn;
