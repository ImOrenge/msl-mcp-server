# MSL MCP Server

🎮 **MSL (Macro Scripting Language) MCP Server with OpenAI Integration**

AI 기반 MSL 스크립트 생성 및 분석을 위한 Model Context Protocol (MCP) 서버입니다.

## ✨ 주요 기능

### 🤖 AI 기반 MSL 생성
- **자연어 → MSL 변환**: "Q키 누르고 500ms 후 W키 누르기" → `Q,(500),W`
- **OpenAI GPT-4o 통합**: 최신 AI 모델로 정확한 스크립트 생성
- **게임 컨텍스트 인식**: FPS, MMORPG, RTS 등 게임별 최적화

### 🔍 스크립트 분석 및 검증
- **구문 분석**: MSL 문법 검증 및 AST 생성
- **성능 분석**: 실행 시간 및 복잡도 계산
- **보안 검증**: 잠재적 위험 요소 탐지

### ⚡ 최적화 및 교육
- **자동 최적화**: 스크립트 성능 향상 및 중복 제거
- **교육적 설명**: 초보자를 위한 상세한 스크립트 해설
- **카테고리별 예제**: 수준별, 게임별 학습 자료

## 🛠️ MCP 도구

| 도구 | 설명 | AI 활용 |
|------|------|---------|
| `parse_msl` | MSL 스크립트 파싱 및 구문 분석 | ❌ |
| `generate_msl` | 자연어로 MSL 스크립트 생성 | ✅ |
| `validate_msl` | 스크립트 검증 및 오류 탐지 | ❌ |
| `optimize_msl` | 스크립트 최적화 | ✅ |
| `explain_msl` | 스크립트 교육적 설명 | ✅ |
| `msl_examples` | 카테고리별 예제 제공 | ❌ |

## 🚀 빠른 시작

### 1. 필수 요구사항
- Python 3.11+
- OpenAI API 키

### 2. 설치 및 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
export OPENAI_API_KEY="your-api-key-here"

# 서버 실행
python server.py
```

### 3. Docker 실행
```bash
# 이미지 빌드
docker build -t msl-mcp-server .

# 컨테이너 실행
docker run -e OPENAI_API_KEY="your-api-key" msl-mcp-server
```

## 📝 사용 예시

### MSL 스크립트 생성
```python
# 자연어로 매크로 생성
generate_msl(
    prompt="공격키 Q를 누르고 500ms 후 스킬키 W를 누르는 매크로",
    game_context="MMORPG",
    complexity="medium"
)
```

### 스크립트 최적화
```python
# 기존 스크립트 최적화
optimize_msl(
    script="Q,(500),W,(500),E,(500),R",
    level="standard",
    target="performance"
)
```

### 스크립트 설명
```python
# 교육적 설명 생성
explain_msl(
    script="Q+Shift,(100),W*3",
    audience="beginner",
    include_tips=True
)
```

## 🎯 MSL 언어 특징

### 기본 연산자
- `,` (순차): 키를 순서대로 실행
- `+` (동시): 키를 동시에 실행  
- `>` (홀드): 키를 누르고 있기
- `|` (병렬): 병렬 실행
- `~` (토글): 토글 동작
- `*` (반복): 반복 실행
- `&` (연속): 연속 실행

### 타이밍 제어
- `(ms)`: 지연 시간
- `[ms]`: 홀드 시간
- `{ms}`: 간격 시간
- `<ms>`: 페이드 시간

### 고급 기능
- `$var`: 변수 사용
- `@(x,y)`: 마우스 좌표
- `wheel+/-`: 마우스 휠

## ⚙️ 설정

### 환경변수
```bash
# OpenAI 설정
MSL_OPENAI_API_KEY=your_api_key
MSL_OPENAI_MODEL=gpt-4o
MSL_OPENAI_MAX_TOKENS=2000

# 서버 설정
MSL_DEBUG=false
MSL_MAX_CONCURRENT_REQUESTS=10
```

## 🔧 개발

### 프로젝트 구조
```
mslmcpserver/
├── server.py              # MCP 서버 메인
├── msl/                    # MSL 파서/AST
├── tools/                  # MCP 도구들
├── ai/                     # OpenAI 통합
├── config/                 # 설정 관리
├── requirements.txt        # 의존성
├── Dockerfile             # Docker 설정
└── smithery.yaml          # Smithery 배포
```

### 개발 환경 설정
```bash
# 개발 의존성 설치
pip install -r requirements.txt

# 테스트 실행
pytest

# 코드 포맷팅
black .
flake8 .
```

## 📚 문서

- **MSL 언어 가이드**: [MSL Language Guide](docs/msl-guide.md)
- **API 참조**: [API Reference](docs/api-reference.md)
- **개발 가이드**: [Development Guide](docs/development.md)

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 지원

- **Issues**: [GitHub Issues](https://github.com/your-repo/msl-mcp-server/issues)
- **Documentation**: [Wiki](https://github.com/your-repo/msl-mcp-server/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/msl-mcp-server/discussions)

---

**Made with ❤️ for the gaming community** 