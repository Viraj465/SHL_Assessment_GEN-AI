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

    console.log("Submitting to:", `${API_URL}/api/recommendations`);

    try {
      const response = await fetch(`${API_URL}/api/recommendations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: JobDescription,
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
      console.log("Recommendations:", data.recommendations);

      if (!data.recommendations) {
        throw new Error("No recommendations in response");
      }
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
            <table className="recommendation-table">
              <thead>
                <tr>
                  <th>Assessment Name</th>
                  <th>Test Type</th>
                  <th>Duration</th>
                  <th>Remote Support</th>
                  <th>Adaptive Support</th>
                  <th>Learn More</th>
                </tr>
              </thead>
              <tbody>
                {recommendation.map((item, index) => (
                  <tr key={index}>
                    <td>{item.assessment_name}</td>
                    <td>{item.test_type}</td>
                    <td>{item.duration}</td>
                    <td>{item.remote_support}</td>
                    <td>{item.adaptive_support}</td>
                    <td>
                      {item.url ? (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Link
                        </a>
                      ) : (
                        "N/A"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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
        <p>Developed by Viraj. SHL Assessment Test.</p>
        <p>© 2025 All rights reserved.</p>
      </footer>
    </div>
  );
};

export default JobDescription;
