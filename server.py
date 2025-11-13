import os
import json
from flask import Flask, Response, request, jsonify
from utils.ascii_video import ASCIIVideoStreamer
from dotenv import load_dotenv

class ASCIIVideoServer:
    def __init__(self, server_url: str = None, video_json: str = "videos.json"):
        load_dotenv()
        self.SERVER_URL = server_url or os.getenv("SERVER_URL", "http://localhost:8000")
        self.VIDEOS = {}
        if os.path.exists(video_json):
            with open(video_json, "r") as f:
                try:
                    self.VIDEOS = json.load(f)
                except json.JSONDecodeError:
                    print("Error: videos.json is not valid JSON.")
        else:
            print("Warning: videos.json not found. No videos available.")
        self.app = Flask(__name__)
        self.register_routes()

    @staticmethod
    def is_curl_request(req) -> bool:
        user_agent = req.headers.get("User-Agent", "").lower()
        return "curl" in user_agent

    @staticmethod
    def parse_bool(param: str, default: bool = True) -> bool:
        if param is None:
            return default
        param = str(param).lower()
        if param in ("1", "true", "yes", "on"):
            return True
        elif param in ("0", "false", "no", "off"):
            return False
        return default

    def register_routes(self):
        @self.app.route("/")
        def list_videos():
            video_list = list(self.VIDEOS.keys())
            response = {
                "available_videos": video_list,
                "instructions": f"Use curl to stream a video: curl {self.SERVER_URL}/<video_name>?width=100&color=true"
            }
            return jsonify(response)

        @self.app.route("/<video_name>")
        def stream_video(video_name):
            if not self.is_curl_request(request):
                return "Access denied. Only curl allowed.", 403

            if video_name not in self.VIDEOS:
                return jsonify({"error": f"Video '{video_name}' not found."}), 404

            video_path = self.VIDEOS[video_name]

            try:
                width = int(request.args.get("width", 100))
                if width < 10 or width > 300:
                    width = 100
            except ValueError:
                width = 100

            color = self.parse_bool(request.args.get("color"), default=True)

            try:
                streamer = ASCIIVideoStreamer(video_path, width=width, color=color)
            except ValueError as e:
                return jsonify({"error": str(e)}), 500

            return Response(streamer.stream(), mimetype="text/plain")

    def run(self, host="0.0.0.0", port=8000, debug=False):
        self.app.run(host=host, port=port, debug=debug)

server = ASCIIVideoServer()
app = server.app

if __name__ == "__main__":
    server.run()