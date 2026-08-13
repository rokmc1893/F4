#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워크넷(고용24) 오픈API 수집 스크립트 — 정책핏 인천 C파트

이 스크립트는 내(Claude)가 실행할 수 없다. Anthropic 샌드박스가 work24.go.kr /
apis.data.go.kr 도메인을 막아놨기 때문. 그래서 로컬(네 컴퓨터)에서 직접
실행해야 한다. 실행 후 나온 CSV를 나한테 다시 업로드하면 분석은 내가 이어서 함.

실행 전 준비:
    pip install requests

실행:
    python collect_worknet.py

산출물 (스크립트와 같은 폴더에 생성):
    01_wanted_raw.csv         — 워크넷 채용정보 원본 (인천 필터링 전)
    02_wanted_incheon.csv     — 근무지역에 '인천'이 들어간 것만 필터링
    03_common_code_TODO.txt   — 공통코드 API 호출 실패 시 안내
    04_ncs_dic_TODO.txt       — NCS 직무데이터사전 API 호출 실패 시 안내
"""

import requests
import xml.etree.ElementTree as ET
import csv
import time
import sys

# ============================================================
# 0. 인증키 — 스크린샷에서 확인된 값. 실제 사용 전 아래 두 가지 확인:
#    1) 이 키들이 진짜 본인 계정의 키가 맞는지
#    2) 이 스크립트를 깃허브(rokmc1893/F4)에 올릴 때는 절대 키 값이 그대로
#       들어간 채로 커밋하지 말 것 — 아래처럼 환경변수로 분리해서 쓰는 걸 권장
# ============================================================
AUTH_KEY_WANTED = "199f63d9-760d-4f4e-b8e0-512742cbeb7b"   # 채용정보
AUTH_KEY_JOBINFO = "d5283b5e-9f24-4d65-8e1d-31b0f67a265b"  # 직무정보(NCS 직무데이터사전)
AUTH_KEY_COMMCODE = "95e324e3-1706-42c4-8ecd-86e005c31e85" # 공통코드
AUTH_KEY_OCCUPATION = "75bbf22e-ddad-4e2c-93f6-77990ea61ae7" # 직업정보

# 환경변수가 있으면 그걸 우선 사용 (.env 방식 쓰고 싶으면 이 부분 활용)
import os
AUTH_KEY_WANTED = os.environ.get("WORKNET_KEY_WANTED", AUTH_KEY_WANTED)
AUTH_KEY_JOBINFO = os.environ.get("WORKNET_KEY_JOBINFO", AUTH_KEY_JOBINFO)
AUTH_KEY_COMMCODE = os.environ.get("WORKNET_KEY_COMMCODE", AUTH_KEY_COMMCODE)
AUTH_KEY_OCCUPATION = os.environ.get("WORKNET_KEY_OCCUPATION", AUTH_KEY_OCCUPATION)

BASE = "http://openapi.work.go.kr/opi/opi/opia"

# 인천 관련 사업(90개)에서 자주 나오는 산업/직무 키워드.
# region 코드가 불확실해서 API 서버 필터 대신 keyword로 넓게 가져온 뒤
# 근무지역 텍스트에 '인천'이 포함된 것만 로컬에서 다시 거른다.
KEYWORDS = [
    "바이오", "반도체", "AI", "인공지능", "로봇", "항공", "물류",
    "제조", "환경", "뷰티", "관광", "간호", "의료", "품질관리", "QA", "QC",
]


def fetch_wanted_page(keyword: str, start_page: int, display: int = 100):
    """채용정보 API 1페이지 호출. 반환: (전체건수, 이 페이지의 row 리스트)"""
    params = {
        "authKey": AUTH_KEY_WANTED,
        "callTp": "L",
        "returnType": "XML",
        "startPage": start_page,
        "display": display,
        "keyword": keyword,
    }
    resp = requests.get(f"{BASE}/wantedApi.do", params=params, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    total = root.findtext("total")
    total = int(total) if total and total.isdigit() else 0

    rows = []
    for w in root.findall(".//wanted"):
        row = {
            "구인인증번호": w.findtext("wantedAuthNo", ""),
            "회사명": w.findtext("company", ""),
            "채용제목": w.findtext("title", ""),
            "임금형태": w.findtext("salTpNm", ""),
            "급여": w.findtext("sal", ""),
            "근무지역": w.findtext("region", ""),
            "근무형태": w.findtext("holidayTpNm", ""),
            "최소학력": w.findtext("minEdubg", ""),
            "경력": w.findtext("career", ""),
            "등록일자": w.findtext("regDt", ""),
            "마감일자": w.findtext("closeDt", ""),
            "직종코드": w.findtext("jobsCd", ""),
            "검색키워드": keyword,
        }
        rows.append(row)
    return total, rows


def collect_wanted():
    print("[1/3] 채용정보 API 수집 시작 (키워드별로 반복)")
    all_rows = []
    for kw in KEYWORDS:
        start_page = 1
        while True:
            try:
                total, rows = fetch_wanted_page(kw, start_page)
            except Exception as e:
                print(f"  키워드 '{kw}' page {start_page} 실패: {e}")
                break
            if not rows:
                break
            all_rows.extend(rows)
            print(f"  키워드 '{kw}': page {start_page}, 누적 {len(all_rows)}건 (전체 {total}건)")
            if start_page * 100 >= total or start_page >= 10:  # 안전장치: 키워드당 최대 1000건
                break
            start_page += 1
            time.sleep(0.3)  # 서버 부하 방지

    if not all_rows:
        print("  ⚠ 수집된 데이터가 없다. authKey가 맞는지, wantedApi.do 응답 구조가")
        print("    바뀌지 않았는지 확인 필요. 아래로 원본 XML 한 번 찍어서 구조 확인해보자:")
        print(f"    {BASE}/wantedApi.do?authKey=YOUR_KEY&callTp=L&returnType=XML&startPage=1&display=5&keyword=바이오")
        return []

    with open("01_wanted_raw.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"  저장 완료: 01_wanted_raw.csv ({len(all_rows)}건, 키워드 중복 포함)")

    # 인천 필터링 + 중복 제거(구인인증번호 기준)
    seen = set()
    incheon_rows = []
    for r in all_rows:
        if "인천" in r["근무지역"] and r["구인인증번호"] not in seen:
            seen.add(r["구인인증번호"])
            incheon_rows.append(r)

    with open("02_wanted_incheon.csv", "w", newline="", encoding="utf-8-sig") as f:
        if incheon_rows:
            writer = csv.DictWriter(f, fieldnames=list(incheon_rows[0].keys()))
            writer.writeheader()
            writer.writerows(incheon_rows)
    print(f"  저장 완료: 02_wanted_incheon.csv (인천 필터링 후 {len(incheon_rows)}건, 중복 제거됨)")
    return incheon_rows


def try_common_code():
    """
    공통코드 API — 정확한 엔드포인트 이름을 검색으로 확정하지 못했다.
    아래는 워크넷 API가 보통 따르는 명명 규칙(opia 하위 *.do)을 참고한 추정 시도이고,
    실패하면 openapi.work.go.kr 로그인 후 '서비스 소개 및 신청' 페이지에서
    공통코드 API 옆의 '개발가이드' 버튼을 눌러 정확한 URL과 파라미터명을 확인해야 한다.
    확인되면 이 함수의 endpoint 변수만 고치면 된다.
    """
    print("[2/3] 공통코드 API 시도 (직종코드 해석용)")
    candidates = ["commCodeApi.do", "codeApi.do", "commonCodeApi.do"]
    for ep in candidates:
        try:
            resp = requests.get(
                f"{BASE}/{ep}",
                params={"authKey": AUTH_KEY_COMMCODE, "returnType": "XML", "comCd": "00"},
                timeout=10,
            )
            if resp.status_code == 200 and b"<" in resp.content[:5]:
                with open("03_common_code_raw.xml", "wb") as f:
                    f.write(resp.content)
                print(f"  응답 받음 (엔드포인트: {ep}) → 03_common_code_raw.xml 저장, 구조 확인 필요")
                return
        except Exception:
            continue
    with open("03_common_code_TODO.txt", "w", encoding="utf-8") as f:
        f.write(
            "공통코드 API 엔드포인트를 자동으로 못 찾았다.\n"
            "openapi.work.go.kr 로그인 → 마이페이지 → OPEN-API 신청현황 → '공통코드' 클릭\n"
            "→ 개발가이드/명세서에서 정확한 URL과 comCd 파라미터 값을 확인해서 알려주면\n"
            "collect_worknet.py의 try_common_code() 함수를 바로 고쳐줄게.\n"
        )
    print("  ⚠ 실패 → 03_common_code_TODO.txt 참고")


def try_ncs_dic():
    """NCS 직무데이터사전 API — 마찬가지로 정확한 엔드포인트 미확정."""
    print("[3/3] NCS 직무데이터사전 API 시도")
    candidates = ["jobDicApi.do", "ncsDicApi.do", "jobinfoApi.do"]
    for ep in candidates:
        try:
            resp = requests.get(
                f"{BASE}/{ep}",
                params={"authKey": AUTH_KEY_JOBINFO, "returnType": "XML", "keyword": "바이오"},
                timeout=10,
            )
            if resp.status_code == 200 and b"<" in resp.content[:5]:
                with open("04_ncs_dic_raw.xml", "wb") as f:
                    f.write(resp.content)
                print(f"  응답 받음 (엔드포인트: {ep}) → 04_ncs_dic_raw.xml 저장, 구조 확인 필요")
                return
        except Exception:
            continue
    with open("04_ncs_dic_TODO.txt", "w", encoding="utf-8") as f:
        f.write(
            "NCS 직무데이터사전 API 엔드포인트를 자동으로 못 찾았다.\n"
            "openapi.work.go.kr 로그인 → 마이페이지 → OPEN-API 신청현황 → '직무정보' 클릭\n"
            "→ 개발가이드/명세서에서 정확한 URL과 파라미터를 확인해서 알려주면\n"
            "collect_worknet.py의 try_ncs_dic() 함수를 바로 고쳐줄게.\n"
        )
    print("  ⚠ 실패 → 04_ncs_dic_TODO.txt 참고")


if __name__ == "__main__":
    collect_wanted()
    try_common_code()
    try_ncs_dic()
    print("\n완료. 이 폴더에 생긴 CSV/XML/TXT 파일 전부 Claude한테 업로드하면 이어서 분석함.")
