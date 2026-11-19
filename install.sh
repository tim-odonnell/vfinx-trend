#!/bin/bash
# Install vfinx-trend for this user: commands, systemd units, desktop icons. Starts in MANUAL mode.
set -eu
REPO="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.local/bin ~/.config/systemd/user ~/Desktop
chmod +x "$REPO"/bin/*
for f in vfinx-trend vfinx-mode vfinx-run-now vfinx-notify; do ln -sfn "$REPO/bin/$f" ~/.local/bin/$f; done
cp "$REPO"/systemd/vfinx-report.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
for f in "$REPO"/desktop/*.desktop; do
    sed "s#/home/user#$HOME#g" "$f" > ~/Desktop/"$(basename "$f")"
    chmod +x ~/Desktop/"$(basename "$f")"
    gio set ~/Desktop/"$(basename "$f")" metadata::trusted true 2>/dev/null || true
done
[ -f ~/.config/vfinx-trend/run-mode ] || { mkdir -p ~/.config/vfinx-trend; echo manual > ~/.config/vfinx-trend/run-mode; }
echo "Installed. Mode: $(cat ~/.config/vfinx-trend/run-mode). Switch with: vfinx-mode nightly | manual"
