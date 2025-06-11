import React, { useState } from 'react';
import axios from 'axios';

const UploadForm = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        responseType: 'blob',
      });

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      // ✅ Send blob URL + filename to App.jsx
      onSuccess({
        url,
        filename: file.name,
      });
    } catch (err) {
      console.error(err);
      alert('❌ Error analyzing file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
      <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileChange} />
      <button type="submit" disabled={loading} style={{ marginLeft: '1rem' }}>
        {loading ? 'Analyzing...' : 'Generate Risk Report'}
      </button>
    </form>
  );
};

export default UploadForm;
