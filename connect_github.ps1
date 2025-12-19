# Скрипт для подключения к GitHub
# Использование: .\connect_github.ps1 -Username "ВАШ_USERNAME" -RepoName "vols-gis"

param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "vols-gis"
)

Write-Host "=== Подключение к GitHub ===" -ForegroundColor Green
Write-Host ""

# Проверка текущей директории
$currentDir = Get-Location
Write-Host "Текущая директория: $currentDir" -ForegroundColor Yellow

# Проверка наличия .git
if (-not (Test-Path ".git")) {
    Write-Host "ОШИБКА: Git репозиторий не найден!" -ForegroundColor Red
    Write-Host "Убедитесь, что вы находитесь в корне проекта Vols BD" -ForegroundColor Yellow
    exit 1
}

# Проверка существования remote
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "Найден существующий remote: $existingRemote" -ForegroundColor Yellow
    $response = Read-Host "Заменить на новый? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        git remote remove origin
        Write-Host "Старый remote удален" -ForegroundColor Green
    } else {
        Write-Host "Отмена операции" -ForegroundColor Yellow
        exit 0
    }
}

# Добавление remote
$remoteUrl = "https://github.com/$Username/$RepoName.git"
Write-Host ""
Write-Host "Добавление remote: $remoteUrl" -ForegroundColor Cyan
git remote add origin $remoteUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Remote успешно добавлен!" -ForegroundColor Green
} else {
    Write-Host "✗ Ошибка при добавлении remote" -ForegroundColor Red
    exit 1
}

# Проверка remote
Write-Host ""
Write-Host "Проверка remote:" -ForegroundColor Cyan
git remote -v

# Проверка текущей ветки
$currentBranch = git branch --show-current
Write-Host ""
Write-Host "Текущая ветка: $currentBranch" -ForegroundColor Cyan

# Предложение отправить код
Write-Host ""
Write-Host "=== Готово к отправке кода ===" -ForegroundColor Green
Write-Host ""
Write-Host "Для отправки кода на GitHub выполните:" -ForegroundColor Yellow
Write-Host "  git push -u origin $currentBranch" -ForegroundColor White
Write-Host ""
Write-Host "Примечание: При первом push GitHub может запросить авторизацию." -ForegroundColor Yellow
Write-Host "Используйте Personal Access Token вместо пароля." -ForegroundColor Yellow
Write-Host ""
$pushNow = Read-Host "Отправить код сейчас? (y/n)"
if ($pushNow -eq "y" -or $pushNow -eq "Y") {
    Write-Host ""
    Write-Host "Отправка кода на GitHub..." -ForegroundColor Cyan
    git push -u origin $currentBranch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Код успешно отправлен на GitHub!" -ForegroundColor Green
        Write-Host "Репозиторий: https://github.com/$Username/$RepoName" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "✗ Ошибка при отправке кода" -ForegroundColor Red
        Write-Host "Проверьте:" -ForegroundColor Yellow
        Write-Host "  1. Репозиторий создан на GitHub" -ForegroundColor Yellow
        Write-Host "  2. Правильность username: $Username" -ForegroundColor Yellow
        Write-Host "  3. Настроена авторизация (Personal Access Token или SSH)" -ForegroundColor Yellow
    }
}

