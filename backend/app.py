from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import re
import torch
import requests

# Define the device: use GPU if available, otherwise CPU.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



# Import transformers for GPT-2 generation fallback
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = Flask(__name__)
CORS(app)

# ----------------------------
# Allowed Options for Dropdowns
# ----------------------------
ALLOWED_COURSES = [
    "beverages", "breakfast", "cocktail", "condiment", "dessert",
    "juice", "main course", "side dish", "snack"
]
ALLOWED_DIETS = [
    "eggetarian", "keto", "non-vegetarian", "sattvik", "vegan", "vegetarian"
]

# ----------------------------
# Load FAISS index, recipe metadata, and SentenceTransformer model
# ----------------------------
faiss_index_path = r"models/Fiass_Index/recipes_faiss.index"
recipes_metadata_path = r"models/Fiass_Index/recipes_metadata.joblib"
embedding_model_path = r"models/recipe_embedding_model"

try:
    faiss_index = faiss.read_index(faiss_index_path)
    recipes = joblib.load(recipes_metadata_path)
    embedding_model = SentenceTransformer(embedding_model_path)
except Exception as e:
    print(f"Error loading FAISS index or models: {e}")
    exit(1)

# ----------------------------
# Load GPT-2 model and tokenizer for fallback generation
# ----------------------------
gpt2_model_path = r"models/fine_tuned_gpt2_2"  # Update this path as needed
# Move the GPT-2 model to the selected device.

try:
    gpt2_tokenizer = GPT2Tokenizer.from_pretrained(gpt2_model_path)
    gpt2_model = GPT2LMHeadModel.from_pretrained(gpt2_model_path).to(device)
    # Set the padding token to the EOS token
    gpt2_tokenizer.pad_token = gpt2_tokenizer.eos_token
except Exception as e:
    print(f"Error loading GPT-2 model: {e}")
    gpt2_model = None

# ----------------------------
# Synonym Dictionary and Helper Functions
# ----------------------------
synonym_dict = {
    # (Include your full synonym dictionary here)
    'tomato': ['tomato', 'tomatoes'],
    'chili': ['chili', 'chillies', 'chili powder', 'chilly powder', 'chili flakes', 'chili flakes powder', 'cayenne'],
    'onion': ['onion', 'onions', 'shallots'],
    # ... (rest of your synonyms)
}

def normalize_ingredients(ingredients):
    """
    Normalize ingredients by converting to lowercase, stripping extra spaces,
    and mapping them to a canonical form using the synonym dictionary.
    """
    normalized = set()
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower().strip()
        for key, synonyms in synonym_dict.items():
            if ingredient_lower in synonyms:
                normalized.add(key)
                break
        else:
            normalized.add(ingredient_lower)
    return list(normalized)

def extract_diet_from_query(query):
    """
    Extract diet preferences from the query string.
    """
    return [diet for diet in ALLOWED_DIETS if diet in query.lower()]

# Define synonyms for allowed diets
DIET_SYNONYMS = {
    "non-vegetarian": ["non-vegetarian", "nonvegetarian", "non veg", "non-veg", "non vegetarian"],
    "vegetarian": ["vegetarian"],
    "keto": ["keto", "ketogenic"],
    "eggetarian": ["eggetarian"],
    "sattvik": ["sattvik", "sattvic"],
    "vegan": ["vegan"],
}

def filter_recipes_by_diet(recipes_list, diet_preferences):
    if not diet_preferences:
        return recipes_list
    filtered = []
    for recipe in recipes_list:
        recipe_diet = str(recipe.get('diet', '')).lower()
        for pref in diet_preferences:
            pref = pref.lower()
            synonyms = DIET_SYNONYMS.get(pref, [pref])
            if any(syn in recipe_diet for syn in synonyms):
                filtered.append(recipe)
                break
    return filtered

def filter_recipes_by_course(recipes_list, preferred_course):
    if not preferred_course:
        return recipes_list
    preferred_course = preferred_course.lower()
    if preferred_course not in ALLOWED_COURSES:
        return recipes_list
    filtered = []
    for recipe in recipes_list:
        recipe_course = recipe.get('course', '').lower()
        if preferred_course in recipe_course:
            filtered.append(recipe)
    return filtered

def filter_recipes_by_time(recipes_list, max_time):
    if max_time is None:
        return recipes_list
    filtered = []
    for recipe in recipes_list:
        total_time = recipe.get('prep_time', 0) + recipe.get('cook_time', 0)
        if total_time <= max_time:
            filtered.append(recipe)
    return filtered

def filter_recipes_by_nutrition(recipes_list, nutrition_preferences):
    standard_values = {
        'high-protein': 20,
        'low-protein': 10,
        'high-carb': 60,
        'low-carb': 30,
        'high-fat': 40,
        'low-fat': 10,
    }
    filtered = []
    for recipe in recipes_list:
        nutrition = recipe.get('nutrition', {})
        if not nutrition:
            continue
        meets_all = True
        for pref in nutrition_preferences:
            if pref in standard_values:
                threshold = standard_values[pref]
                if pref == 'high-protein' and nutrition.get('protein', 0) < threshold:
                    meets_all = False
                    break
                if pref == 'low-protein' and nutrition.get('protein', 0) > threshold:
                    meets_all = False
                    break
                if pref == 'high-carb' and nutrition.get('carbs', 0) < threshold:
                    meets_all = False
                    break
                if pref == 'low-carb' and nutrition.get('carbs', 0) > threshold:
                    meets_all = False
                    break
                if pref == 'high-fat' and nutrition.get('fat', 0) < threshold:
                    meets_all = False
                    break
                if pref == 'low-fat' and nutrition.get('fat', 0) > threshold:
                    meets_all = False
                    break
        if meets_all:
            filtered.append(recipe)
    return filtered

def search_similar_recipes(query, k=5):
    """
    Encode the query using SentenceTransformer, perform a FAISS search,
    and return recipes with a normalized similarity score >= 0.5.
    """
    diet_preferences = extract_diet_from_query(query)
    normalized_query = normalize_ingredients(query.split())
    query_str = " ".join(normalized_query)
    query_embedding = embedding_model.encode([query_str])
    distances, indices = faiss_index.search(np.array(query_embedding).astype(np.float32), k)
    similarity_scores = 1 / (1 + distances)
    matched_recipes = []
    for score, idx in zip(similarity_scores[0], indices[0]):
        if score >= 0.5:
            recipe = recipes[idx]
            recipe["similarity_score"] = float(score)
            recipe["source"] = "FAISS"
            matched_recipes.append(recipe)
    return filter_recipes_by_diet(matched_recipes, diet_preferences)

def recipe_to_dict(recipe):
    data = {
        "recipe_name": recipe.get("recipe_name", ""),
        "cuisine": recipe.get("cuisine", ""),
        "course": recipe.get("course", ""),
        "prep_time": recipe.get("prep_time", 0),
        "cook_time": recipe.get("cook_time", 0),
        "servings": recipe.get("servings", ""),
        "ingredients": recipe.get("ingredients", []),
        "diet": recipe.get("diet", "N/A"),
        "nutrition": recipe.get("nutrition", {}),
        "instructions": recipe.get("instructions", "")
    }
    if "similarity_score" in recipe:
        data["similarity_score"] = recipe["similarity_score"]
    return data

# ----------------------------
# GPT-2 Recipe Generation Function (Fallback)
# ----------------------------
def generate_recipe(prompt, max_length=1024, num_return_sequences=1):
   
    if not gpt2_model:
        print("GPT-2 model not available.")
        return ["Error: GPT-2 model not loaded."]
    try:
        inputs = gpt2_tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(device)
        outputs = gpt2_model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            pad_token_id=gpt2_tokenizer.pad_token_id,
            eos_token_id=gpt2_tokenizer.eos_token_id,
            do_sample=True,
            top_k=50,
            top_p=0.9,
            temperature=0.8,
        )
        return [gpt2_tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
    except Exception as e:
        print(f"Error generating recipe: {e}")
        return ["Error generating recipe"]

# ----------------------------
# Flask API Endpoint
# ----------------------------
@app.route('/get_recipe', methods=['POST'])
def get_recipe_endpoint():
    try:
        data = request.get_json()
        if not data or "ingredients" not in data:
            return jsonify({"error": "Invalid input. Please provide ingredients."}), 400

        # Retrieve input parameters
        ingredients = data.get("ingredients", [])
        preferred_course = data.get("preferredCourse", "")
        preferred_diet = data.get("preferredDiet", "")
        # max_time = data.get("max_time", None)

        if not ingredients:
            return jsonify({"error": "Please provide at least one ingredient."}), 400

        # Build a query string from the inputs
        query = f"{', '.join(ingredients)} {preferred_course} {preferred_diet}".strip()

        # Search for similar recipes using FAISS
        matching_recipes = search_similar_recipes(query)
        matching_recipes = filter_recipes_by_course(matching_recipes, preferred_course)
        # If needed, you can uncomment the next line to filter by time
        # matching_recipes = filter_recipes_by_time(matching_recipes, max_time)
        if preferred_diet:
            matching_recipes = filter_recipes_by_diet(matching_recipes, [preferred_diet.lower()])
        recipes_list = [recipe_to_dict(recipe) for recipe in matching_recipes]
        recipes_list = recipes_list[:1]

        # If no recipes were found via FAISS, use GPT-2 to generate one.
        if not recipes_list:
            print("No matching recipes found in FAISS. Falling back to GPT-2 generation.")
            # Create a prompt for GPT-2. (You can modify the prompt format as needed.)
            input_prompt = (
                f"Diet: {preferred_diet or ''}\n"
                f"Course: {preferred_course or ''}\n"
                f"Ingredients: {', '.join(ingredients)}\n"
            )
            generated_recipes = generate_recipe(input_prompt)

            if not generated_recipes:
                return jsonify({"error": "Failed to generate a recipe."}), 500

            generated_recipe = generated_recipes[0] if generated_recipes else ""
            print(generated_recipe)
            generated_recipe_dict = {
                "recipe_name": re.search(r"RecipeName:\s*(.+)", generated_recipe).group(1),
                "servings": re.search(r"Servings:\s*(\d+)", generated_recipe).group(1),
                "total_time": re.search(r"TotalTimeInMinutes:\s*(\d+)", generated_recipe).group(1),
                "ingredients": re.search(r"RecipeIngredients:\s*(.+)", generated_recipe).group(1).split(", "),
                "instructions": re.search(r"RecipeInstructions:\s*(.+)", generated_recipe).group(1),
                "source": "GPT2"  # Mark the recipe as generated by GPT-2
            }
            return jsonify({"recipes": [generated_recipe_dict]}), 200

        return jsonify({"recipes": recipes_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Replace these with your actual API credentials
APP_ID = '96021791'
API_KEY = '732c5eb97098873bbb6de814aaabd3bd'
    
def preprocess_ingredients(ingredient_list):
    """
    Simplifies and structures the ingredient list to retain valid quantities and units.
    """
    ingredient_items = ingredient_list.split(',')

    # Variables to track total weight of known ingredients and placeholders for missing quantities
    total_weight = 0
    ingredients_with_no_quantity = []

    # Clean and standardize each ingredient
    processed_items = []
    for item in ingredient_items:
        item = re.sub(r'\(.*?\)', '', item)
        item = re.sub(r'\b(chopped|slit|finely|picked|optional|to taste|thinly sliced|deseeded|etc.)\b', '', item, flags=re.IGNORECASE)
        item = re.sub(r'\s+', ' ', item).strip()  # Remove excess whitespace

        # If the item contains a number, parse it
        match = re.match(r'(\d+\.?\d*)\s*(\w+)', item)
        if match:
            quantity = float(match.group(1))
            unit = match.group(2)
            total_weight += quantity  # Accumulate the total weight
        else:
            # Mark ingredients that don't have explicit quantities (like "to taste")
            ingredients_with_no_quantity.append(item)

        processed_items.append(item)

    # Dynamically calculate salt or other missing quantities based on total weight
    for ingredient in ingredients_with_no_quantity:
        if 'salt' in ingredient.lower():
            # Example: Use 0.5% of the total weight for salt
            estimated_salt = total_weight * 0.05  # Salt as 0.5% of the total weight
            processed_items.append(f"{estimated_salt} grams salt")

    return processed_items, total_weight

def analyze_single_ingredient(ingredient):
    """
    Analyzes a single ingredient using the Edamam API.
    """
    url = "https://api.edamam.com/api/nutrition-data"
    params = {
        'app_id': APP_ID,
        'app_key': API_KEY,
        'ingr': ingredient
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            nutrition = response.json().get('totalNutrients', {})
            return {
                'Calories': nutrition.get('ENERC_KCAL', {}).get('quantity', 0),
                'Protein': nutrition.get('PROCNT', {}).get('quantity', 0),
                'Carbs': nutrition.get('CHOCDF', {}).get('quantity', 0),
                'Fat': nutrition.get('FAT', {}).get('quantity', 0),
                'Fiber': nutrition.get('FIBTG', {}).get('quantity', 0),
                'Sugars': nutrition.get('SUGAR', {}).get('quantity', 0),
                'Sodium': nutrition.get('NA', {}).get('quantity', 0),
                'Calcium': nutrition.get('CA', {}).get('quantity', 0),
                'Iron': nutrition.get('FE', {}).get('quantity', 0),
                'Vitamin A': nutrition.get('VITA_RAE', {}).get('quantity', 0),
                'Vitamin C': nutrition.get('VITC', {}).get('quantity', 0),
                'Potassium': nutrition.get('K', {}).get('quantity', 0),
                'Magnesium': nutrition.get('MG', {}).get('quantity', 0),
                'Cholesterol': nutrition.get('CHOLE', {}).get('quantity', 0),
                'Saturated Fat': nutrition.get('FASAT', {}).get('quantity', 0),
            }
    except Exception as e:
        print(f"[ERROR] Exception occurred for ingredient: {ingredient} - {e}")
    return {key: 0 for key in [
        'Calories', 'Protein', 'Carbs', 'Fat', 'Fiber', 'Sugars', 'Sodium',
        'Calcium', 'Iron', 'Vitamin A', 'Vitamin C', 'Potassium', 'Magnesium',
        'Cholesterol', 'Saturated Fat'
    ]}

def analyze_ingredients(ingredients):
    """
    Analyzes all ingredients individually and aggregates the results.
    """
    aggregated_nutrition = {key: 0 for key in [
        'Calories', 'Protein', 'Carbs', 'Fat', 'Fiber', 'Sugars', 'Sodium',
        'Calcium', 'Iron', 'Vitamin A', 'Vitamin C', 'Potassium', 'Magnesium',
        'Cholesterol', 'Saturated Fat'
    ]}
    for ingredient in ingredients:
        print(f"[INFO] Analyzing: {ingredient}")
        nutrition = analyze_single_ingredient(ingredient)
        for key, value in nutrition.items():
            aggregated_nutrition[key] += value
    return aggregated_nutrition


@app.route('/get_nutrition', methods=['POST'])
def get_nutrition():
    try:
        data = request.get_json()
        if not data or "ingredients" not in data:
            return jsonify({"error": "Invalid input. Please provide ingredients."}), 400

        ingredients = data["ingredients"]
        if not ingredients:
            return jsonify({"error": "Ingredient list is empty."}), 400

        # Preprocess the ingredients
        processed_ingredients, _ = preprocess_ingredients(", ".join(ingredients))

        # Analyze nutrition
        nutrition_info = analyze_ingredients(processed_ingredients)
        print(nutrition_info)

        return jsonify({"nutrition": nutrition_info}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ----------------------------
# Main
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)