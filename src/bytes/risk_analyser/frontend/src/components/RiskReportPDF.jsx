import React from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

const RiskReportPDF = ({ extractedData, onBack }) => {
  const { kpis, quantitative, qualitative } = extractedData;

  const chartData = {
    labels: Object.keys(quantitative),
    datasets: [
      {
        label: 'Quantitative Risk Scores',
        data: Object.values(quantitative),
        backgroundColor: '#4a90e2',
        borderColor: '#1c3f63',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div style={{ marginTop: '2rem', padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <button
        onClick={onBack}
        style={{
          marginBottom: '1rem',
          padding: '0.5rem 1rem',
          backgroundColor: '#003366',
          color: '#fff',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
        }}
      >
        🔙 Back
      </button>

      <h1 style={{ color: '#003366' }}>📄 Risk Analysis Report</h1>

      <section style={{ marginTop: '2rem' }}>
        <h2 style={{ color: '#2c3e50' }}>📌 Key Performance Indicators (KPIs)</h2>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            marginTop: '1rem',
            marginBottom: '2rem',
            backgroundColor: '#fdfdfd',
          }}
        >
          <thead>
            <tr style={{ backgroundColor: '#003366', color: '#fff' }}>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>KPI</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Value</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(kpis).map(([key, value], index) => (
              <tr
                key={key}
                style={{
                  backgroundColor: index % 2 === 0 ? '#f5f9ff' : '#ffffff',
                }}
              >
                <td style={{ padding: '0.75rem', borderBottom: '1px solid #ddd' }}>{key}</td>
                <td style={{ padding: '0.75rem', borderBottom: '1px solid #ddd' }}>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2 style={{ color: '#2c3e50' }}>📊 Quantitative Risk Scores</h2>
        <div style={{ width: '80%', margin: '2rem auto' }}>
          <Bar data={chartData} />
        </div>
      </section>

      <section>
        <h2 style={{ color: '#2c3e50' }}>🧠 Qualitative Risk Insights</h2>
        <div
          style={{
            border: '1px solid #ccc',
            padding: '1.5rem',
            backgroundColor: '#f7f9fb',
            borderRadius: '8px',
            marginTop: '1rem',
            whiteSpace: 'pre-wrap',
            fontSize: '1rem',
            color: '#333',
            lineHeight: '1.6',
          }}
        >
          {qualitative
            .split('\n')
            .filter((line) => line.trim())
            .map((line, idx) => (
              <p key={idx} style={{ marginBottom: '0.75rem' }}>
                • {line.trim()}
              </p>
            ))}
        </div>
      </section>
    </div>
  );
};

export default RiskReportPDF;
