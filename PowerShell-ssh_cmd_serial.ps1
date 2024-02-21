$number = 1

# SSH连接
$useSSH = 0
if ($useSSH -eq 1) {
    Write-Host "-----------------------------------------"
    Write-Host "[$number]. run SSH:"
    $number += 1
    Write-Host "-----------------------------------------"
    # $server = "192.168.59.32"
    # $username = "chenshuai"
    # $password = "cs.123"
    # $command = "ls" # 命令
    # $secpasswd = ConvertTo-SecureString $password -AsPlainText -Force
    # $mycreds = New-Object System.Management.Automation.PSCredential ($username, $secpasswd)
    # Invoke-SSHCommand -Index 0 -Command $command -ComputerName $server -UserName $username -Password $mycreds
    # Disconnect-SSHSession -Index 0 # 断开ssh[0]连接

    $server = "192.168.59.32"
    $username = "chenshuai"
    $password = "cs.123"
    $secure = $password | ConvertTo-SecureString -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential($username,$secure)
    $session = New-SSHSession -ComputerName $server -Credential $cred -Port 2 -AcceptKey -Verbose
    Invoke-SSHCommand -SessionId 0 -Command "ls" # 命令
    Remove-SSHSession -Session $session # 断开ssh连接
}


# cmd连接
Write-Host "-----------------------------------------"
Write-Host "[$number]. run cmd:"
$number += 1
Write-Host "-----------------------------------------"
$cmdCommand = "adb root" # 命令
Write-Host "[cmd: $cmdCommand]"
Invoke-Expression -Command $cmdCommand


# serial串口连接
Write-Host "-----------------------------------------"
Write-Host "[$number]. run serial:"
$number += 1
Write-Host "-----------------------------------------"
$port = New-Object System.IO.Ports.SerialPort
$port.PortName = "COM3"  # 串口号
$port.BaudRate = 115200  # 波特率	
$useSerialPrint = 0 # 是否监听串口输出
$port.Open()
if ($useSerialPrint -eq 1) {
     # 监听串口输出
    Register-ObjectEvent -InputObject $port -EventName DataReceived -Action {
        $data = $port.ReadLine()
        Write-Host "Received data: $data"
    }
}
$command = "ls" # 命令
Write-Host "[serial: $command]"
$port.Write($command)
$port.Close() # 断开串口连接

