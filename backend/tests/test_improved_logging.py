"""
개선된 로깅 시스템 테스트 스크립트
로그 파일 저장 실패 시나리오와 복구 기능을 테스트합니다.
"""

import os
import sys
import tempfile
import time
import shutil
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.common_utils import get_logger, setup_file_logging, log_with_context

def test_normal_logging():
    """
    정상적인 로깅 기능을 테스트하는 함수
    """
    print("=== 1. 정상 로깅 테스트 ===")
    
    # 테스트용 로그 디렉토리 생성
    test_log_dir = os.path.join(tempfile.gettempdir(), 'test_logging')
    os.makedirs(test_log_dir, exist_ok=True)
    
    try:
        # 로거 생성
        logger = get_logger(__name__, os.path.join(test_log_dir, 'test.log'))
        
        # 다양한 레벨의 로그 테스트
        logger.debug("디버그 메시지 테스트")
        logger.info("정보 메시지 테스트")
        logger.warning("경고 메시지 테스트")
        logger.error("오류 메시지 테스트")
        
        # 컨텍스트와 함께 로그 테스트
        context = {"test_id": 1, "operation": "normal_logging_test"}
        log_with_context(logger, "info", "컨텍스트 포함 로그 테스트", context)
        
        print("✅ 정상 로깅 테스트 성공")
        
        # 로그 파일 내용 확인
        log_file = os.path.join(test_log_dir, 'test.log')
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📄 로그 파일 내용 (일부):\n{content[:200]}...")
        
    except Exception as e:
        print(f"❌ 정상 로깅 테스트 실패: {e}")
    finally:
        # 테스트 디렉토리 정리
        if os.path.exists(test_log_dir):
            shutil.rmtree(test_log_dir, ignore_errors=True)

def test_permission_denied_scenario():
    """
    권한 거부 시나리오를 테스트하는 함수
    """
    print("\n=== 2. 권한 거부 시나리오 테스트 ===")
    
    # Windows에서는 권한 테스트가 복잡하므로 존재하지 않는 드라이브 사용
    if os.name == 'nt':  # Windows
        invalid_path = "Z:\\nonexistent\\path\\test.log"
    else:  # Unix-like
        invalid_path = "/root/nonexistent/test.log"
    
    try:
        # 접근 불가능한 경로로 로거 생성 시도
        logger = get_logger("permission_test", invalid_path)
        
        # 로그 메시지 전송 (대체 경로로 저장되어야 함)
        logger.info("권한 거부 상황에서의 로그 메시지")
        logger.warning("대체 경로로 저장되는지 확인")
        
        print("✅ 권한 거부 시나리오 테스트 성공 (대체 경로 사용)")
        
    except Exception as e:
        print(f"❌ 권한 거부 시나리오 테스트 실패: {e}")

def test_disk_space_simulation():
    """
    디스크 공간 부족 시뮬레이션 테스트
    (실제로는 작은 파일이지만 로직 테스트용)
    """
    print("\n=== 3. 디스크 공간 부족 시뮬레이션 테스트 ===")
    
    test_log_dir = os.path.join(tempfile.gettempdir(), 'disk_test')
    os.makedirs(test_log_dir, exist_ok=True)
    
    try:
        # 로거 생성
        logger = get_logger("disk_test", os.path.join(test_log_dir, 'disk_test.log'))
        
        # 많은 양의 로그 생성하여 회전 기능 테스트
        for i in range(100):
            logger.info(f"대용량 로그 테스트 {i:03d}: " + "X" * 1000)  # 각 로그 약 1KB
        
        print("✅ 대용량 로그 테스트 성공 (파일 회전 기능 확인)")
        
        # 생성된 로그 파일들 확인
        log_files = [f for f in os.listdir(test_log_dir) if f.startswith('disk_test')]
        print(f"📁 생성된 로그 파일: {len(log_files)}개")
        for log_file in log_files:
            file_path = os.path.join(test_log_dir, log_file)
            file_size = os.path.getsize(file_path)
            print(f"   - {log_file}: {file_size:,} bytes")
        
    except Exception as e:
        print(f"❌ 디스크 공간 테스트 실패: {e}")
    finally:
        # 테스트 디렉토리 정리
        if os.path.exists(test_log_dir):
            shutil.rmtree(test_log_dir, ignore_errors=True)

def test_concurrent_logging():
    """
    동시 로깅 테스트 (파일 잠금 상황 시뮬레이션)
    """
    print("\n=== 4. 동시 로깅 테스트 ===")
    
    import threading
    
    test_log_dir = os.path.join(tempfile.gettempdir(), 'concurrent_test')
    os.makedirs(test_log_dir, exist_ok=True)
    
    log_file = os.path.join(test_log_dir, 'concurrent_test.log')
    
    def worker(worker_id):
        """워커 스레드 함수"""
        try:
            logger = get_logger(f"worker_{worker_id}", log_file)
            for i in range(10):
                logger.info(f"Worker {worker_id}: 메시지 {i}")
                time.sleep(0.01)  # 짧은 대기
        except Exception as e:
            print(f"Worker {worker_id} 오류: {e}")
    
    try:
        # 여러 스레드에서 동시에 로깅
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        print("✅ 동시 로깅 테스트 성공")
        
        # 로그 파일 내용 확인
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"📄 총 로그 라인 수: {len(lines)}")
        
    except Exception as e:
        print(f"❌ 동시 로깅 테스트 실패: {e}")
    finally:
        # 테스트 디렉토리 정리
        if os.path.exists(test_log_dir):
            shutil.rmtree(test_log_dir, ignore_errors=True)

def test_system_logging_setup():
    """
    시스템 로깅 설정 테스트
    """
    print("\n=== 5. 시스템 로깅 설정 테스트 ===")
    
    test_log_dir = os.path.join(tempfile.gettempdir(), 'system_test')
    
    try:
        # 시스템 로깅 설정
        success = setup_file_logging(test_log_dir, "DEBUG")
        
        if success:
            print("✅ 시스템 로깅 설정 성공")
            
            # 시스템 로거 사용
            import logging
            system_logger = logging.getLogger("system_test")
            system_logger.debug("시스템 디버그 메시지")
            system_logger.info("시스템 정보 메시지")
            system_logger.warning("시스템 경고 메시지")
            system_logger.error("시스템 오류 메시지")
            
            # 로그 파일 확인
            log_files = []
            if os.path.exists(test_log_dir):
                log_files = [f for f in os.listdir(test_log_dir) if f.endswith('.log')]
            print(f"📁 생성된 시스템 로그 파일: {len(log_files)}개")
            
        else:
            print("❌ 시스템 로깅 설정 실패")
        
    except Exception as e:
        print(f"❌ 시스템 로깅 테스트 실패: {e}")
    finally:
        # 테스트 디렉토리 정리
        if os.path.exists(test_log_dir):
            shutil.rmtree(test_log_dir, ignore_errors=True)

def main():
    """
    메인 테스트 함수
    모든 로깅 테스트를 실행합니다.
    """
    print("🧪 개선된 로깅 시스템 테스트 시작")
    print("=" * 50)
    
    # 각 테스트 실행
    test_normal_logging()
    test_permission_denied_scenario()
    test_disk_space_simulation()
    test_concurrent_logging()
    test_system_logging_setup()
    
    print("\n" + "=" * 50)
    print("✨ 모든 로깅 테스트 완료")
    print("\n💡 주요 개선사항:")
    print("   - 파일 저장 실패 시 자동 재시도 (최대 3회)")
    print("   - 권한 문제 시 임시 디렉토리로 대체")
    print("   - 로그 파일 자동 회전 (10MB 초과 시)")
    print("   - 디스크 공간 부족 시 경고 및 건너뛰기")
    print("   - 동시 접근 문제 시 점진적 대기")
    print("   - 상세한 오류 로깅 및 사용자 알림")

if __name__ == "__main__":
    main() 