# 🧠 AI-Based Recipe Generator and Nutrient Analyzer

An intelligent meal recommendation system that generates personalized recipes based on available ingredients, dietary preferences, and time constraints. It also provides a detailed macronutrient and micronutrient breakdown using the Edamam API, ensuring that users can make healthy and informed food choices.

<p align="center" style="margin-bottom: 0;">
  <img src="README_images/Homepage.png" width="700"/>
</p>

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

---

**2️⃣ Edemam API KEY setup**
This project uses the Edamam API for recipe and nutrition data. To use this service, you must get your own API credentials.

📌 How to Get Your API Credentials
Go to the Edamam Developer Portal.

Sign up and subscribe to the Recipe Search API and/or Nutrition Analysis API.

You'll receive an APP ID and API KEY.

🔧 Add Your Credentials
In app.py, locate this section:
```python
APP_ID = "your_app_id_here"
API_KEY = "your_api_key_here"
```
Replace the placeholders ("your_app_id_here" and "your_api_key_here") with your actual Edamam APP ID and API KEY.

---
**🧪 Example Use Case** 

Enter ingredients you have (e.g., "tomato, rice, garlic")
Select dietary preference (e.g., vegan), course (e.g., main dish), and total cooking time
The system:

Retrieves best match using FAISS
Or generates a new recipe using DistilGPT-2
Returns a detailed recipe + nutritional breakdown
 
 <p align="center" style="margin-bottom: 0;">
  <img src="README_images/img2.png" width="700"/>
</p>
<p align="center" style="margin-bottom: 0;">
  <img src="README_images/img3.png" width="700"/>
</p>

