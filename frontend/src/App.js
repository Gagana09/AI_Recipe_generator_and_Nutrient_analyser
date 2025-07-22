import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import HomePage from "./components/Homepage"; // Import HomePage
import RecipeGenerator from "./components/RecipeGeneration"; // Import RecipeGenerator

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Define route for HomePage */}
        <Route path="/" element={<HomePage />} />
        
        {/* Define route for RecipeGenerator */}
        <Route path="/recipe-generator" element={<RecipeGenerator />} />
      </Routes>
    </Router>
  );
};

export default App;
