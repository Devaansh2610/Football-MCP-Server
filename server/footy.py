from mcp.server.fastmcp import FastMCP
from mcp import Tool
import time
import signal
import sys
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import os
import requests
from dotenv import load_dotenv
load_dotenv()
os.environ["RAPID_API_KEY_FOOTBALL"]=os.getenv("RAPID_API_KEY_FOOTBALL") 
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import json
# Step 1: Load correct key
REAL_KEY = os.getenv("WITTY_KEY")          # your server’s internal secret
USER_KEY = os.getenv("USER_WITTY_KEY")     # provided by user

if USER_KEY != REAL_KEY:
    print("Access denied. Invalid USER_WITTY_KEY.")
    exit(1)
else:
    print("Access granted.")


mcp = FastMCP(
    name="footy_server"
    # host="127.0.0.1",
    # port=8080,

)

@mcp.tool()
def get_league_id_by_name(league_name: str) -> Dict[str, Any]:
    """Retrieve the league ID for a given league name.

    This tool searches for a league by its name and returns its ID.  It uses the
    `/leagues` endpoint of the API-Football API.

    **Args:**

        league_name (str): The name of the league (e.g., "Premier League", "La Liga").

    **Returns:**

        Dict[str, Any]: A dictionary containing the league ID, or an error message.  Key fields:

            *   "league_id" (int): The ID of the league, if found.
            *   "error" (str): An error message if the league is not found or an error occurs.

    **Example:**
        ```
        get_league_id_by_name(league_name="Premier League")
        # Expected output (may vary):  {"league_id": 39}
        ```
    """
    api_key = os.getenv("RAPID_API_KEY_FOOTBALL")
    if not api_key:
        return {"error": "RAPID_API_KEY_FOOTBALL environment variable not set."}

    base_url = "https://api-football-v1.p.rapidapi.com/v3"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": "f58d71e49amsh773b93ab46e7bc2p11a412jsn8b59820e1412"
    }

    try:
        leagues_url = f"{base_url}/leagues"
        leagues_params = {"search": league_name}
        resp = requests.get(leagues_url, headers=headers, params=leagues_params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("response"):
            return {"error": f"No leagues found matching '{league_name}'."}

        league_id = data["response"][0]["league"]["id"]
        return {"league_id": league_id}

    except Exception as e:
        return {"error": str(e)}  


@mcp.tool()
def get_standings(league_id: Optional[List[int]], season: List[int], team: Optional[int] = None) -> Dict[str, Any]:
    """Retrieve league standings for multiple leagues and seasons, optionally filtered by team.

    This tool retrieves the standings table for one or more leagues, across multiple
    seasons. It can optionally filter the results to show standings for a specific team.
    Uses the `/standings` endpoint.

    **Args:**

        league_id (Optional[List[int]]): A list of league IDs to retrieve standings for.
        season (List[int]): A list of 4-digit season years (e.g., [2021, 2022]).
        team (Optional[int]):  A specific team ID to filter the standings.

    **Returns:**

        Dict[str, Any]: A dictionary containing the standings, or an error message.  The structure is:

            *   `{league_id: {season: standings_data}}`

            `standings_data` is the raw JSON response from the API for the given league and season.  If an error occurs
            for a specific league/season, the `standings_data` will be `{"error": "error message"}`.

        **Example:**

          ```python
            get_standings(league_id=[39, 140], season=[2022, 2023], team=None)
          ```
    """
    api_key = os.getenv("RAPID_API_KEY_FOOTBALL")
    if not api_key:
        return {"error": "RAPID_API_KEY_FOOTBALL environment variable not set."}

    base_url = "https://api-football-v1.p.rapidapi.com/v3"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": "f58d71e49amsh773b93ab46e7bc2p11a412jsn8b59820e1412"
    }

    results: Dict[int, Dict[int, Any]] = {}
    leagues = league_id if league_id else []

    for league in leagues:
        results[league] = {}
        for year in season:
            url = f"{base_url}/standings"
            params = {"season": year, "league": league}

            if team is not None:
                params["team"] = team

            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                results[league][year] = response.json()
            except Exception as e:
                results[league][year] = {"error": str(e)}

    return results      


@mcp.tool()
def get_player_id(player_name: str) -> Dict[str, Any]:
    """Retrieve a list of player IDs and identifying information for players matching a given name.

    This tool searches for players by either their first *or* last name and returns a list of
    potential matches.  It includes identifying information to help disambiguate players.
    Uses the `/players/profiles` endpoint.

    **Args:**

        player_name (str): The first *or* last name of the player (e.g., "Lionel" or "Messi").
                           Do *not* provide both first and last names.  The name must be at least
                           3 characters long.

    **Returns:**

        Dict[str, Any]: A dictionary containing a list of players or an error message. Key fields:
            * "players" (List[Dict[str, Any]]): A list of dictionaries, each representing a player.
              Each player dictionary includes:
                * "player_id" (int): The player's ID.
                * "firstname" (str): The player's first name.
                * "lastname" (str): The player's last name.
                * "age" (int): The player's age.
                * "nationality" (str): The player's nationality.
                * "birth_date" (str): The player's birth date (YYYY-MM-DD).
                * "birth_place" (str): The player's birth place.
                *  "birth_country" (str)
                * "height" (str): The player's height (e.g., "170 cm").
                * "weight" (str): The player's weight (e.g., "68 kg").
            * "error" (str): An error message if no players are found or an error occurs.

    **Example:**
        ```
        get_player_id(player_name="Messi")
        ```

    """
    if " " in player_name.strip():
        return {"error": "Please enter only the first *or* last name, not both."}
    if len(player_name.strip()) < 3:
         return {"error": "The name must be at least 3 characters long."}


    api_key = os.getenv("RAPID_API_KEY_FOOTBALL")
    if not api_key:
        return {"error": "RAPID_API_KEY_FOOTBALL environment variable not set."}

    base_url = "https://api-football-v1.p.rapidapi.com/v3"
    url = f"{base_url}/players/profiles"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": api_key,
    }
    params = {
        "search": player_name,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("response"):
            return {"error": f"No players found matching '{player_name}'."}

        player_list = []
        for item in data["response"]:
            player = item.get("player", {})
            player_info = {
                "player_id": player.get("id"),
                "firstname": player.get("firstname"),
                "lastname": player.get("lastname"),
                "age": player.get("age"),
                "nationality": player.get("nationality"),
                "birth_date": player.get("birth", {}).get("date"),
                "birth_place": player.get("birth", {}).get("place"),
                "birth_country": player.get("birth", {}).get("country"),
                "height": player.get("height"),
                "weight": player.get("weight")
            }
            player_list.append(player_info)

        return {"players": player_list}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


@mcp.tool()
def get_player_profile(player_name: str) -> Dict[str, Any]:
    """Retrieve a single player's profile information by their last name.

    This tool retrieves a player's profile by searching for their last name.  It uses
    the `/players/profiles` endpoint.

    **Args:**

        player_name (str): The last name of the player to look up. Must be >= 3 characters.

    **Returns:**

        Dict[str, Any]: The raw JSON response from the API, or a dictionary with an "error" key
        if the request fails.

    **Example:**
    ```python
    get_player_profile(player_name = "Messi")
    ```
    """
    if len(player_name.strip()) < 3:
         return {"error": "The name must be at least 3 characters long."}

    api_key = os.getenv("RAPID_API_KEY_FOOTBALL")
    if not api_key:
        return {"error": "RAPID_API_KEY_FOOTBALL environment variable not set."}


    base_url = "https://api-football-v1.p.rapidapi.com/v3"
    url = f"{base_url}/players/profiles"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }

    params = {
        "search": player_name,
        "page": 1  # Fetch only the first page
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}



@mcp.tool()
def get_player_statistics(player_id: int, seasons: List[int], league_name: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve detailed player statistics for given seasons and optional league name.

    This tool retrieves detailed player statistics, including advanced stats, for a
    specified player ID.  It filters the results by a list of seasons and, optionally,
    by a league name. It uses the /players endpoint.

    **Args:**

        player_id (int): The ID of the player.
        seasons (List[int]): A list of seasons to get statistics for (4-digit years,
            e.g., [2021, 2022] or [2023]).
        league_name (Optional[str]): The name of the league (e.g., "Premier League").
            If provided, statistics will be retrieved only for this league.  If the
            league name cannot be found for a given season, an error will be included
            in the results for that season.

    **Returns:**

        Dict[str, Any]: A dictionary containing the player statistics or error messages. Key fields:

            *   "player_statistics" (List[Dict[str, Any]]): A list of dictionaries, each
                representing player statistics for a specific season (and league, if
                specified).
            *   "error" (str):  An error message may be present *within* the
                `player_statistics` list if there was a problem fetching data for a specific
                season, or at the top level if no statistics at all could be retrieved.

            Each dictionary in "player_statistics" contains detailed statistics, grouped
            by category ("player", "team", "league", "games", "substitutes", "shots",
            "goals", "passes", "tackles", "duels", "dribbles", "fouls", "cards", "penalty").
    """
    api_key = os.getenv("RAPID_API_KEY_FOOTBALL")
    if not api_key:
        return {"error": "RAPID_API_KEY_FOOTBALL environment variable not set."}
    if isinstance(seasons, int):
        seasons = [seasons]
    if league_name is not None and len(league_name.strip()) < 3:
        return {"error": "League name must be at least 3 characters long."}

    base_url = "https://api-football-v1.p.rapidapi.com/v3"
    url = f"{base_url}/players"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": api_key,
    }
    all_stats = []

    def _get_league_id(league_name: str, season: int) -> Optional[int]:
        """Helper function to get the league ID from the league name."""
        url = f"{base_url}/leagues"
        headers = {
            "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
            "x-rapidapi-key": api_key,
        }
        params = {"name": league_name, "season": season}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("response"):
                return None

            for league_data in data["response"]:
                if league_data["league"]["name"].lower() == league_name.lower():
                    for league_season in league_data["seasons"]:
                        if league_season["year"] == season:
                            return league_data["league"]["id"]
            return None

        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None
    # End of helper function

    for current_season in seasons:
        league_id = None
        if league_name:
            league_id = _get_league_id(league_name, current_season)
            if league_id is None:
                all_stats.append({
                    "error": f"Could not find league ID for '{league_name}' in season {current_season}."
                })
                continue

        params: Dict[str, Any] = {"id": player_id, "season": current_season}
        if league_id:
            params["league"] = league_id

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("response"):
                continue

            for entry in data["response"]:
                player_info = entry.get("player", {})
                for stats in entry.get("statistics", []):
                    extracted_stats: Dict[str, Any] = {
                        "player": {
                            "id": player_info.get("id"),
                            "name": player_info.get("name"),
                            "photo": player_info.get("photo"),
                        },
                        "team": {
                            "id": stats.get("team", {}).get("id"),
                            "name": stats.get("team", {}).get("name"),
                            "logo": stats.get("team", {}).get("logo"),
                        },
                        "league": {
                            "id": stats.get("league", {}).get("id"),
                            "name": stats.get("league", {}).get("name"),
                            "season": stats.get("league", {}).get("season"),
                            "country": stats.get("league", {}).get("country"),
                            "flag": stats.get("league", {}).get("flag"),
                        },
                        "games": {
                            "appearances": stats.get("games", {}).get("appearences"),
                            "lineups": stats.get("games", {}).get("lineups"),
                            "minutes": stats.get("games", {}).get("minutes"),
                            "position": stats.get("games", {}).get("position"),
                            "rating": stats.get("games", {}).get("rating"),
                        },
                        "substitutes": {
                            "in": stats.get("substitutes", {}).get("in"),
                            "out": stats.get("substitutes", {}).get("out"),
                            "bench": stats.get("substitutes", {}).get("bench"),
                        },
                        "shots": {
                            "total": stats.get("shots", {}).get("total"),
                            "on": stats.get("shots", {}).get("on"),
                        },
                        "goals": {
                            "total": stats.get("goals", {}).get("total"),
                            "conceded": stats.get("goals", {}).get("conceded"),
                            "assists": stats.get("goals", {}).get("assists"),
                            "saves": stats.get("goals", {}).get("saves"),
                        },
                        "passes": {
                            "total": stats.get("passes", {}).get("total"),
                            "key": stats.get("passes", {}).get("key"),
                            "accuracy": stats.get("passes", {}).get("accuracy"),
                        },
                        "tackles": {
                            "total": stats.get("tackles", {}).get("total"),
                            "blocks": stats.get("tackles", {}).get("blocks"),
                            "interceptions": stats.get("tackles", {}).get("interceptions"),
                        },
                        "duels": {
                            "total": stats.get("duels", {}).get("total"),
                            "won": stats.get("duels", {}).get("won"),
                        },
                        "dribbles": {
                            "attempts": stats.get("dribbles", {}).get("attempts"),
                            "success": stats.get("dribbles", {}).get("success"),
                        },
                        "fouls": {
                            "drawn": stats.get("fouls", {}).get("drawn"),
                            "committed": stats.get("fouls", {}).get("committed"),
                        },
                        "cards": {
                            "yellow": stats.get("cards", {}).get("yellow"),
                            "red": stats.get("cards", {}).get("red"),
                        },
                        "penalty": {
                            "won": stats.get("penalty", {}).get("won"),
                            "committed": stats.get("penalty", {}).get("committed"),
                            "scored": stats.get("penalty", {}).get("scored"),
                            "missed": stats.get("penalty", {}).get("missed"),
                            "saved": stats.get("penalty", {}).get("saved"),
                        },
                    }
                    all_stats.append(extracted_stats)

        except requests.exceptions.RequestException as e:
            all_stats.append({"error": f"Request failed for season {current_season}: {e}"})
        except Exception as e:
            all_stats.append({"error": f"An unexpected error occurred for season {current_season}: {e}"})

    if not all_stats:
        return {
            "error": f"No statistics found for player ID {player_id} for the specified seasons/league."
        }

    return {"player_statistics": all_stats}



logger.info("before mcp run")

if __name__ == "__main__":
    try:
        print("Starting server")
        logger.info("starting mcp run")
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error: {e}")

    

    