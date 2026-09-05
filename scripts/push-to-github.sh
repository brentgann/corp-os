#!/usr/bin/env bash
# Create github.com/brentgann/corp-os and push this repository to it.
#
# Run this from your own machine -- the sandbox that built this repo has no
# network access to GitHub, so the commit exists locally but has no remote yet.
#
#   ./scripts/push-to-github.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

REPO="${REPO:-brentgann/corp-os}"
DESC="A portable, configurable personal work OS, as a Claude plugin."

if git remote get-url origin >/dev/null 2>&1; then
  echo "origin already set: $(git remote get-url origin)"
else
  if command -v gh >/dev/null 2>&1; then
    echo "Creating $REPO via gh..."
    gh repo create "$REPO" --private --source=. --remote=origin --description "$DESC"
  else
    cat <<MSG

The GitHub CLI (gh) is not installed, so create the repository by hand:

  1. Open https://github.com/new
  2. Name it: ${REPO#*/}
  3. Do NOT add a README, .gitignore, or license -- this repo already has them.
  4. Then run:

     git remote add origin git@github.com:$REPO.git
     ./scripts/push-to-github.sh

MSG
    exit 1
  fi
fi

git push -u origin "$(git branch --show-current)"
echo
echo "Pushed. https://github.com/$REPO"
