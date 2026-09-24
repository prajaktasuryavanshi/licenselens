import re

def parse_requirements(filepath):
    deps = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"^([A-Za-z0-9_.\-]+)\s*(==|>=|<=)?\s*([\w.\-]*)$", line)
            if match:
                deps.append({"name": match.group(1), "version": match.group(3) or "latest"})
    return deps
