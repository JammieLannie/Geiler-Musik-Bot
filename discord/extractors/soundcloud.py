import json

import aiohttp
import async_timeout

import logging_manager
from bot.type.error import Error
from bot.type.song import Song


class SoundCloud:
    def __init__(self):
        self.log = logging_manager.LoggingManager()
        self.log.debug("[Startup]: Initializing SoundCloud Module . . .")
        self.client = aiohttp.ClientSession()

    async def soundcloud_track(self, url: str):
        try:
            async with async_timeout.timeout(timeout=10):
                async with self.client.post(
                    "http://parent:8008/research/soundcloud_track", data=url
                ) as r:
                    if r.status != 200:
                        return Error(True)
                    response: dict = await r.json()
                    song: Song = Song(
                        title=response.get("title", None),
                        link=response.get("link", ""),
                        stream=response.get("stream", None),
                        duration=response.get("duration", 0),
                        thumbnail=response.get("thumbnail", ""),
                        loadtime=response.get("loadtime", 0),
                        abr=response.get("abr", None),
                        term=response.get("term", ""),
                        codec=response.get("codec", ""),
                    )
                    if song.duration == 0:
                        # try to determine the songs length by content length
                        if song.abr:
                            abr = song.abr * 1000 / 8
                            async with aiohttp.request(
                                "HEAD", song.stream
                            ) as _r:
                                cl = _r.headers.get("Content-Length", "")
                            try:
                                song.duration = int(cl) / abr
                            except ValueError:
                                pass
                    return song
        except (TimeoutError, AttributeError) as e:
            self.log.error(e)
            return Error(True)

    async def soundcloud_playlist(self, url: str):
        try:
            async with async_timeout.timeout(timeout=10):
                async with aiohttp.request(
                    "POST",
                    "http://parent:8008/research/soundcloud_playlist",
                    data=url,
                ) as r:
                    response = await r.text()
                    if r.status != 200:
                        return Error(True, response)
                    parsed_response = json.loads(response)
                    songs = []
                    for s in parsed_response:
                        song: Song = Song()
                        song.link = s.get("link", None)
                        if song.link:
                            songs.append(song)
                    return songs
        except (TimeoutError, AttributeError) as e:
            self.log.error(e)
            return Error(True)
