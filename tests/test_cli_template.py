"""Tests for envdiff.cli_template."""
import argparse
import os
from pathlib import Path

import pytest

from envdiff.cli_template import build_template_subparser, cmd_template


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(
        from_file=None,
        from_keys=None,
        no_redact=False,
        placeholder="",
        output="-",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# build_template_subparser
# ---------------------------------------------------------------------------

def test_subparser_registers_template_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_template_subparser(sub)
    args = parser.parse_args(["template", "--from-keys", "FOO", "BAR"])
    assert args.from_keys == ["FOO", "BAR"]


# ---------------------------------------------------------------------------
# cmd_template — from-keys
# ---------------------------------------------------------------------------

class TestCmdTemplateFromKeys:
    def test_outputs_keys_to_stdout(self, capsys):
        args = _make_args(from_keys=["HOST", "PORT"])
        rc = cmd_template(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "HOST=" in out
        assert "PORT=" in out

    def test_custom_placeholder_in_output(self, capsys):
        args = _make_args(from_keys=["DB_URL"], placeholder="<required>")
        cmd_template(args)
        out = capsys.readouterr().out
        assert "DB_URL=<required>" in out

    def test_writes_to_file(self, tmp_path):
        out_file = tmp_path / "out.env"
        args = _make_args(from_keys=["FOO"], output=str(out_file))
        rc = cmd_template(args)
        assert rc == 0
        assert "FOO=" in out_file.read_text()


# ---------------------------------------------------------------------------
# cmd_template — from-file
# ---------------------------------------------------------------------------

class TestCmdTemplateFromFile:
    def test_reads_file_and_outputs_template(self, tmp_path, capsys):
        env_file = tmp_path / ".env"
        env_file.write_text("APP_NAME=myapp\nDB_PASSWORD=secret\n")
        args = _make_args(from_file=str(env_file))
        rc = cmd_template(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "APP_NAME=myapp" in out
        # sensitive value should be redacted
        assert "DB_PASSWORD=" in out
        assert "secret" not in out

    def test_no_redact_flag_preserves_values(self, tmp_path, capsys):
        env_file = tmp_path / ".env"
        env_file.write_text("API_TOKEN=tok123\n")
        args = _make_args(from_file=str(env_file), no_redact=True)
        cmd_template(args)
        out = capsys.readouterr().out
        assert "API_TOKEN=tok123" in out

    def test_missing_file_returns_error(self, capsys):
        args = _make_args(from_file="/nonexistent/.env")
        rc = cmd_template(args)
        assert rc == 1
        assert "error" in capsys.readouterr().err

    def test_bad_output_path_returns_error(self, tmp_path, capsys):
        env_file = tmp_path / ".env"
        env_file.write_text("X=1\n")
        args = _make_args(from_file=str(env_file), output="/no/such/dir/out.env")
        rc = cmd_template(args)
        assert rc == 1
