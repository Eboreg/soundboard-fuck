import time
import wave
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Callable
from uuid import uuid4

import pyaudio
from pydub import AudioSegment

from soundboard_fuck.player.abstractplayer import AbstractPlayer


if TYPE_CHECKING:
    from soundboard_fuck.data.sound import Sound
    from soundboard_fuck.player.playerprogress import PlayerProgress


class WavPlayer(AbstractPlayer):
    stream: pyaudio.Stream | None = None

    def __init__(
        self,
        sound: "Sound",
        p: pyaudio.PyAudio,
        on_stop: "Callable[[WavPlayer], Any]",
        on_progress: "Callable[[PlayerProgress], Any]",
    ):
        self.sound = sound
        self.p = p
        self.id = uuid4()
        self.on_stop = on_stop
        self.is_playing = False
        self.on_progress = on_progress
        self.progress = 0.0
        self.created = time.time()

    def _play(self, path: str):
        self.is_playing = True

        with wave.open(path, "rb") as wf:
            assert isinstance(wf, wave.Wave_read)

            # pylint: disable=unused-argument
            def callback(_, frame_count: int, *args, **kwargs):
                data = wf.readframes(frame_count)
                return (data, pyaudio.paContinue)

            frame_rate = wf.getframerate()
            frame_count = wf.getnframes()
            duration_seconds = frame_rate and frame_count / frame_rate or 0.0
            start_time: float | None = None

            stream = self.p.open(
                format=self.p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=frame_rate,
                output=True,
                stream_callback=callback,
                frames_per_buffer=500,
            )
            self.stream = stream

            while stream.is_active():
                stream_time = stream.get_time()
                if start_time is None:
                    start_time = stream_time
                if duration_seconds:
                    self._on_progress((stream_time - start_time) / duration_seconds)
                time.sleep(0.1)

            self._on_progress(1.0)
            stream.close()
            self.on_stop(self)
            self.is_playing = False

    def play(self):
        if self.sound.format != "wav":
            segment: AudioSegment = AudioSegment.from_file(file=self.sound.path, format=self.sound.format)
            with NamedTemporaryFile("w+b", suffix=".wav") as f:
                segment.export(f.name, "wav")
                self._play(f.name)
        else:
            self._play(str(self.sound.path))

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
