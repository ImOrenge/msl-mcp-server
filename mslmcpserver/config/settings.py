"""
MSL MCP 서버 설정

환경변수와 기본 설정값들을 관리합니다.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field


class MSLSettings(BaseSettings):
    """MSL MCP 서버 설정 클래스"""
    
    # 서버 기본 설정
    server_name: str = Field(default="MSL MCP Server", description="서버 이름")
    server_version: str = Field(default="1.0.0", description="서버 버전")
    debug: bool = Field(default=False, description="디버그 모드 활성화")
    
    # OpenAI API 설정
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API 키")
    openai_model: str = Field(default="gpt-4o", description="사용할 OpenAI 모델")
    openai_max_tokens: int = Field(default=2000, description="최대 토큰 수")
    openai_temperature: float = Field(default=0.7, description="창의성 설정")
    
    # MSL 파서 설정
    msl_max_script_length: int = Field(default=10000, description="최대 스크립트 길이")
    msl_timeout_seconds: int = Field(default=30, description="스크립트 처리 타임아웃")
    
    # 로깅 설정
    log_level: str = Field(default="INFO", description="로그 레벨")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="로그 포맷")
    
    # 도구별 설정
    enable_parse_tool: bool = Field(default=True, description="파싱 도구 활성화")
    enable_generate_tool: bool = Field(default=True, description="생성 도구 활성화")
    enable_validate_tool: bool = Field(default=True, description="검증 도구 활성화")
    enable_optimize_tool: bool = Field(default=True, description="최적화 도구 활성화")
    enable_explain_tool: bool = Field(default=True, description="설명 도구 활성화")
    enable_examples_tool: bool = Field(default=True, description="예제 도구 활성화")
    
    # 성능 설정
    max_concurrent_requests: int = Field(default=10, description="최대 동시 요청 수")
    request_timeout: int = Field(default=60, description="요청 타임아웃 (초)")
    
    class Config:
        env_file = ".env"
        env_prefix = "MSL_"
        case_sensitive = False


class ConfigManager:
    """설정 관리자 클래스"""
    
    def __init__(self):
        self._settings = None
        self._patterns = None
        self._examples = None
    
    @property
    def settings(self) -> MSLSettings:
        """설정 인스턴스 반환"""
        if self._settings is None:
            self._settings = MSLSettings()
        return self._settings
    
    def get_openai_config(self) -> Dict[str, Any]:
        """OpenAI 설정 반환"""
        settings = self.settings
        return {
            "api_key": settings.openai_api_key or os.environ.get("OPENAI_API_KEY"),
            "model": settings.openai_model,
            "max_tokens": settings.openai_max_tokens,
            "temperature": settings.openai_temperature
        }
    
    def get_msl_config(self) -> Dict[str, Any]:
        """MSL 파서 설정 반환"""
        settings = self.settings
        return {
            "max_script_length": settings.msl_max_script_length,
            "timeout_seconds": settings.msl_timeout_seconds
        }
    
    def get_enabled_tools(self) -> Dict[str, bool]:
        """활성화된 도구 목록 반환"""
        settings = self.settings
        return {
            "parse_msl": settings.enable_parse_tool,
            "generate_msl": settings.enable_generate_tool,
            "validate_msl": settings.enable_validate_tool,
            "optimize_msl": settings.enable_optimize_tool,
            "explain_msl": settings.enable_explain_tool,
            "msl_examples": settings.enable_examples_tool
        }
    
    def load_msl_patterns(self) -> Dict[str, Any]:
        """MSL 패턴 데이터 로드"""
        if self._patterns is None:
            # 기본 패턴들
            self._patterns = {
                "basic_keys": {
                    "enter": "Enter",
                    "space": "Space", 
                    "escape": "Escape",
                    "tab": "Tab",
                    "backspace": "Backspace"
                },
                "modifier_keys": {
                    "ctrl": "Ctrl",
                    "shift": "Shift",
                    "alt": "Alt",
                    "win": "Win"
                },
                "mouse_actions": {
                    "left_click": "LMB",
                    "right_click": "RMB", 
                    "middle_click": "MMB",
                    "scroll_up": "wheel+",
                    "scroll_down": "wheel-"
                },
                "operators": {
                    "sequential": ",",
                    "simultaneous": "+",
                    "hold": ">",
                    "parallel": "|",
                    "toggle": "~",
                    "repeat": "*",
                    "continuous": "&"
                },
                "timing": {
                    "delay": "({})",
                    "hold": "[{}]",
                    "interval": "{{{}}}", 
                    "fade": "<{}>"
                }
            }
        return self._patterns
    
    def load_msl_examples(self) -> Dict[str, Any]:
        """MSL 예제 데이터 로드"""
        if self._examples is None:
            self._examples = {
                "basic": [
                    {
                        "name": "단순 키 누르기",
                        "script": "A",
                        "description": "A키를 한 번 누릅니다"
                    },
                    {
                        "name": "순차 키 누르기", 
                        "script": "A,B,C",
                        "description": "A, B, C 키를 순서대로 누릅니다"
                    }
                ],
                "intermediate": [
                    {
                        "name": "조합키 사용",
                        "script": "Ctrl+C",
                        "description": "Ctrl과 C를 동시에 누릅니다"
                    },
                    {
                        "name": "지연이 있는 키 입력",
                        "script": "A,(500),B",
                        "description": "A키를 누르고 500ms 후 B키를 누릅니다"
                    }
                ],
                "advanced": [
                    {
                        "name": "마우스와 키보드 조합",
                        "script": "@(100,200),LMB,(100),Ctrl+V",
                        "description": "(100,200) 좌표로 이동 후 클릭하고 100ms 후 붙여넣기"
                    },
                    {
                        "name": "반복 동작",
                        "script": "Q*5",
                        "description": "Q키를 5번 반복해서 누릅니다"
                    }
                ]
            }
        return self._examples
    
    def validate_settings(self) -> bool:
        """설정 유효성 검증"""
        settings = self.settings
        
        # OpenAI API 키 확인
        if not settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
            print("⚠️  경고: OpenAI API 키가 설정되지 않았습니다. AI 기능이 제한될 수 있습니다.")
            return False
        
        # 모델명 검증
        valid_models = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
        if settings.openai_model not in valid_models:
            print(f"⚠️  경고: 알 수 없는 OpenAI 모델입니다: {settings.openai_model}")
        
        # 토큰 수 검증
        if settings.openai_max_tokens < 100 or settings.openai_max_tokens > 4000:
            print(f"⚠️  경고: 비정상적인 최대 토큰 수입니다: {settings.openai_max_tokens}")
        
        return True


# 전역 설정 인스턴스
config_manager = ConfigManager()


def get_settings() -> MSLSettings:
    """전역 설정 인스턴스 반환"""
    return config_manager.settings


def get_config_manager() -> ConfigManager:
    """설정 관리자 인스턴스 반환"""
    return config_manager 