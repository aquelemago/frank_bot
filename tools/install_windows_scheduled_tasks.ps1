[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$RequesterTime = "08:00",
    [string]$AttendantTime = "09:00",
    [string]$TaskPath = "\FrankBot\",
    [System.Management.Automation.PSCredential]$Credential,
    [switch]$ValidateOnly,
    [switch]$RemoveLegacyStartupShortcut
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$mainPath = Join-Path $projectRoot "main.py"
$taskDefinitions = @(
    [pscustomobject]@{
        Name = "Frank Bot - Solicitantes"
        Arguments = "main.py --solicitante"
        TimeText = $RequesterTime
        Description = "Envia diariamente o relatorio de solicitantes do Frank Bot."
    },
    [pscustomobject]@{
        Name = "Frank Bot - Atendentes"
        Arguments = "main.py"
        TimeText = $AttendantTime
        Description = "Envia diariamente o relatorio de atendentes do Frank Bot."
    }
)

function ConvertTo-DailyTime {
    param([Parameter(Mandatory)][string]$Value)

    $parsed = [datetime]::MinValue
    $valid = [datetime]::TryParseExact(
        $Value,
        "HH:mm",
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::None,
        [ref]$parsed
    )
    if (-not $valid) {
        throw "Horario invalido: use HH:mm."
    }
    return $parsed
}

function Assert-Prerequisites {
    if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
        throw "Python da .venv nao encontrado no projeto."
    }
    if (-not (Test-Path -LiteralPath $mainPath -PathType Leaf)) {
        throw "main.py nao encontrado no projeto."
    }
    if (-not $TaskPath.StartsWith("\") -or -not $TaskPath.EndsWith("\")) {
        throw "TaskPath deve comecar e terminar com barra invertida."
    }
    foreach ($definition in $taskDefinitions) {
        $definition | Add-Member -NotePropertyName At -NotePropertyValue (
            ConvertTo-DailyTime -Value $definition.TimeText
        ) -Force
    }
    foreach ($command in @(
        "Get-ScheduledTask",
        "New-ScheduledTaskAction",
        "New-ScheduledTaskTrigger",
        "New-ScheduledTaskSettingsSet",
        "New-ScheduledTask",
        "Register-ScheduledTask"
    )) {
        if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
            throw "Cmdlet obrigatorio indisponivel: $command"
        }
    }
}

function Assert-RegisteredTask {
    param([Parameter(Mandatory)]$Definition)

    $task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $Definition.Name
    if ($task.Actions.Count -ne 1) {
        throw "A tarefa registrada possui quantidade inesperada de acoes."
    }
    $action = $task.Actions[0]
    if ($action.Execute -ne $pythonPath -or
        $action.Arguments -ne $Definition.Arguments -or
        $action.WorkingDirectory -ne $projectRoot) {
        throw "A acao registrada nao corresponde ao projeto atual."
    }
    if ($task.Triggers.Count -ne 1 -or -not $task.Triggers[0].Enabled) {
        throw "O gatilho diario nao foi registrado corretamente."
    }
    $registeredAt = [datetime]$task.Triggers[0].StartBoundary
    if ($registeredAt.TimeOfDay -ne $Definition.At.TimeOfDay) {
        throw "O horario diario registrado nao corresponde ao solicitado."
    }
    if ($task.Settings.MultipleInstances -ne "IgnoreNew") {
        throw "A politica de instancia unica nao foi registrada."
    }
    if ($task.Settings.StartWhenAvailable) {
        throw "A tarefa foi registrada para executar atrasada, contrariando a politica."
    }
}

function Remove-VerifiedLegacyShortcut {
    $startup = [Environment]::GetFolderPath("Startup")
    $shortcutPath = Join-Path $startup "Frank Bot Scheduler.lnk"
    if (-not (Test-Path -LiteralPath $shortcutPath -PathType Leaf)) {
        Write-Output "LEGACY_SHORTCUT=NAO_ENCONTRADO"
        return
    }

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $expectedTarget = (Join-Path $projectRoot ".venv\Scripts\pythonw.exe")
    $expectedService = (Join-Path $projectRoot "service.py")
    $targetMatches = [string]::Equals(
        [IO.Path]::GetFullPath($shortcut.TargetPath),
        [IO.Path]::GetFullPath($expectedTarget),
        [StringComparison]::OrdinalIgnoreCase
    )
    $argumentsMatch = $shortcut.Arguments.Contains($expectedService)
    if (-not $targetMatches -or -not $argumentsMatch) {
        throw "O atalho legado existe, mas nao aponta para o scheduler deste projeto."
    }
    Remove-Item -LiteralPath $shortcutPath
    Write-Output "LEGACY_SHORTCUT=REMOVIDO"
}

Assert-Prerequisites

if ($ValidateOnly) {
    Write-Output "VALIDATION=PASSOU"
    Write-Output "PROJECT_ROOT_PRESENT=SIM"
    Write-Output "PYTHON_VENV_PRESENT=SIM"
    Write-Output "TASK_COUNT=2"
    Write-Output "REQUESTER_TIME_VALID=SIM"
    Write-Output "ATTENDANT_TIME_VALID=SIM"
    Write-Output "EXTERNAL_INTEGRATION_EXECUTED=NAO"
    return
}

if ($null -eq $Credential) {
    $Credential = Get-Credential -Message "Informe a conta tecnica que executara o Frank Bot"
}
if ($null -eq $Credential -or [string]::IsNullOrWhiteSpace($Credential.UserName)) {
    throw "Uma conta tecnica valida e obrigatoria."
}

$plainPassword = $Credential.GetNetworkCredential().Password
try {
    foreach ($definition in $taskDefinitions) {
        $action = New-ScheduledTaskAction `
            -Execute $pythonPath `
            -Argument $definition.Arguments `
            -WorkingDirectory $projectRoot
        $trigger = New-ScheduledTaskTrigger -Daily -At $definition.At
        $settings = New-ScheduledTaskSettingsSet `
            -MultipleInstances IgnoreNew `
            -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
            -StartWhenAvailable:$false `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries
        $task = New-ScheduledTask `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Description $definition.Description

        if ($PSCmdlet.ShouldProcess("$TaskPath$($definition.Name)", "Registrar tarefa diaria")) {
            Register-ScheduledTask `
                -TaskPath $TaskPath `
                -TaskName $definition.Name `
                -InputObject $task `
                -User $Credential.UserName `
                -Password $plainPassword `
                -Force | Out-Null
            Assert-RegisteredTask -Definition $definition
            Write-Output ("TASK_VALIDATED={0}" -f $definition.Name)
        }
    }

    if ($RemoveLegacyStartupShortcut -and
        $PSCmdlet.ShouldProcess("Frank Bot Scheduler.lnk", "Remover atalho legado validado")) {
        Remove-VerifiedLegacyShortcut
    }
    Write-Output "INSTALLATION=PASSOU"
    Write-Output "TASKS_EXECUTED=NAO"
}
finally {
    $plainPassword = $null
}
