using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Text;
using System.Linq;
using System.Runtime.InteropServices;

namespace VoiceMacroPro.Services
{
    /// <summary>
    /// 로그 레벨 열거형
    /// PRD 3.5.2에 정의된 로그 레벨을 구현합니다.
    /// </summary>
    public enum LogLevel
    {
        Debug = 0,
        Info = 1,
        Warning = 2,
        Error = 3
    }

    /// <summary>
    /// 로그 항목을 나타내는 클래스
    /// UI 바인딩을 위해 INotifyPropertyChanged를 구현합니다.
    /// </summary>
    public class LogEntry : INotifyPropertyChanged
    {
        private string _message = string.Empty;
        private LogLevel _level = LogLevel.Info;
        private DateTime _timestamp = DateTime.Now;
        private int? _macroId;

        /// <summary>
        /// 로그 메시지
        /// </summary>
        public string Message
        {
            get => _message;
            set
            {
                _message = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// 로그 레벨
        /// </summary>
        public LogLevel Level
        {
            get => _level;
            set
            {
                _level = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(LevelText));
                OnPropertyChanged(nameof(LevelColor));
            }
        }

        /// <summary>
        /// 로그 발생 시간
        /// </summary>
        public DateTime Timestamp
        {
            get => _timestamp;
            set
            {
                _timestamp = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(TimeText));
            }
        }

        /// <summary>
        /// 관련 매크로 ID (선택사항)
        /// </summary>
        public int? MacroId
        {
            get => _macroId;
            set
            {
                _macroId = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// UI 표시용 시간 텍스트
        /// </summary>
        public string TimeText => Timestamp.ToString("HH:mm:ss.fff");

        /// <summary>
        /// UI 표시용 레벨 텍스트
        /// </summary>
        public string LevelText => Level.ToString().ToUpper();

        /// <summary>
        /// UI 표시용 레벨 색상
        /// </summary>
        public string LevelColor => Level switch
        {
            LogLevel.Debug => "#6C757D",    // 회색
            LogLevel.Info => "#17A2B8",     // 청색
            LogLevel.Warning => "#FFC107",  // 황색
            LogLevel.Error => "#DC3545",    // 적색
            _ => "#000000"
        };

        /// <summary>
        /// 전체 로그 텍스트 (파일 저장용)
        /// </summary>
        public string FullText => $"[{TimeText}] [{LevelText}] {Message}" + 
                                 (MacroId.HasValue ? $" (Macro ID: {MacroId})" : "");

        public event PropertyChangedEventHandler? PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string? propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    /// <summary>
    /// 로깅 서비스 클래스
    /// PRD 3.5 로그 및 모니터링 시스템을 구현합니다.
    /// </summary>
    public class LoggingService : INotifyPropertyChanged
    {
        private static LoggingService? _instance;
        private LogLevel _currentLogLevel = LogLevel.Info;
        private bool _isAutoScroll = true;
        private string _logFilePath;

        /// <summary>
        /// 싱글톤 인스턴스
        /// </summary>
        public static LoggingService Instance => _instance ??= new LoggingService();

        /// <summary>
        /// 실시간 로그 항목 컬렉션 (UI 바인딩용)
        /// </summary>
        public ObservableCollection<LogEntry> LogEntries { get; } = new();

        /// <summary>
        /// 현재 로그 레벨
        /// 이 레벨보다 낮은 로그는 무시됩니다.
        /// </summary>
        public LogLevel CurrentLogLevel
        {
            get => _currentLogLevel;
            set
            {
                _currentLogLevel = value;
                OnPropertyChanged();
                LogInfo($"로그 레벨이 {value}로 변경되었습니다.");
            }
        }

        /// <summary>
        /// 자동 스크롤 활성화 여부
        /// </summary>
        public bool IsAutoScroll
        {
            get => _isAutoScroll;
            set
            {
                _isAutoScroll = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// 총 로그 항목 수
        /// </summary>
        public int TotalLogCount => LogEntries.Count;

        /// <summary>
        /// 로깅 서비스 생성자
        /// 로그 파일 경로를 설정하고 초기화합니다.
        /// 개선된 버전: 사전 검증 및 대체 경로 준비
        /// </summary>
        public LoggingService()
        {
            try
            {
                // 기본 로그 폴더 경로
                var logDirectory = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Logs");
                
                // 로그 폴더 생성 및 검증
                if (!EnsureLogDirectory(logDirectory))
                {
                    // 기본 경로 실패 시 대체 경로 사용
                    logDirectory = Path.Combine(Path.GetTempPath(), "VoiceMacroPro_Logs");
                    if (!EnsureLogDirectory(logDirectory))
                    {
                        // 모든 경로 실패 시 기본값 설정 (메모리에만 로그 유지)
                        _logFilePath = "";
                        LogWarning("로그 파일 저장을 사용할 수 없습니다. 메모리에만 로그를 유지합니다.");
                        return;
                    }
                    else
                    {
                        LogWarning($"기본 로그 디렉토리 접근 실패. 임시 디렉토리 사용: {logDirectory}");
                    }
                }

                // 로그 파일 경로 설정 (날짜별)
                var today = DateTime.Now.ToString("yyyy-MM-dd");
                _logFilePath = Path.Combine(logDirectory, $"VoiceMacroPro_{today}.log");

                // 파일 쓰기 권한 테스트
                if (!TestFileWritePermission(_logFilePath))
                {
                    // 권한 문제 시 타임스탬프 포함한 대체 파일명 사용
                    var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                    _logFilePath = Path.Combine(logDirectory, $"VoiceMacroPro_{today}_{timestamp}.log");
                    
                    if (!TestFileWritePermission(_logFilePath))
                    {
                        LogWarning("로그 파일 쓰기 권한 문제로 인해 파일 로깅이 제한될 수 있습니다.");
                    }
                }

                // 서비스 시작 로그
                LogInfo($"로깅 서비스가 시작되었습니다. 로그 파일: {_logFilePath}", null);
                
                // 시스템 정보 로그
                LogInfo($"애플리케이션 버전: {GetApplicationVersion()}", null);
                LogInfo($"시스템 정보: {Environment.OSVersion}", null);
                LogInfo($"사용 가능한 메모리: {GC.GetTotalMemory(false):N0} bytes", null);
            }
            catch (Exception ex)
            {
                // 초기화 실패 시에도 서비스는 동작해야 함
                _logFilePath = "";
                Console.WriteLine($"로깅 서비스 초기화 중 오류 발생: {ex.Message}");
                
                // 기본 로그 항목 추가
                var errorEntry = new LogEntry
                {
                    Timestamp = DateTime.Now,
                    Level = LogLevel.Error,
                    Message = $"로깅 서비스 초기화 실패: {ex.Message}",
                    MacroId = null
                };
                LogEntries.Add(errorEntry);
            }
        }
        
        /// <summary>
        /// 로그 디렉토리 생성 및 검증하는 메서드
        /// </summary>
        /// <param name="directoryPath">검증할 디렉토리 경로</param>
        /// <returns>디렉토리 사용 가능 여부</returns>
        private bool EnsureLogDirectory(string directoryPath)
        {
            try
            {
                // 디렉토리 생성
                Directory.CreateDirectory(directoryPath);
                
                // 쓰기 권한 테스트
                var testFile = Path.Combine(directoryPath, $"test_{Guid.NewGuid():N}.tmp");
                File.WriteAllText(testFile, "test");
                File.Delete(testFile);
                
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"로그 디렉토리 설정 실패: {directoryPath} - {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// 파일 쓰기 권한을 테스트하는 메서드
        /// </summary>
        /// <param name="filePath">테스트할 파일 경로</param>
        /// <returns>쓰기 가능 여부</returns>
        private bool TestFileWritePermission(string filePath)
        {
            try
            {
                // 임시 내용으로 쓰기 테스트
                var testContent = $"# VoiceMacro Pro 로그 파일 - 생성 시간: {DateTime.Now:yyyy-MM-dd HH:mm:ss}" + Environment.NewLine;
                File.WriteAllText(filePath, testContent);
                return true;
            }
            catch
            {
                return false;
            }
        }
        
        /// <summary>
        /// 애플리케이션 버전을 가져오는 메서드
        /// </summary>
        /// <returns>애플리케이션 버전 문자열</returns>
        private string GetApplicationVersion()
        {
            try
            {
                var assembly = System.Reflection.Assembly.GetExecutingAssembly();
                var version = assembly.GetName().Version;
                return version?.ToString() ?? "Unknown";
            }
            catch
            {
                return "Unknown";
            }
        }

        /// <summary>
        /// Debug 레벨 로그 기록
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="macroId">관련 매크로 ID (선택사항)</param>
        public void LogDebug(string message, int? macroId = null)
        {
            WriteLog(LogLevel.Debug, message, macroId);
        }

        /// <summary>
        /// Info 레벨 로그 기록
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="macroId">관련 매크로 ID (선택사항)</param>
        public void LogInfo(string message, int? macroId = null)
        {
            WriteLog(LogLevel.Info, message, macroId);
        }

        /// <summary>
        /// Warning 레벨 로그 기록
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="macroId">관련 매크로 ID (선택사항)</param>
        public void LogWarning(string message, int? macroId = null)
        {
            WriteLog(LogLevel.Warning, message, macroId);
        }

        /// <summary>
        /// Error 레벨 로그 기록
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="macroId">관련 매크로 ID (선택사항)</param>
        public void LogError(string message, int? macroId = null)
        {
            WriteLog(LogLevel.Error, message, macroId);
        }

        /// <summary>
        /// 예외 정보를 포함한 Error 로그 기록
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="exception">예외 객체</param>
        /// <param name="macroId">관련 매크로 ID (선택사항)</param>
        public void LogError(string message, Exception exception, int? macroId = null)
        {
            var fullMessage = $"{message}\n예외: {exception.Message}\n스택 트레이스: {exception.StackTrace}";
            WriteLog(LogLevel.Error, fullMessage, macroId);
        }

        /// <summary>
        /// 실제 로그를 기록하는 내부 메서드
        /// </summary>
        /// <param name="level">로그 레벨</param>
        /// <param name="message">로그 메시지</param>
        /// <param name="macroId">관련 매크로 ID</param>
        private void WriteLog(LogLevel level, string message, int? macroId = null)
        {
            // 현재 설정된 로그 레벨보다 낮으면 무시
            if (level < _currentLogLevel)
                return;

            var logEntry = new LogEntry
            {
                Level = level,
                Message = message,
                MacroId = macroId,
                Timestamp = DateTime.Now
            };

            // UI 스레드에서 컬렉션 업데이트
            Application.Current?.Dispatcher.Invoke(() =>
            {
                LogEntries.Add(logEntry);

                // 로그 항목이 너무 많으면 오래된 항목 제거 (최대 1000개 유지)
                while (LogEntries.Count > 1000)
                {
                    LogEntries.RemoveAt(0);
                }

                // PropertyChanged 이벤트 발생
                OnPropertyChanged(nameof(LogEntries));
                OnPropertyChanged(nameof(TotalLogCount));
            });

            // 파일에 비동기로 기록
            _ = Task.Run(() => WriteLogToFile(logEntry));

            // 콘솔에도 출력 (디버그 모드)
            Console.WriteLine(logEntry.FullText);
        }

        /// <summary>
        /// 로그를 파일에 기록하는 메서드 (개선된 버전)
        /// 파일 저장 실패 시 재시도 및 대체 경로 사용
        /// </summary>
        /// <param name="logEntry">기록할 로그 항목</param>
        private async Task WriteLogToFile(LogEntry logEntry)
        {
            const int maxRetries = 3;
            int retryCount = 0;
            
            while (retryCount < maxRetries)
            {
                try
                {
                    // 디렉토리 존재 확인 및 생성
                    var directory = Path.GetDirectoryName(_logFilePath);
                    if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                    {
                        Directory.CreateDirectory(directory);
                    }
                    
                    // 디스크 공간 확인 (최소 10MB 필요)
                    var driveInfo = new DriveInfo(Path.GetPathRoot(_logFilePath) ?? "C:");
                    if (driveInfo.AvailableFreeSpace < 10 * 1024 * 1024) // 10MB
                    {
                        Console.WriteLine("경고: 디스크 공간이 부족합니다. 로그 파일 저장을 건너뜁니다.");
                        return;
                    }
                    
                    // 파일 크기 확인 (10MB 초과 시 새 파일 생성)
                    if (File.Exists(_logFilePath))
                    {
                        var fileInfo = new FileInfo(_logFilePath);
                        if (fileInfo.Length > 10 * 1024 * 1024) // 10MB
                        {
                            await RotateLogFile();
                        }
                    }
                    
                    // 파일에 로그 기록
                    await File.AppendAllTextAsync(_logFilePath, logEntry.FullText + Environment.NewLine);
                    return; // 성공 시 메서드 종료
                }
                catch (UnauthorizedAccessException ex)
                {
                    if (retryCount == maxRetries - 1)
                    {
                        // 마지막 재시도에서도 실패하면 대체 경로 시도
                        await TryAlternativeLogPath(logEntry, ex);
                        return;
                    }
                }
                catch (DirectoryNotFoundException ex)
                {
                    Console.WriteLine($"로그 디렉토리를 찾을 수 없습니다: {ex.Message}");
                    // 디렉토리 재생성 시도
                    try
                    {
                        var directory = Path.GetDirectoryName(_logFilePath);
                        if (!string.IsNullOrEmpty(directory))
                        {
                            Directory.CreateDirectory(directory);
                        }
                    }
                    catch (Exception createEx)
                    {
                        Console.WriteLine($"디렉토리 생성 실패: {createEx.Message}");
                    }
                }
                catch (IOException ex) when (ex.Message.Contains("being used"))
                {
                    // 파일이 다른 프로세스에서 사용 중인 경우 잠시 대기
                    await Task.Delay(100 * (retryCount + 1)); // 점진적 대기
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"로그 파일 기록 실패 (시도 {retryCount + 1}/{maxRetries}): {ex.Message}");
                    
                    if (retryCount == maxRetries - 1)
                    {
                        // 마지막 재시도에서도 실패하면 대체 방법 사용
                        await TryAlternativeLogPath(logEntry, ex);
                        return;
                    }
                }
                
                retryCount++;
                
                // 재시도 전 짧은 대기
                if (retryCount < maxRetries)
                {
                    await Task.Delay(200 * retryCount); // 점진적 대기 (200ms, 400ms, 600ms)
                }
            }
        }
        
        /// <summary>
        /// 로그 파일 회전 (크기가 커졌을 때 새 파일 생성)
        /// </summary>
        private async Task RotateLogFile()
        {
            try
            {
                var directory = Path.GetDirectoryName(_logFilePath);
                var fileName = Path.GetFileNameWithoutExtension(_logFilePath);
                var extension = Path.GetExtension(_logFilePath);
                var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                
                var rotatedFileName = $"{fileName}_{timestamp}{extension}";
                var rotatedFilePath = Path.Combine(directory ?? "", rotatedFileName);
                
                // 기존 파일을 회전된 이름으로 이동
                if (File.Exists(_logFilePath))
                {
                    File.Move(_logFilePath, rotatedFilePath);
                }
                
                // 새로운 로그 파일 시작 메시지
                var rotationEntry = new LogEntry
                {
                    Timestamp = DateTime.Now,
                    Level = LogLevel.Info,
                    Message = $"로그 파일이 회전되었습니다. 이전 파일: {rotatedFileName}"
                };
                
                await File.AppendAllTextAsync(_logFilePath, rotationEntry.FullText + Environment.NewLine);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"로그 파일 회전 실패: {ex.Message}");
            }
        }
        
        /// <summary>
        /// 대체 로그 경로를 시도하는 메서드
        /// </summary>
        /// <param name="logEntry">기록할 로그 항목</param>
        /// <param name="originalException">원본 예외</param>
        private async Task TryAlternativeLogPath(LogEntry logEntry, Exception originalException)
        {
            try
            {
                // 임시 디렉토리에 로그 파일 생성 시도
                var tempLogPath = Path.Combine(Path.GetTempPath(), "VoiceMacroPro_Logs");
                Directory.CreateDirectory(tempLogPath);
                
                var today = DateTime.Now.ToString("yyyy-MM-dd");
                var alternativeLogFile = Path.Combine(tempLogPath, $"VoiceMacroPro_Emergency_{today}.log");
                
                // 첫 번째 대체 경로 사용 시 알림 메시지 추가
                if (!File.Exists(alternativeLogFile))
                {
                    var warningMessage = $"[{DateTime.Now:HH:mm:ss.fff}] [WARNING] 기본 로그 경로 실패로 임시 경로 사용: {alternativeLogFile}" + Environment.NewLine;
                    warningMessage += $"[{DateTime.Now:HH:mm:ss.fff}] [ERROR] 원본 오류: {originalException.Message}" + Environment.NewLine;
                    await File.AppendAllTextAsync(alternativeLogFile, warningMessage);
                }
                
                await File.AppendAllTextAsync(alternativeLogFile, logEntry.FullText + Environment.NewLine);
                
                // 한 번만 경고 메시지 출력
                if (_logFilePath != alternativeLogFile)
                {
                    Console.WriteLine($"경고: 기본 로그 파일 저장 실패. 임시 경로 사용: {alternativeLogFile}");
                    _logFilePath = alternativeLogFile; // 이후 로그들도 대체 경로 사용
                }
            }
            catch (Exception altEx)
            {
                // 대체 경로도 실패하면 메모리에만 보관하고 콘솔에 출력
                Console.WriteLine($"모든 로그 파일 저장 방법 실패: 원본 오류={originalException.Message}, 대체 경로 오류={altEx.Message}");
                Console.WriteLine($"로그 내용: {logEntry.FullText}");
                
                // 사용자에게 알림 (UI 스레드에서 실행)
                Application.Current?.Dispatcher.BeginInvoke(() =>
                {
                    var warningEntry = new LogEntry
                    {
                        Timestamp = DateTime.Now,
                        Level = LogLevel.Warning,
                        Message = "로그 파일 저장에 실패했습니다. 로그는 화면에만 표시됩니다.",
                        MacroId = null
                    };
                    LogEntries.Add(warningEntry);
                });
            }
        }

        /// <summary>
        /// 로그를 파일로 내보내는 메서드
        /// </summary>
        /// <param name="filePath">저장할 파일 경로</param>
        public async Task ExportLogsAsync(string filePath)
        {
            try
            {
                var logs = LogEntries.ToList();
                var content = new StringBuilder();
                
                // 헤더 추가
                content.AppendLine("VoiceMacro Pro 로그 내보내기");
                content.AppendLine($"내보낸 시간: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
                content.AppendLine($"총 로그 개수: {logs.Count}");
                content.AppendLine(new string('=', 50));
                content.AppendLine();

                // 로그 엔트리들 추가
                foreach (var log in logs.OrderBy(l => l.Timestamp))
                {
                    content.AppendLine($"[{log.TimeText}] [{log.LevelText}] {log.Message}");
                    if (log.MacroId.HasValue)
                    {
                        content.AppendLine($"  - 매크로 ID: {log.MacroId}");
                    }
                    content.AppendLine();
                }

                await File.WriteAllTextAsync(filePath, content.ToString(), Encoding.UTF8);
                LogInfo($"로그가 파일로 내보내졌습니다: {filePath}");
            }
            catch (Exception ex)
            {
                LogError($"로그 내보내기 실패: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// 모든 로그를 지우는 메서드
        /// </summary>
        public void ClearLogs()
        {
            try
            {
                var count = LogEntries.Count;
                LogEntries.Clear();
                
                // 로그 삭제 후 시스템 메시지 추가
                var clearMessage = new LogEntry
                {
                    Timestamp = DateTime.Now,
                    Level = LogLevel.Info,
                    Message = $"{count}개의 로그가 삭제되었습니다",
                    MacroId = null
                };
                
                LogEntries.Add(clearMessage);
            }
            catch (Exception ex)
            {
                LogError($"로그 삭제 실패: {ex.Message}");
            }
        }

        /// <summary>
        /// 로그 엔트리를 제한된 개수로 유지하는 메서드
        /// </summary>
        private void TrimLogs()
        {
            const int maxLogEntries = 1000; // 최대 1000개 로그 유지
            
            if (LogEntries.Count > maxLogEntries)
            {
                var excessCount = LogEntries.Count - maxLogEntries;
                for (int i = 0; i < excessCount; i++)
                {
                    LogEntries.RemoveAt(0); // 오래된 로그부터 제거
                }
            }
        }

        /// <summary>
        /// 매크로 실행 시작 로그
        /// </summary>
        /// <param name="macroName">매크로 이름</param>
        /// <param name="macroId">매크로 ID</param>
        public void LogMacroStart(string macroName, int macroId)
        {
            LogInfo($"매크로 실행 시작: {macroName}", macroId);
        }

        /// <summary>
        /// 매크로 실행 완료 로그
        /// </summary>
        /// <param name="macroName">매크로 이름</param>
        /// <param name="macroId">매크로 ID</param>
        /// <param name="duration">실행 시간</param>
        public void LogMacroComplete(string macroName, int macroId, TimeSpan duration)
        {
            LogInfo($"매크로 실행 완료: {macroName} (소요시간: {duration.TotalMilliseconds:F0}ms)", macroId);
        }

        /// <summary>
        /// 음성 인식 결과 로그
        /// </summary>
        /// <param name="recognizedText">인식된 텍스트</param>
        /// <param name="confidence">신뢰도</param>
        public void LogVoiceRecognition(string recognizedText, float confidence)
        {
            LogInfo($"음성 인식 결과: '{recognizedText}' (신뢰도: {confidence:P1})");
        }

        /// <summary>
        /// 매크로 매칭 결과 로그
        /// </summary>
        /// <param name="voiceCommand">음성 명령</param>
        /// <param name="matchedMacro">매칭된 매크로 이름</param>
        /// <param name="similarity">유사도</param>
        public void LogMacroMatch(string voiceCommand, string matchedMacro, float similarity)
        {
            LogInfo($"매크로 매칭: '{voiceCommand}' → '{matchedMacro}' (유사도: {similarity:P1})");
        }

        /// <summary>
        /// 로그 레벨을 설정하는 메서드
        /// </summary>
        /// <param name="level">설정할 로그 레벨 (Debug, Info, Warning, Error)</param>
        public void SetMinimumLevel(string level)
        {
            if (Enum.TryParse<LogLevel>(level, true, out var logLevel))
            {
                _currentLogLevel = logLevel;
                LogInfo($"로그 레벨이 {level}로 변경되었습니다");
            }
            else
            {
                LogWarning($"알 수 없는 로그 레벨: {level}");
            }
        }

        /// <summary>
        /// 자동 스크롤 설정 메서드
        /// </summary>
        /// <param name="enabled">자동 스크롤 활성화 여부</param>
        public void SetAutoScroll(bool enabled)
        {
            _isAutoScroll = enabled;
            LogDebug($"자동 스크롤이 {(enabled ? "활성화" : "비활성화")}되었습니다");
        }

        public event PropertyChangedEventHandler? PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string? propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        public void Dispose()
        {
            // 필요시 리소스 정리
        }
    }
} 