import time

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal


class CameraThread(QThread):
    frame_ready = Signal(str, np.ndarray)
    camera_error = Signal(str)

    def __init__(self, camera_name, camera_index):
        super().__init__()
        self.camera_name = camera_name
        self.camera_index = camera_index
        self._running = False
        self._latest_frame = None

    def run(self):
        capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not capture.isOpened():
            capture.release()
            self.camera_error.emit(f"No se pudo abrir la camara {self.camera_name}.")
            return
        self._running = True
        try:
            while self._running:
                ok, frame = capture.read()
                if ok:
                    self._latest_frame = frame.copy()
                    self.frame_ready.emit(self.camera_name, frame)
                else:
                    time.sleep(0.05)
                self.msleep(15)
        finally:
            capture.release()

    def latest_frame(self):
        return None if self._latest_frame is None else self._latest_frame.copy()

    def stop(self):
        self._running = False
        if self.isRunning():
            self.wait(2000)


class CameraManager:
    def __init__(self, camera_indexes):
        self.threads = {
            name: CameraThread(name, index) for name, index in camera_indexes.items()
        }

    def start(self, frame_callback, error_callback):
        for thread in self.threads.values():
            thread.frame_ready.connect(frame_callback)
            thread.camera_error.connect(error_callback)
            thread.start()

    def capture(self):
        return {
            name: thread.latest_frame()
            for name, thread in self.threads.items()
            if thread.latest_frame() is not None
        }

    def stop(self):
        for thread in self.threads.values():
            thread.stop()
