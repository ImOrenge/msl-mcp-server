from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import json
import logging
from datetime import datetime

class Prompt(BaseModel):
    """프롬프트 모델"""
    prompt_id: str
    content: str
    language: str = "ko"
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class PromptTemplate(BaseModel):
    """프롬프트 템플릿 모델"""
    template_id: str
    template: str
    parameters: List[str] = []
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}

class PromptManager:
    """프롬프트 관리자"""
    def __init__(self):
        self.prompts: Dict[str, Prompt] = {}
        self.templates: Dict[str, PromptTemplate] = {}
        self.logger = logging.getLogger("PromptManager")
        
        # 기본 템플릿 로드
        self.load_default_templates()
        
    def load_default_templates(self):
        """기본 템플릿 로드"""
        try:
            # 기본 템플릿 정의
            default_templates = [
                PromptTemplate(
                    template_id="window_command",
                    template="{program} {action}하기",
                    parameters=["program", "action"],
                    description="윈도우 프로그램 제어 명령"
                ),
                PromptTemplate(
                    template_id="input_command",
                    template="{text} 입력하기",
                    parameters=["text"],
                    description="텍스트 입력 명령"
                )
            ]
            
            # 템플릿 등록
            for template in default_templates:
                self.templates[template.template_id] = template
                
        except Exception as e:
            self.logger.error(f"Failed to load default templates: {str(e)}")
    
    async def create_prompt(self, prompt: Prompt) -> bool:
        """프롬프트 생성"""
        try:
            self.prompts[prompt.prompt_id] = prompt
            return True
        except Exception as e:
            self.logger.error(f"Failed to create prompt: {str(e)}")
            return False
    
    async def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """프롬프트 조회"""
        return self.prompts.get(prompt_id)
    
    async def update_prompt(self, prompt_id: str, content: str) -> bool:
        """프롬프트 업데이트"""
        try:
            if prompt_id in self.prompts:
                prompt = self.prompts[prompt_id]
                prompt.content = content
                prompt.updated_at = datetime.now()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to update prompt: {str(e)}")
            return False
    
    async def delete_prompt(self, prompt_id: str) -> bool:
        """프롬프트 삭제"""
        try:
            if prompt_id in self.prompts:
                del self.prompts[prompt_id]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete prompt: {str(e)}")
            return False
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """템플릿 조회"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[PromptTemplate]:
        """템플릿 목록 조회"""
        return list(self.templates.values()) 