# 이음24 MVP

참여 이력에서 다음 고용서비스를 잇는 공모전 시연용 웹 MVP입니다. 관심 분야를 고르면 고용24 공개 정보(연동 전에는 예시 목록)를 살펴보고, 질문을 입력하면 Gemini API가 후보 정보와 질문을 바탕으로 참고 설명을 만듭니다. 신청 자격을 자동 판정하지 않습니다.

## 구성

- 서비스 미리보기: `https://<배포 후 Vercel 주소>`
- 화면: 서비스 소개, 지원사업 탐색, AI 안내, 서비스 설명
- 프런트엔드: 순수 HTML/CSS/JavaScript
- 백엔드: Vercel Python Serverless Functions (`api/`)
- 데이터: 고용24 OPEN-API 정부지원일자리정보·훈련과정 (키와 공식 API 주소를 설정하면 연결)
- 생성형 AI: Gemini API, 모델 기본값 `gemini-3.5-flash-lite`

## 실행

Python 3.12 이상과 Node.js가 있는 환경에서 저장소 루트에서:

```powershell
python dev_server.py
```

미리보기 주소 `http://localhost:8000`에서 화면·반응형 레이아웃과 Vercel Python 핸들러를 함께 볼 수 있습니다. 키가 설정되지 않았을 때는 예시 데이터 및 AI 키 설정 안내가 표시됩니다.

```powershell
npx vercel dev
```

`npx vercel dev`는 계정 로그인과 프로젝트 연결이 필요한 배포 도구입니다.

## 환경 변수

API 키는 브라우저에 넣거나 소스 코드·README·화면 캡처에 적지 않습니다. 로컬에서는 `.env.local`에, 배포 시에는 Vercel 프로젝트의 **Settings → Environment Variables**에 설정하세요. `.env.local`은 Git에 포함되지 않습니다.

| 변수 | 설명 |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio에서 발급한 Gemini API 키 |
| `GEMINI_MODEL` | 선택 변수. 기본 `gemini-3.5-flash-lite` |
| `WORK24_API_URL` | 고용24에서 승인받은 API의 공식 HTTPS 엔드포인트 |
| `WORK24_API_KEY` | 고용24 OPEN-API 승인 키 |
| `WORK24_AUTH_PARAM` | 공식 개발명세에 적힌 인증 쿼리 매개변수 이름. 기본 `authKey` |

고용24 API 신청과 발급은 별도 심사를 거칩니다. 서비스별 개발명세에서 실제 엔드포인트·인증 매개변수·응답 항목을 확인한 다음 설정하세요. API 키가 없으면 화면은 시연용 예시 정보를 명시해 보여 줍니다. 설정된 API 호출이 실패하면 예시 정보로 위장하지 않고 오류를 안내합니다.

Gemini API 무료 이용은 모델·계정별 할당량과 조건에 따릅니다. 무료 등급 입력 데이터는 Google 서비스 개선에 사용될 수 있으므로, 실명·주민등록번호·고객 문서 등 개인정보나 비공개 업무자료를 입력하지 마세요. 키에는 Gemini API만 허용하는 제한을 설정하고 호출 사용량을 확인하세요.

## 배포

1. GitHub 저장소에 이 프로젝트를 올립니다.
2. Vercel에서 해당 저장소를 가져와 배포합니다. 프로젝트 루트 디렉터리는 저장소 루트(`.`)입니다.
3. Vercel 프로젝트의 Settings → Environment Variables에 Gemini 키를 등록합니다.
4. 고용24 OpenAPI 승인을 받은 다음 공식 개발명세에 맞는 API 환경 변수를 추가합니다.
5. 새 배포 후 Vercel URL에서 메뉴 이동, 모바일 레이아웃, 예시/실제 출처 배지, AI 정상 응답 및 오류 안내를 확인합니다.

Vercel Hobby는 개인·비상업적 사용 범위의 무료 플랜입니다. 계정별 기능·할당량은 바뀔 수 있습니다. `vercel.json`의 Python 함수 런타임도 Vercel 공식 안내에서 Beta로 안내되어 있으므로 과제 운영 전 다시 확인하세요.

## 시연 흐름

1. `지원사업 찾기`에서 관심 분야와 지역을 골라 공개 정보 또는 표시된 예시 정보를 봅니다.
2. `AI 안내`에 500자 이내로 개인정보 없는 질문을 씁니다.
3. AI가 후보 ID를 목록에 있는 항목으로 제한해 이유·다음 확인 항목·출처를 보여 줍니다.
4. 빈 입력, API 미설정, API 오류, 한도 초과, 응답 지연 메시지를 확인합니다.

AI 안내는 참고 정보입니다. 서비스는 지원 적격성, 지급 여부, 부정수급 또는 기업의 채용 결정을 판정하지 않습니다. 사용자 입력은 저장하지 않습니다.

## 미리보기 증빙

`screenshots/`에는 데스크톱·모바일 전체 화면과 AI 입력 및 키 설정 안내 화면이 들어 있습니다. AI 캡처는 키 미설정 상태를 사실대로 보여 주며 실제 AI 생성 결과 캡처가 아닙니다. AI 키를 설정한 뒤 생성 결과를 다시 확인해 제출 증빙을 교체하세요. 재캡처에는 Playwright와 Microsoft Edge가 필요합니다.
