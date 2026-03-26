import argparse
import asyncio
import json
import subprocess
from pathlib import Path
import edge_tts

VOICE = "nl-NL-FennaNeural"

async def synthesize(text, out_path, rate="+0%", volume="+0%"):
    communicate = edge_tts.Communicate(text=text, voice=VOICE, rate=rate, volume=volume)
    await communicate.save(out_path)


def normalize_audio(path: Path):
    tmp = path.with_suffix(".tmp.mp3")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(path),
        "-filter:a",
        "loudnorm=I=-16:LRA=11:TP=-1.5",
        str(tmp),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


async def worker(queue, semaphore, normalize):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            return
        text, out_path = item
        async with semaphore:
            try:
                await synthesize(text, out_path)
                if normalize:
                    normalize_audio(Path(out_path))
            except Exception as e:
                print("ERR", text, out_path, e)
        queue.task_done()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args()

    with open("data/words.json", "r", encoding="utf-8") as f:
        words = json.load(f)

    out_dir = Path("audio_examples")
    out_dir.mkdir(parents=True, exist_ok=True)

    start = args.start
    end = start + args.limit - 1 if args.limit else len(words)

    queue = asyncio.Queue()
    semaphore = asyncio.Semaphore(args.concurrency)

    for item in words:
        rank = int(item["rank"])
        if rank < start or rank > end:
            continue
        filename = f"{rank:04d}.mp3"
        out_path = out_dir / filename
        if out_path.exists():
            continue
        text = item.get('example','')
        if not text:
            continue
        await queue.put((text, str(out_path)))

    workers = [asyncio.create_task(worker(queue, semaphore, args.normalize)) for _ in range(args.concurrency)]
    for _ in workers:
        await queue.put(None)
    await queue.join()
    for w in workers:
        await w


if __name__ == "__main__":
    asyncio.run(main())
