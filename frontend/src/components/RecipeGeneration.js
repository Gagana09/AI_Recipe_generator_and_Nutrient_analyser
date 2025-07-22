import React, { useState } from "react";
import "../styles/RecipeGeneration.css"; // Ensure you style this file
import Chatbot from "./chatbot.js";

const RecipeGenerator = () => {
  const [ingredients, setIngredients] = useState([""]);
  const [preferredCourse, setPreferredCourse] = useState("");
  const [preferredDiet, setPreferredDiet] = useState("");
  const [generatedRecipes, setGeneratedRecipes] = useState([]);
  const [showChatbot, setShowChatbot] = useState(false);
  const [nutritionInfo, setNutritionInfo] = useState(null); // To store the nutritional data


  const handleAddIngredient = () => {
    setIngredients([...ingredients, ""]);
  };

  const handleIngredientChange = (index, value) => {
    const updatedIngredients = [...ingredients];
    updatedIngredients[index] = value;
    setIngredients(updatedIngredients);
  };

  // Function to fetch nutrition information based on the ingredients
  const fetchNutrition = async (ingredients) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/get_nutrition", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ingredients: ingredients.filter((ing) => ing.trim() !== ""),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch nutrition information");
      }

      const data = await response.json();
      setNutritionInfo(data.nutrition || {});
    } catch (error) {
      console.error("Error fetching nutrition info:", error);
    }
  };


  const toggleChatbot = () => {
    setShowChatbot(!showChatbot);
  };


  // Function to send data to Flask backend and fetch generated recipes
  const generateRecipe = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/get_recipe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ingredients: ingredients.filter((ing) => ing.trim() !== ""),
          preferredCourse,
          preferredDiet,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch recipes");
      }

      const data = await response.json();
      setGeneratedRecipes(data.recipes || []);
      if (data.recipes && data.recipes.length > 0) {
        const allIngredients = data.recipes.flatMap((recipe) => recipe.ingredients);
        fetchNutrition(allIngredients); // Fetch nutrition for the generated ingredients
      }
    } catch (error) {
      console.error("Error fetching recipes:", error);
    }
  };

  return (
    <div className="recipe-generator-container">
      {/* Header Image */}
      <header className="header-image">
        <h1>Find Your Next Favorite Recipe</h1>
      </header>

      <div className="main-content">
        {/* Left Section for Inputs */}
        <div className="left-section">
          <h2>Customize Your Recipe</h2>

          {/* Preferred Course Dropdown */}
          <div className="dropdown-group">
            <label>Preferred Course: </label>
            <select
              value={preferredCourse}
              onChange={(e) => setPreferredCourse(e.target.value)}
            >
              <option value="">Select a course</option>
              <option value="Beverages">Beverages</option>
              <option value="Breakfast">Breakfast</option>
              <option value="Cocktail">Cocktail</option>
              <option value="Condiment">Condiment</option>
              <option value="Dessert">Dessert</option>
              <option value="Juice">Juice</option>
              <option value="Main Course">Main Course</option>
              <option value="Side Dish">Side Dish</option>
              <option value="Snack">Snack</option>
            </select>
          </div>

          {/* Preferred Diet Dropdown */}
          <div className="dropdown-group">
            <label>Diet Preference: </label>
            <select
              value={preferredDiet}
              onChange={(e) => setPreferredDiet(e.target.value)}
            >
              <option value="">Select a diet</option>
              <option value="Eggetarian">Eggetarian</option>
              <option value="Keto">Keto</option>
              <option value="Non-Vegetarian">Non-Vegetarian</option>
              <option value="Sattvik">Sattvik</option>
              <option value="Vegan">Vegan</option>
              <option value="Vegetarian">Vegetarian</option>
            </select>
          </div>

          {/* Ingredients Input */}
          <label>Ingredients:</label>
          {ingredients.map((ingredient, index) => (
            <div key={index} className="ingredient-input">
              <input
                type="text"
                value={ingredient}
                onChange={(e) =>
                  handleIngredientChange(index, e.target.value)
                }
                placeholder="Enter an ingredient"
              />
            </div>
          ))}
          <button className="add-ingredient-btn" onClick={handleAddIngredient}>
            +
          </button>

          {/* Generate Recipe Button */}
          <div className="buttons">
            <button className="generate-recipe" onClick={generateRecipe}>
              Generate Recipe
            </button>
          </div>
        </div>

        {/* Right Section for Output */}
        <div className="right-section">
          <h2>Generated Recipes</h2>
          {generatedRecipes.length > 0 ? (
            generatedRecipes.map((recipe, index) => (
              <div key={index} className="recipe-output">
                {recipe.source === "GPT2" ? (
                  <>
                  <h3>Recipe Name: {recipe.recipe_name}</h3>
                  <p><strong>Servings:</strong> {recipe.servings}</p>
                  <p><strong>Total Time in Minutes:</strong> {recipe.total_time}</p>
                  <p><strong>Recipe Ingredients:</strong> {recipe.ingredients.join(", ")}</p>
                  <p><strong>Recipe Instructions:</strong></p>
                  <ol>
                  {recipe.instructions.split(/\d+\.\s*/).map((step, stepIndex) => 
                  step.trim() ? <li key={stepIndex}>{step.trim()}</li> : null
                  )}
                  </ol>
                    
                  </>
                ) : (
                  <>
                    <h3>{recipe.recipe_name}</h3>
                    <p>
                      <strong>Cuisine:</strong> {recipe.cuisine}
                    </p>
                    <p>
                      <strong>Course:</strong> {recipe.course}
                    </p>
                    <p>
                      <strong>Prep Time:</strong> {recipe.prep_time} minutes
                    </p>
                    <p>
                      <strong>Cook Time:</strong> {recipe.cook_time} minutes
                    </p>
                    <p>
                      <strong>Ingredients:</strong>{" "}
                      {Array.isArray(recipe.ingredients)
                        ? recipe.ingredients.join(", ")
                        : recipe.ingredients}
                    </p>
                    <p>
                      <strong>Instructions:</strong> {recipe.instructions}
                    </p>
                  </>
                )}
              </div>
            ))
          ) : (
            <p>Your recipe will appear here.</p>
          )}
          <div className="nutrition-info">
            {nutritionInfo ? (
              <div>
                <h3>Nutrition Information</h3>
                    <p><strong>Calories:</strong> {nutritionInfo.Calories} kcal</p>
                    <p><strong>Protein:</strong> {nutritionInfo.Protein} g</p>
                    <p><strong>Carbs:</strong> {nutritionInfo.Carbs} g</p>
                    <p><strong>Fat:</strong> {nutritionInfo.Fat} g</p>
                    <p><strong>Fiber:</strong> {nutritionInfo.Fiber} g</p>
                    <p><strong>Sugars:</strong> {nutritionInfo.Sugars} g</p>
                    <p><strong>Sodium:</strong> {nutritionInfo.Sodium} mg</p>
                    <p><strong>Calcium:</strong> {nutritionInfo.Calcium} mg</p>
                    <p><strong>Iron:</strong> {nutritionInfo.Iron} mg</p>
                    <p><strong>Vitamin A:</strong> {nutritionInfo["Vitamin A"]} IU</p>
                    <p><strong>Vitamin C:</strong> {nutritionInfo["Vitamin C"]} mg</p>
                    <p><strong>Potassium:</strong> {nutritionInfo.Potassium} mg</p>
                    <p><strong>Magnesium:</strong> {nutritionInfo.Magnesium} mg</p>
                    <p><strong>Cholesterol:</strong> {nutritionInfo.Cholesterol} mg</p>
                    <p><strong>Saturated Fat:</strong> {nutritionInfo["Saturated Fat"]} g</p>
                {/* Add other nutritional values as needed */}
              </div>
            ) : (
              <p><strong>Analyzing Nutritional Info....</strong></p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecipeGenerator;