"""
VoiceMacro Pro 통합 테스트 스크립트
GPT-4o 실시간 음성 인식 → 매크로 매칭 → 실행까지의 전체 파이프라인 테스트
"""

import asyncio
import time
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from backend.services.gpt4o_transcription_service import GPT4oTranscriptionService
from backend.services.macro_matching_service import get_macro_matching_service
from backend.services.macro_service import macro_service
from backend.services.macro_execution_service import macro_execution_service
from backend.utils.config import Config


class IntegratedVoiceMacroTest:
    """통합 음성 매크로 테스트 클래스"""
    
    def __init__(self):
        """테스트 초기화"""
        self.gpt4o_service = None
        self.matching_service = get_macro_matching_service()
        
        # 테스트 결과 저장
        self.test_results = []
        
        print("🔧 VoiceMacro Pro 통합 테스트 초기화 중...")
    
    async def setup_services(self):
        """서비스 설정 및 초기화"""
        print("\n📋 1단계: 서비스 초기화")
        
        # GPT-4o 서비스 초기화 (API 키가 있는 경우에만)
        if Config.OPENAI_API_KEY and Config.GPT4O_ENABLED:
            try:
                self.gpt4o_service = GPT4oTranscriptionService(Config.OPENAI_API_KEY)
                self.gpt4o_service.set_transcription_callback(self.handle_transcription_result)
                
                # 연결 시도
                connected = await self.gpt4o_service.connect()
                if connected:
                    print("✅ GPT-4o 트랜스크립션 서비스 연결 성공")
                else:
                    print("⚠️ GPT-4o 서비스 연결 실패, 시뮬레이션 모드로 진행")
                    self.gpt4o_service = None
            except Exception as e:
                print(f"⚠️ GPT-4o 서비스 초기화 실패: {e}, 시뮬레이션 모드로 진행")
                self.gpt4o_service = None
        else:
            print("⚠️ GPT-4o API 키가 없어 시뮬레이션 모드로 진행")
            self.gpt4o_service = None
        
        # 매크로 데이터베이스 확인
        macros = macro_service.get_all_macros()
        print(f"📊 등록된 매크로: {len(macros)}개")
        
        if len(macros) < 5:
            print("⚠️ 테스트용 매크로가 부족합니다. 기본 매크로를 생성합니다.")
            await self.create_test_macros()
    
    async def create_test_macros(self):
        """테스트용 기본 매크로 생성"""
        test_macros = [
            {
                "name": "공격 매크로",
                "voice_command": "공격해",
                "action_type": "combo",
                "key_sequence": "Q,W,E",
                "settings": '{"delay": 100}'
            },
            {
                "name": "포션 사용",
                "voice_command": "포션 먹어",
                "action_type": "key",
                "key_sequence": "H",
                "settings": '{"hold_time": 0}'
            },
            {
                "name": "스킬 콤보",
                "voice_command": "스킬 사용",
                "action_type": "combo", 
                "key_sequence": "R,T,Y",
                "settings": '{"delay": 150}'
            },
            {
                "name": "점프 공격",
                "voice_command": "점프해서 공격",
                "action_type": "combo",
                "key_sequence": "Space,Q",
                "settings": '{"delay": 200}'
            },
            {
                "name": "회복 물약",
                "voice_command": "회복해",
                "action_type": "key",
                "key_sequence": "G",
                "settings": '{"hold_time": 0}'
            }
        ]
        
        for macro_data in test_macros:
            try:
                result = macro_service.create_macro(
                    name=macro_data["name"],
                    voice_command=macro_data["voice_command"],
                    action_type=macro_data["action_type"],
                    key_sequence=macro_data["key_sequence"],
                    settings=macro_data["settings"]
                )
                if result.get("success"):
                    print(f"✅ 테스트 매크로 생성: {macro_data['name']}")
                else:
                    print(f"⚠️ 매크로 생성 실패: {macro_data['name']} - {result.get('message')}")
            except Exception as e:
                print(f"❌ 매크로 생성 오류: {macro_data['name']} - {e}")
    
    async def handle_transcription_result(self, transcription_data):
        """GPT-4o 트랜스크립션 결과 처리"""
        if transcription_data.get("type") == "final":
            text = transcription_data.get("text", "").strip()
            confidence = transcription_data.get("confidence", 0.0)
            
            print(f"🎤 음성 인식 결과: '{text}' (신뢰도: {confidence:.2f})")
            
            # 매크로 매칭 및 실행
            await self.process_voice_command(text, confidence)
    
    async def process_voice_command(self, text: str, confidence: float):
        """음성 명령어 처리 (매칭 + 실행)"""
        try:
            # 매크로 매칭
            matches = self.matching_service.find_matching_macros(text)
            
            if matches:
                best_match = matches[0]
                print(f"🎯 매크로 매칭: '{best_match.macro_name}' (유사도: {best_match.similarity:.2f})")
                
                # 매크로 실행
                execution_result = await self.execute_macro(best_match.macro_id, text, confidence)
                
                # 결과 저장
                self.test_results.append({
                    "input_text": text,
                    "confidence": confidence,
                    "matched_macro": best_match.macro_name,
                    "similarity": best_match.similarity,
                    "execution_success": execution_result,
                    "timestamp": time.time()
                })
                
            else:
                print(f"❌ 매칭되는 매크로가 없습니다: '{text}'")
                self.test_results.append({
                    "input_text": text,
                    "confidence": confidence,
                    "matched_macro": None,
                    "similarity": 0.0,
                    "execution_success": False,
                    "timestamp": time.time()
                })
                
        except Exception as e:
            print(f"❌ 음성 명령어 처리 오류: {e}")
    
    async def execute_macro(self, macro_id: int, original_text: str, confidence: float) -> bool:
        """매크로 실행"""
        try:
            print(f"⚡ 매크로 실행 시작: ID={macro_id}")
            
            # 매크로 데이터 가져오기
            macro_data = None
            macros = macro_service.get_all_macros()
            for macro in macros:
                if macro.get('id') == macro_id:
                    macro_data = macro
                    break
            
            if not macro_data:
                print(f"❌ 매크로를 찾을 수 없습니다: ID={macro_id}")
                return False
            
            # 매크로 실행 서비스 인스턴스 생성 및 비동기 실행
            from backend.services.macro_execution_service import MacroExecutionService
            execution_service = MacroExecutionService()
            
            # 비동기 매크로 실행
            success = await execution_service.execute_macro(macro_data)
            
            if success:
                print(f"✅ 매크로 실행 완료: {macro_data.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ 매크로 실행 실패: {macro_data.get('name', 'Unknown')}")
                return False
                
        except Exception as e:
            print(f"❌ 매크로 실행 오류: {e}")
            return False
    
    async def test_voice_simulation(self):
        """음성 명령어 시뮬레이션 테스트"""
        print("\n📋 2단계: 음성 명령어 시뮬레이션 테스트")
        
        # 테스트할 음성 명령어들
        test_commands = [
            {"text": "공격해", "confidence": 0.95},
            {"text": "포션 먹어", "confidence": 0.90},
            {"text": "스킬 사용", "confidence": 0.88},
            {"text": "점프해서 공격", "confidence": 0.85},
            {"text": "회복해", "confidence": 0.92},
            {"text": "어택", "confidence": 0.87},  # 동의어 테스트
            {"text": "치료", "confidence": 0.82},  # 부분 매칭 테스트
            {"text": "알 수 없는 명령어", "confidence": 0.70},  # 매칭 실패 테스트
        ]
        
        print(f"🎯 {len(test_commands)}개의 테스트 명령어 실행 중...")
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n--- 테스트 {i}/{len(test_commands)} ---")
            await self.process_voice_command(command["text"], command["confidence"])
            await asyncio.sleep(0.5)  # 잠시 대기
    
    async def test_real_time_audio(self):
        """실시간 오디오 테스트 (GPT-4o가 연결된 경우)"""
        if not self.gpt4o_service:
            print("\n⚠️ GPT-4o 서비스가 연결되지 않아 실시간 오디오 테스트를 건너뜁니다.")
            return
        
        print("\n📋 3단계: 실시간 오디오 테스트")
        print("🎤 실제 마이크로 음성 명령어를 말해보세요.")
        print("💡 예시: '공격해', '포션 먹어', '스킬 사용' 등")
        print("⏰ 5초간 녹음합니다...")
        
        try:
            # 실제 마이크 입력 구현
            await self._record_and_process_real_audio()
            
        except Exception as e:
            print(f"❌ 실시간 오디오 테스트 오류: {e}")
    
    async def _record_and_process_real_audio(self):
        """실제 마이크에서 오디오를 녹음하고 처리"""
        try:
            import sounddevice as sd
            import numpy as np
            
            # 오디오 설정 (GPT-4o 최적화)
            sample_rate = 24000  # 24kHz
            channels = 1  # Mono
            duration = 5.0  # 5초간 녹음
            
            print(f"🎙️ 마이크 녹음 시작 ({duration}초)...")
            
            # 실제 마이크에서 녹음
            audio_data = sd.rec(
                int(duration * sample_rate), 
                samplerate=sample_rate, 
                channels=channels,
                dtype='float32'
            )
            
            # 녹음 완료 대기
            sd.wait()
            
            print("📡 오디오 데이터를 GPT-4o로 전송 중...")
            
            # float32 numpy array를 int16 PCM으로 변환
            audio_int16 = (audio_data.flatten() * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()
            
            # 청크 단위로 전송 (100ms씩)
            chunk_size = int(sample_rate * 0.1 * 2)  # 100ms * 2 bytes per sample
            total_chunks = len(audio_bytes) // chunk_size
            
            for i in range(total_chunks):
                start_idx = i * chunk_size
                end_idx = min(start_idx + chunk_size, len(audio_bytes))
                chunk = audio_bytes[start_idx:end_idx]
                
                # GPT-4o로 오디오 청크 전송
                await self.gpt4o_service.send_audio_chunk(chunk)
                
                # 짧은 대기 (실시간 시뮬레이션)
                await asyncio.sleep(0.01)
            
            # 마지막 오디오 버퍼 커밋
            await self.gpt4o_service.commit_audio_buffer()
            
            print("✅ 오디오 전송 완료. 트랜스크립션 결과를 기다리는 중...")
            
            # 트랜스크립션 결과 대기 (최대 5초)
            await asyncio.sleep(5)
            
        except ImportError:
            print("⚠️ sounddevice 라이브러리가 설치되지 않았습니다.")
            print("   'pip install sounddevice' 명령으로 설치해주세요.")
            
            # 대안: 시뮬레이션 모드
            await self._simulate_audio_input()
            
        except Exception as e:
            print(f"❌ 실제 마이크 녹음 오류: {e}")
            print("🔄 시뮬레이션 모드로 전환합니다.")
            await self._simulate_audio_input()
    
    async def _simulate_audio_input(self):
        """오디오 입력 시뮬레이션"""
        print("🎭 오디오 입력 시뮬레이션 모드")
        
        # 가상의 오디오 데이터 생성 (사인파)
        import math
        sample_rate = 24000
        duration = 1.0  # 1초
        frequency = 440  # A4 음계
        
        samples = []
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            sample = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * t))
            samples.extend([sample & 0xFF, (sample >> 8) & 0xFF])
        
        audio_bytes = bytes(samples)
        
        # 청크 단위로 전송
        chunk_size = 2400  # 100ms chunk
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i+chunk_size]
            await self.gpt4o_service.send_audio_chunk(chunk)
            await asyncio.sleep(0.1)  # 100ms 간격
        
        await self.gpt4o_service.commit_audio_buffer()
        print("✅ 시뮬레이션 오디오 전송 완료")
        
        # 잠시 대기
        await asyncio.sleep(2)
    
    def print_test_results(self):
        """테스트 결과 출력"""
        print("\n📊 테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_matches = sum(1 for r in self.test_results if r["matched_macro"] is not None)
        successful_executions = sum(1 for r in self.test_results if r["execution_success"])
        
        print(f"📈 전체 테스트: {total_tests}개")
        print(f"✅ 매칭 성공: {successful_matches}개 ({successful_matches/total_tests*100:.1f}%)")
        print(f"⚡ 실행 성공: {successful_executions}개 ({successful_executions/total_tests*100:.1f}%)")
        
        print("\n📋 상세 결과:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["execution_success"] else "❌"
            matched = result["matched_macro"] or "매칭 실패"
            print(f"{status} {i}. '{result['input_text']}' → {matched} (유사도: {result['similarity']:.2f})")
        
        # 매칭 서비스 통계
        stats = self.matching_service.get_matching_stats()
        print(f"\n📊 매칭 서비스 통계:")
        print(f"   전체 매칭 시도: {stats['total_matches']}회")
        print(f"   성공률: {stats['success_rate']:.1f}%")
        print(f"   정확한 매칭: {stats['match_types']['exact']}회")
        print(f"   부분 매칭: {stats['match_types']['partial']}회")
        print(f"   동의어 매칭: {stats['match_types']['synonym']}회")
        print(f"   퍼지 매칭: {stats['match_types']['fuzzy']}회")
    
    async def cleanup(self):
        """테스트 후 정리"""
        print("\n🧹 테스트 정리 중...")
        
        if self.gpt4o_service:
            try:
                await self.gpt4o_service.disconnect()
                print("✅ GPT-4o 서비스 연결 해제 완료")
            except Exception as e:
                print(f"⚠️ GPT-4o 연결 해제 오류: {e}")
    
    async def run_full_test(self):
        """전체 테스트 실행"""
        print("🚀 VoiceMacro Pro 통합 테스트 시작")
        print("=" * 60)
        
        try:
            # 1. 서비스 초기화
            await self.setup_services()
            
            # 2. 음성 명령어 시뮬레이션 테스트
            await self.test_voice_simulation()
            
            # 3. 실시간 오디오 테스트 (선택적)
            await self.test_real_time_audio()
            
            # 4. 결과 출력
            self.print_test_results()
            
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
        finally:
            await self.cleanup()
        
        print("\n🎉 통합 테스트 완료!")


async def main():
    """메인 함수"""
    test = IntegratedVoiceMacroTest()
    await test.run_full_test()


if __name__ == "__main__":
    print("🎯 VoiceMacro Pro 통합 테스트")
    print("GPT-4o 실시간 음성 인식 → 매크로 매칭 → 실행 파이프라인 테스트")
    print()
    
    # API 키 확인
    if Config.OPENAI_API_KEY:
        print(f"🔑 OpenAI API 키: {Config.OPENAI_API_KEY[:10]}...")
    else:
        print("⚠️ OpenAI API 키가 설정되지 않았습니다.")
        print("   환경변수 OPENAI_API_KEY를 설정하거나 .env 파일을 만들어주세요.")
    
    print()
    
    # 비동기 실행
    asyncio.run(main()) 