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
        default_templates = {
            "voice_command": PromptTemplate(
                template_id="voice_command",
                template="사용자가 '{command}'라고 말했습니다. 이 명령을 실행하기 위한 Windows 자동화 동작을 생성해주세요.",
                parameters=["command"],
                description="음성 명령을 Windows 자동화 동작으로 변환하는 템플릿"
            ),
            "error_handling": PromptTemplate(
                template_id="error_handling",
                template="명령 실행 중 오류가 발생했습니다: {error}. 이 오류를 해결하기 위한 제안사항을 제공해주세요.",
                parameters=["error"],
                description="오류 처리를 위한 템플릿"
            )
        }
        
        for template in default_templates.values():
            self.register_template(template)
            
    def register_template(self, template: PromptTemplate) -> bool:
        """템플릿 등록"""
        try:
            self.templates[template.template_id] = template
            return True
        except Exception as e:
            self.logger.error(f"Error registering template: {str(e)}")
            return False
            
    async def create_prompt(self, template_id: str, parameters: Dict[str, str]) -> Optional[Prompt]:
        """프롬프트 생성"""
        if template_id not in self.templates:
            return None
            
        try:
            template = self.templates[template_id]
            content = template.template.format(**parameters)
            
            prompt = Prompt(
                prompt_id=f"{template_id}_{datetime.now().timestamp()}",
                content=content,
                metadata={
                    "template_id": template_id,
                    "parameters": parameters
                }
            )
            
            self.prompts[prompt.prompt_id] = prompt
            return prompt
            
        except Exception as e:
            self.logger.error(f"Error creating prompt: {str(e)}")
            return None
            
    async def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """프롬프트 조회"""
        return self.prompts.get(prompt_id)
        
    async def update_prompt(self, prompt_id: str, content: str) -> bool:
        """프롬프트 업데이트"""
        if prompt_id in self.prompts:
            prompt = self.prompts[prompt_id]
            prompt.content = content
            prompt.updated_at = datetime.now()
            return True
        return False
        
    async def delete_prompt(self, prompt_id: str) -> bool:
        """프롬프트 삭제"""
        if prompt_id in self.prompts:
            del self.prompts[prompt_id]
            return True
        return False
        
    def list_templates(self) -> List[PromptTemplate]:
        """템플릿 목록 조회"""
        return list(self.templates.values()) 