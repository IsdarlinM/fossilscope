from typer.testing import CliRunner

import fossilscope.cli_update as cli_update
from fossilscope import __version__
from fossilscope.cli_all import app
from sric.updater import UpdateCheck


def test_update_force_uses_official_channel_without_manifest_or_key(monkeypatch) -> None:
    seen: dict[str, object] = {}

    def fake_update(**kwargs):
        seen.update(kwargs)
        return UpdateCheck(
            current_version=__version__,
            available_version=__version__,
            update_available=False,
            same_version=True,
            forced=True,
            installed=True,
            product="fossilscope",
            artifact="official",
            channel="official-github-signed-commit",
        )

    monkeypatch.delenv("FOSSILSCOPE_RELEASE_MANIFEST_URL", raising=False)
    monkeypatch.delenv("FOSSILSCOPE_RELEASE_PUBLIC_KEY", raising=False)
    monkeypatch.setattr(cli_update, "perform_product_update", fake_update)

    result = CliRunner().invoke(app, ["update", "--force"])
    assert result.exit_code == 0, result.output
    assert seen["expected_product"] == "fossilscope"
    assert seen["force"] is True
    assert seen["manifest_source"] is None
    assert seen["public_key_path"] is None
