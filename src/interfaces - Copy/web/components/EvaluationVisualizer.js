import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

function EvaluationVisualizer({ modelId, evaluationData }) {
  const [metrics, setMetrics] = useState({
    text: {},
    image: {},
    training: {}
  });

  useEffect(() => {
    if (evaluationData) {
      setMetrics(evaluationData);
    }
  }, [evaluationData]);

  const renderMetricsSection = (title, data, color) => (
    <div className="metrics-section glassmorphic">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data.history || []}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color} 
            dot={false}
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="metrics-summary">
        {Object.entries(data.current || {}).map(([key, value]) => (
          <div key={key} className="metric-item">
            <span className="metric-label">{key}:</span>
            <span className="metric-value">{value.toFixed(4)}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="evaluation-visualizer">
      <h2>Advanced Evaluation Visualization</h2>
      
      <div className="metrics-grid">
        {/* Text Metrics */}
        {metrics.text && renderMetricsSection(
          'Text Generation Metrics',
          metrics.text,
          '#1f77b4'
        )}

        {/* Image Metrics */}
        {metrics.image && renderMetricsSection(
          'Image Generation Metrics',
          metrics.image,
          '#2ca02c'
        )}

        {/* Training Metrics */}
        {metrics.training && renderMetricsSection(
          'Training Progress',
          metrics.training,
          '#ff7f0e'
        )}
      </div>

      <style jsx>{`
        .evaluation-visualizer {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .metrics-section {
          padding: 20px;
          border-radius: 10px;
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .metrics-summary {
          margin-top: 15px;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 10px;
        }

        .metric-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 5px;
        }

        .metric-label {
          color: #888;
          font-size: 0.9em;
        }

        .metric-value {
          font-weight: 500;
          color: #fff;
        }
      `}</style>
    </div>
  );
}

export default EvaluationVisualizer;
