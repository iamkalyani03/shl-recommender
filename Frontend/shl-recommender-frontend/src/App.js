import React, { useState } from "react";
import {
  FaRobot,
  FaSearch,
  FaExternalLinkAlt,
  FaSpinner
} from "react-icons/fa";

import "./App.css";

function App() {

  const [query, setQuery] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);


  const fetchRecommendations = async () => {

    if (!query.trim()) {
      alert("Please enter a query.");
      return;
    }

    setLoading(true);

    try {

      const res = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query,
          top_k: 10
        })
      });

      const data = await res.json();

      setRecommendations(data.recommendations || []);

    } catch (e) {

      alert("API connection failed.");

    }

    setLoading(false);
  };


  const handleKeyPress = (e) => {

    if (e.key === "Enter") {
      fetchRecommendations();
    }

  };


  return (

    <div className="app-container">

      <h1 className="app-title">
        <FaRobot style={{ marginRight: 10 }} />
        SHL AI Assessment Recommender
      </h1>

      <div className="input-group">

        <input
          type="text"
          placeholder="Example: Python developer with leadership skills"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyPress}
        />

        <button onClick={fetchRecommendations}>

          {loading ? (
            <>
              <FaSpinner className="spin" />
              Searching
            </>
          ) : (
            <>
              <FaSearch />
              Recommend
            </>
          )}

        </button>

      </div>


      {recommendations.length > 0 && (

        <div className="results-grid">

          {recommendations.map((rec, idx) => (

            <div className="result-card" key={idx}>

              <div className="result-info">

                <h3>
                  {idx + 1}. {rec.assessment_name}
                </h3>

                <div className="score">
                  Match Score: {rec.score.toFixed(4)}
                </div>

              </div>

              <a
                className="result-link"
                href={rec.assessment_url}
                target="_blank"
                rel="noreferrer"
              >
                View <FaExternalLinkAlt />
              </a>

            </div>

          ))}

        </div>

      )}


      {recommendations.length === 0 && !loading && (

        <div className="empty">
          🤖 Ask the AI what assessment you need.
        </div>

      )}

    </div>

  );

}

export default App;