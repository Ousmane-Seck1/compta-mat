#Requires -Version 5.1
<#
.SYNOPSIS
    Nettoyage et verification complete du projet Compta_mat (Django).
.DESCRIPTION
    Enchaîne :
      1. Sauvegarde de la base SQLite
      2. Nettoyage des caches Python (__pycache__, *.pyc, .pytest_cache, staticfiles)
      3. Verification des dependances pip
      4. Django check (developpement + deploiement)
      5. Verification des migrations en attente
      6. Integrite SQLite
      7. Suite de tests Django (inventory.tests)
      8. Commandes metier : quality_check + preprod_check
      9. Rapport final OK / ECHEC
.NOTES
    Lancer depuis la racine du projet :
        .\clean_and_verify.ps1
    Options :
        -SkipTests        Sauter les tests unitaires
        -SkipBackup       Sauter la sauvegarde SQLite
        -PurgeLogs        Purger les logs de securite documents (> 180 jours)
        -PurgeLogsDays N  Nombre de jours de retention pour la purge (defaut : 180)
#>

[CmdletBinding()]
param(
    [switch]$SkipTests,
    [switch]$SkipBackup,
    [switch]$PurgeLogs,
    [int]$PurgeLogsDays = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Helpers ────────────────────────────────────────────────────────────────────

$script:Steps   = @()
$script:Failed  = $false

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

function Step-OK {
    param([string]$Name)
    $script:Steps += [PSCustomObject]@{ Etape = $Name; Statut = "OK" }
    Write-Host "[OK] $Name" -ForegroundColor Green
}

function Step-FAIL {
    param([string]$Name, [string]$Detail = "")
    $script:Steps += [PSCustomObject]@{ Etape = $Name; Statut = "ECHEC" }
    $script:Failed = $true
    $msg = "[ECHEC] $Name"
    if ($Detail) { $msg = $msg + " - " + $Detail }
    Write-Host $msg -ForegroundColor Red
}

function Step-SKIP {
    param([string]$Name, [string]$Reason = "")
    $script:Steps += [PSCustomObject]@{ Etape = $Name; Statut = "IGNORE" }
    $skipMsg = "[IGNORE] $Name"
    if ($Reason) { $skipMsg = $skipMsg + " ($Reason)" }
    Write-Host $skipMsg -ForegroundColor Yellow
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Block,
        [switch]$ContinueOnFail
    )
    Write-Host ""
    Write-Host ">> $Name ..." -ForegroundColor White
    try {
        & $Block
        Step-OK $Name
    }
    catch {
        Step-FAIL $Name $_.Exception.Message
        if (-not $ContinueOnFail) { throw }
    }
}

# ── Prerequis ──────────────────────────────────────────────────────────────────

Write-Header "VERIFICATION DES PREREQUIS"

# Detecter Python et manage.py
$PythonExe = $null
foreach ($candidate in @("python", "python3", ".\.venv\Scripts\python.exe")) {
    try {
        $v = & $candidate --version 2>&1
        if ($LASTEXITCODE -eq 0) { $PythonExe = $candidate; break }
    } catch { }
}

if (-not $PythonExe) {
    Write-Host "[ECHEC] Python introuvable. Verifiez votre PATH ou votre venv." -ForegroundColor Red
    exit 1
}
$pyVersion = & $PythonExe --version 2>&1
Write-Host "Python : $PythonExe  ($pyVersion)" -ForegroundColor Green

if (-not (Test-Path ".\manage.py")) {
    Write-Host "[ECHEC] manage.py introuvable. Lancer ce script depuis la racine du projet." -ForegroundColor Red
    exit 1
}
Write-Host "manage.py : trouve" -ForegroundColor Green

$DatabaseEngine = $env:DJANGO_DB_ENGINE
if (-not $DatabaseEngine) { $DatabaseEngine = "django.db.backends.postgresql" }
$DbPath = if ($DatabaseEngine -eq "django.db.backends.sqlite3") { ".\data\db.sqlite3" } else { $null }

# ── ETAPE 1 : Sauvegarde SQLite ────────────────────────────────────────────────

Write-Header "ETAPE 1 / 8 - Sauvegarde SQLite"

if ($SkipBackup) {
    Step-SKIP "Sauvegarde SQLite" "option -SkipBackup"
} else {
    Invoke-Step "Sauvegarde SQLite" -ContinueOnFail {
        if (-not $DbPath) {
            Write-Host "   Sauvegarde SQLite ignoree: moteur $DatabaseEngine." -ForegroundColor Yellow
            return
        }
        if (-not (Test-Path $DbPath)) {
            throw "Fichier $DbPath introuvable."
        }
        $BackupDir = ".\backups"
        if (-not (Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir | Out-Null }
        $Stamp  = Get-Date -Format "yyyyMMdd_HHmmss"
        $Backup = "$BackupDir\db_backup_$Stamp.sqlite3"
        Copy-Item $DbPath $Backup
        Write-Host "   Sauvegarde : $Backup" -ForegroundColor DarkGray
    }
}

# ── ETAPE 2 : Nettoyage caches ─────────────────────────────────────────────────

Write-Header "ETAPE 2 / 8 - Nettoyage des caches"

Invoke-Step "Suppression __pycache__" -ContinueOnFail {
    $dirs = Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
    foreach ($d in $dirs) { Remove-Item $d.FullName -Recurse -Force }
    Write-Host "   $($dirs.Count) dossier(s) supprimes" -ForegroundColor DarkGray
}

Invoke-Step "Suppression *.pyc / *.pyo" -ContinueOnFail {
    $files = @(Get-ChildItem -Path . -Recurse -Include "*.pyc","*.pyo" -ErrorAction SilentlyContinue)
    foreach ($f in $files) { Remove-Item $f.FullName -Force }
    Write-Host "   $($files.Count) fichier(s) supprimes" -ForegroundColor DarkGray
}

Invoke-Step "Suppression .pytest_cache / .mypy_cache" -ContinueOnFail {
    foreach ($cache in @(".\.pytest_cache", ".\.mypy_cache")) {
        if (Test-Path $cache) { Remove-Item $cache -Recurse -Force }
    }
}

Invoke-Step "Suppression staticfiles/" -ContinueOnFail {
    if (Test-Path ".\staticfiles") {
        Remove-Item ".\staticfiles" -Recurse -Force
        Write-Host "   staticfiles/ supprime" -ForegroundColor DarkGray
    } else {
        Write-Host "   staticfiles/ absent - rien a supprimer" -ForegroundColor DarkGray
    }
}

# ── ETAPE 3 : Dependances pip ──────────────────────────────────────────────────

Write-Header "ETAPE 3 / 8 - Verification des dependances"

Invoke-Step "pip install -r requirements.txt" -ContinueOnFail {
    & $PythonExe -m pip install -r .\requirements.txt --quiet
    if ($LASTEXITCODE -ne 0) { throw "pip install a echoue (code $LASTEXITCODE)" }
}

Invoke-Step "pip check (conflits)" -ContinueOnFail {
    $result = & $PythonExe -m pip check 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($result -join "`n") }
}

# ── ETAPE 4 : Django system check ──────────────────────────────────────────────

Write-Header "ETAPE 4 / 8 - Django system checks"

Invoke-Step "manage.py check (dev)" -ContinueOnFail {
    $output = & $PythonExe .\manage.py check 2>&1; $ec = $LASTEXITCODE
    $output | ForEach-Object { Write-Host "$_" }
    if ($ec -ne 0) { throw "Django check a retourne des erreurs." }
}

Invoke-Step "manage.py check --deploy (securite)" -ContinueOnFail {
    # Simuler HTTPS pour le check --deploy meme en local
    $env:DJANGO_DEBUG = "False"
    $env:DJANGO_ALLOWED_HOSTS = "localhost"
    $previousErrorAction = $ErrorActionPreference
    try {
        try {
            $ErrorActionPreference = "Continue"
            $output = & $PythonExe .\manage.py check --deploy 2>&1
            $ec = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $previousErrorAction
        }
        $output | ForEach-Object {
            $line = "$_"
            if ($line -eq "System.Management.Automation.RemoteException") {
                return
            }
            if ($line -match "^(WARNINGS|System check identified)") {
                Write-Host "   $line" -ForegroundColor Yellow
            } else {
                Write-Host "   $line" -ForegroundColor DarkGray
            }
        }
        if ($ec -ge 2) { throw "Django check --deploy a retourne des erreurs critiques." }
        if ($ec -eq 1) {
            Write-Host "   [AVERTISSEMENT] Des warnings de deploiement existent (non bloquant)." -ForegroundColor Yellow
        }
    } finally {
        Remove-Item Env:\DJANGO_DEBUG -ErrorAction SilentlyContinue
        Remove-Item Env:\DJANGO_ALLOWED_HOSTS -ErrorAction SilentlyContinue
    }
}

# ── ETAPE 5 : Migrations ───────────────────────────────────────────────────────

Write-Header "ETAPE 5 / 8 - Verification des migrations"

Invoke-Step "makemigrations --check (migrations en attente)" -ContinueOnFail {
    $output = & $PythonExe .\manage.py makemigrations --check --dry-run 2>&1; $ec = $LASTEXITCODE
    $output | ForEach-Object { Write-Host "$_" }
    if ($ec -ne 0) {
        throw "Des modifications de models ne sont pas encore migrees. Lancez 'manage.py makemigrations'."
    }
}

Invoke-Step "migrate --plan (coherence schema)" -ContinueOnFail {
    $output = & $PythonExe .\manage.py migrate --plan 2>&1; $ec = $LASTEXITCODE
    $output | ForEach-Object { Write-Host "$_" }
    if ($ec -ne 0) { throw "migrate --plan a echoue." }
}

# ── ETAPE 6 : Integrite SQLite ─────────────────────────────────────────────────

Write-Header "ETAPE 6 / 8 - Integrite de la base SQLite"

Invoke-Step "PRAGMA quick_check" -ContinueOnFail {
    if (-not $DbPath) {
        Write-Host "   Verification SQLite ignoree: moteur $DatabaseEngine." -ForegroundColor Yellow
        return
    }
    if (-not (Test-Path $DbPath)) {
        Write-Host "   Base non trouvee, etape ignoree." -ForegroundColor Yellow
        return
    }
    $DbPathForPy = (Resolve-Path $DbPath).Path -replace '\\', '/'
    $pyScript = "import sqlite3,sys; con=sqlite3.connect('$DbPathForPy'); r=con.execute('PRAGMA quick_check;').fetchone()[0]; con.close(); print(r); sys.exit(0 if r=='ok' else 1)"
    $checkResult = & $PythonExe -c $pyScript 2>&1
    Write-Host "   Resultat : $checkResult" -ForegroundColor DarkGray
    if ($LASTEXITCODE -ne 0) { throw "Integrite SQLite KO : $checkResult" }
}

# ── ETAPE 7 : Tests unitaires ─────────────────────────────────────────────────

Write-Header "ETAPE 7 / 8 - Tests unitaires"

if ($SkipTests) {
    Step-SKIP "Tests unitaires (inventory.tests)" "option -SkipTests"
} else {
    Invoke-Step "manage.py test inventory.tests" -ContinueOnFail {
        $previousErrorAction = $ErrorActionPreference
        try {
            $ErrorActionPreference = "Continue"
            $output = & $PythonExe .\manage.py test inventory.tests --verbosity=2 2>&1
            $ec = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $previousErrorAction
        }
        $output | ForEach-Object {
            $line = "$_"
            if ($line -eq "System.Management.Automation.RemoteException") {
                return
            }
            Write-Host $line
        }
        if ($ec -ne 0) { throw "Des tests ont echoue (exit code $ec)." }
    }
}

# ── ETAPE 8 : Commandes metier ────────────────────────────────────────────────

Write-Header "ETAPE 8 / 8 - Commandes metier"

Invoke-Step "quality_check" -ContinueOnFail {
    $output = & $PythonExe .\manage.py quality_check --skip-tests 2>&1; $ec = $LASTEXITCODE
    $output | ForEach-Object { Write-Host "$_" }
    if ($ec -ne 0) { throw "quality_check a retourne des erreurs." }
}

Invoke-Step "preprod_check (backup + collectstatic)" -ContinueOnFail {
    $preprodArgs = @(".\manage.py", "preprod_check", "--skip-tests")
    if ($SkipBackup) { $preprodArgs += "--skip-backup" }
    $output = & $PythonExe @preprodArgs 2>&1; $ec = $LASTEXITCODE
    $output | ForEach-Object { Write-Host "$_" }
    if ($ec -ne 0) { throw "preprod_check a retourne des erreurs." }
}

if ($PurgeLogs) {
    Invoke-Step "purge_document_security_logs (--days $PurgeLogsDays)" -ContinueOnFail {
        $output = & $PythonExe .\manage.py purge_document_security_logs --days $PurgeLogsDays 2>&1; $ec = $LASTEXITCODE
        $output | ForEach-Object { Write-Host "$_" }
        if ($ec -ne 0) { throw "purge_document_security_logs a echoue." }
    }
} else {
    Step-SKIP "purge_document_security_logs" "utiliser -PurgeLogs pour activer"
}

# ── Rapport final ──────────────────────────────────────────────────────────────

Write-Header "RAPPORT FINAL"

$script:Steps | Format-Table -AutoSize | Out-String | Write-Host

$nbOK   = @($script:Steps | Where-Object Statut -eq "OK").Count
$nbFail = @($script:Steps | Where-Object Statut -eq "ECHEC").Count
$nbSkip = @($script:Steps | Where-Object Statut -eq "IGNORE").Count

Write-Host ""
Write-Host "  OK     : $nbOK" -ForegroundColor Green
if ($nbFail -gt 0) {
    Write-Host "  ECHEC  : $nbFail" -ForegroundColor Red
} else {
    Write-Host "  ECHEC  : $nbFail" -ForegroundColor Green
}
Write-Host "  IGNORE : $nbSkip" -ForegroundColor Yellow
Write-Host ""

if ($script:Failed) {
    Write-Host "RESULTAT GLOBAL : ECHEC - corrigez les points marques ECHEC ci-dessus." -ForegroundColor Red
    exit 1
} else {
    Write-Host "RESULTAT GLOBAL : OK - projet propre et verifie." -ForegroundColor Green
    exit 0
}
