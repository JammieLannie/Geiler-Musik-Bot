"""
SpotifyType
"""
import re
from typing import Optional

from bot.type.variable_store import VariableStore


class SpotifyType:
    """
    SpotifyType
    """

    SPOTIFY_URI = "SPOTIFY_URI"
    SPOTIFY_URL = "SPOTIFY_URL"

    def __init__(self, url) -> None:
        self.url = url

    @property
    def valid(self) -> bool:
        """
        Checks if the provided spotify url is valid.
        @return:
        """
        if re.match(VariableStore.spotify_url_pattern, self.url) is not None:
            return True
        if re.match(VariableStore.spotify_uri_pattern, self.url) is not None:
            return True
        return False

    @property
    def type(self) -> Optional[str]:
        """
        Returns the type of the provided spotify url
        @return:
        """
        if self.valid:
            if (
                re.match(VariableStore.spotify_url_pattern, self.url)
                is not None
            ):
                return self.SPOTIFY_URL
            if (
                re.match(VariableStore.spotify_uri_pattern, self.url)
                is not None
            ):
                return self.SPOTIFY_URI
        return None

    @property
    def id(self) -> Optional[str]:  # pylint: disable=invalid-name
        """
        Extract the id from the provided url
        @return:
        """
        if self.type is self.SPOTIFY_URL:
            return re.search(VariableStore.spotify_url_pattern, self.url).group(
                "id"
            )
        if self.type is self.SPOTIFY_URI:
            return re.search(VariableStore.spotify_uri_pattern, self.url).group(
                "id"
            )
        return None
