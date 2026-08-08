from __future__ import annotations

import wave

import lameenc


def wav_to_mp3(wav_path, mp3_path, bitrate: int = 192) -> None:
    with wave.open(str(wav_path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        pcm_data = wav_file.readframes(wav_file.getnframes())

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(channels)
    encoder.set_quality(2)

    mp3_data = encoder.encode(pcm_data) + encoder.flush()

    with open(mp3_path, "wb") as mp3_file:
        mp3_file.write(mp3_data)
