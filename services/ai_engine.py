import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client=genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

async def generate_roast_stream(game_name,player_data, context):

    prompt=f"""
    Roast this {game_name} player!
    Stats:
    {player_data}

    Context/Details:
    {context}
    """

    response=client.models.generate_content_stream(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=f"You are a rude, hilarious and witty roast master on video games. You are roasting a {game_name} player. Keep it banter freindly and focus on their specific stats depending on the game. For clash royale specifically suggest edits to the deck so that the player can win more games.Since most games have win rate judge them highly on that. Look at the Recent Battle Log carefully. If they lost to a weird deck, roast them for it. If they have a ""Loss"" streak, destroy them.If they use ""Elite Barbarians"", ""Elixir Golem"", or ""Mega Knight"", roast their lack of skill.Dont put quotes on card names or game terms.",
    ),
        contents=prompt 
    )


    for chunk in response:
        yield chunk.text