from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SCREENCAST_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCREENCAST_DIR / "output"
WEB_OUTPUT_DIR = OUTPUT_DIR / "web"

# Never upscale: a scenario recorded narrower than this (see VIEWPORT_SIZE in
# scenarios/conftest.py) is left at its native width.
MAX_WIDTH = 1280
SCALE_FILTER = f"scale='min({MAX_WIDTH},iw)':-2"


def find_ffmpeg() -> str:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise OSError(
            "ffmpeg was not found on PATH. It is required to produce "
            "web-optimized videos from the recorded screencast .webm files. "
            "Install it (e.g. `brew install ffmpeg` on macOS, "
            "`apt-get install ffmpeg` on Debian/Ubuntu) and ensure it is on "
            "PATH, then re-run this command."
        )
    return ffmpeg_path


def encode_webm(ffmpeg_path: str, source: Path, destination: Path) -> None:
    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-i",
            str(source),
            "-vf",
            SCALE_FILTER,
            "-c:v",
            "libvpx-vp9",
            "-b:v",
            "0",
            "-crf",
            "32",
            "-an",
            str(destination),
        ],
        check=True,
    )


def encode_mp4(ffmpeg_path: str, source: Path, destination: Path) -> None:
    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-i",
            str(source),
            "-vf",
            SCALE_FILTER,
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-preset",
            "slow",
            "-movflags",
            "+faststart",
            "-an",
            str(destination),
        ],
        check=True,
    )


def optimize_one(ffmpeg_path: str, source: Path) -> None:
    scenario_name = source.stem
    webm_destination = WEB_OUTPUT_DIR / f"{scenario_name}.webm"
    mp4_destination = WEB_OUTPUT_DIR / f"{scenario_name}.mp4"

    print(f"🎬 Optimizing {source.name} for the web...")  # noqa: T201
    encode_webm(ffmpeg_path, source, webm_destination)
    encode_mp4(ffmpeg_path, source, mp4_destination)

    for destination in (webm_destination, mp4_destination):
        size_mb = destination.stat().st_size / (1024 * 1024)
        print(f"   -> {destination} ({size_mb:.2f} MB)")  # noqa: T201


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Converts recorded screencast .webm files in "
            f"{OUTPUT_DIR.relative_to(SCREENCAST_DIR.parent.parent)} into "
            "muted, web-optimized .webm (VP9) and .mp4 (H.264) pairs "
            f"under {WEB_OUTPUT_DIR.relative_to(SCREENCAST_DIR.parent.parent)}."
        )
    )
    parser.add_argument(
        "--focus",
        default=None,
        help=(
            "Only optimize the recording for this scenario name (e.g. "
            "hello_world), instead of every .webm in the output directory."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        ffmpeg_path = find_ffmpeg()
    except OSError as error:
        print(error, file=sys.stderr)  # noqa: T201
        return 1

    if args.focus is not None:
        sources = [OUTPUT_DIR / f"{args.focus}.webm"]
        if not sources[0].is_file():
            print(  # noqa: T201
                f"No recording found at {sources[0]}. Record it first with "
                f"`invoke test-screencast --record-video --focus={args.focus}`.",
                file=sys.stderr,
            )
            return 1
    else:
        sources = sorted(OUTPUT_DIR.glob("*.webm"))
        if not sources:
            print(  # noqa: T201
                f"No .webm recordings found in {OUTPUT_DIR}. Record some "
                "first with `invoke test-screencast --record-video`.",
                file=sys.stderr,
            )
            return 1

    WEB_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for source in sources:
        optimize_one(ffmpeg_path, source)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
