import requests
import os
from .base import GameInterface


class Valorant(GameInterface):
    SUPPORTED_REGIONS = ["ap", "na", "eu", "kr", "latam", "br"]

    def __init__(self):
        self.api_key = os.getenv("VALORANT_API_KEY")
        self.headers = {"Authorization": self.api_key} if self.api_key else {}
        self.base_url = "https://api.henrikdev.xyz/valorant"
        self.region_cache = {}  # Cache for detected regions

    # ---------- REGION AUTO-DETECTION ----------
    def detect_region(self, name: str, tag: str) -> str:
        cache_key = f"{name}#{tag}"
        if cache_key in self.region_cache:
            return self.region_cache[cache_key]

        for region in self.SUPPORTED_REGIONS:
            url = f"{self.base_url}/v2/mmr/{region}/{name}/{tag}"
            res = requests.get(url, headers=self.headers)

            if res.status_code == 200 and res.json().get("data"):
                self.region_cache[cache_key] = region
                return region

        raise Exception("Player not found in any supported region.")

    # ---------- DATA FETCH ----------
    def get_player_data(self, player_id: str):
        if "#" not in player_id:
            raise ValueError("Invalid format. Use Name#Tag")

        name, tag = player_id.split("#", 1)
        region = self.detect_region(name, tag)

        mmr_url = f"{self.base_url}/v2/mmr/{region}/{name}/{tag}"
        matches_url = f"{self.base_url}/v3/matches/{region}/{name}/{tag}"

        mmr_res = requests.get(mmr_url, headers=self.headers)
        matches_res = requests.get(matches_url, headers=self.headers)

        if matches_res.status_code != 200:
            raise Exception("Failed to fetch match history.")

        return {
            "player_name": name,      # No tag repetition later
            "tag": tag,
            "region": region,
            "mmr": mmr_res.json().get("data", {}),
            "matches": matches_res.json().get("data", []),
        }

    # ---------- CLEAN AI-FRIENDLY OUTPUT ----------
    def format_data(self, raw_data: dict):
        player_name = raw_data.get("player_name", "Unknown")
        region = raw_data.get("region", "Unknown")
        mmr_data = raw_data.get("mmr", {})
        matches = raw_data.get("matches", [])

        # Rank info
        current_data = mmr_data.get("current_data", {})
        highest_rank = mmr_data.get("highest_rank", {})

        current_rank = current_data.get("currenttierpatched", "Unranked")
        elo = current_data.get("elo", 0)
        peak_rank = highest_rank.get("patched_tier", "Unknown")

        # Performance stats
        total_kills = total_deaths = 0
        total_hs = total_shots = 0
        agents = []
        match_history = []

        for match in matches:
            map_name = match.get("metadata", {}).get("map", "Unknown")
            players = match.get("players", {}).get("all_players", [])

            player = next(
                (p for p in players if p.get("name", "").lower() == player_name.lower()),
                None,
            )

            if not player:
                continue

            stats = player.get("stats", {})
            kills = stats.get("kills", 0)
            deaths = stats.get("deaths", 0)
            assists = stats.get("assists", 0)

            hs = stats.get("headshots", 0)
            body = stats.get("bodyshots", 0)
            leg = stats.get("legshots", 0)

            total_kills += kills
            total_deaths += deaths
            total_hs += hs
            total_shots += (hs + body + leg)

            agent = player.get("character", "Unknown")
            agents.append(agent)

            team = player.get("team", "").lower()
            teams = match.get("teams", {})
            result = "WIN" if teams.get(team, {}).get("has_won") else "LOSS"

            match_history.append({
                "result": result,
                "map": map_name,
                "agent": agent,
                "kda": f"{kills}/{deaths}/{assists}"
            })

        kd_ratio = round(total_kills / total_deaths, 2) if total_deaths else total_kills
        hs_percentage = round((total_hs / total_shots) * 100, 1) if total_shots else 0
        main_agent = max(set(agents), key=agents.count) if agents else "Unknown"

        # ---------- FINAL OUTPUT ----------
        return {
            "player": player_name,
            "region": region,
            "rank": {
                "current": current_rank,
                "peak": peak_rank,
                "elo": elo
            },
            "performance_last_5": {
                "kd_ratio": kd_ratio,
                "headshot_percentage": hs_percentage,
                "main_agent": main_agent
            },
            "recent_matches": match_history
        }
