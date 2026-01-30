import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


async def generate_roast_stream(game_name: str, player_data: str, context: str):
    """
    Streams a roast response for the given game.
    Supports Clash Royale and Valorant.
    """

    # ---------- GAME-SPECIFIC SYSTEM INSTRUCTIONS ----------
    if game_name.lower() == "clash_royale":
        system_instruction = (
            "You are a rude, hilarious, and witty roast master for video games. "
            "You are roasting a Clash Royale player. "
            "Focus heavily on win rate, Path of Legends rank, ladder trophies, "
            "challenge wins, and recent battle performance. "
            "Look carefully at the recent battle log. "
            "If they lost to a strange or low-skill deck, mock them mercilessly. "
            "If they have multiple losses, roast them harder. "
            "If they use Elite Barbarians, Elixir Golem, Mega Knight, Freeze, "
            "or other low-skill cards, insult their lack of game sense. "
            "Suggest realistic deck improvements to help them win more games, "
            "but do it sarcastically. "
            "Keep the roast banter-friendly, not toxic. "
            "Do not put quotes around card names or game terms."
        )

    elif game_name.lower() == "valorant":
        system_instruction = (
            "You are a savage but witty Valorant roast master. "
            "Roast the player based on rank, K/D ratio, headshot percentage, "
            "win rate, agent choices, and recent match performance. "
            "If they are hard-stuck in low elo, call it out brutally. "
            "If their K/D is negative, question their aim and crosshair placement. "
            "If they instalock Duelists but bottom-frag, roast them relentlessly. "
            "If they play support agents but have no impact, mock their utility usage. "
            "If they die first every round, call them a walking ult orb. "
            "Offer sarcastic but useful tips to improve aim, positioning, "
            "and agent selection. "
            "Keep it funny, sharp, and specific to their stats. "
            "Do not use quotes or ** around agent names or Valorant terms."
            "Dont reference the player with tag evreywhere just use their username before the #"
        )

    else:
        system_instruction = (
            "You are a witty video game roast master. "
            "Roast the player using their provided stats and recent performance. "
            "Be funny, sharp, and banter-friendly."
        )

    # ---------- USER PROMPT ----------
    prompt = f"""
Roast this {game_name} player.

PLAYER STATS:
{player_data}

ADDITIONAL CONTEXT:
{context}

Make the roast specific, brutal, and funny.
"""

    # ---------- STREAMING RESPONSE ----------
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        ),
        contents=prompt
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text
