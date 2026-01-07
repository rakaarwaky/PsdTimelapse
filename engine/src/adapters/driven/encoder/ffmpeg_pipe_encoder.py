import queue
import subprocess
import threading


class FfmpegPipeEncoder:
    def __init__(self, width: int, height: int, fps: int = 30, output_path: str = "output.mp4"):
        self.width = width
        self.height = height
        self.fps = fps
        self.output_path = output_path

        # Start FFmpeg with NVENC expecting raw NV12 via stdin
        self.cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "nv12",
            "-s",
            f"{width}x{height}",
            "-r",
            str(fps),
            "-i",
            "-",  # Input from pipe
            "-c:v",
            "h264_nvenc",
            "-preset",
            "p4",  # Balanced preset
            "-tune",
            "hq",  # High quality tuning
            "-b:v",
            "5M",  # 5 Mbps bitrate
            "-bufsize",
            "10M",
            "-maxrate",
            "10M",
            output_path,
        ]

        print(f"🎬 Initializing FFmpeg Pipe: {' '.join(self.cmd)}")

        self.process = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,  # Capture stderr for debugging
        )

        # Async writer queue
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
            except BrokenPipeError:
                print("❌ FFmpeg Pipe Broken!")
                break
            except Exception as e:
                print(f"❌ Writer Error: {e}")
                break

    def encode_frame(self, nv12_gpu_array) -> None:  # type: ignore[no-untyped-def]
        """
        Takes a CuPy NV12 array, downloads to host, and queues for encoding.
        """
        try:
            # Download to host (Device -> Host)
            # Note: asnumpy() implicitly blocks until GPU processing is complete
            # ideally we use a stream, but for MVP this is fast enough (proven 289 FPS).
            host_data = nv12_gpu_array.tobytes()

            # Queue for async writing
            self.write_queue.put(host_data)

        except Exception as e:
            print(f"Error encoding frame: {e}")

    def release(self) -> None:
        """Finalize encoding"""
        print("💾 Finalizing Video...")
        self.write_queue.put(None)
        self.writer_thread.join()

        if self.process.stdin:
            self.process.stdin.close()

        self.process.wait()

        if self.process.returncode != 0:
            err = self.process.stderr.read().decode()  # type: ignore[union-attr]
            print(f"❌ FFmpeg Error:\n{err}")
        else:
            print("✅ Video Saved Successfully.")
