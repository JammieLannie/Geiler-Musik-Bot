"""
Genius
"""
import re
import traceback
import urllib.parse
from typing import Tuple
from html import unescape

import aiohttp
import async_timeout

import logging_manager
from bot.type.errors import Errors
from bot.type.exceptions import BasicError, NoResultsFound

# pulled from my project ArtistWordRanker:
# https://github.com/tooxo/ArtistWordRanker


class Genius:
    """
    Genius
    """

    PATTERN_RAW = re.compile(r"<div class=\"lyrics\">(.*)<!--/sse-->", re.S)
    PATTERN_RAW_2 = re.compile(
        r'<div class="Lyrics__Container-sc-1ynbvzw-2 \S+">(.*)</div>', re.S
    )
    PATTERN = re.compile(r"<[^>]*>", re.S)
    TITLE_PATTERN = re.compile(
        r"<h1[^>]*header_with_cover_art-primary_info-title[^>]*>(.+)</h1>", re.S
    )
    TITLE_PATTERN_2 = re.compile(
        r'<h1 class="SongHeader__Title-sc-1b7aqpg-7 \S+">([^<]+)</h1>', re.S
    )
    ARTIST_PATTERN = re.compile(
        r"<a[^>]*header_with_cover_art-primary_info-primary_artist"
        r"[^>]*>([^<]*)</a>",
        re.S,
    )
    ARTIST_PATTERN_2 = re.compile(
        r'<a[^>]+class="Link-h3isu4-0 dpVWpH '
        r'SongHeader__Artist-sc-1b7aqpg-8 \S+"[^>]+>([^<]+)</a>',
        re.S,
    )

    @staticmethod
    async def search_genius(track_name: str, artist: str):
        """
        Search Genius
        @param track_name:
        @param artist:
        @return:
        """
        base_url = "https://genius.com/api/search/multi?q="
        url = base_url + urllib.parse.quote(
            re.sub(r"\(.+\)", string=track_name, repl="")
            + " "
            + re.sub(r"\(.+\)", string=artist, repl="")
        )
        async with async_timeout.timeout(timeout=8):
            async with aiohttp.request("GET", url=url) as resp:
                if resp.status not in (200, 301, 302):
                    raise BasicError(Errors.default)
                response = await resp.json()
                try:
                    for cat in response["response"]["sections"]:
                        for item in cat["hits"]:
                            if item["index"] != "song":
                                continue
                            if item["result"]["url"].endswith("lyrics"):
                                return item["result"]["url"]
                except (IndexError, ValueError, TypeError):
                    traceback.print_exc()
                    raise NoResultsFound(Errors.no_results_found)
                raise NoResultsFound(Errors.no_results_found)

    @staticmethod
    async def extract_from_genius(url: str) -> Tuple[str, str]:
        """
        Extract lyrics from genius
        @param url:
        @return:
        """
        async with async_timeout.timeout(timeout=8):
            async with aiohttp.request("GET", url=url) as resp:
                if resp.status not in (200, 301, 302):
                    logging_manager.LoggingManager().info(
                        "Genius search failed with: " + url
                    )
                    resp.close()
                    raise BasicError(Errors.default)
                text = (await resp.read()).decode("UTF-8")
                if "LyricsPlaceholder__Message" in text:
                    parsed_lyrics = "This song is an instrumental"
                else:
                    matcher = Genius.PATTERN_RAW.search(text)
                    if not matcher:
                        matcher = Genius.PATTERN_RAW_2.search(text)
                    raw_lyrics = matcher.group(1)
                    parsed_lyrics = Genius.PATTERN.sub("", raw_lyrics)
                artist_matcher = Genius.ARTIST_PATTERN.search(text)
                if not artist_matcher:
                    artist_matcher = Genius.ARTIST_PATTERN_2.search(text)
                artist = artist_matcher.group(1)
                title_matcher = Genius.TITLE_PATTERN.search(text)
                if not title_matcher:
                    title_matcher = Genius.TITLE_PATTERN_2.search(text)
                title = title_matcher.group(1)
            return (
                LyricsCleanup.clean_up(lyrics=parsed_lyrics),
                artist + " - " + title,
            )


class LyricsCleanup:
    """
    LyricsCleanup
    """

    @staticmethod
    def remove_html_tags(lyrics: str):
        """
        This removes any other html tags from the lyrics
        (the regex was stolen from here: https://www.regextester.com/93515)
        :param lyrics: input lyrics
        :return: filtered lyrics
        """
        html_tag_regex = r"<[^>]*>"
        return re.sub(pattern=html_tag_regex, string=lyrics, repl="")

    @staticmethod
    def remove_double_spaces(lyrics: str) -> str:
        """
        Remove double spaces from the lyrics
        @param lyrics:
        @return:
        """
        while "  " in lyrics:
            lyrics = lyrics.replace("  ", " ")
        return lyrics

    @staticmethod
    def remove_start_and_end_spaces(lyrics: str) -> str:
        """
        Remove spaces at the start and the end of the lyrics
        @param lyrics:
        @return:
        """
        start_of_line = r"^[ ]+"
        end_of_line = r"[ ]+$"
        lyrics = re.sub(
            pattern=start_of_line, string=lyrics, repl="", flags=re.M
        )
        lyrics = re.sub(pattern=end_of_line, string=lyrics, repl="", flags=re.M)
        return lyrics

    @staticmethod
    def clean_up(lyrics: str) -> str:
        """
        runs all of them
        :param lyrics:
        :return:
        """
        return unescape(
            LyricsCleanup.remove_start_and_end_spaces(
                LyricsCleanup.remove_double_spaces(
                    LyricsCleanup.remove_html_tags(lyrics=lyrics)
                )
            )
        )
