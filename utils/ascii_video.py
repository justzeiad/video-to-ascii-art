import cv2
import time

class ASCIIVideoStreamer:
    """Convert a video to ASCII frames."""
    
    # Color version (dense gradient)
    ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    # Grayscale version (enhanced readability)
    ASCII_CHARS_GRAY = "@%#*+=-:. "

    def __init__(self, video_path: str, width: int = 100, color: bool = True):
        """
        Initialize the streamer.

        :param video_path: Path to the video file.
        :param width: Width in characters for ASCII output.
        :param color: True for color ASCII, False for grayscale.
        """
        self.video_path = video_path
        self.width = width
        self.color = color

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.delay = 1 / self.fps

    def resize_frame(self, frame):
        """Resize frame preserving aspect ratio for ASCII conversion."""
        height, width = frame.shape[:2]
        aspect_ratio = height / width
        new_height = int(aspect_ratio * self.width * 0.55)
        return cv2.resize(frame, (self.width, new_height))

    def frame_to_ascii(self, frame):
        """Convert a single frame to ASCII, using color or grayscale mapping."""
        ascii_str = ""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.color:
            num_chars = len(self.ASCII_CHARS)
        else:
            num_chars = len(self.ASCII_CHARS_GRAY)
            gamma = 0.6  # Enhance grayscale contrast

        for y, row in enumerate(gray):
            for x, pixel in enumerate(row):
                if self.color:
                    char_index = int((pixel / 255) * (num_chars - 1))
                    char = self.ASCII_CHARS[char_index]
                    b, g, r = frame[y, x]
                    ascii_str += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
                else:
                    # Gamma corrected grayscale mapping
                    normalized = (pixel / 255) ** gamma
                    char_index = int(normalized * (num_chars - 1))
                    char = self.ASCII_CHARS_GRAY[char_index]
                    ascii_str += char
            ascii_str += "\n"

        return ascii_str

    def stream(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = self.resize_frame(frame)
            ascii_frame = self.frame_to_ascii(frame)

            # Always clear screen for every frame
            yield f"\033[2J\033[H{ascii_frame}"

            time.sleep(self.delay)

        self.cap.release()
