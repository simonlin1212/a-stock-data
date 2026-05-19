#!/usr/bin/env bash
# Install a-stock-data Claude Skill to ~/.claude/skills/a-stock-data/
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/install.sh | bash
#
# Override defaults via env vars:
#   INSTALL_DIR=/custom/path/to/skill BRANCH=dev curl -fsSL ... | bash

set -euo pipefail

REPO="simonlin1212/a-stock-data"
BRANCH="${BRANCH:-main}"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
INSTALL_DIR="${INSTALL_DIR:-${HOME}/.claude/skills/a-stock-data}"

# Skill 内容清单 — 新增/重命名 reference 时改这里即可
FILES=(
  "SKILL.md"
  "references/01-quotes.md"
  "references/02-research.md"
  "references/03-signals.md"
  "references/04-capital.md"
  "references/05-news.md"
  "references/06-fundamentals.md"
  "references/07-filings.md"
  "references/workflows.md"
  "references/faq.md"
)

echo "Installing a-stock-data skill -> ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}/references"

for f in "${FILES[@]}"; do
  echo "  - ${f}"
  curl -fsSL "${BASE_URL}/${f}" -o "${INSTALL_DIR}/${f}"
done

echo ""
echo "Installed ${#FILES[@]} files."
echo ""
echo "Next:"
echo "  pip install mootdx requests pandas stockstats"
echo ""
echo "Launch Claude Code and ask: \"帮我看看 688017 的估值\""
