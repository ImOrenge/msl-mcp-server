# MSL-MCP-Server

MSL(Macro Script Language) 서버는 한국어 음성 명령을 처리하여 Windows 자동화를 수행하는 서버입니다.

## 기능

- 한국어 음성 명령 처리
- MSL 스크립트 생성 및 실행
- WebSocket을 통한 실시간 통신
- 마우스/키보드 자동화
- 에러 처리 및 재시도 로직

## 시스템 요구사항

- Python 3.8 이상
- Windows 10/11
- 관리자 권한 (자동화 기능 사용 시)

## 설치

1. 저장소 클론:
```bash
git clone https://github.com/yourusername/msl-mcp-server.git
cd msl-mcp-server
```

2. 가상 환경 생성 및 활성화:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

## 실행

1. 서버 실행:
```bash
uvicorn server.app:app --reload
```

2. API 문서 접근:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API 엔드포인트

### REST API

- `POST /api/voice`: 음성 명령 처리
- `POST /api/script`: MSL 스크립트 직접 실행
- `POST /api/stop`: 실행 중인 스크립트 중지
- `GET /health`: 서버 상태 확인

### WebSocket

- `ws://localhost:8000/ws`: 실시간 명령 처리

## 음성 명령 예시

- "100, 200 클릭해줘"
- "안녕하세요 입력해줘"
- "엔터 키 눌러줘"
- "3초 기다려줘"
- "300, 400으로 마우스 이동해줘"
- "100, 200에서 300, 400으로 드래그해줘"
- "위로 스크롤해줘"
- "컨트롤 + C 눌러줘"

## 개발

### 프로젝트 구조

```
msl-mcp-server/
├── src/
│   ├── msl/
│   │   ├── parser.py      # MSL 파서
│   │   ├── interpreter.py # MSL 인터프리터
│   │   └── generator.py   # MSL 생성기
│   ├── prompt/
│   │   └── analyzer.py    # 한국어 의도 분석기
│   └── server/
│       └── app.py         # FastAPI 서버
├── tests/                 # 테스트 코드
├── requirements.txt       # 의존성 목록
└── README.md             # 문서
```

### 테스트 실행

```bash
pytest tests/
```

## 라이선스

MIT License 