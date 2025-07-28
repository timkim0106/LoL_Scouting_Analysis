"""Player model for tracking professional and high-ranking players."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class Player(BaseModel):
    """Represents a League of Legends player."""
    
    puuid: str = Field(..., description="Player UUID from Riot API")
    game_name: str = Field(..., description="In-game name")
    tag_line: str = Field(..., description="Tag line (e.g., NA1)")
    summoner_id: Optional[str] = Field(None, description="Summoner ID")
    account_id: Optional[str] = Field(None, description="Account ID")
    
    # Professional info
    team: Optional[str] = Field(None, description="Professional team")
    role: Optional[str] = Field(None, description="Primary role")
    region: str = Field("NA", description="Server region")
    
    # Tracking metadata
    last_updated: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(True, description="Whether account is still being tracked")
    
    @validator("role")
    def validate_role(cls, v):
        """Validate player role."""
        if v is not None:
            valid_roles = {"TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"}
            if v.upper() not in valid_roles:
                raise ValueError(f"Role must be one of {valid_roles}")
            return v.upper()
        return v
    
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        return f"{self.game_name}#{self.tag_line}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return self.dict()


class PlayerStats(BaseModel):
    """Player performance statistics."""
    
    puuid: str = Field(..., description="Player UUID")
    champion: str = Field(..., description="Champion name")
    games_played: int = Field(0, ge=0, description="Number of games")
    wins: int = Field(0, ge=0, description="Number of wins")
    losses: int = Field(0, ge=0, description="Number of losses")
    
    # Performance metrics
    avg_kda: float = Field(0.0, ge=0, description="Average KDA ratio")
    avg_damage: float = Field(0.0, ge=0, description="Average damage dealt")
    avg_gold: float = Field(0.0, ge=0, description="Average gold earned")
    
    # Time tracking
    last_game: Optional[datetime] = Field(None, description="Last game timestamp")
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.games_played == 0:
            return 0.0
        return (self.wins / self.games_played) * 100


# Professional teams and their players
PROFESSIONAL_TEAMS = {
    "100T": {
        "name": "100 Thieves",
        "players": [
            {"game_name": "100 Sniper", "tag_line": "NA1", "role": "TOP"},
            {"game_name": "100 Batman", "tag_line": "123", "role": "JUNGLE"},
            {"game_name": "tree frog", "tag_line": "100", "role": "MIDDLE"},
            {"game_name": "tiki and taka", "tag_line": "NA1", "role": "BOTTOM"},
            {"game_name": "Yves", "tag_line": "100", "role": "SUPPORT"},
        ]
    },
    "C9": {
        "name": "Cloud9",
        "players": [
            {"game_name": "God of death", "tag_line": "kr2", "role": "TOP"},
            {"game_name": "blaberfish2", "tag_line": "NA1", "role": "JUNGLE"},
            {"game_name": "jjjjjjjjj", "tag_line": "1212", "role": "MIDDLE"},
            {"game_name": "C9 Berserker", "tag_line": "NA1", "role": "BOTTOM"},
            {"game_name": "VULCAN", "tag_line": "5125", "role": "SUPPORT"},
        ]
    },
    "TL": {
        "name": "Team Liquid",
        "players": [
            {"game_name": "TL HONDA IMPACT", "tag_line": "XDDD", "role": "TOP"},
            {"game_name": "TL Honda UmTi", "tag_line": "0602", "role": "JUNGLE"},
            {"game_name": "lcs villain", "tag_line": "APA", "role": "MIDDLE"},
            {"game_name": "TL Honda Yeon", "tag_line": "NA1", "role": "BOTTOM"},
            {"game_name": "TL Honda CoreJJ", "tag_line": "1123", "role": "SUPPORT"},
        ]
    }
}