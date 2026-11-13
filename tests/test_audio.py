from array import array

from respeake.audio import extract_channel, rms_level


def test_extracts_first_channel_from_six_channel_pcm() -> None:
    interleaved = array("h", [100, 1, 2, 3, 4, 5, -200, 6, 7, 8, 9, 10]).tobytes()
    output = array("h")
    output.frombytes(extract_channel(interleaved))
    assert output.tolist() == [100, -200]


def test_rms_level_is_bounded() -> None:
    silence = array("h", [0] * 320).tobytes()
    loud = array("h", [32767] * 320).tobytes()
    assert rms_level(silence)[0] == 0.0
    assert rms_level(loud)[0] == 1.0
