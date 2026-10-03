import os
from http.server import BaseHTTPRequestHandler
from api._shared import json_response

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        work24=bool(os.environ.get("WORK24_API_URL") and os.environ.get("WORK24_API_KEY"))
        json_response(self,200,{"aiAvailable":bool(os.environ.get("GEMINI_API_KEY")),"publicDataAvailable":work24,"source":"work24" if work24 else "sample"})
