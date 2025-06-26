# MSL MCP Server 개발 가이드

## 개발 환경 설정

### 필수 요구사항

- Python 3.8 이상
- Poetry (의존성 관리)
- Windows 10/11
- Git

### 개발 환경 설정

1. Python 설치:
   - [Python 공식 웹사이트](https://www.python.org/downloads/)에서 Python 3.8 이상 버전 설치
   - 설치 시 "Add Python to PATH" 옵션 선택

2. Poetry 설치:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. 저장소 클론:
   ```bash
   git clone https://github.com/yourusername/msl-mcp-server.git
   cd msl-mcp-server
   ```

4. 의존성 설치:
   ```bash
   poetry install
   ```

## 프로젝트 구조

```
msl-mcp-server/
├── src/
│   ├── server/
│   │   ├── fastmcp.py        # FastMCP 기본 서버
│   │   ├── resources.py      # 리소스 관리
│   │   ├── tools.py          # 도구 관리
│   │   ├── prompts.py        # 프롬프트 관리
│   │   └── msl_mcp_server.py # MSL MCP 서버 구현
│   └── main.py               # 서버 실행 스크립트
├── tests/                    # 테스트 코드
├── docs/                     # 문서
├── pyproject.toml           # 프로젝트 설정
└── README.md                # 프로젝트 문서
```

## 개발 가이드라인

### 코드 스타일

- Black 코드 포맷터 사용
- isort로 import 정렬
- Flake8 린터 사용
- Type hints 사용

### 테스트

- pytest 프레임워크 사용
- 테스트 커버리지 80% 이상 유지
- 단위 테스트와 통합 테스트 작성
- 테스트 데이터는 fixtures 사용

### Git 워크플로우

1. 브랜치 명명 규칙:
   - feature/: 새로운 기능
   - bugfix/: 버그 수정
   - hotfix/: 긴급 수정
   - release/: 릴리스 준비

2. 커밋 메시지 형식:
   ```
   [타입] 제목

   본문

   Footer
   ```

   타입:
   - feat: 새로운 기능
   - fix: 버그 수정
   - docs: 문서 수정
   - style: 코드 포맷팅
   - refactor: 코드 리팩토링
   - test: 테스트 코드
   - chore: 기타 변경사항

### 컴포넌트 개발 가이드

#### FastMCP 서버

- `FastMCP` 클래스 상속
- WebSocket 연결 관리 구현
- 컨텍스트 관리 구현
- 에러 처리 구현

예시:
```python
from fastmcp import FastMCP

class CustomServer(FastMCP):
    async def handle_message(self, message: dict) -> dict:
        # 메시지 처리 로직
        return response
```

#### 리소스 관리

- Pydantic 모델 사용
- CRUD 작업 구현
- 유효성 검사 추가
- 에러 처리 구현

예시:
```python
from pydantic import BaseModel

class Resource(BaseModel):
    id: str
    data: dict

class ResourceManager:
    async def create(self, resource: Resource) -> bool:
        # 생성 로직
        return True
```

#### 도구 개발

1. 도구 클래스 생성:
```python
class CustomTool:
    async def execute(self, params: dict) -> dict:
        # 실행 로직
        return result
```

2. 도구 등록:
```python
tool_manager.register_tool("custom_tool", CustomTool())
```

#### 프롬프트 템플릿

1. 템플릿 정의:
```python
template = PromptTemplate(
    template_id="custom",
    template="{{param1}} {{param2}}",
    parameters=["param1", "param2"]
)
```

2. 템플릿 사용:
```python
prompt = template.format(
    param1="value1",
    param2="value2"
)
```

### 에러 처리

1. 커스텀 예외 정의:
```python
class CustomError(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code
```

2. 에러 처리:
```python
try:
    result = await process()
except CustomError as e:
    handle_error(e)
```

### 로깅

- 구조화된 로깅 사용
- 적절한 로그 레벨 사용
- 컨텍스트 정보 포함

예시:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing request", extra={
    "request_id": request_id,
    "user_id": user_id
})
```

## 테스트 작성 가이드

### 단위 테스트

```python
import pytest

def test_feature():
    # 준비
    data = prepare_test_data()
    
    # 실행
    result = process_data(data)
    
    # 검증
    assert result.status == "success"
```

### 통합 테스트

```python
@pytest.mark.asyncio
async def test_workflow():
    # 시스템 설정
    server = setup_test_server()
    
    # 테스트 실행
    result = await server.process_request(test_request)
    
    # 결과 검증
    assert result.status == "success"
```

### 성능 테스트

```python
@pytest.mark.benchmark
def test_performance(benchmark):
    result = benchmark(process_data, test_data)
    assert result.success
```

## 배포 가이드

### Docker 배포

1. 이미지 빌드:
```bash
docker build -t msl-mcp-server .
```

2. 컨테이너 실행:
```bash
docker run -p 8000:8000 msl-mcp-server
```

### 환경 변수

필수 환경 변수:
- `MSL_MCP_HOST`: 서버 호스트
- `MSL_MCP_PORT`: 서버 포트
- `MSL_MCP_LOG_LEVEL`: 로그 레벨

### 모니터링

- 헬스 체크 엔드포인트 사용
- 로그 모니터링 설정
- 메트릭 수집

## 문제 해결

### 일반적인 문제

1. WebSocket 연결 실패
   - 포트 개방 확인
   - 방화벽 설정 확인
   - SSL/TLS 설정 확인

2. 성능 이슈
   - 로그 레벨 조정
   - 비동기 처리 확인
   - 리소스 사용량 모니터링

3. 메모리 누수
   - 연결 관리 확인
   - 리소스 정리 확인
   - 가비지 컬렉션 모니터링 