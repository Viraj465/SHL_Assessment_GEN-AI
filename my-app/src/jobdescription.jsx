import React, { useState } from "react";
import "./App.css";

const JobDescription = () => {
  const [JobDescription, setJobDescription] = useState("");
  const [recommendation, setRecommendation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL =
    process.env.NODE_ENV === "production"
      ? window.location.origin
      : "http://localhost:7860";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    console.log("Submitting to:", `${API_URL}/api/recommendations/`);

    try {
      const response = await fetch(`${API_URL}/api/recommendations/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: JobDescription,
          history: [],
        }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(
          `HTTP error! status: ${response.status}, message: ${errorData}`
        );
      }

      const data = await response.json();
      console.log("Response data:", data);

      if (!data.recommendations) {
        throw new Error("No recommendations in response");
      }
    //   setRecommendation(data.recommendations || []);
    setRecommendation(data.recommendations);
    } catch (error) {
      console.error("Error fetching recommendation:", error);
      setError(
        `Failed to get recommendations. Please try again., ${error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>SHL Assessment Recommender</h1>
      <div className="form-container">
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <textarea
              value={JobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Enter job description here..."
              rows="10"
              required
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? "Getting Recommendations..." : "Get Recommendations"}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {recommendation.length > 0 && (
          <div className="results">
            <h2>Recommended Assessments:</h2>
            <div className="recommendations-grid">
              {recommendation.map((item, index) => (
                <div key={index} className="recommendation-card">
                  <h3>{item.Assessment_Name}</h3>
                  <div className="card-content">
                    <p>
                      <strong>Test Type:</strong> {item.Test_Type}
                    </p>
                    <p>
                      <strong>Duration:</strong> {item.Duration}
                    </p>
                    <p>
                      <strong>Remote Support:</strong> {item.Remote_Support}
                    </p>
                    <p>
                      <strong>Adaptive Support:</strong> {item.Adaptive_Support}
                    </p>
                    {item.URL && (
                      <a
                        href={item.URL}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Learn More
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {recommendation.length === 0 && !loading && !error && (
          <div className="no-results">
            <p>
              No recommendations available. Please submit a job description.
            </p>
          </div>
        )}
      </div>

      <footer>
        <p>Developed by Viraj</p>
        <p>© 2024 All rights reserved.</p>
      </footer>
    </div>
  );
};

export default JobDescription;
