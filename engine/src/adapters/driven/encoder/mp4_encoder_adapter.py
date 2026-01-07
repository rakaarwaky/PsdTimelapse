import queue
import subprocess
import threading

from PIL import Image


class Mp4EncoderAdapter:
    def __init__(self, width: int, height: int, fps: int = 24, output_path: str = "output.mp4"):
        self.width = width
        self.height = height
        self.fps = fps
        self.output_path = output_path

        # Start FFmpeg
        # Input: Raw RGBA video from pipe
        # Output: MP4 (H.264), YUV420P
        self.cmd = [
            "ffmpeg",
            "-y",  # Overwrite
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-s",
            f"{width}x{height}",
            "-pix_fmt",
            "rgba",  # Input format
            "-r",
            str(fps),
            "-i",
            "-",  # Input from stdin
            "-c:v",
            "libx264",  # Encoder
            "-preset",
            "fast",
            "-crf",
            "23",  # Quality
            "-pix_fmt",
            "yuv420p",  # Output pixel format for compatibility
            output_path,
        ]

        print(f"🎬 Initializing FFmpeg MP4 Encoder: {' '.join(self.cmd)}")

        self.process = subprocess.Popen(
            self.cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )

        self.write_queue = queue.Queue(maxsize=30)  # type: ignore[var-annotated]
        self.writer_thread = threading.Thread(target=self._writer_worker, daemon=True)
        self.writer_thread.start()

    def _writer_worker(self) -> None:
        while True:
            data = self.write_queue.get()
            if data is None:
                break

            try:
                self.process.stdin.write(data)  # type: ignore[union-attr]
            except (BrokenPipeError, OSError):
                # Process might have crashed or closed
                break
            except Exception as e:
                print(f"❌ Writer Error: {e}")
                break

    def encode_frame(self, frame_image: Image.Image) -> None:
        """
        Takes a PIL Image (RGBA), converts to bytes, and queues for encoding.
        """
        try:
            # Ensure RGBA
            if frame_image.mode != "RGBA":
                frame_image = frame_image.convert("RGBA")

            # Get raw bytes
            raw_data = frame_image.tobytes()

            # Queue for async writing
            self.write_queue.put(raw_data)

        except Exception as e:
            print(f"Error encoding frame: {e}")

    def release(self) -> None:
        """Finalize encoding"""
        print("💾 Finalizing MP4 Video...")
        self.write_queue.put(None)
        self.writer_thread.join()

        if self.process.stdin:
            self.process.stdin.close()

        self.process.wait()

        if self.process.returncode != 0:
            err = self.process.stderr.read().decode()  # type: ignore[union-attr]
            print(f"❌ FFmpeg Error:\n{err}")
        else:
            print(f"✅ Video Saved: {self.output_path}")
