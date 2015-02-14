import-module WASP
# http://gallery.technet.microsoft.com/scriptcenter/Write-timestamped-output-4ff1565f
import-module logging

$p = split-path $script:MyInvocation.MyCommand.Path
$dt = Get-Date -format "yyyyMMddHHmmss"
[string]$cmdn = $script:MyInvocation.MyCommand
[string]$pcmdn = $script:MyInvocation.MyCommand.ScriptName
$cmd = $cmdn.split('.') 
$logn = $cmd[0]+"_"+$dt+".log"
$log = join-path -path $env:TEMP -childpath $logn
$dttmstmp = get-date
$LogFilePreference = $log

Write-Host "`n`n"
Write-Host "PunchClockTimer Position starting $dttmstmp; log file $log"
Write-Host "Command Script `t`t $cmdn"
Write-Host "Path `t`t`t $p"
Write-Host "Parent Script Name `t $pcmdn`n"

Write-Host "Sleeping"
sleep 25
Write-Host "Waking"
$wh = Select-Window -ProcessName PunchClockTimer
Write-Host "Window Handle $wh"
$posb = Get-WindowPosition -window $wh
Set-WindowPosition -X 1 -Y 70 -window $wh
$posa = Get-WindowPosition -window $wh
Write-Host "Position Before $posb After $posa"
