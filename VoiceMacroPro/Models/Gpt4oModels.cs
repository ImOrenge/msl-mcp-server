using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace VoiceMacroPro.Models
{
    /// <summary>
    /// 트랜스크립션 결과 정보
    /// OpenAI GPT-4o 실시간 음성 인식 결과를 담는 클래스
    /// </summary>
    public class TranscriptionData
    {
        /// <summary>
        /// 트랜스크립션 타입 (partial, final)
        /// </summary>
        [JsonPropertyName("type")]
        public string type { get; set; } = string.Empty;

        /// <summary>
        /// 인식된 텍스트 내용
        /// </summary>
        [JsonPropertyName("text")]
        public string text { get; set; } = string.Empty;

        /// <summary>
        /// 인식 신뢰도 (0.0 ~ 1.0)
        /// </summary>
        [JsonPropertyName("confidence")]
        public double confidence { get; set; }

        /// <summary>
        /// 세션 ID
        /// </summary>
        [JsonPropertyName("session_id")]
        public string session_id { get; set; } = string.Empty;

        /// <summary>
        /// 타임스탬프
        /// </summary>
        [JsonPropertyName("timestamp")]
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 서버 연결 확인 데이터
    /// </summary>
    public class ConnectionEstablishedData
    {
        public bool success { get; set; }
        public string session_id { get; set; } = string.Empty;
        public string server_time { get; set; } = string.Empty;
        public string[] features { get; set; } = Array.Empty<string>();
        public string message { get; set; } = string.Empty;
    }

    /// <summary>
    /// 음성인식 상태 데이터
    /// </summary>
    public class VoiceRecognitionStatusData
    {
        public bool success { get; set; }
        public string session_id { get; set; } = string.Empty;
        public string message { get; set; } = string.Empty;
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 음성인식 오류 데이터
    /// </summary>
    public class VoiceRecognitionErrorData
    {
        public bool success { get; set; }
        public string error { get; set; } = string.Empty;
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 오디오 청크 수신 확인 데이터
    /// </summary>
    public class AudioChunkReceivedData
    {
        public bool success { get; set; }
        public int audio_length { get; set; }
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 오디오 처리 오류 데이터
    /// </summary>
    public class AudioProcessingErrorData
    {
        public string error { get; set; } = string.Empty;
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 트랜스크립션 오류 데이터
    /// </summary>
    public class TranscriptionErrorData
    {
        public string error { get; set; } = string.Empty;
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 매크로 실행 시작 데이터
    /// </summary>
    public class MacroExecutionStartedData
    {
        public int macro_id { get; set; }
        public string macro_name { get; set; } = string.Empty;
        public string input_text { get; set; } = string.Empty;
        public double confidence { get; set; }
        public double similarity { get; set; }
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 매크로 실행 완료 데이터
    /// </summary>
    public class MacroExecutionCompletedData
    {
        public int macro_id { get; set; }
        public string macro_name { get; set; } = string.Empty;
        public bool success { get; set; }
        public int execution_time { get; set; }
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 매크로 실행 실패 데이터
    /// </summary>
    public class MacroExecutionFailedData
    {
        public int macro_id { get; set; }
        public string macro_name { get; set; } = string.Empty;
        public string error { get; set; } = string.Empty;
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 매크로 매칭 실패 데이터
    /// </summary>
    public class MacroMatchFailedData
    {
        public string input_text { get; set; } = string.Empty;
        public double confidence { get; set; }
        public string message { get; set; } = string.Empty;
        public string timestamp { get; set; } = string.Empty;
    }

    /// <summary>
    /// 핑 응답 데이터
    /// </summary>
    public class PongData
    {
        public string session_id { get; set; } = string.Empty;
        public string server_time { get; set; } = string.Empty;
        public int connected_clients { get; set; }
    }

    /// <summary>
    /// 실시간 오디오 캡처 설정 정보
    /// 윈도우 기본 마이크 장치를 자동으로 사용하는 GPT-4o 최적화 설정
    /// </summary>
    public class AudioCaptureSettings
    {
        /// <summary>
        /// 샘플링 레이트 (GPT-4o 최적화: 24kHz)
        /// </summary>
        public int SampleRate { get; set; } = 24000;

        /// <summary>
        /// 비트 깊이 (16비트)
        /// </summary>
        public int BitsPerSample { get; set; } = 16;

        /// <summary>
        /// 채널 수 (모노: 1)
        /// </summary>
        public int Channels { get; set; } = 1;

        /// <summary>
        /// 버퍼 크기 (밀리초, 실시간 처리용: 100ms)
        /// </summary>
        public int BufferMilliseconds { get; set; } = 100;

        /// <summary>
        /// 마이크 장치 번호 (-1: 윈도우 기본 마이크 자동 선택, 0 이상: 특정 장치 지정)
        /// </summary>
        public int DeviceNumber { get; set; } = -1;

        /// <summary>
        /// 자동으로 윈도우 기본 마이크를 사용할지 여부
        /// </summary>
        public bool UseWindowsDefaultMicrophone { get; set; } = true;

        /// <summary>
        /// 마이크 감도 조절 (0.0 ~ 1.0, 기본값: 0.8)
        /// </summary>
        public double MicrophoneSensitivity { get; set; } = 0.8;

        /// <summary>
        /// 오디오 볼륨 증폭 배율 (1.0 = 증폭 없음, 2.0 = 2배 증폭, 0.5 = 절반 감소)
        /// 권장 범위: 0.1 ~ 5.0
        /// </summary>
        public double VolumeAmplification { get; set; } = 2.0;

        /// <summary>
        /// 볼륨 증폭 활성화 여부
        /// </summary>
        public bool EnableVolumeAmplification { get; set; } = true;

        /// <summary>
        /// 오디오 클리핑 방지 활성화 여부 (볼륨 증폭 시 신호가 왜곡되는 것을 방지)
        /// </summary>
        public bool EnableClippingPrevention { get; set; } = true;

        /// <summary>
        /// 자동 게인 컨트롤 (AGC) 활성화 여부
        /// 입력 볼륨에 따라 자동으로 증폭 배율을 조정
        /// </summary>
        public bool EnableAutoGainControl { get; set; } = false;

        /// <summary>
        /// 자동 게인 컨트롤 목표 레벨 (0.0 ~ 1.0)
        /// AGC가 활성화된 경우 이 레벨을 유지하도록 자동 조정
        /// </summary>
        public double AutoGainTargetLevel { get; set; } = 0.5;

        /// <summary>
        /// 노이즈 감소 활성화 여부
        /// </summary>
        public bool EnableNoiseReduction { get; set; } = true;

        /// <summary>
        /// 음성 활동 감지 (VAD) 활성화 여부
        /// </summary>
        public bool EnableVoiceActivityDetection { get; set; } = true;

        /// <summary>
        /// 오디오 설정 요약 문자열
        /// </summary>
        public string SettingsSummary =>
            $"{SampleRate}Hz, {BitsPerSample}bit, {Channels}ch, {BufferMilliseconds}ms 버퍼" +
            $"{(UseWindowsDefaultMicrophone ? " (윈도우 기본 마이크)" : $" (장치 {DeviceNumber})")}" +
            $"{(EnableVolumeAmplification ? $", 볼륨 증폭: {VolumeAmplification:F1}x" : "")}" +
            $"{(EnableAutoGainControl ? $", AGC 활성화 (목표: {AutoGainTargetLevel:F1})" : "")}";

        /// <summary>
        /// GPT-4o에 최적화된 기본 설정으로 초기화
        /// </summary>
        public void SetOptimalSettingsForGPT4o()
        {
            SampleRate = 24000;           // GPT-4o 권장 샘플링 레이트
            BitsPerSample = 16;           // 16비트 깊이
            Channels = 1;                 // 모노 채널
            BufferMilliseconds = 100;     // 실시간 처리용 100ms 버퍼
            UseWindowsDefaultMicrophone = true;  // 윈도우 기본 마이크 사용
            DeviceNumber = -1;            // 시스템 기본 장치
            MicrophoneSensitivity = 0.8;  // 적절한 감도 설정
            VolumeAmplification = 2.0;    // 기본 2배 증폭
            EnableVolumeAmplification = true;   // 볼륨 증폭 활성화
            EnableClippingPrevention = true;    // 클리핑 방지 활성화
            EnableAutoGainControl = false;      // AGC는 기본적으로 비활성화
            AutoGainTargetLevel = 0.5;    // AGC 목표 레벨
            EnableNoiseReduction = true;  // 노이즈 감소 활성화
            EnableVoiceActivityDetection = true;  // VAD 활성화
        }

        /// <summary>
        /// 볼륨 증폭 설정을 안전한 범위로 검증하고 조정
        /// </summary>
        public void ValidateAndAdjustAmplificationSettings()
        {
            // 볼륨 증폭 배율을 안전한 범위로 제한
            VolumeAmplification = Math.Max(0.1, Math.Min(5.0, VolumeAmplification));
            
            // AGC 목표 레벨을 유효한 범위로 제한
            AutoGainTargetLevel = Math.Max(0.1, Math.Min(0.9, AutoGainTargetLevel));
            
            // 마이크 감도를 유효한 범위로 제한
            MicrophoneSensitivity = Math.Max(0.0, Math.Min(1.0, MicrophoneSensitivity));
        }
    }

    /// <summary>
    /// 음성 인식 세션 정보
    /// </summary>
    public class VoiceSession
    {
        /// <summary>
        /// 세션 ID
        /// </summary>
        public string SessionId { get; set; } = string.Empty;

        /// <summary>
        /// 녹음 시작 시간
        /// </summary>
        public DateTime StartTime { get; set; }

        /// <summary>
        /// 마지막 활동 시간
        /// </summary>
        public DateTime LastActivity { get; set; }

        /// <summary>
        /// 총 트랜스크립션 수
        /// </summary>
        public int TranscriptionCount { get; set; }

        /// <summary>
        /// 성공한 매크로 실행 수
        /// </summary>
        public int SuccessfulMacroExecutions { get; set; }

        /// <summary>
        /// 평균 신뢰도
        /// </summary>
        public double AverageConfidence { get; set; }

        /// <summary>
        /// 세션 통계 문자열
        /// </summary>
        public string SessionStats =>
            $"트랜스크립션: {TranscriptionCount}개 | 매크로 실행: {SuccessfulMacroExecutions}개 | 평균 신뢰도: {AverageConfidence:F2}";
    }

    /// <summary>
    /// 음성 매칭 결과
    /// </summary>
    public class VoiceMatchResult
    {
        public int MacroId { get; set; }
        public string MacroName { get; set; } = string.Empty;
        public string InputText { get; set; } = string.Empty;
        public double Confidence { get; set; }
        public double Similarity { get; set; }
        public bool IsExecuting { get; set; }
        public bool IsSuccess { get; set; }
        public string ErrorMessage { get; set; } = string.Empty;
        public int ExecutionTime { get; set; }
        public DateTime ExecutionStartTime { get; set; }
        public DateTime ExecutionEndTime { get; set; }
        
        // 호환성을 위한 속성들
        public bool IsExecuted => IsSuccess;
        public string MatchedCommand => InputText;
        public DateTime Timestamp => ExecutionStartTime != default ? ExecutionStartTime : DateTime.Now;
    }
} 