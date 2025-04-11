import { useState } from 'react'
import './App.css'

function App() {
  const [jobDescription, setJobDescription] = useState('')
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://viraj0112-shl-assessment.hf.space'
  : 'http://localhost:7860';

  const handleSubmit = async (e) => {
     e.preventDefault();
    setLoading(true);
    try {
        const response = await fetch(`${API_URL}/api/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ job_description: jobDescription }),
        });
        const data = await response.json();
        setRecommendations(data);
    } catch (error) {
        console.error('Error:', error);
    } finally {
        setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>SHL Assessment Recommender</h1>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Enter job description..."
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Getting Recommendations...' : 'Get Recommendations'}
        </button>
      </form>

      {recommendations.length > 0 && (
        <div className="results">
          <h2>Recommended Assessments</h2>
          <ul>
            {recommendations.map((rec, index) => (
              <li key={index}>
                <h3>{rec.title}</h3>
                <p>{rec.description}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App