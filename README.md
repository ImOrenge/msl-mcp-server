# MSL MCP Server

Windows 자동화를 위한 한국어 음성 명령 처리 서버입니다. Context7 MCP 표준을 준수하는 FastAPI 기반의 WebSocket 및 REST API 서버입니다.

## 기능

- WebSocket 및 REST API 엔드포인트
- JSON-RPC 2.0 프로토콜 지원
- 한국어 음성 명령 처리
- Windows 자동화 기능
- 상태 추적 및 지속성
- 프롬프트 템플릿 시스템
- 종합적인 오류 처리
- 로깅 시스템
- 테스트 커버리지
- Docker 컨테이너화

## 요구사항

- Python 3.8 이상
- Poetry (의존성 관리)
- Windows 운영체제

## 설치

1. 저장소 클론:
```bash
git clone https://github.com/ImOrenge/msl-mcp-server.git
cd msl-mcp-server
```

2. Poetry를 사용하여 의존성 설치:
```bash
poetry install
```

## 실행

### 개발 모드

```bash
poetry run python src/main.py
```

### 프로덕션 모드 (Docker)

```bash
docker-compose up -d
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트

```bash
poetry run pytest
```

## 프로젝트 구조

```
msl-mcp-server/
├── src/
│   ├── server/
│   │   ├── fastmcp.py        # FastMCP 기본 서버 클래스
│   │   ├── resources.py      # 리소스 관리
│   │   ├── tools.py          # 도구 관리
│   │   ├── prompts.py        # 프롬프트 처리
│   │   └── msl_mcp_server.py # MSL MCP 서버 구현
│   └── main.py               # 메인 애플리케이션
├── tests/                    # 테스트 파일
├── docs/                     # 문서
├── Dockerfile               # Docker 설정
├── docker-compose.yml       # Docker Compose 설정
├── pyproject.toml          # Poetry 프로젝트 설정
└── README.md               # 프로젝트 설명
```

## 라이선스

MIT License 