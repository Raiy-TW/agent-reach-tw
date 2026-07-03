# -*- coding: utf-8 -*-
"""Tests for Taiwan Edition setup documentation."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TAIWAN_DOCS = [
    "README.md",
    "docs/README_zh-TW.md",
    "docs/server-agent-install.md",
    "docs/IMPLEMENTATION_PLAN_TW.md",
    "docs/SPEC_TW.md",
    "agent_reach/guides/setup-taiwan.md",
    "agent_reach/skill/SKILL.md",
    "agent_reach/skill/SKILL_en.md",
]
PRIVATE_IDENTIFIERS = [
    "oci-raiy",
    "Raiy",
    "raiy",
    "Maigo",
    "40_Maigo",
    "/Volumes/",
    "/Users/rayyang",
    "Hermes",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_server_install_guide_documents_generic_agent_install_path():
    doc = _read("docs/server-agent-install.md")

    required_phrases = [
        "Server Agent 安裝指南",
        "通用 CLI + Python package",
        "Claude Code",
        "Codex",
        "任何 agent runtime",
        "agent-reach install --env=server --channels=tw --dry-run",
        "agent-reach doctor --json",
        "不需要桌面瀏覽器",
        "不要把特定私有部署名稱寫進公開文件",
    ]

    for phrase in required_phrases:
        assert phrase in doc


def test_taiwan_setup_guide_is_traditional_chinese_and_server_first():
    doc = _read("agent_reach/guides/setup-taiwan.md")

    required_phrases = [
        "# Taiwan Edition 安裝指南",
        "Server / OCI 環境",
        "pipx",
        "venv",
        "agent-reach install --env=server --channels=tw --dry-run",
        "Claude Code",
        "Codex",
        "generic agent runtime",
        "桌面瀏覽器登入態不是必要條件",
    ]

    for phrase in required_phrases:
        assert phrase in doc


def test_readme_links_to_server_guide_and_marks_desktop_channels_optional():
    doc = _read("docs/README_zh-TW.md")

    assert "docs/server-agent-install.md" in doc
    assert "桌面 Chrome session 的平台應標記為 optional" in doc


def test_root_readme_is_taiwan_edition_entrypoint():
    doc = _read("README.md")

    required_phrases = [
        "Agent Reach Taiwan Edition",
        "台灣平台能力層",
        "通用 CLI + Python package",
        "Claude Code",
        "Codex",
        "任何 agent runtime",
        "agent-reach install --env=server --channels=tw --dry-run",
        "docs/README_zh-TW.md",
        "上游專案",
    ]

    for phrase in required_phrases:
        assert phrase in doc


def test_taiwan_skill_installs_under_distinct_skill_name():
    skill = _read("agent_reach/skill/SKILL.md")
    english_skill = _read("agent_reach/skill/SKILL_en.md")
    cli = _read("agent_reach/cli.py")
    readme = _read("README.md")

    assert "name: agent-reach-tw" in skill
    assert "name: agent-reach-tw" in english_skill
    assert '_SKILL_INSTALL_NAME = "agent-reach-tw"' in cli
    assert 'f"~/.agents/skills/{_SKILL_INSTALL_NAME}"' in cli
    assert "~/.agents/skills/agent-reach-tw" in readme


def test_public_taiwan_docs_do_not_expose_private_deployment_identifiers():
    for path in PUBLIC_TAIWAN_DOCS:
        doc = _read(path)
        for private_identifier in PRIVATE_IDENTIFIERS:
            assert private_identifier not in doc, f"{path} leaks {private_identifier}"
