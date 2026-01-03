import os
import json
import ast
from collections import defaultdict

PROJECT_ROOT = "."
PY_FILES = []

# ---------------------------------
# Discover Python files
# ---------------------------------
for root, _, files in os.walk(PROJECT_ROOT):
    for f in files:
        if f.endswith(".py") and "__pycache__" not in root:
            PY_FILES.append(os.path.join(root, f))

# ---------------------------------
# Helpers
# ---------------------------------
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def infer_literal_type(node):
    if isinstance(node, ast.Dict):
        return "dict"
    if isinstance(node, ast.List):
        return "list"
    if isinstance(node, ast.Constant):
        return type(node.value).__name__
    return "unknown"


# ---------------------------------
# Deep Python Analysis
# ---------------------------------
def analyze_python_file(path):
    report = {
        "functions": {},
        "returns": defaultdict(set),
        "json_files_used": set(),
        "risks": []
    }

    try:
        tree = ast.parse(read_file(path))
    except Exception as e:
        report["risks"].append(f"Syntax error: {e}")
        return report

    for node in ast.walk(tree):

        # Function definitions
        if isinstance(node, ast.FunctionDef):
            report["functions"][node.name] = {
                "args": [a.arg for a in node.args.args],
                "returns": set()
            }

        # Return statements
        if isinstance(node, ast.Return):
            fn = next(
                (p.name for p in ast.walk(tree)
                 if isinstance(p, ast.FunctionDef) and node in ast.walk(p)),
                None
            )
            if fn:
                report["functions"][fn]["returns"].add(
                    infer_literal_type(node.value)
                )

        # json.load usage
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "load":
                    report["json_files_used"].add("json.load detected")

    # Heuristic risk detection
    for fn, meta in report["functions"].items():
        if "str" in meta["returns"] and "dict" in meta["returns"]:
            report["risks"].append(
                f"Function '{fn}' returns mixed types (str + dict)"
            )

    return report


# ---------------------------------
# JSON Inspection
# ---------------------------------
def inspect_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    info = {
        "type": type(data).__name__,
        "length": len(data) if isinstance(data, list) else None,
        "element_types": set()
    }

    if isinstance(data, list):
        for el in data[:5]:
            info["element_types"].add(type(el).__name__)

    return info


# ---------------------------------
# MAIN SCAN
# ---------------------------------
def scan():
    print("\n🔍 TRAVEL VALUE AGENT — INTELLIGENT SCAN\n")

    # 1️⃣ Python analysis
    print("🐍 CODE ANALYSIS:")
    for f in PY_FILES:
        print(f"\n▶ {f}")
        analysis = analyze_python_file(f)

        for fn, meta in analysis["functions"].items():
            print(f"  Function: {fn}")
            print(f"    Args: {meta['args']}")
            print(f"    Returns: {meta['returns'] or 'unknown'}")

        if analysis["risks"]:
            print("  🚨 Risks:")
            for r in analysis["risks"]:
                print("   -", r)

    # 2️⃣ JSON analysis
    print("\n🧾 JSON DATA ANALYSIS:")
    for root, _, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.endswith(".json"):
                path = os.path.join(root, f)
                try:
                    info = inspect_json(path)
                    print(f"\n▶ {path}")
                    print(json.dumps(info, indent=2))
                except Exception as e:
                    print(f"\n▶ {path}")
                    print("  ❌ Invalid JSON:", e)

    print("\n✅ Intelligent scan complete.")
    print("➡ Future code changes will be based on THIS output only.\n")


if __name__ == "__main__":
    scan()
