#!/bin/bash
# Install vfinx-trend for this user: commands, systemd units, desktop icons. Starts in MANUAL mode.
set -eu
REPO="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.local/bin ~/.config/systemd/user
chmod +x "$REPO"/bin/*
for f in vfinx-trend vfinx-mode vfinx-run-now vfinx-notify; do ln -sfn "$REPO/bin/$f" ~/.local/bin/$f; done
cp "$REPO"/systemd/vfinx-report.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
# Icons go in the Desktop folder good-guy-daily with the other report shortcuts (run-folder-launcher runs them there)
DEST=~/Desktop/good-guy-daily; mkdir -p "$DEST"
for f in "$REPO"/desktop/*.desktop; do
    t="$DEST/$(basename "$f")"
    sed "s#/home/user#$HOME#g" "$f" > "$t"
    chmod +x "$t"
    rm -f ~/Desktop/"$(basename "$f")"          # an older loose copy from before the folder
    icon=$(grep -m1 '^Icon=' "$t" | cut -d= -f2-)
    if [[ $icon == /* ]]; then gio set "$t" metadata::custom-icon "file://$icon" 2>/dev/null || true
    else gio set "$t" metadata::custom-icon-name "$icon" 2>/dev/null || true; fi
    gio set "$t" metadata::trusted true 2>/dev/null || true
done
[ -f ~/.config/vfinx-trend/run-mode ] || { mkdir -p ~/.config/vfinx-trend; echo manual > ~/.config/vfinx-trend/run-mode; }
echo "Installed. Mode: $(cat ~/.config/vfinx-trend/run-mode). Switch with: vfinx-mode nightly | manual"
