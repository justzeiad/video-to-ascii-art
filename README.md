# ASCII Video Streamer

A compact Python service that converts videos into **animated ASCII art** and streams them over HTTP so you can watch them in your terminal using `curl`.

This README explains **how it works** (internals + pipeline), the components, configuration, and usage.

---

## How it works (high level)

1. **Video source** – A list of videos and their file paths is stored in `videos.json` (a simple manifest). The server only serves files listed in that manifest.

2. **HTTP server** – `server.py` (Flask) exposes two endpoints:

   * `/` — returns a JSON list of available video keys and basic instructions.
   * `/<video_name>` — streams the selected video as ASCII frames.

   The server enforces that requests come from command-line clients (it checks the `User-Agent` for `curl`) to avoid browser-based access.

3. **Frame processing** – For each frame of the chosen video, the `ASCIIVideoStreamer` class (in `utils/ascii_video.py`) does the following:

   * Read a frame from the video file using OpenCV.
   * Resize the frame to the requested column width while preserving aspect ratio (compensating for character cell height).
   * Convert to grayscale to choose an ASCII character based on brightness.
   * If **color mode** is enabled, the streamer emits ANSI 24-bit color escape codes so each ASCII character is colored according to the pixel's RGB value.
   * The streamer prepends a screen-clear sequence (`[2J[H`) before every frame so the terminal shows a single, updating frame rather than a growing scroll.

4. **Streaming via HTTP** – Flask returns a streaming `text/plain` response that yields frames continuously. `curl` prints the streamed text to the terminal, producing an animated ASCII playback.

---

## Components

* `server.py` — Flask application. Loads `videos.json`, parses query params (`width`, `color`), enforces `curl` access, instantiates the streamer, and returns a streaming response.

* `videos.json` — JSON manifest mapping short names to file paths. Example:

```json
{
  "ben10": ".videos/ben10opening.mp4",
  "demo": ".videos/demo.mp4"
}
```

* `utils/ascii_video.py` — Contains `ASCIIVideoStreamer` class that does the video → ASCII conversion and yields frames. Key responsibilities:

  * Resizing frames to a character column width
  * Mapping pixel brightness to ASCII characters (enhanced grayscale uses a dedicated, readable charset and gamma correction)
  * Emitting ANSI RGB color codes when `color=True`
  * Yielding `[2J[H` + ASCII per frame so the terminal updates in-place

---

## Configuration

* **Environment**

  * `SERVER_URL` (optional) — used in the `/` endpoint example instructions; defaults to `http://localhost:8000`.

* **videos.json**

  * Add entries for every video you want the server to serve. Only these entries are accessible (prevents arbitrary file access).

* **Dependencies**

  * `flask`, `opencv-python`, `python-dotenv` (if using `.env`).

Install with:

```bash
pip install -r requirements.txt
```

---

## API / Usage

* **List available videos**

```bash
curl http://127.0.0.1:8000/
```

Response (JSON):

```json
{ "available_videos": ["ben10","demo"], "instructions": "Use curl to stream a video: curl http://localhost:8000/<video_name>" }
```

* **Stream a video**

```bash
curl "http://127.0.0.1:8000/<video_name>"
```

Query parameters:

* `width` — desired ASCII columns (integer). The server clamps invalid values; recommended between `10` and `300`.
* `color` — toggle color; accepted truthy values: `1`, `true`, `yes`, `on`; falsy: `0`, `false`, `no`, `off`. **Default: `true`**.

Examples:

```bash
# color (default) with width 100
curl "http://127.0.0.1:8000/ben10"

# grayscale, width 150
curl "http://127.0.0.1:8000/ben10?color=false&width=150"
```

---


## Troubleshooting

* **Cannot open video** — Ensure `videos.json` points to an existing file and the server process has read permissions.
* **No color shown** — Your terminal may not support 24-bit color. Test in a modern terminal or use `color=false`.
* **Frames stack / scrolling** — If you still see multiple frames in a row:

  * Ensure your terminal supports ANSI clear (`[2J[H`).
  * Try Windows Terminal or PowerShell if using Windows.
  * Reduce `width` so frames fit your terminal height.

---
## License

This project is licensed under the MIT License.
