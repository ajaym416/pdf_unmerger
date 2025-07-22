// src/components/UploadForm.js
import React, { useState } from 'react';
import axios from 'axios';

const UploadForm = ({ onUploadSuccess }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setError(null); // Clear previous errors
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError("Please select a file first.");
            return;
        }

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await axios.post('http://localhost:8000/api/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            onUploadSuccess(response.data.task_id);
            setSelectedFile(null); // Clear selected file after upload
        } catch (err) {
            console.error("Error uploading file:", err);
            setError("Failed to upload file. Please try again.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <h2>Upload PDF for Unmerging</h2>
            <input type="file" accept="application/pdf" onChange={handleFileChange} />
            <button onClick={handleUpload} disabled={!selectedFile || uploading}>
                {uploading ? 'Uploading...' : 'Upload PDF'}
            </button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};

export default UploadForm;