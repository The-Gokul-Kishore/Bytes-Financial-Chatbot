import React, { useState } from 'react';
import UploadForm from './components/UploadForm';

const App = () => {
  const [report, setReport] = useState(null);

  const handleUploadSuccess = (data) => {
    setReport(data); // { url, filename }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1>📊 Risk Analysis Report Generator</h1>

      {!report ? (
        <UploadForm onSuccess={handleUploadSuccess} />
      ) : (
        <div style={{ marginTop: '2rem' }}>
          ✅ Report Ready: 
          <a href={report.url} download="Risk_Report.pdf">
            📥 Download {report.filename}
          </a>
          <iframe
            src={report.url}
            width="100%"
            height="600px"
            style={{ border: '1px solid #ccc', marginTop: '1rem' }}
          />
        </div>
      )}
    </div>
  );
};

export default App;
