import sys, os, subprocess, json, uuid, time, requests, glob, threading
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap
import vlc

# ========= CONFIG =========
BG = "#121212"
CARD = "#1e1e1e"
ACCENT = "#1DB954"

MUSIC_DIR = "Music"
TEMP_DIR = "temp"

os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


# ========= CLEANUP =========
def cleanup_temp():
    for f in glob.glob(f"{TEMP_DIR}/temp_*.webm"):
        try:
            os.remove(f)
        except:
            pass


# ========= WORKER =========
class Worker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        result = self.fn()
        self.finished.emit(result)


# ========= PLAYER =========
class AudioPlayer:
    def __init__(self):
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()
        self.process = None
        self.file = None

    def play(self, url):
        self.stop()

        self.file = f"{TEMP_DIR}/temp_{uuid.uuid4().hex}.webm"

        self.process = subprocess.Popen([
            "yt-dlp",
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "-f", "bestaudio[ext=webm]/bestaudio",
            "--concurrent-fragments", "5",
            "-o", self.file,
            "--quiet",
            url
        ])

        for _ in range(100):
            if os.path.exists(self.file) and os.path.getsize(self.file) > 2_000_000:
                break
            time.sleep(0.1)

        media = self.instance.media_new(self.file)
        media.add_option(":demux=any")
        media.add_option(":file-caching=1500")

        self.player.set_media(media)
        self.player.play()

    def stop(self):
        try:
            self.player.stop()

            if self.process:
                self.process.terminate()

            if self.file:
                threading.Thread(target=self.safe_delete, daemon=True).start()
        except:
            pass

    def safe_delete(self):
        time.sleep(2)
        try:
            if self.file and os.path.exists(self.file):
                os.remove(self.file)
        except:
            pass


# ========= SEARCH =========
def search_youtube(query):
    cmd = [
        "yt-dlp",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        f"ytsearch8:{query}",
        "--dump-json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    data = []
    for line in result.stdout.split("\n"):
        if line.strip():
            j = json.loads(line)
            data.append({
                "title": j["title"],
                "url": j["webpage_url"],
                "thumb": j["thumbnail"]
            })
    return data


# ========= CARD =========
class SongCard(QFrame):
    def __init__(self, item, callback):
        super().__init__()
        self.item = item
        self.callback = callback

        self.setFixedSize(180, 220)
        self.setStyleSheet("""
            QFrame { background:#1e1e1e; border-radius:10px; }
            QFrame:hover { background:#2a2a2a; }
        """)

        layout = QVBoxLayout(self)

        self.img = QLabel()
        self.img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.img)

        title = QLabel(item["title"][:40])
        title.setWordWrap(True)
        layout.addWidget(title)

        # async image loading
        self.worker = Worker(lambda: requests.get(item["thumb"]).content)
        self.worker.finished.connect(self.set_image)
        self.worker.start()

    def set_image(self, data):
        pix = QPixmap()
        pix.loadFromData(data)
        self.img.setPixmap(pix.scaled(160, 100))

    def mousePressEvent(self, e):
        self.callback(self.item)


# ========= APP =========
class App(QWidget):
    def __init__(self):
        super().__init__()
        cleanup_temp()

        self.setWindowTitle("Music App")
        self.resize(1100, 650)
        self.setStyleSheet(f"background:{BG}; color:white;")

        self.player = AudioPlayer()
        self.current_url = None
        self.results = []
        self.workers = []

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

    def run_worker(self, fn, callback=None):
        worker = Worker(fn)
        self.workers.append(worker)

        if callback:
            worker.finished.connect(callback)

        worker.finished.connect(lambda: self.workers.remove(worker))
        worker.start()

    def init_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self.search_box = QLineEdit()
        btn = QPushButton("Search")
        btn.clicked.connect(self.search)

        top.addWidget(self.search_box)
        top.addWidget(btn)
        layout.addLayout(top)

        self.scroll = QScrollArea()
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)

        self.scroll.setWidget(self.grid_widget)
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        ctrl = QHBoxLayout()

        play = QPushButton("▶")
        stop = QPushButton("⏹")
        dl = QPushButton("⬇")

        play.clicked.connect(self.play)
        stop.clicked.connect(self.player.stop)
        dl.clicked.connect(self.download)

        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setValue(70)
        self.volume.valueChanged.connect(
            lambda v: self.player.player.audio_set_volume(v)
        )

        self.time = QLabel("00:00 / 00:00")

        ctrl.addWidget(play)
        ctrl.addWidget(stop)
        ctrl.addWidget(dl)
        ctrl.addWidget(self.time)
        ctrl.addWidget(self.seek)
        ctrl.addWidget(self.volume)

        layout.addLayout(ctrl)

    def search(self):
        query = self.search_box.text()
        self.run_worker(lambda: search_youtube(query), self.render_results)

    def render_results(self, results):
        self.results = results

        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().deleteLater()

        for i, item in enumerate(results):
            card = SongCard(item, self.select)
            self.grid.addWidget(card, i // 4, i % 4)

    def select(self, item):
        self.current_url = item["url"]

    def play(self):
        if self.current_url:
            self.run_worker(lambda: self.player.play(self.current_url))

    def download(self):
        if self.current_url:
            self.run_worker(lambda: subprocess.run([
                "yt-dlp",
                "--js-runtimes", "node",
                "--remote-components", "ejs:github",
                self.current_url,
                "-x", "--audio-format", "mp3",
                "-o", f"{MUSIC_DIR}/%(title)s.%(ext)s"
            ]))

    def update_ui(self):
        p = self.player.player
        if p.is_playing():
            length = p.get_length()
            cur = p.get_time()

            if length > 0:
                self.seek.setValue(int(cur / length * 1000))

                def fmt(ms):
                    s = int(ms / 1000)
                    return f"{s//60:02}:{s%60:02}"

                self.time.setText(f"{fmt(cur)} / {fmt(length)}")


# ========= RUN =========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())