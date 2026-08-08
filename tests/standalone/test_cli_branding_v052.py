from typer.main import get_command

from fossilscope.cli_all import BRAND, app
from sric.cli_style import build_banner


def test_fossilscope_brand_identity() -> None:
    banner = build_banner(BRAND)
    product = banner.index("FossilScope :: v0.5.2")
    developer = banner.index("Developer: IsdarlinM")
    description = banner.index("historical attack surface")
    assert product < developer < description
    assert "IsdarlinM ::" not in banner


def test_no_color_option_is_registered() -> None:
    command = get_command(app)
    assert any("--no-color" in getattr(param, "opts", ()) for param in command.params)
