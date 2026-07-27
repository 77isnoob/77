# 第二大脑自动同步脚本
# 监测文件变化，自动 git add + commit + push

$watchPath = $PSScriptRoot
$debounceSeconds = 10  # 保存后等10秒再同步（避免频繁提交）

Write-Host "🧠 第二大脑自动同步已启动" -ForegroundColor Green
Write-Host "📁 监测目录: $watchPath" -ForegroundColor Cyan
Write-Host "⏱  保存后 ${debounceSeconds}秒 自动同步" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止`n" -ForegroundColor Yellow

# 进入仓库目录
Set-Location $watchPath

# 创建文件监测器
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $watchPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::Directory

# 防抖计时器
$lastSync = [DateTime]::MinValue

# 注册事件
Register-ObjectEvent $watcher "Changed" -Action {
    $now = Get-Date
    $elapsed = ($now - $lastSync).TotalSeconds
    
    # 忽略 .git 目录的变化
    if ($Event.SourceEventArgs.FullPath -like "*\.git\*") { return }
    if ($elapsed -lt $debounceSeconds) { return }
    
    $global:lastSync = $now
    $changedFile = $Event.SourceEventArgs.Name
    
    Write-Host "📝 检测到变化: $changedFile" -ForegroundColor Yellow
    
    Set-Location $watchPath
    git add . 2>$null
    $status = git status --porcelain 2>$null
    
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "自动同步: $timestamp" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            git push 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 同步成功!" -ForegroundColor Green
            } else {
                Write-Host "❌ 推送失败，请检查网络" -ForegroundColor Red
            }
        }
    }
}

Register-ObjectEvent $watcher "Created" -Action {
    $now = Get-Date
    $elapsed = ($now - $lastSync).TotalSeconds
    
    if ($Event.SourceEventArgs.FullPath -like "*\.git\*") { return }
    if ($elapsed -lt $debounceSeconds) { return }
    
    $global:lastSync = $now
    $changedFile = $Event.SourceEventArgs.Name
    
    Write-Host "🆕 新文件: $changedFile" -ForegroundColor Yellow
    
    Set-Location $watchPath
    git add . 2>$null
    $status = git status --porcelain 2>$null
    
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "自动同步: $timestamp" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            git push 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 同步成功!" -ForegroundColor Green
            } else {
                Write-Host "❌ 推送失败，请检查网络" -ForegroundColor Red
            }
        }
    }
}

Register-ObjectEvent $watcher "Deleted" -Action {
    $now = Get-Date
    $elapsed = ($now - $lastSync).TotalSeconds
    
    if ($Event.SourceEventArgs.FullPath -like "*\.git\*") { return }
    if ($elapsed -lt $debounceSeconds) { return }
    
    $global:lastSync = $now
    $changedFile = $Event.SourceEventArgs.Name
    
    Write-Host "🗑  删除文件: $changedFile" -ForegroundColor Yellow
    
    Set-Location $watchPath
    git add . 2>$null
    $status = git status --porcelain 2>$null
    
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "自动同步: $timestamp" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            git push 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 同步成功!" -ForegroundColor Green
            } else {
                Write-Host "❌ 推送失败，请检查网络" -ForegroundColor Red
            }
        }
    }
}

# 保持运行
while ($true) { Start-Sleep -Seconds 1 }
