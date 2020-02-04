from bot.type.variable_store import strip_youtube_title

from .error import Error


class Song:
    def __init__(
        self,
        song=None,
        title=None,
        term=None,
        id=None,
        link=None,
        stream=None,
        duration=None,
        loadtime=None,
        thumbnail=None,
        error=Error(False),
        user=None,
        image_url=None,
        abr=None,
        codec=None,
        song_name=None,
        artist=None,
    ):
        if song:
            self.title = song.title
            self.term = song.term
            self.id = song.id
            self.link = song.link
            self.stream = song.stream
            self.duration = song.duration
            self.loadtime = song.loadtime
            self.error = song.error
            self.user = song.user
            self.image_url = song.image_url
            self.abr = song.abr
            self.codec = song.codec

            self.song_name = song.song_name
            self.artist = song.artist
        else:
            self.title = title
            self.term = term
            self.id = id
            self.link = link
            self.stream = stream
            self.duration = duration
            self.loadtime = loadtime
            self.thumbnail = thumbnail
            self.error = error
            self.user = user
            self.image_url = image_url
            self.abr = abr
            self.codec = codec

            self.song_name = song_name
            self.artist = artist

    @property
    def image(self):
        if self.image_url is not None and self.image_url != "":
            return self.image_url
        if self.thumbnail is not None and self.thumbnail != "":
            return self.thumbnail
        return None

    @staticmethod
    def from_dict(d: dict):
        song = Song()
        song.title = strip_youtube_title(d["title"])
        song.term = d["term"]
        song.id = d["id"]
        song.link = d["link"]
        song.stream = d["stream"]
        song.duration = d["duration"]
        song.loadtime = d["loadtime"]
        song.thumbnail = d["thumbnail"]
        song.codec = d["codec"]
        song.abr = d.get("abr", 0)
        return song

    @staticmethod
    def copy_song(_from, _to):
        _from: Song
        _to: Song
        for attribute in _from.__dict__.keys():
            if hasattr(_from, attribute) and attribute != "image_url":
                if getattr(_from, attribute) is not None:
                    setattr(_to, attribute, getattr(_from, attribute))
        return _to

    def to_string(self):
        return self.__dict__
