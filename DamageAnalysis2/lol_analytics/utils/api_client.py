"""Riot API client with proper error handling and rate limiting."""

import time
from typing import Optional, Dict, Any, List
from urllib.parse import quote
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import settings
from .logger import logger


class RiotAPIError(Exception):
    """Custom exception for Riot API errors."""
    
    def __init__(self, status_code: int, message: str, response_data: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        super().__init__(f"API Error {status_code}: {message}")


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, requests_per_second: int = 50):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


class RiotAPIClient:
    """
    Riot Games API client with proper error handling, rate limiting, and retries.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        region: str = "americas",
        rate_limit: int = 50,
        timeout: int = 30
    ):
        """
        Initialize the API client.
        
        Args:
            api_key: Riot API key (uses settings if None)
            region: API region
            rate_limit: Requests per second limit
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.riot_api_key
        self.region = region
        self.timeout = timeout
        self.rate_limiter = RateLimiter(rate_limit)
        
        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Base URLs
        self.base_urls = {
            "account": f"https://{self.region}.api.riotgames.com/riot/account/v1",
            "summoner": f"https://{self.region}.api.riotgames.com/lol/summoner/v4",
            "league": f"https://{self.region}.api.riotgames.com/lol/league/v4",
            "match": f"https://{self.region}.api.riotgames.com/lol/match/v5"
        }
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Riot API with proper error handling.
        
        Args:
            url: API endpoint URL
            params: Query parameters
        
        Returns:
            JSON response data
        
        Raises:
            RiotAPIError: If API request fails
        """
        self.rate_limiter.wait_if_needed()
        
        # Add API key to params
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        
        try:
            logger.debug(f"Making API request to: {url}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise RiotAPIError(404, "Resource not found", response.json() if response.text else None)
            elif response.status_code == 429:
                raise RiotAPIError(429, "Rate limit exceeded", response.json() if response.text else None)
            elif response.status_code == 403:
                raise RiotAPIError(403, "Forbidden - check API key", response.json() if response.text else None)
            else:
                response.raise_for_status()
                
        except requests.exceptions.Timeout:
            raise RiotAPIError(408, f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise RiotAPIError(503, "Connection error - API may be unavailable")
        except requests.exceptions.RequestException as e:
            raise RiotAPIError(500, f"Request failed: {str(e)}")
    
    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Dict[str, Any]:
        """
        Get account information by Riot ID.
        
        Args:
            game_name: Player's game name
            tag_line: Player's tag line
        
        Returns:
            Account data including puuid
        """
        # URL encode the names to handle special characters
        encoded_game_name = quote(game_name)
        encoded_tag_line = quote(tag_line)
        
        url = f"{self.base_urls['account']}/accounts/by-riot-id/{encoded_game_name}/{encoded_tag_line}"
        
        try:
            data = self._make_request(url)
            logger.info(f"Retrieved account data for {game_name}#{tag_line}")
            return data
        except RiotAPIError as e:
            logger.error(f"Failed to get account for {game_name}#{tag_line}: {e}")
            raise
    
    def get_account_by_puuid(self, puuid: str) -> Dict[str, Any]:
        """
        Get account information by PUUID.
        
        Args:
            puuid: Player's PUUID
        
        Returns:
            Account data
        """
        url = f"{self.base_urls['account']}/accounts/by-puuid/{puuid}"
        
        try:
            data = self._make_request(url)
            logger.info(f"Retrieved account data for PUUID: {puuid[:8]}...")
            return data
        except RiotAPIError as e:
            logger.error(f"Failed to get account for PUUID {puuid[:8]}...: {e}")
            raise
    
    def get_summoner_by_puuid(self, puuid: str) -> Dict[str, Any]:
        """
        Get summoner information by PUUID.
        
        Args:
            puuid: Player's PUUID
        
        Returns:
            Summoner data
        """
        url = f"{self.base_urls['summoner']}/summoners/by-puuid/{puuid}"
        
        try:
            data = self._make_request(url)
            logger.info(f"Retrieved summoner data for PUUID: {puuid[:8]}...")
            return data
        except RiotAPIError as e:
            logger.error(f"Failed to get summoner for PUUID {puuid[:8]}...: {e}")
            raise
    
    def get_league_entries(self, summoner_id: str) -> List[Dict[str, Any]]:
        """
        Get ranked league entries for a summoner.
        
        Args:
            summoner_id: Summoner ID
        
        Returns:
            List of league entries
        """
        url = f"{self.base_urls['league']}/entries/by-summoner/{summoner_id}"
        
        try:
            data = self._make_request(url)
            logger.info(f"Retrieved league entries for summoner: {summoner_id}")
            return data
        except RiotAPIError as e:
            logger.error(f"Failed to get league entries for {summoner_id}: {e}")
            raise
    
    def get_match_history(self, puuid: str, count: int = 20, start: int = 0) -> List[str]:
        """
        Get match history for a player.
        
        Args:
            puuid: Player's PUUID
            count: Number of matches to retrieve
            start: Starting index
        
        Returns:
            List of match IDs
        """
        url = f"{self.base_urls['match']}/matches/by-puuid/{puuid}/ids"
        params = {"count": count, "start": start}
        
        try:
            data = self._make_request(url, params)
            logger.info(f"Retrieved {len(data)} match IDs for PUUID: {puuid[:8]}...")
            return data
        except RiotAPIError as e:
            logger.error(f"Failed to get match history for PUUID {puuid[:8]}...: {e}")
            raise
    
    def get_match_details(self, match_id: str) -> Dict[str, Any]:
        """
        Get detailed match information.
        
        Args:
            match_id: Match ID
        
        Returns:
            Match details
        """
        url = f"{self.base_urls['match']}/matches/{match_id}"
        
        try:
            data = self._make_request(url)
            logger.info(f"Retrieved match details for: {match_id}")
            return data
        except RiotAPIError as e:
            logger.error(f"Failed to get match details for {match_id}: {e}")
            raise
    
    def batch_get_accounts(self, player_list: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
        """
        Get account information for multiple players.
        
        Args:
            player_list: List of dicts with 'game_name' and 'tag_line' keys
        
        Returns:
            Dictionary mapping display names to account data
        """
        results = {}
        
        for player in player_list:
            game_name = player["game_name"]
            tag_line = player["tag_line"]
            display_name = f"{game_name}#{tag_line}"
            
            try:
                account_data = self.get_account_by_riot_id(game_name, tag_line)
                results[display_name] = account_data
                logger.info(f"Successfully retrieved data for {display_name}")
            except RiotAPIError as e:
                logger.warning(f"Failed to retrieve data for {display_name}: {e}")
                results[display_name] = None
            
            # Small delay between requests
            time.sleep(0.1)
        
        return results