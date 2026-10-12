import io
import socket
import ssl
import struct
import threading
import time
from urllib.parse import quote


class BambuCameraService:
    """Provides the latest camera frame as a JPEG, for both Bambu camera types.

    The camera connection only runs while someone is viewing it, and
    closes after IDLE_TIMEOUT seconds without a request.
    """

    RTSP_PORT = 322     # X1 / H2D series: H.264 over RTSPS
    JPEG_PORT = 6000    # P1 / A1 series: JPEG frames over TLS
    IDLE_TIMEOUT = 30   # seconds without a viewer before disconnecting
    RETRY_DELAY = 2     # seconds between reconnection attempts
    RTSP_MAX_FPS = 2    # how often to convert RTSP video frames to JPEG

    def __init__(self, host: str, access_token: str):
        self.host = host
        self.access_token = access_token

        self._mode: str | None = None  # "rtsp" or "jpeg", detected on first use
        self._frame: bytes | None = None
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._last_request = 0.0

    # Public

    def get_frame(self) -> bytes | None:
        """Return the latest frame, starting the camera connection if needed."""
        self._last_request = time.monotonic()

        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._run, daemon=True)
                self._thread.start()
            return self._frame

    # Background thread

    def _viewer_active(self) -> bool:
        return time.monotonic() - self._last_request < self.IDLE_TIMEOUT

    def _set_frame(self, jpeg: bytes) -> None:
        with self._lock:
            self._frame = jpeg

    def _run(self) -> None:
        while self._viewer_active():
            try:
                if self._mode is None:
                    self._mode = self._detect_mode()

                if self._mode == "rtsp":
                    self._stream_rtsp()
                else:
                    self._stream_jpeg()
            except Exception as e:
                message = str(e).replace(self.access_token, "***")
                print(f"[BambuCamera] {self.host}: {message}")
                time.sleep(self.RETRY_DELAY)

        with self._lock:
            self._frame = None

    def _detect_mode(self) -> str:
        """Work out which camera type the printer has (raises if neither is reachable)."""
        for port, mode in ((self.RTSP_PORT, "rtsp"), (self.JPEG_PORT, "jpeg")):
            try:
                socket.create_connection((self.host, port), timeout=3).close()
                return mode
            except OSError:
                continue

        raise ConnectionError("No camera found (is LAN liveview enabled?)")

    # X1 / H2D: H.264 video over RTSPS

    def _stream_rtsp(self) -> None:
        import av  # imported here so P1/A1 users don't need PyAV installed
        import av.logging

        av.logging.set_level(av.logging.VERBOSE)

        url = (
            f"rtsps://bblp:{quote(self.access_token)}@{self.host}:"
            f"{self.RTSP_PORT}/streaming/live/1"
        )

        with av.open(url, options={"rtsp_transport": "tcp", "tls_verify": "0"}, timeout=10) as container:
            interval = 1 / self.RTSP_MAX_FPS
            last_saved = 0.0

            # Every frame has to be decoded (H.264 depends on previous frames),
            # but only a couple per second are converted to JPEG
            for frame in container.decode(video=0):
                if not self._viewer_active():
                    return

                now = time.monotonic()
                if now - last_saved < interval:
                    continue

                buffer = io.BytesIO()
                frame.to_image().save(buffer, format="JPEG", quality=80)
                self._set_frame(buffer.getvalue())
                last_saved = now

    # P1 / A1: JPEG frames over a TLS socket

    def _stream_jpeg(self) -> None:
        auth = (
            struct.pack("<IIII", 0x40, 0x3000, 0, 0)
            + b"bblp".ljust(32, b"\0")
            + self.access_token.encode().ljust(32, b"\0")
        )

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # printer uses a self-signed certificate

        with socket.create_connection((self.host, self.JPEG_PORT), timeout=10) as raw:
            with context.wrap_socket(raw, server_hostname=self.host) as sock:
                sock.sendall(auth)

                while self._viewer_active():
                    header = self._recv_exact(sock, 16)
                    size = int.from_bytes(header[0:4], "little")
                    jpeg = self._recv_exact(sock, size)

                    if jpeg.startswith(b"\xff\xd8"):  # valid JPEG
                        self._set_frame(jpeg)

    @staticmethod
    def _recv_exact(sock, length: int) -> bytes:
        data = bytearray()
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                raise ConnectionError("Camera closed the connection")
            data.extend(chunk)
        return bytes(data)