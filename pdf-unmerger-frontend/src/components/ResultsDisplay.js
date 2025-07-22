// src/components/ResultsDisplay.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ResultsDisplay = ({ taskId }) => {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!taskId) {
            setLoading(false);
            return;
        }

        const fetchResults = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/results/${taskId}`);
                if (response.data.status === "success") {
                    setFiles(response.data.files);
                } else {
                    setError(response.data.message || "No files found or an error occurred.");
                }
            } catch (err) {
                console.error("Error fetching results:", err);
                setError("Failed to fetch results. Please check task status.");
            } finally {
                setLoading(false);
            }
        };

        fetchResults();
    }, [taskId]);

    if (loading) return <p>Loading results...</p>;
    if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;
    if (files.length === 0) return <p>No unmerged files found for this task ID.</p>;

    return (
        <div>
            <h3>Unmerged PDF Files:</h3>
            <ul>
                {files.map((filePath, index) => {
                    // The filename here is the full S3 key, e.g., "task_id/page_1.pdf"
                    // The download endpoint expects the full S3 key as `filename:path`
                    const downloadUrl = `http://localhost:8000/api/download/${encodeURIComponent(filePath)}`;
                    const displayFilename = filePath.split('/').pop(); // Extract just the file name for display

                    return (
                        <li key={index}>
                            <a href={downloadUrl} target="_blank" rel="noopener noreferrer">
                                {displayFilename}
                            </a>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};

export default ResultsDisplay;