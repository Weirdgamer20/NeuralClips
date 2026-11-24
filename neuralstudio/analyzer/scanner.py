from pathlib import Path
import os
EXT = {
".py":"Python",".pyw":"Python",".js":"JavaScript",".jsx":"JavaScript",
".ts":"TypeScript",".tsx":"TypeScript",".java":"Java",".kt":"Kotlin",
".cpp":"C++",".cc":"C++",".cxx":"C++",".hpp":"C++",".h":"C/C++",
".c":"C",".cs":"C#",".go":"Go",".rs":"Rust",".rb":"Ruby",".php":"PHP",
".swift":"Swift",".scala":"Scala",".r":"R",".jl":"Julia",".m":"MATLAB/Objective-C",
".dart":"Dart",".lua":"Lua",".sh":"Shell",".sql":"SQL"
}
SKIP={".git",".hg",".svn",".venv","venv","env","__pycache__","node_modules",
"dist","build",".idea",".vscode",".pytest_cache","site-packages","target"}
def scan_project(root):
    base=Path(root).expanduser().resolve()
    if not base.is_dir(): raise NotADirectoryError(str(base))
    files=[]; counts={}; warnings=[]
    for current, dirs, names in os.walk(base):
        dirs[:]=[d for d in dirs if d not in SKIP]
        for name in names:
            p=Path(current)/name; lang=EXT.get(p.suffix.lower())
            if not lang: continue
            try:
                if p.stat().st_size>2_000_000:
                    warnings.append(f"Skipped oversized file: {p.relative_to(base)}"); continue
                txt=p.read_text(encoding="utf-8",errors="replace")
                files.append((p,lang,txt)); counts[lang]=counts.get(lang,0)+1
            except OSError as e: warnings.append(f"Could not read {p}: {e}")
    return files,counts,warnings
