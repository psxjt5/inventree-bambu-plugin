import io
import socket
import ssl
import struct
import threading
import time
from urllib.parse import quote

class BambuCameraService:
    """Provides the latest camera frame as either RTSP or JPEG, depending on the Bambu camera type.

    RTSP streaming is not possible on the P1 / A1 printers.

    The printer camera connection closes when the last peer disconnects, after the IDLE_TIMEOUT.
    """

    # H.264 over RTSPS
    RTSP_PORT = 322

    # JPEG frames over TLS
    JPEG_PORT = 6000

    # Seconds without a viewer before disconnecting from the camera
    IDLE_TIMEOUT = 30

    # Seconds between reconnection attempts
    RETRY_DELAY = 2

    # RTSP FPS (how often RTSP video frames are delivered as JPEG frames).
    RTSP_MAX_FPS = 2

    def __init__(self, ip: str, token: str, name: str):
        self.ip_address = ip
        self.token = token
        self.name = name

        # Printer video mode
        self.camera_model: str | None = None  # "rtsp" or "jpeg", detected on first use

        # Current Frame
        self.latest_frame: bytes | None = None

        # Update Lock
        self.lock = threading.Lock()

        # Video fetch thread
        self.video_thread: threading.Thread | None = None

        # Time of the last request (for timeout)
        self.last_request_time = 0.0

    # Determines if the printer supports a video stream.
    def supports_video(self):

        # Check for RTSP
        try:
            socket.create_connection((self.ip_address, self.RTSP_PORT), timeout=3).close()
            self.log("RTSP Connection Test Successful")
            return True
        except OSError:
            pass

        # Check for JPEG
        try:
            socket.create_connection((self.ip_address, self.JPEG_PORT), timeout=3).close()
            self.log("JPEG Connection Test Successful")
            return False
        except OSError:
            pass

        # Neither?
        raise ConnectionError("No camera found (is LAN liveview enabled?)")

    # Camera RTSP Stream -> MP4 Stream
    def stream_mp4(self):
        import av

        url = f"rtsps://bblp:{quote(self.token)}@{self.ip_address}:{self.RTSP_PORT}/streaming/live/1"

        output_buffer = _ChunkCollector()

        with av.open(url, options={"rtsp_transport": "tcp", "tls_verify": "0"}, timeout=10) as source:
            in_stream = source.streams.video[0]

            output = av.open(output_buffer, mode="w", format="mp4", options={"movflags": "frag_keyframe+empty_moov+default_base_moof"})

            out_stream = output.add_stream_from_template(in_stream)

            try:
                offset = None
                last_dts = None

                for packet in source.demux(in_stream):
                    if packet.dts is None:
                        continue

                    # Start on a keyframe, with timestamps from zero, so the browser can play it
                    if offset is None:
                        if not packet.is_keyframe:
                            continue
                        offset = packet.dts
                
                    packet.dts -= offset
                    if packet.pts is not None:
                        packet.pts -= offset

                    # Change arrival time if necessary to display all frames.
                    if last_dts is not None and packet.dts <= last_dts:
                        packet.dts = last_dts + 1
                    if packet.pts is not None and packet.pts < packet.dts:
                        packet.pts = packet.dts
                    last_dts = packet.dts
                
                    packet.stream = out_stream
                    output.mux(packet)
                
                    data = output_buffer.take()
                    if data:
                        yield data
            finally:
                    try:
                        output.close()
                    except Exception:
                        pass  # viewer disconnected mid-write; nothing to finish
        
    # JPEG
    def stream_mjpeg(self):
        last_sent = None

        while True:
            frame = self.get_frame()  # also keeps the camera connection alive

            if frame is not None and frame is not last_sent:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    + f"Content-Length: {len(frame)}\r\n\r\n".encode()
                    + frame
                    + b"\r\n"
                )
                last_sent = frame

            time.sleep(0.2)


    # Get the latest frame (start a new thread if needed).
    def get_frame(self) -> bytes | None:

        # Update the last request time.
        self.last_request_time = time.monotonic()

        # Process the next frame.
        with self.lock:

            # Start a new thread if one doesn't exist.
            if self.video_thread is None or not self.video_thread.is_alive():
                self.video_thread = threading.Thread(target=self._run, daemon=True)
                self.video_thread.start()

            # Return the new frame
            return self.latest_frame

    # Background thread methods

    # Background thread run loop.
    def _run(self) -> None:
        while self._viewer_active():
            try:
                self._stream_jpeg()
            except Exception as e:
                message = str(e).replace(self.token, "***")
                print(f"[BambuCamera] {self.ip_address}: {message}")
                time.sleep(self.RETRY_DELAY)

        with self.lock:
            self.latest_frame = None

    # Determine if a viewer is connected.
    def _viewer_active(self) -> bool:
        return time.monotonic() - self.last_request_time < self.IDLE_TIMEOUT

    # Get the latest frame from the printer and store it.
    def _stream_jpeg(self) -> None:
        auth = (
            struct.pack("<IIII", 0x40, 0x3000, 0, 0)
            + b"bblp".ljust(32, b"\0")
            + self.token.encode().ljust(32, b"\0")
        )

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # printer uses a self-signed certificate

        with socket.create_connection((self.ip_address, self.JPEG_PORT), timeout=10) as raw:
            with context.wrap_socket(raw, server_hostname=self.ip_address) as sock:
                sock.sendall(auth)

                while self._viewer_active():
                    header = self._recv_exact(sock, 16)
                    size = int.from_bytes(header[0:4], "little")
                    jpeg = self._recv_exact(sock, size)

                    if jpeg.startswith(b"\xff\xd8"):  # valid JPEG
                        self._set_frame(jpeg)
    
    # Update the latest frame.
    def _set_frame(self, jpeg: bytes) -> None:
        with self.lock:
            self.latest_frame = jpeg

    # Receive the correct amount of data over the socket.
    @staticmethod
    def _recv_exact(sock, length: int) -> bytes:
        data = bytearray()
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                raise ConnectionError("Camera closed the connection")
            data.extend(chunk)
        return bytes(data)

    # Log a message about this machine
    def log(self, message):
            print(f"[BambuCameraService - {self.name}] - {message}")

class _ChunkCollector:
    """File-like object that collects what PyAV writes, so it can be sent on."""

    def __init__(self):
        self._data = bytearray()

    def write(self, data) -> int:
        self._data.extend(data)
        return len(data)

    def take(self) -> bytes:
        data = bytes(self._data)
        self._data.clear()
        return data