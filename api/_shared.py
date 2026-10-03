"""Shared helpers for the small Vercel Python functions."""
from __future__ import annotations
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SAMPLES = [
    {"id":"sample-job","title":"정부지원 일자리 정보 찾아보기","category":"취업","summary":"공공 일자리 사업과 참여자 모집 정보를 고용24에서 살펴보세요.","eligibility":"대상·모집 지역·기간은 각 공고에서 확인해 주세요.","tags":["취업","일자리","지원","청년","중장년","기업"],"source_name":"고용24 정부지원 일자리정보","source_url":"https://www.work24.go.kr/","is_sample":True},
    {"id":"sample-training","title":"직업훈련 과정 찾아보기","category":"훈련","summary":"관심 직무와 지역을 기준으로 직업훈련 과정을 비교해 보세요.","eligibility":"과정별 지원 대상과 자부담은 공식 과정 안내에서 확인해 주세요.","tags":["훈련","교육","직무","역량","취업","청년","기업"],"source_name":"고용24 훈련과정 OpenAPI 안내","source_url":"https://www.work24.go.kr/cm/e/a/0110/selectOpenApiIntro.do","is_sample":True},
    {"id":"sample-employer","title":"채용·기업 지원 정보 찾아보기","category":"기업","summary":"기업의 채용 계획과 지역에 맞는 일자리 사업 정보를 살펴보세요.","eligibility":"기업 규모·채용 조건·사업별 중복 제한을 해당 공고에서 확인해 주세요.","tags":["기업","채용","고용","지원금","청년","일자리"],"source_name":"고용24 정부지원 일자리정보","source_url":"https://www.work24.go.kr/","is_sample":True},
]

def json_response(handler, status: int, payload: dict) -> None:
    raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type","application/json; charset=utf-8")
    handler.send_header("Cache-Control","no-store")
    handler.send_header("X-Content-Type-Options","nosniff")
    handler.end_headers()
    handler.wfile.write(raw)

def request_json(handler,limit=4000):
    try:
        length=int(handler.headers.get("Content-Length","0"))
        if length<=0 or length>limit:return None
        body=json.loads(handler.rfile.read(length).decode("utf-8"))
        return body if isinstance(body,dict) else None
    except (ValueError,UnicodeDecodeError):return None

ALIASES={
 "title":{"사업명","사업명칭","일자리사업명","모집공고명","공고명","bizNm","bizName","recrutTitle","wantedTitle","title","programName"},
 "summary":{"사업내용","사업소개","사업개요","모집내용","상세내용","contents","bizCn","bizCont","description","summary"},
 "eligibility":{"지원대상","참여대상","신청자격","자격요건","대상","target","targetNm","qualifications","eligibility"},
 "category":{"분야","사업유형","사업구분","유형","bizType","type","category"},
 "region":{"지역","모집지역","근무지역","region","areaNm","workRegion"},
 "start_date":{"모집시작일","접수시작일","시작일","접수기간시작","startDate","start_date","recrutStartDt"},
 "end_date":{"모집종료일","접수종료일","종료일","마감일","endDate","end_date","recrutEndDt"},
 "url":{"상세URL","공고URL","신청URL","링크","url","detailUrl","link"},
}
def _key_map(element):
    out={}
    for node in element.iter():
        tag=node.tag.split("}")[-1].split(":")[-1]
        if node.text and node.text.strip():out[tag]=node.text.strip()
        for k,v in node.attrib.items():out.setdefault(k.split("}")[-1],v)
    result={}
    for name,keys in ALIASES.items():
        value=next((out[k] for k in keys if k in out),"")
        result[name]=value
    return result

def parse_programs(raw:bytes,content_type:str=""):
    if "json" in content_type.lower() or raw.lstrip().startswith((b"{",b"[")):
        data=json.loads(raw.decode("utf-8-sig"))
        if isinstance(data,dict):
            candidates=[]
            def find(obj):
                if isinstance(obj,list):
                    if obj and all(isinstance(x,dict) for x in obj):candidates.append(obj)
                    for x in obj:find(x)
                elif isinstance(obj,dict):
                    for x in obj.values():find(x)
            find(data)
            rows=max(candidates,key=len) if candidates else ([data] if any(k in data for k in ALIASES["title"]) else [])
        else:rows=data if isinstance(data,list) else []
        records=[]
        for row in rows:
            if not isinstance(row,dict):continue
            flat={str(k):str(v) for k,v in row.items() if v is not None}
            item={name:next((flat[k] for k in keys if k in flat),"") for name,keys in ALIASES.items()}
            if item["title"]:records.append(item)
    else:
        root=ET.fromstring(raw)
        candidates=[]
        title_tags={k for k in ALIASES["title"]}
        for node in root.iter():
            children=list(node)
            if children and any(c.tag.split("}")[-1].split(":")[-1] in title_tags for c in children):
                candidates.append(node)
        records=[_key_map(n) for n in candidates]
        records=[r for r in records if r["title"]]
    result=[]
    for i,row in enumerate(records[:50]):
        detail=(row["summary"] or "사업 세부 내용은 공식 공고에서 확인해 주세요.").strip()
        category=(row["category"] or "고용지원").strip()
        source=row["url"].strip()
        if not source.startswith("https://www.work24.go.kr/"):source="https://www.work24.go.kr/"
        result.append({"id":f"work24-{i}","title":row["title"][:140],"category":category[:30],"summary":detail[:320],"eligibility":(row["eligibility"] or "대상과 세부 조건은 원문 공고에서 확인해 주세요.")[:180],"region":row["region"][:60],"start_date":row["start_date"][:30],"end_date":row["end_date"][:30],"tags":list({category,*(re.findall(r"[가-힣A-Za-z0-9]{2,}",row["title"]+" "+detail)[:12])}),"source_name":"고용24 OpenAPI","source_url":source,"is_sample":False})
    return result

def load_programs():
    endpoint=os.environ.get("WORK24_API_URL","").strip()
    key=os.environ.get("WORK24_API_KEY","").strip()
    if not endpoint or not key:return SAMPLES,"sample"
    if not endpoint.startswith("https://"):
        raise ValueError("WORK24_API_URL은 공식 HTTPS API 주소여야 합니다.")
    parts=urllib.parse.urlsplit(endpoint)
    query=urllib.parse.parse_qsl(parts.query,keep_blank_values=True)
    auth_name=os.environ.get("WORK24_AUTH_PARAM","authKey")
    query=[(k,v) for k,v in query if k!=auth_name]
    query.append((auth_name,key))
    url=urllib.parse.urlunsplit((parts.scheme,parts.netloc,parts.path,urllib.parse.urlencode(query),parts.fragment))
    req=urllib.request.Request(url,headers={"Accept":"application/xml, application/json","User-Agent":"Ieum24-MVP/1.0"})
    with urllib.request.urlopen(req,timeout=8) as response:
        raw=response.read(1_500_001)
        if len(raw)>1_500_000:raise ValueError("고용24 응답 크기 제한을 초과했습니다.")
        items=parse_programs(raw,response.headers.get("Content-Type",""))
    if not items:raise ValueError("API 응답에서 사업 목록을 찾지 못했습니다. 공식 개발명세와 항목 이름을 확인해 주세요.")
    return items,"work24"
