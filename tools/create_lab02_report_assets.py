"""Generate verified terminal screenshots for the laboratory work 2 report."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "screenshots" / "lab02"
PYTHON = ROOT / ".venv" / "bin" / "python"
FONT_PATH = Path("/System/Library/Fonts/Menlo.ttc")


def run(*command: str) -> str:
    """Run a verified project command and return combined output."""

    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return (completed.stdout + completed.stderr).strip()


def wrap_terminal_lines(text: str, width: int = 104) -> list[str]:
    """Wrap long terminal lines without splitting words."""

    lines: list[str] = []
    for raw_line in text.expandtabs(4).splitlines():
        if not raw_line:
            lines.append("")
            continue
        lines.extend(
            textwrap.wrap(
                raw_line,
                width=width,
                replace_whitespace=False,
                drop_whitespace=False,
                break_long_words=False,
                break_on_hyphens=False,
            )
            or [""]
        )
    return lines


def render_terminal(title: str, text: str, path: Path) -> None:
    """Render deterministic terminal output as a PNG figure."""

    font = ImageFont.truetype(str(FONT_PATH), 20)
    title_font = ImageFont.truetype(str(FONT_PATH), 19)
    lines = wrap_terminal_lines(text)
    line_height = 30
    width = 1840
    height = 76 + max(1, len(lines)) * line_height + 28

    image = Image.new("RGB", (width, height), "#15181E")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), 18, fill="#15181E")
    draw.rectangle((0, 0, width, 58), fill="#252A33")
    draw.ellipse((22, 19, 42, 39), fill="#FF5F57")
    draw.ellipse((54, 19, 74, 39), fill="#FEBC2E")
    draw.ellipse((86, 19, 106, 39), fill="#28C840")
    draw.text((132, 16), title, font=title_font, fill="#D8DEE9")

    y = 75
    for line in lines:
        color = "#E5E9F0"
        if line.startswith("$"):
            color = "#88C0D0"
        elif "passed" in line or "99.80%" in line:
            color = "#A3BE8C"
        draw.text((30, y), line, font=font, fill=color)
        y += line_height

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def main() -> None:
    """Generate application, benchmark, and test figures."""

    application_output = run(
        str(PYTHON),
        "-m",
        "student_grading",
        "--threshold",
        "80",
    )
    application_lines = application_output.splitlines()
    split_at = 28
    render_terminal(
        "student-grading — Lab 02 output 1",
        "$ python -m student_grading --threshold 80\n"
        + "\n".join(application_lines[:split_at]),
        OUTPUT_DIR / "application_output_1.png",
    )
    render_terminal(
        "student-grading — Lab 02 output 2",
        "\n".join(application_lines[split_at:]),
        OUTPUT_DIR / "application_output_2.png",
    )

    benchmark_output = run(str(PYTHON), "-m", "student_grading", "--benchmark")
    render_terminal(
        "student-grading — list vs dict benchmark",
        "$ python -m student_grading --benchmark\n" + benchmark_output,
        OUTPUT_DIR / "benchmark_results.png",
    )

    test_output = run(
        str(PYTHON),
        "-m",
        "pytest",
        "--cov=student_grading",
        "--cov-report=term-missing",
        "-q",
    )
    render_terminal(
        "student-grading — pytest and coverage",
        "$ python -m pytest --cov=student_grading --cov-report=term-missing -q\n"
        + test_output,
        OUTPUT_DIR / "test_results.png",
    )


if __name__ == "__main__":
    main()
