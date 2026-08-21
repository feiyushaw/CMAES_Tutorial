import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

NOTEBOOKS = [
    "0_black_box_optimization.ipynb",
    "1_evolution_strategy.ipynb",
    "2_step_size_adaptation.ipynb",
    "3_covariance_matrix_adaptation.ipynb",
    "4_nonseparability.ipynb",
    "5_multimodality.ipynb",
    "6_advanced_adaptation_mechanisms.ipynb",
    "a1_minmax_optimization.ipynb",
    "cmaes_acceleration.ipynb",
    "cmaes_practical_guide.ipynb",
]

JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")
# Protect material that machine translation must not rewrite.
PROTECTED_RE = re.compile(
    r"(\$\$.*?\$\$|\$[^\n$]+?\$|`[^`]+`|https?://[^\s)）>]+|\\begin\{.*?\\end\{[^}]+\})",
    re.S,
)

translator = GoogleTranslator(source="ja", target="zh-CN")
cache = {}


def protect(text):
    items = []
    def repl(m):
        token = f"ZXQPH{len(items)}QXZ"
        items.append(m.group(0))
        return token
    return PROTECTED_RE.sub(repl, text), items


def restore(text, items):
    for i, value in enumerate(items):
        text = text.replace(f"ZXQPH{i}QXZ", value)
        text = text.replace(f"ZXQPH {i} QXZ", value)
    return text


def translate_text(text):
    if not text.strip() or not JP_RE.search(text):
        return text
    if text in cache:
        return cache[text]
    safe, items = protect(text)
    # Google Translate has request-size limits; translate paragraph-sized chunks.
    chunks = re.split(r"(\n\s*\n)", safe)
    out = []
    for chunk in chunks:
        if not chunk.strip() or not JP_RE.search(chunk):
            out.append(chunk)
            continue
        try:
            translated = translator.translate(chunk)
            out.append(translated if translated else chunk)
            time.sleep(0.08)
        except Exception:
            # Retry once, then keep source so the verification step can flag it.
            time.sleep(1.0)
            try:
                translated = translator.translate(chunk)
                out.append(translated if translated else chunk)
            except Exception:
                out.append(chunk)
    result = restore("".join(out), items)
    cache[text] = result
    return result


def translate_code_line(line):
    # Translate Japanese comments/docstrings while leaving executable Python intact.
    if not JP_RE.search(line):
        return line
    if "#" in line:
        prefix, comment = line.split("#", 1)
        if JP_RE.search(comment):
            return prefix + "#" + translate_text(comment)
    # Japanese text inside docstring/string-only lines is instructional text.
    stripped = line.strip()
    if stripped.startswith(('"""', "'''")) or stripped.endswith(('"""', "'''")):
        indent = line[: len(line) - len(line.lstrip())]
        return indent + translate_text(line[len(indent):])
    # Common parameter-description lines inside multi-line docstrings.
    if not any(tok in line for tok in ["=", "(", ")", "[", "]", "return ", "def ", "class "]):
        indent = line[: len(line) - len(line.lstrip())]
        return indent + translate_text(line[len(indent):])
    return line


def process(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for cell in data.get("cells", []):
        src = cell.get("source", [])
        as_list = isinstance(src, list)
        text = "".join(src) if as_list else src
        if cell.get("cell_type") == "markdown":
            text = translate_text(text)
        elif cell.get("cell_type") == "code":
            text = "".join(translate_code_line(x) for x in text.splitlines(keepends=True))
        cell["source"] = text.splitlines(keepends=True) if as_list else text
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    for name in NOTEBOOKS:
        process(Path(name))
    remaining = []
    for name in NOTEBOOKS:
        data = json.loads(Path(name).read_text(encoding="utf-8"))
        for i, cell in enumerate(data.get("cells", [])):
            text = "".join(cell.get("source", [])) if isinstance(cell.get("source", []), list) else cell.get("source", "")
            if JP_RE.search(text):
                remaining.append(f"{name}: cell {i}")
    Path("translation_report.txt").write_text(
        "Remaining cells containing Japanese/CJK source after translation:\n" + "\n".join(remaining) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
