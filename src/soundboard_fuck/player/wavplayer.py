from contextlib import redirect_stderr
import logging
import time
import wave
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, Callable
from uuid import uuid4

import pyaudio
from pydub import AudioSegment

from soundboard_fuck import log_handler
from soundboard_fuck.player.abstractplayer import AbstractPlayer


if TYPE_CHECKING:
    from soundboard_fuck.data.sound import Sound
    from soundboard_fuck.player.playerprogress import PlayerProgress


class WavPlayer(AbstractPlayer):
    stream: pyaudio.Stream | None = None
    stopsignal: bool = False

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

    def _play_2(self, path: str):
        self.is_playing = True
        # init_time = time.time()

        with wave.open(path, "rb") as wf:
            assert isinstance(wf, wave.Wave_read)

            frame_rate = wf.getframerate()
            frame_count = wf.getnframes()
            duration_seconds = frame_rate and frame_count / frame_rate or 0.0
            start_time: float | None = None
            sample_format = self.p.get_format_from_width(wf.getsampwidth())
            sample_size = self.p.get_sample_size(sample_format)
            channels = wf.getnchannels()

            # iteration = 0
            # latency = 0.0
            # last_time = 0.0
            stream_time = 0.0
            # chunk_time = 0.0
            chunk_size = int(frame_rate / 10)

            stream = self.p.open(
                format=sample_format,
                channels=channels,
                rate=frame_rate,
                output=True,
                frames_per_buffer=chunk_size,
            )
            self.stream = stream

            # Troligen ej meningsfullt m lägre readframes() än frams-per-buffer
            # Värden <= 1024: underruns
            # 2028 / 2048: 0.02119
            # 2048 / 4096: 0.02093
            # Goldilocks zone:
            # 4096 / 4096: 0.00630
            # 4096 / 8192: 0.01554
            # 8192 / 8192: 0.01753

            while not self.stopsignal and len(data := wf.readframes(chunk_size)):
                num_frames = int(len(data) / (channels * sample_size))
                stream.write(data, exception_on_underflow=False, num_frames=num_frames)
                stream_time = stream.get_time()
                if start_time is None:
                    start_time = stream_time
                    # latency = stream_time - init_time
                if duration_seconds:
                    progress = (stream_time - start_time) / duration_seconds
                    self._on_progress(progress)
                # chunk_time = max(chunk_time, num_frames / frame_rate)
                # print(
                #     f"{num_frames}, {len(data)}, {channels}, {sample_size}, {frame_rate}, {frame_count}, "
                #     f"{(1000 * (stream_time - last_time)):.2f}, {latency:.5f}, {chunk_time}"
                # )
                # last_time = stream_time
                # iteration += 1

            if progress and progress < 1.0:
                remains = duration_seconds * (1.0 - progress)
                for _ in range(int(remains / 0.1) + 1):
                    time.sleep(0.1)
                    progress += 0.1 / duration_seconds
                    self._on_progress(progress)

    def _play(self, path: str):
        self.is_playing = True

        with wave.open(path, "rb") as wf:
            assert isinstance(wf, wave.Wave_read)

            # pylint: disable=unused-argument
            def callback(_, frame_count: int, *args, **kwargs):
                with redirect_stderr(log_handler):
                    data = wf.readframes(frame_count)
                    # print(f"{time.time()}, {frame_count}, {len(data)}")
                    return (data, pyaudio.paContinue)

            frame_rate = wf.getframerate()
            frame_count = wf.getnframes()
            duration_seconds = frame_rate and frame_count / frame_rate or 0.0
            start_time: float | None = None
            chunk_size = int(frame_rate / 10)
            progress = 0.0

            stream = self.p.open(
                format=self.p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=frame_rate,
                output=True,
                stream_callback=callback,
                frames_per_buffer=chunk_size,
            )
            self.stream = stream

            while not self.stopsignal and stream.is_active():
                stream_time = stream.get_time()
                if start_time is None:
                    start_time = stream_time
                if duration_seconds:
                    progress = (stream_time - start_time) / duration_seconds
                    self._on_progress(progress)
                time.sleep(0.2)

            if not self.stopsignal and 0.0 > progress < 1.0:
                remains = duration_seconds * (1.0 - progress)
                # print(f"{remains}, {chunk_size}")
                time.sleep(remains)

    def play(self):
        with redirect_stderr(log_handler):
            try:
                if self.sound.format != "wav":
                    segment: AudioSegment = AudioSegment.from_file(file=self.sound.path, format=self.sound.format)
                    with NamedTemporaryFile("w+b", suffix=".wav") as f:
                        segment.export(f.name, "wav")
                        self._play_2(f.name)
                else:
                    self._play_2(str(self.sound.path))
            except Exception as e:
                logging.error(str(e), exc_info=e)
            finally:
                if self.stream:
                    self.stream.close()
                self._on_progress(1.0)
                self.on_stop(self)
                self.is_playing = False

    def stop(self):
        self.stopsignal = True
        # if self.stream:
        #     self.stream.stop_stream()
        #     self.stream.close()
