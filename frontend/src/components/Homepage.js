import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Homepage.css";

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="homepage-container">
      <div className="content">
        <h1 className="AI RECIPE GENERATOR AND NUTRITIONAL ANALYSER">AI Recipe Generator</h1>
        <p className="subtitle">Discover delicious recipes and nutritional insights tailored for you!</p>
        <button className="cta-button" onClick={() => navigate("/recipe-generator")}>
          Let's Get Cooking
        </button>
      </div>
    </div>
  );
};

export default HomePage;
