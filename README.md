# 🧠 AI-Based Recipe Generator and Nutrient Analyzer

An intelligent meal recommendation system that generates personalized recipes based on available ingredients, dietary preferences, and time constraints. It also provides a detailed macronutrient and micronutrient breakdown using the Edamam API, ensuring that users can make healthy and informed food choices.

**✨ Features**

* 🔍 **Recipe Search** using FAISS for fast similarity-based retrieval.
* 🤖 **Recipe Generation** using fine-tuned DistilGPT-2 when matches are unavailable.
* 🍽️ **Personalization** by diet (vegetarian, vegan, non-veg), course (main, dessert), time, and serving size.
* 📊 **Nutrient Analysis** via Edamam API for every recipe.
* 🧠 Preprocessed dataset from Archana's Kitchen (~6,850 recipes).
* 🌐 React-based frontend for seamless user experience.

---

**🚀 Getting Started**

**📦 Prerequisites**

* Python 3.9+
* Node.js & npm or Yarn
* Edamam API credentials
* OpenAI/FAISS model files (fine-tuned DistilGPT-2 + FAISS index)

---

**1️⃣ Backend Setup (Flask)**

```bash
cd backend
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
---
**2️⃣ Frontend Setup (React)**
```bash
cd frontend
npm install         # or yarn install
npm start           # or yarn start
```
Frontend runs on http://localhost:3000
Backend (API) runs on http://localhost:5000

**🧪 Example Use Case** 

Enter ingredients you have (e.g., "tomato, rice, garlic")
Select dietary preference (e.g., vegan), course (e.g., main dish), and total cooking time
The system:

Retrieves best match using FAISS
Or generates a new recipe using DistilGPT-2
Returns a detailed recipe + nutritional breakdown


