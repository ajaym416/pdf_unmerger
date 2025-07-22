// src/components/TaskStatus.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TaskStatus = ({ taskId, onTaskComplete }) => {
    const [status, setStatus] = useState("PENDING");
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!taskId) return;

        const pollStatus = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/status/${taskId}`);
                const newStatus = response.data.status;
                setStatus(newStatus);

                if (newStatus === "SUCCESS" || newStatus === "FAILURE") {
                    clearInterval(interval); // Stop polling
                    onTaskComplete(newStatus); // Notify parent component
                }
            } catch (err) {
                console.error("Error fetching task status:", err);
                setError("Failed to fetch task status.");
                clearInterval(interval); // Stop polling on error
            }
        };

        const interval = setInterval(pollStatus, 3000); // Poll every 3 seconds

        // Clear interval on component unmount
        return () => clearInterval(interval);
    }, [taskId, onTaskComplete]);

    return (
        <div>
            <h3>Processing Status for Task ID: {taskId}</h3>
            <p>Status: <strong>{status}</strong></p>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {status === "FAILURE" && <p style={{ color: 'red' }}>Task failed. Please check backend logs.</p>}
        </div>
    );
};

export default TaskStatus;