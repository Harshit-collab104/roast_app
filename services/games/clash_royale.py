import requests
import os
from dotenv import load_dotenv

load_dotenv()


class ClashRoyale:
    BASE_URL = "https://api.clashroyale.com/v1"

    # Official Path of Legends league mapping
    POL_LEAGUES = {
        1: "Bronze",
        2: "Silver",
        3: "Gold",
        4: "Platinum",
        5: "Diamond",
        6: "Master",
        7: "Champion",
        8: "Grand Champion",
        9: "Royal Champion",
        10: "Ultimate Champion"
    }

    def __init__(self):
        self.api_key = os.getenv("CR_API_KEY")
        if not self.api_key:
            raise RuntimeError("CR_API_KEY not found in environment")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

    # --------------------------------------------------
    # API CALLS
    # --------------------------------------------------

    def get_player_data(self, player_tag: str):
        encoded_tag = "%23" + player_tag.lstrip("#")

        player_url = f"{self.BASE_URL}/players/{encoded_tag}"
        battle_url = f"{self.BASE_URL}/players/{encoded_tag}/battlelog"

        player_res = requests.get(player_url, headers=self.headers)
        if player_res.status_code != 200:
            raise Exception(
                f"Player API Error {player_res.status_code}: {player_res.text}"
            )

        battle_res = requests.get(battle_url, headers=self.headers)
        battles = battle_res.json()[:5] if battle_res.status_code == 200 else []

        return {
            "player": player_res.json(),
            "battles": battles
        }

    # --------------------------------------------------
    # FORMAT DATA FOR AI
    # --------------------------------------------------

    def format_data(self, data):
        p = data.get("player", {})
        battles = data.get("battles", [])

        # ---------- BASIC STATS ----------
        wins = p.get("wins", 0)
        losses = p.get("losses", 0)
        win_rate = round((wins / (wins + losses)) * 100, 2) if (wins + losses) else 0

        trophies = p.get("trophies", 0)
        best_trophies = p.get("bestTrophies", 0)

        # ---------- PATH OF LEGENDS ----------
        pol_current = p.get("currentPathOfLegendSeasonResult")
        pol_best = p.get("bestPathOfLegendSeasonResult")

        pol_stats = "Has not played Path of Legends this season."

        if pol_current:
            league_num = pol_current.get("leagueNumber")
            medals = pol_current.get("trophies", 0)
            rank = pol_current.get("rank")

            league_name = self.POL_LEAGUES.get(league_num, f"League {league_num}")
            pol_stats = (
                f"{league_name} | Medals: {medals} | Global Rank: #{rank}"
                if rank else f"{league_name} | Medals: {medals}"
            )

        elif pol_best:
            best_league = pol_best.get("leagueNumber")
            if best_league:
                pol_stats = (
                    f"Not playing this season. Best finish: "
                    f"{self.POL_LEAGUES.get(best_league, f'League {best_league}')}"
                )

        # ---------- BADGES (YEARS + IMPORTANT) ----------
        badges = p.get("badges", [])

        years_played = None
        important_badges = []

        for badge in badges:
            name = badge.get("name", "")
            lname = name.lower()

            # Extract numeric years
            if "year" in lname:
                for token in lname.split():
                    if token.isdigit():
                        years_played = int(token)

            # Important / skill-relevant badges
            if any(keyword in lname for keyword in [
                "crl",
                "champion",
                "global tournament",
                "top",
                "grand challenge",
                "classic challenge",
                "veteran",
                "clan war",
                "beta",
                "global launch"
            ]):
                important_badges.append(name)

        years_text = f"{years_played} Years Played" if years_played else "Casual / Unknown Experience"
        badges_text = ", ".join(important_badges) if important_badges else "No notable competitive badges"

        # ---------- DECK ----------
        deck = p.get("currentDeck", [])
        deck_names = [c["name"] for c in deck]
        avg_elixir = (
            round(sum(c.get("elixirCost", 0) for c in deck) / 8, 2)
            if deck else 0.0
        )
        fav_card = p.get("currentFavouriteCard", {}).get("name", "Unknown")

        # ---------- CHALLENGES ----------
        max_wins = p.get("challengeMaxWins", 0)
        cards_won = p.get("challengeCardsWon", 0)

        # ---------- RECENT BATTLES ----------
        recent = []
        for b in battles:
            my = b["team"][0].get("crowns", 0)
            opp = b["opponent"][0].get("crowns", 0)

            result = "Draw" if my == opp else "Win" if my > opp else "Loss"
            opp_deck = [c["name"] for c in b["opponent"][0].get("cards", [])[:3]]

            recent.append(f"{result} ({my}-{opp}) vs {', '.join(opp_deck)}")

        recent_log = "\n".join(recent) if recent else "No recent battles found."

        # ---------- FINAL AI SUMMARY ----------
        return f"""
**Player Identity**
- Name: {p.get('name')}
- Experience: {years_text}
- Notable Badges: {badges_text}
- Win Rate: {win_rate}% (Wins: {wins}, Losses: {losses})

**Ladder Performance**
- Current Trophies: {trophies}
- Best Trophies: {best_trophies}

**Path of Legends**
- {pol_stats}
- (Ultimate Champion is League 10. Below League 7 = casual or mid-ladder.)

**Challenges**
- Max Wins: {max_wins} (12+ is respectable)
- Cards Won: {cards_won}

**Deck**
- Cards: {", ".join(deck_names)}
- Avg Elixir: {avg_elixir}
- Favorite Card: {fav_card}

**Recent Matches (Last 5)**
{recent_log}

**Roast Rules**
- Mega Knight / E-Giant / Freeze = zero skill
- Many years + no badges = wasted lifetime
- Low challenge wins = mid-ladder menace
- Reference recent losses directly
"""
