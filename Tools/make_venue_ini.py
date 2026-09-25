"""Build the kiosk dev-loop GALE01r2.ini: Slippi's stock ini with ONLY the
recording codes enabled (no General Codes / Slippi Online netplay behaviour),
plus the venue's Nintendont codesets converted verbatim from kernel/gecko/*.bin
so Dolphin runs what the venue Wiis run."""
import struct, subprocess, os

ISH = r"P:\Projects\Ishiiruka"
GECKO = r"P:\Projects\Nintendont\kernel\gecko"
UPSTREAM = "e7711b104"

VENUE = [  # (ini title, bin, enabled)
    ("Venue: UCF 0.84 [Nintendont MeleeCodes cfOptionUcf084]", "g_ucf_084.bin", True),
    ("Venue: Tournament Mods [Nintendont MeleeCodes modsOptionTournament]", "g_mods_tournament.bin", True),
    ("Venue: Frozen Pokemon Stadium [Nintendont MeleeCodes stagesOptionStadium]", "g_stages_stadium.bin", False),
]

def bin_to_lines(path):
    b = open(path, "rb").read()
    out = []
    for i in range(0, len(b) - len(b) % 8, 8):
        a, v = struct.unpack(">II", b[i:i + 8])
        out.append(f"{a:08X} {v:08X}")
    return out

ini = subprocess.run(["git", "-C", ISH, "show", f"{UPSTREAM}:Data/Sys/GameSettings/GALE01r2.ini"],
                     capture_output=True, text=True).stdout
lines = ini.splitlines()
# rewrite [Gecko_Enabled]
out = []
i = 0
while i < len(lines):
    if lines[i].strip() == "[Gecko_Enabled]":
        out.append("[Gecko_Enabled]")
        out.append("$Required: Slippi Recording")
        for title, _, enabled in VENUE:
            if enabled:
                # [Gecko_Enabled] holds the NAME only; the [creator] bracket is
                # part of the [Gecko] definition line, not the name.
                out.append("$" + title.split(" [")[0])
        i += 1
        while i < len(lines) and lines[i].startswith("$"):
            i += 1
        continue
    out.append(lines[i])
    i += 1
# venue codes appended to [Gecko]
out.append("")
out.append("# --- Tournament kiosk: the venue's Nintendont codesets, byte for byte")
out.append("# --- (tournament-reporter design.md, vanilla-ISO architecture). Regenerate")
out.append("# --- with tools/make_venue_ini.py; do not hand-edit the code lines.")
for title, name, _ in VENUE:
    out.append("$" + title)
    out.extend(bin_to_lines(os.path.join(GECKO, name)))
text = "\n".join(out) + "\n"
for dst in [os.path.join(ISH, "Data", "Sys", "GameSettings", "GALE01r2.ini"),
            os.path.join(ISH, "Binary", "x64", "Sys", "GameSettings", "GALE01r2.ini")]:
    open(dst, "w", encoding="utf-8", newline="\n").write(text)
    print("wrote", dst)
en = [l for l in out[out.index("[Gecko_Enabled]") + 1:] if l.startswith("$")]
print("enabled:", en[:4])
