from typer.testing import CliRunner
from fossilscope.cli import app


def test_collect_is_passive() -> None:
    res = CliRunner().invoke(app, ["collect"])
    assert res.exit_code == 0
    assert "no unbounded active crawling" in res.stdout
