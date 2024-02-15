from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSlider,
    QLabel,
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Video Player")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        # Play button
        self.playButton = QPushButton("Play")
        self.playButton.clicked.connect(self.play_video)

        # Slider for video
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addWidget(self.playButton)
        layout.addWidget(self.slider)

        self.setLayout(layout)
        self.mediaPlayer.setVideoOutput(videoWidget)

        # Load video
        self.mediaPlayer.setMedia(
            QMediaContent(
                QUrl.fromLocalFile(
                    "/home/irving/webdev/irving/sportlight/output/nba/videos/175_06:28_James 2' Running Dunk .mp4"
                )
            )
        )
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setText("Play")
        else:
            self.mediaPlayer.play()
            self.playButton.setText("Pause")

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
