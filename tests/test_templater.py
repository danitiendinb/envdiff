"""Tests for envdiff.templater."""
import pytest

from envdiff.templater import (
    EnvTemplate,
    TemplateEntry,
    build_template,
    render_template,
    template_from_keys,
)


# ---------------------------------------------------------------------------
# build_template
# ---------------------------------------------------------------------------

class TestBuildTemplate:
    def test_keys_are_sorted(self):
        env = {"ZEBRA": "z", "ALPHA": "a"}
        tmpl = build_template(env)
        assert [e.key for e in tmpl.entries] == ["ALPHA", "ZEBRA"]

    def test_plain_value_preserved(self):
        tmpl = build_template({"HOST": "localhost"})
        assert tmpl.entries[0].default == "localhost"

    def test_sensitive_key_redacted_by_default(self):
        tmpl = build_template({"DB_PASSWORD": "secret"})
        assert tmpl.entries[0].default == ""

    def test_sensitive_key_not_redacted_when_disabled(self):
        tmpl = build_template({"DB_PASSWORD": "secret"}, redact_sensitive=False)
        assert tmpl.entries[0].default == "secret"

    def test_custom_placeholder(self):
        tmpl = build_template({"API_TOKEN": "tok"}, placeholder="CHANGE_ME")
        assert tmpl.entries[0].default == "CHANGE_ME"

    def test_sensitive_comment_added(self):
        tmpl = build_template({"SECRET_KEY": "s"})
        assert tmpl.entries[0].comment is not None
        assert "sensitive" in tmpl.entries[0].comment

    def test_non_sensitive_no_comment(self):
        tmpl = build_template({"APP_NAME": "myapp"})
        assert tmpl.entries[0].comment is None

    def test_to_dict(self):
        env = {"A": "1", "B": "2"}
        tmpl = build_template(env, redact_sensitive=False)
        assert tmpl.to_dict() == {"A": "1", "B": "2"}


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

class TestRenderTemplate:
    def test_basic_render(self):
        tmpl = EnvTemplate(entries=[TemplateEntry(key="FOO", default="bar")])
        output = render_template(tmpl)
        assert "FOO=bar" in output

    def test_comment_rendered_before_key(self):
        tmpl = EnvTemplate(
            entries=[TemplateEntry(key="DB_PASS", default="", comment="sensitive")]
        )
        lines = render_template(tmpl).splitlines()
        assert lines[0] == "# sensitive"
        assert lines[1] == "DB_PASS="

    def test_empty_template_returns_empty_string(self):
        assert render_template(EnvTemplate()) == ""

    def test_trailing_newline(self):
        tmpl = EnvTemplate(entries=[TemplateEntry(key="X", default="1")])
        assert render_template(tmpl).endswith("\n")


# ---------------------------------------------------------------------------
# template_from_keys
# ---------------------------------------------------------------------------

class TestTemplateFromKeys:
    def test_all_keys_present(self):
        tmpl = template_from_keys(["B", "A", "C"])
        assert [e.key for e in tmpl.entries] == ["A", "B", "C"]

    def test_all_required(self):
        tmpl = template_from_keys(["HOST", "PORT"])
        assert all(e.required for e in tmpl.entries)

    def test_custom_placeholder(self):
        tmpl = template_from_keys(["FOO"], placeholder="<fill>")
        assert tmpl.entries[0].default == "<fill>"

    def test_empty_list(self):
        tmpl = template_from_keys([])
        assert tmpl.entries == []
