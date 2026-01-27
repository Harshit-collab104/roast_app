import requests
import os
from .base import GameInterface

class Valorant(GameInterface):
    def __init__(self):
        self.api_key = os.getenv("VALORANT_API_KEY")
        self.headers = {"Authorization": self.api_key}
        self.base_url = "https://api.henrikdev.xyz/valorant"
        self.region = "ap" 

    def get_player_data(self, player_id: str):
        # Expected input: "Name#Tag" (e.g., "Viper#123")
        if "#" not in player_id:
            raise Exception("Invalid Format. Use Name#Tag (e.g., Player#123)")
        
        name, tag = player_id.split("#")
        
        # 1. Get MMR (Rank Info)
        # v2/mmr/{region}/{name}/{tag}
        mmr_url = f"{self.base_url}/v2/mmr/{self.region}/{name}/{tag}"
        mmr_res = requests.get(mmr_url, headers=self.headers)
        
        # 2. Get Match History (Last 5 games)
        # v3/matches/{region}/{name}/{tag}
        matches_url = f"{self.base_url}/v3/matches/{self.region}/{name}/{tag}"
        matches_res = requests.get(matches_url, headers=self.headers)

        if matches_res.status_code != 200:
            raise Exception(f"Player not found in region '{self.region}'. Check spelling or Region.")

        return {
            "mmr": mmr_res.json().get('data', {}),
            "matches": matches_res.json().get('data', []),
            "name": f"{name}#{tag}"
        }

    def format_data(self, raw_data):
        mmr_data = raw_data['mmr']
        matches = raw_data['matches'] # List of last 5 matches
        name = raw_data['name']

        # --- 1. RANK INFO ---
        current_rank = mmr_data.get('current_data', {}).get('currenttierpatched', 'Unranked')
        elo = mmr_data.get('current_data', {}).get('elo', 0)
        peak_rank = mmr_data.get('highest_rank', {}).get('patched_tier', 'Unknown')
        
        # --- 2. PERFORMANCE STATS (Average over last 5 games) ---
        total_kills = 0
        total_deaths = 0
        total_hs_shots = 0
        total_shots = 0
        agents_played = []
        
        match_summaries = []

        for match in matches:
            # Find the player in the match metadata
            meta = match.get('metadata', {})
            map_name = meta.get('map', 'Unknown')
            
            # Find player stats inside the match
            my_stats = next((p for p in match.get('players', {}).get('all_players', []) 
                             if p['name'].lower() == name.split('#')[0].lower()), None)
            
            if my_stats:
                character = my_stats.get('character', 'Unknown')
                k = my_stats['stats']['kills']
                d = my_stats['stats']['deaths']
                a = my_stats['stats']['assists']
                score = my_stats['stats']['score']
                
                # Headshot calc
                hs = my_stats['stats']['headshots']
                bodys = my_stats['stats']['bodyshots']
                legs = my_stats['stats']['legshots']
                
                total_kills += k
                total_deaths += d
                total_hs_shots += hs
                total_shots += (hs + bodys + legs)
                agents_played.append(character)
                
                # Did they win?
                team = my_stats['team'] # 'Red' or 'Blue'
                winning_team = match['teams'][team.lower()]['has_won']
                result = "WIN" if winning_team else "LOSS"
                
                match_summaries.append(f"{result} on {map_name} as {character} (KDA: {k}/{d}/{a})")

        # Averages
        kd_ratio = round(total_kills / total_deaths, 2) if total_deaths > 0 else total_kills
        hs_percentage = round((total_hs_shots / total_shots) * 100, 1) if total_shots > 0 else 0
        most_played_agent = max(set(agents_played), key=agents_played.count) if agents_played else "Unknown"

        # --- 3. FINAL SUMMARY FOR AI ---
        summary = f"""
        **Identity:**
        - Name: {name}
        - Current Rank: {current_rank} (Elo: {elo})
        - Peak Rank: {peak_rank}
        
        **Skill Stats (Last 5 Games):**
        - K/D Ratio: {kd_ratio} (If < 1.0, they are getting carried. If < 0.8, they are throwing.)
        - Headshot %: {hs_percentage}% (Pro is >25%. If < 15%, roast their aim.)
        - Main Agent: {most_played_agent}
        
        **Match History:**
        {"; ".join(match_summaries)}
        
        **Roast Guidelines:**
        1. If they main **Reyna** or **Jett** and have a low K/D (<1.0), destroy them for instalocking and bottom fragging.
        2. If their Headshot % is low, tell them to stop aiming at toes.
        3. Compare their Peak Rank to Current Rank. If they fell off (e.g., Peak Ascendant, currently Gold), roast them for being "washed".
        4. If they are "Iron" or "Bronze", mock them for playing on a trackpad.
        5. Look at the Match History. If they have many "LOSS" entries, mock their "Red Carpet" match history.
        """
        return summary