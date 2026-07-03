#!/bin/sh
# Installs the safe-push gate tools to ~/.local/bin.
# Usage:  git clone <this repo> && cd <repo> && ./install.sh
set -e

BIN="$HOME/.local/bin"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$BIN"

for tool in safe-push-init safe-push-final safe-push-team \
            safe-push-daemon safe-push-tui; do
    cp "$HERE/$tool" "$BIN/$tool"
    chmod +x "$BIN/$tool"
    echo "✓ installed $tool"
done

echo
command -v git >/dev/null 2>&1 || echo "⚠  git not found — required"
command -v python3 >/dev/null 2>&1 || echo "⚠  python3 not found — required (3.9+)"
if ! command -v claude >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/claude" ]; then
    echo "⚠  claude CLI not found — install it and log in:"
    echo "     curl -fsSL https://claude.ai/install.sh | bash"
    echo "     claude   (then complete the sign-in)"
fi
case ":$PATH:" in
    *":$BIN:"*) ;;
    *) echo "⚠  $BIN is not in your PATH. Add it:"
       echo "     echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc" ;;
esac

echo
echo "🛡  Installed. To arm a repository:"
echo "     cd your-repo"
echo "     safe-push-init"
echo "     \$EDITOR .safe-push.yaml    # set your test command"
