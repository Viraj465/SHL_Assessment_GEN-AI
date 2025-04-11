import { useState, useEffect } from "react";
import "./App.css";

const HomePage = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [recommendation, setRecommendation] = useState([]);
  const [loading, setLoading] = useState(false);

  const API_URL =
    process.env.NODE_ENV === "production"
      ? "https://huggingface.co/spaces/Viraj0112/SHL_Assessment"
      : "http://localhost:7860";

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent the default form submission
    setLoading(true); // Set loading state to true

    try {
      const response = await fetch(`${API_URL}/api/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: jobDescription,
        }),
      });
      const data = await response.json();
      setRecommendation(data.recommendation); // Set the recommendation state with the response data
    } catch (error) {
      console.error("Error fetching recommendation:", error);
      setLoading(false);
    } finally {
      setLoading(false); // Set loading state to false
    }
  };

  return (
    <div className="container">
      <h1>SHL Assessment Recommender</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Enter job description here..."
          rows="10"
          cols="50"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Loading..." : "Get Recommendation"}
        </button>
      </form>
      {recommendation.length > 0 && (
        <div className="recommendation">
          <h2>Recommended Questions:</h2>
          <ul>
            {recommendation.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      )}
      {recommendation.length === 0 && !loading && (
        <div className="no-recommendation">
          <p>No recommendations available.</p>
        </div>
      )}
      <footer>
        <p>Developed by Viraj</p>
        <p>Powered by Hugging Face</p>
        <p>Version 1.0</p>
        <p>© 2023 Viraj. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default HomePage;
