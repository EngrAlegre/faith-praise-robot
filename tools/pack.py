import os, zipfile

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
zip_path = os.path.join(root, "Five_Sides_STL_pack.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for base in ("cad", "stl", "plates", "renders", "firmware"):
        for dirpath, _, files in os.walk(os.path.join(root, base)):
            for f in sorted(files):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                z.write(full, rel)
    for extra in ("README.md", "MATERIALS.md", "BUILD.md", "Five_Sides_Build_Club_v2.pptx",
                  "renders_deck/wiring_screen.png", "renders_deck/wiring_sound.png",
                  "renders_deck/flow.png", "renders_deck/parts.png", "renders_deck/exploded.png",
                  "renders_deck/plates.png"):
        z.write(os.path.join(root, extra), extra)

names = zipfile.ZipFile(zip_path).namelist()
print(f"{len(names)} files, {os.path.getsize(zip_path)/1024:.0f} kB")
for n in names:
    print("  ", n)
