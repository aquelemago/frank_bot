[CmdletBinding(SupportsShouldProcess, ConfirmImpact = "High")]
param(
    [string]$TaskPath = "\FrankBot\",
    [switch]$ValidateOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$managedTaskNames = @(
    "Frank Bot - Solicitantes",
    "Frank Bot - Atendentes"
)

if (-not $TaskPath.StartsWith("\") -or -not $TaskPath.EndsWith("\")) {
    throw "TaskPath deve comecar e terminar com barra invertida."
}
foreach ($command in @("Get-ScheduledTask", "Unregister-ScheduledTask")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Cmdlet obrigatorio indisponivel: $command"
    }
}

if ($ValidateOnly) {
    Write-Output "VALIDATION=PASSOU"
    Write-Output "MANAGED_TASK_COUNT=2"
    Write-Output "TASKS_REMOVED=NAO"
    return
}

foreach ($taskName in $managedTaskNames) {
    $task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $taskName -ErrorAction SilentlyContinue
    if ($null -eq $task) {
        Write-Output ("TASK_NOT_FOUND={0}" -f $taskName)
        continue
    }
    if ($PSCmdlet.ShouldProcess("$TaskPath$taskName", "Remover tarefa gerenciada")) {
        Unregister-ScheduledTask -TaskPath $TaskPath -TaskName $taskName -Confirm:$false
        Write-Output ("TASK_REMOVED={0}" -f $taskName)
    }
}
