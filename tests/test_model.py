from respeake.model import RadarState


def test_state_normalizes_values() -> None:
    state = RadarState()
    state.update(725, True, 1.5)
    snapshot = state.snapshot()
    assert snapshot["angle"] == 5
    assert snapshot["level"] == 1
    assert len(snapshot["history"]) == 1


def test_device_status() -> None:
    state = RadarState()
    state.set_device("respeaker", True)
    snapshot = state.snapshot()
    assert snapshot["source"] == "respeaker"
    assert snapshot["connected"] is True
    assert snapshot["error"] is None


def test_audio_and_recording_state() -> None:
    state = RadarState()
    state.update_level(0.42, -37.2)
    state.set_audio(True)
    state.set_recording(True)
    state.add_recording("voice.wav", 1.25, 40044)
    snapshot = state.snapshot()
    assert snapshot["level"] == 0.42
    assert snapshot["dbfs"] == -37.2
    assert snapshot["audio_connected"] is True
    assert snapshot["recording"] is True
    assert snapshot["recordings"][0]["filename"] == "voice.wav"

