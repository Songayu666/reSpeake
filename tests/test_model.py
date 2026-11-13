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

