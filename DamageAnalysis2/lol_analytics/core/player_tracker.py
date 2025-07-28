"""Core player tracking functionality."""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..models.player import Player, PlayerStats, PROFESSIONAL_TEAMS
from ..utils.api_client import RiotAPIClient, RiotAPIError
from ..utils.logger import logger
from ..config.settings import settings


class PlayerTracker:
    """
    Track professional and high-ranking League of Legends players.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the player tracker.
        
        Args:
            data_dir: Directory for storing player data
        """
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.api_client = RiotAPIClient()
        self.players: Dict[str, Player] = {}
        self.player_stats: Dict[str, List[PlayerStats]] = {}
        
        logger.info("PlayerTracker initialized")
    
    def add_player(
        self,
        game_name: str,
        tag_line: str,
        team: Optional[str] = None,
        role: Optional[str] = None
    ) -> Optional[Player]:
        """
        Add a player to the tracking system.
        
        Args:
            game_name: Player's game name
            tag_line: Player's tag line
            team: Professional team (optional)
            role: Player role (optional)
        
        Returns:
            Player object if successful, None otherwise
        """
        try:
            # Get account data from Riot API
            account_data = self.api_client.get_account_by_riot_id(game_name, tag_line)
            
            player = Player(
                puuid=account_data["puuid"],
                game_name=account_data["gameName"],
                tag_line=account_data["tagLine"],
                team=team,
                role=role,
                last_updated=datetime.now()
            )
            
            self.players[player.puuid] = player
            logger.info(f"Added player: {player.display_name}")
            
            return player
            
        except RiotAPIError as e:
            logger.error(f"Failed to add player {game_name}#{tag_line}: {e}")
            return None
    
    def batch_add_players(self, player_list: List[Dict[str, str]]) -> Dict[str, Optional[Player]]:
        """
        Add multiple players in batch.
        
        Args:
            player_list: List of player dictionaries
        
        Returns:
            Dictionary mapping display names to Player objects
        """
        results = {}
        
        for player_info in player_list:
            game_name = player_info["game_name"]
            tag_line = player_info["tag_line"]
            team = player_info.get("team")
            role = player_info.get("role")
            
            display_name = f"{game_name}#{tag_line}"
            player = self.add_player(game_name, tag_line, team, role)
            results[display_name] = player
            
            # Rate limiting
            time.sleep(1.2)
        
        logger.info(f"Batch add complete. Added {sum(1 for p in results.values() if p)} players")
        return results
    
    def load_professional_teams(self) -> Dict[str, List[Player]]:
        """
        Load all professional team players.
        
        Returns:
            Dictionary mapping team names to player lists
        """
        all_players = {}
        
        for team_code, team_info in PROFESSIONAL_TEAMS.items():
            team_name = team_info["name"]
            players_data = team_info["players"]
            
            logger.info(f"Loading team: {team_name}")
            
            team_players = []
            for player_data in players_data:
                player = self.add_player(
                    game_name=player_data["game_name"],
                    tag_line=player_data["tag_line"],
                    team=team_code,
                    role=player_data["role"]
                )
                
                if player:
                    team_players.append(player)
                
                time.sleep(1.2)  # Rate limiting
            
            all_players[team_code] = team_players
        
        return all_players
    
    def update_player_name(self, puuid: str) -> Optional[Player]:
        """
        Update a player's current name using their PUUID.
        
        Args:
            puuid: Player's PUUID
        
        Returns:
            Updated Player object if successful
        """
        if puuid not in self.players:
            logger.warning(f"Player with PUUID {puuid[:8]}... not found")
            return None
        
        try:
            account_data = self.api_client.get_account_by_puuid(puuid)
            
            player = self.players[puuid]
            old_name = player.display_name
            
            player.game_name = account_data["gameName"]
            player.tag_line = account_data["tagLine"]
            player.last_updated = datetime.now()
            
            new_name = player.display_name
            
            if old_name != new_name:
                logger.info(f"Name change detected: {old_name} -> {new_name}")
            
            return player
            
        except RiotAPIError as e:
            logger.error(f"Failed to update player {puuid[:8]}...: {e}")
            return None
    
    def bulk_update_names(self) -> Dict[str, bool]:
        """
        Update names for all tracked players.
        
        Returns:
            Dictionary mapping PUUIDs to success status
        """
        results = {}
        
        logger.info(f"Updating names for {len(self.players)} players")
        
        for puuid in self.players.keys():
            success = self.update_player_name(puuid) is not None
            results[puuid] = success
            time.sleep(1.2)  # Rate limiting
        
        successful_updates = sum(results.values())
        logger.info(f"Updated {successful_updates}/{len(self.players)} players successfully")
        
        return results
    
    def get_player_match_history(
        self,
        puuid: str,
        count: int = 20
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent match history for a player.
        
        Args:
            puuid: Player's PUUID
            count: Number of matches to retrieve
        
        Returns:
            List of match data
        """
        try:
            match_ids = self.api_client.get_match_history(puuid, count)
            matches = []
            
            for match_id in match_ids[:5]:  # Limit to avoid rate limits
                match_data = self.api_client.get_match_details(match_id)
                matches.append(match_data)
                time.sleep(0.5)
            
            logger.info(f"Retrieved {len(matches)} matches for {puuid[:8]}...")
            return matches
            
        except RiotAPIError as e:
            logger.error(f"Failed to get match history for {puuid[:8]}...: {e}")
            return None
    
    def analyze_player_performance(self, puuid: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a player's recent performance.
        
        Args:
            puuid: Player's PUUID
        
        Returns:
            Performance analysis
        """
        matches = self.get_player_match_history(puuid)
        if not matches:
            return None
        
        player = self.players.get(puuid)
        if not player:
            return None
        
        # Extract performance metrics
        champion_stats = {}
        total_games = 0
        total_wins = 0
        
        for match in matches:
            # Find the player's participant data
            participant = None
            for p in match["info"]["participants"]:
                if p["puuid"] == puuid:
                    participant = p
                    break
            
            if not participant:
                continue
            
            champion = participant["championName"]
            won = participant["win"]
            
            if champion not in champion_stats:
                champion_stats[champion] = {
                    "games": 0,
                    "wins": 0,
                    "kills": 0,
                    "deaths": 0,
                    "assists": 0,
                    "damage": 0
                }
            
            stats = champion_stats[champion]
            stats["games"] += 1
            stats["wins"] += 1 if won else 0
            stats["kills"] += participant["kills"]
            stats["deaths"] += participant["deaths"]
            stats["assists"] += participant["assists"]
            stats["damage"] += participant["totalDamageDealtToChampions"]
            
            total_games += 1
            total_wins += 1 if won else 0
        
        # Calculate averages
        for champion, stats in champion_stats.items():
            games = stats["games"]
            stats["avg_kda"] = (stats["kills"] + stats["assists"]) / max(stats["deaths"], 1)
            stats["avg_damage"] = stats["damage"] / games
            stats["win_rate"] = (stats["wins"] / games) * 100
        
        analysis = {
            "player": player.display_name,
            "puuid": puuid,
            "total_games": total_games,
            "total_wins": total_wins,
            "overall_win_rate": (total_wins / total_games * 100) if total_games > 0 else 0,
            "champion_stats": champion_stats,
            "most_played": max(champion_stats.keys(), key=lambda c: champion_stats[c]["games"]) if champion_stats else None,
            "analysis_date": datetime.now().isoformat()
        }
        
        return analysis
    
    def save_player_data(self, filename: str = "player_data.json") -> Path:
        """
        Save player tracking data to file.
        
        Args:
            filename: Output filename
        
        Returns:
            Path to saved file
        """
        output_path = self.data_dir / filename
        
        # Convert players to serializable format
        player_data = {
            puuid: player.dict() for puuid, player in self.players.items()
        }
        
        save_data = {
            "players": player_data,
            "last_updated": datetime.now().isoformat(),
            "total_players": len(self.players)
        }
        
        with open(output_path, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        logger.info(f"Player data saved to: {output_path}")
        return output_path
    
    def load_player_data(self, filename: str = "player_data.json") -> bool:
        """
        Load player tracking data from file.
        
        Args:
            filename: Input filename
        
        Returns:
            True if successful
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            logger.warning(f"Player data file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Load players
            for puuid, player_data in data["players"].items():
                self.players[puuid] = Player(**player_data)
            
            logger.info(f"Loaded {len(self.players)} players from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load player data: {e}")
            return False
    
    def get_team_summary(self, team_code: str) -> Optional[Dict[str, Any]]:
        """
        Get summary statistics for a team.
        
        Args:
            team_code: Team code (e.g., "C9", "TL")
        
        Returns:
            Team summary data
        """
        team_players = [p for p in self.players.values() if p.team == team_code]
        
        if not team_players:
            logger.warning(f"No players found for team: {team_code}")
            return None
        
        summary = {
            "team_code": team_code,
            "team_name": PROFESSIONAL_TEAMS.get(team_code, {}).get("name", team_code),
            "player_count": len(team_players),
            "players": [
                {
                    "name": p.display_name,
                    "role": p.role,
                    "last_updated": p.last_updated.isoformat() if p.last_updated else None
                }
                for p in team_players
            ],
            "last_bulk_update": max(p.last_updated for p in team_players if p.last_updated)
        }
        
        return summary