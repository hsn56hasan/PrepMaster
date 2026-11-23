# PrepKampüs başlatıcı (masaüstü kısayolu bunu çalıştırır)
# - Sunucu zaten açıksa yalnızca tarayıcıyı açar.
# - Kapalıysa sunucuyu küçültülmüş bir pencerede başlatır, hazır olunca tarayıcıyı açar.
# Sunucuyu kapatmak için görev çubuğundaki "PrepKampüs Sunucu" penceresini kapatın.

$port = 8050
$url  = "http://localhost:$port"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Invoke-WebRequest PowerShell 5.1'de takılabildiği için doğrudan port bağlantısı denenir.
function Test-Server {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $wait = $client.BeginConnect("127.0.0.1", $port, $null, $null)
        $wait.AsyncWaitHandle.WaitOne(1000) -and $client.Connected
    } catch {
        $false
    } finally {
        $client.Close()
    }
}

if (-not (Test-Server)) {
    # 0.0.0.0: aynı Wi-Fi'daki telefondan da açılabilsin (run.bat ile aynı davranış).
    $cmd = "title PrepKampüs Sunucu && cd /d `"$root`" && python -m uvicorn backend.app:app --host 0.0.0.0 --port $port"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $cmd -WindowStyle Minimized

    $ready = $false
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-Server) { $ready = $true; break }
    }
    if (-not $ready) {
        Add-Type -AssemblyName PresentationFramework
        [System.Windows.MessageBox]::Show(
            "PrepKampüs sunucusu 20 saniyede başlamadı.`nGörev çubuğundaki 'PrepKampüs Sunucu' penceresindeki hata mesajına bakın.",
            "PrepKampüs") | Out-Null
        exit 1
    }
}

Start-Process $url
