from typer.testing import CliRunner

from fossilscope.cli_all import BRAND, app
from sric.cli_style import build_banner


def test_fossilscope_brand_identity() -> None:
    banner = build_banner(BRAND)
    assert "FossilScope" in banner
    assert "historical attack surface" in banner
    assert "IsdarlinM :: v0.5.2" in banner


def test_root_help_documents_no_color() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--no-color" in result.stdout
