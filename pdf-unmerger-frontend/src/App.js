import logo from './logo.svg';
import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import TaskStatus from './components/TaskStatus';
import ResultsDisplay from './components/ResultsDisplay';
import './App.css';

function App() {
  const [taskId, setTaskId] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);

  const handleUploadSuccess = (id) => {
    setTaskId(id);
    setTaskStatus(null);
  };

  const handleTaskComplete = (status) => {
    setTaskStatus(status);
  };

  const resetApplication = () => {
    setTaskId(null);
    setTaskStatus(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PDF Unmerger</h1>
      </header>
      <main>
        {!taskId && (
          <UploadForm onUploadSuccess={handleUploadSuccess} />
        )}

        {taskId && !taskStatus && (
          <TaskStatus taskId={taskId} onTaskComplete={handleTaskComplete} />
        )}

        {taskStatus === "SUCCESS" && taskId && (
          <>
            <ResultsDisplay taskId={taskId} />
            <button onClick={resetApplication} style={{ marginTop: '20px' }}>
              Unmerge Another PDF
            </button>
          </>
        )}

        {taskStatus === "FAILURE" && taskId && (
          <>
            <p className="error-message">
              PDF processing failed for task <strong>{taskId}</strong>. Please try again or check backend logs.
            </p>
            <button onClick={resetApplication} style={{ marginTop: '20px' }}>
              Try Again
            </button>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
