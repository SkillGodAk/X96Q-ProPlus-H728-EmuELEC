#!/bin/sh
# H728 quit-event boot target dispatcher.
# Generic system reboot emits: quit reboot.
# Before systemctl reboot runs, restore SD BootROM magic for one-shot EmuELEC.
set -eu

[ "${1:-}" = "quit" ] || exit 0
[ "${2:-}" = "reboot" ] || exit 0

if command -v reboottoemuelec >/dev/null 2>&1; then
  exec reboottoemuelec
fi

HELPER=/storage/.h728-bin/reboottoemuelec
[ -x "$HELPER" ] || exit 0
exec "$HELPER"
