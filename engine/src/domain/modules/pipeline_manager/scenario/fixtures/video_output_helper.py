import os
import cv2
import numpy as np
from PIL import Image

class VideoTestHelper:
    def __init__(self, output_dir, filename_base, fps=30, width=800, height=600):
        self.output_dir = output_dir
        self.fps = fps
        self.width = width
        self.height = height
        
        os.makedirs(output_dir, exist_ok=True)
        self.video_path = os.path.join(output_dir, f"{filename_base}.webm")
        self.gif_path = os.path.join(output_dir, f"{filename_base}.gif")
        
        # Initialize Video Writer
        fourcc = cv2.VideoWriter_fourcc(*'VP80')
        self.out_video = cv2.VideoWriter(self.video_path, fourcc, fps, (width, height))
        
        self.gif_frames = []

    def write_frame(self, pil_image, save_to_gif=True, gif_interval=2):
        """
        Write a PIL image to video and optionally accumulate for GIF.
        gif_interval: Save every Nth frame to GIF to reduce size.
        """
        # Save to WebM
        img_np = np.array(pil_image)
        # Convert RGBA to BGR for OpenCV
        if img_np.shape[2] == 4:
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
        else:
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
        if self.out_video.isOpened():
            self.out_video.write(img_bgr)
            
        # Accumulate for GIF
        if save_to_gif and (len(self.gif_frames) % gif_interval == 0): # Check implicitly via external counter or just append?
            # Ideally we need a frame counter, but let's just append and filter later? 
            # Or reliance on caller to call this based on interval?
            # Let's just append everything the caller asks us to.
            self.gif_frames.append(pil_image.convert('RGB'))

    def finalize(self):
        if self.out_video.isOpened():
            self.out_video.release()
            print(f"Video saved: {self.video_path}")
            
        if self.gif_frames:
            print("Saving GIF...")
            duration = 1000 / (self.fps / 2) # Assuming we skipped every 2nd frame roughly implicitly via caller or just 15fps
            # Actually, standardizing on 15fps for GIF is good.
            self.gif_frames[0].save(
                self.gif_path,
                save_all=True,
                append_images=self.gif_frames[1:],
                duration=duration,
                loop=0
            )
            print(f"GIF saved: {self.gif_path}")
