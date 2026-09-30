import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROUTES = {
    Path("C:/inbox/js"): Path("C:/projekty/js"),
    Path("C:/inbox/pdf"): Path("C:/dokumenty/pdf"),
}


class File:
    def __init__(self, path):
        self.path = Path(path)

    @property
    def extension(self):
        return self.path.suffix.lower()

    @property
    def name(self):
        return self.path.name

    @property
    def folder(self):
        return self.path.parent

    def wait_until_ready(self, timeout=30):
        last = -1
        for _ in range(timeout):
            try:
                size = self.path.stat().st_size
            except FileNotFoundError:
                return False
            if size == last:
                return True
            last = size
            time.sleep(1)
        return False

    def move_to(self, target_dir):
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / self.name

        if dest.exists():
            stamp = time.strftime("%Y%m%d_%H%M%S")
            dest = target_dir / f"{self.path.stem}_{stamp}{self.path.suffix}"
        shutil.move(str(self.path), str(dest))
        return dest


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        self.process(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self.process(event.dest_path)

    def process(self, path):
        f = File(path)
        target = ROUTES.get(f.folder)
        if target is None:
            return
        if not f.wait_until_ready():
            print(f"Skipped (file unavailable): {f.name}")
            return
        dest = f.move_to(target)
        print(f"{f.name}: {f.folder} moved to: {dest.parent}")


if __name__ == "__main__":
    observer = Observer()
    handler = Handler()
    for source in ROUTES:
        source.mkdir(parents=True, exist_ok=True)
        print("ooooooo: ", source.resolve())
        observer.schedule(handler, str(source), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()