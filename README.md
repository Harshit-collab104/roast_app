# 🔥 GameRoast AI

**GameRoast AI** is a witty, ruthless, and AI-powered web application that analyzes your gaming stats and roasts you based on your performance. 

Built with **FastAPI** and **Google Gemini 1.5 Flash**, it currently supports **Clash Royale** and **Valorant**.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)

## 🎮 Features

### 👑 Clash Royale
- **Deep Stat Analysis:** Checks Win %, Total Games, and Years Played.
- **Deck Synergy Check:** Roasts you for using "toxic" cards (e.g., Mega Knight, E-Giant).
- **Battle Log Review:** Analyzes your last 5 games to see if you choked a lead.
- **Path of Legends:** Compares your league ranking to your years played.

### 🔫 Valorant
- **Rank Shaming:** Compares your Current Rank vs. Peak Rank (checks if you are "washed").
- **Aim Analysis:** Roasts low Headshot percentages.
- **K/D Check:** Calls you out if you are getting carried (K/D < 1.0).
- **Match History:** Looks at your recent W/L streak.

## 🚀 Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ROAST_APP.git
cd ROAST_APP

```
### 2. Install Dependencies in a virtual environment
```bash
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```
### 3. Configuration

To run this project, you need to create a `.env` file containing your API keys.

1.  **Rename the template file:**
    Rename the file `.env.example` to `.env` (or create a new `.env` file).

2.  **Add your API Keys:**
    Copy .env.example to .env
    Open the `.env` file and paste your keys like this:

    ```ini
    GOOGLE_API_KEY=your_actual_google_key_here
    CR_API_KEY=your_actual_clash_royale_key_here
    VALORANT_API_KEY=your_actual_valorant_key_here
    ```

    > **Note:** Do not share your `.env` file publicly!

### 4. Run the Application
```bash
uvicorn main:app --reload
```

### 5. Acces the app
Open your browser and navigate to:
http://127.0.0.1:8000