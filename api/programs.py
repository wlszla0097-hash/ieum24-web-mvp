from http.server import BaseHTTPRequestHandler
from api._shared import json_response,load_programs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            programs,source=load_programs()
            json_response(self,200,{"programs":programs,"source":source,"sourceLabel":"고용24 공개 API" if source=="work24" else "시연용 예시 정보","note":"신청 자격과 모집 현황은 공식 공고에서 확인해 주세요."})
        except Exception as exc:
            print("programs_api_error",type(exc).__name__)
            json_response(self,502,{"error":"공개 정보를 불러오지 못했어요. 잠시 뒤 다시 시도해 주세요.","code":"SOURCE_UNAVAILABLE"})
    def do_POST(self):json_response(self,405,{"error":"GET 요청만 지원해요."})
