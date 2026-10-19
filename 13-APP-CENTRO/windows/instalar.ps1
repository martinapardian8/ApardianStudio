# Instala Centro APARDIAN en Windows: deja el icono en el Escritorio y en
# el menu Inicio. Abre la app del estudio en una ventana propia (Edge o
# Chrome en modo app, sin pestanas). No instala programas ni toca nada mas.
$ErrorActionPreference = 'Stop'
$URL    = 'https://claude.ai/artifact/7rZCs1Sf3iuHJwueEd9QYf'
$Nombre = 'Centro APARDIAN'
$Aqui   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dest   = Join-Path $env:LOCALAPPDATA 'CentroAPARDIAN'

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Copy-Item (Join-Path $Aqui 'CentroAPARDIAN.ico') (Join-Path $Dest 'CentroAPARDIAN.ico') -Force
$Icono = Join-Path $Dest 'CentroAPARDIAN.ico'

# Edge viene con Windows; si esta Chrome, se usa Chrome (ahi suele estar la sesion de claude.ai)
$candidatos = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
)
$Nav = $candidatos | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

$sh = New-Object -ComObject WScript.Shell
$lugares = @(
  [Environment]::GetFolderPath('Desktop'),
  [Environment]::GetFolderPath('Programs')
)
foreach ($carpeta in $lugares) {
  $lnk = $sh.CreateShortcut((Join-Path $carpeta "$Nombre.lnk"))
  if ($Nav) {
    $lnk.TargetPath = $Nav
    $lnk.Arguments  = "--app=$URL --window-size=1280,860"
  } else {
    $lnk.TargetPath = "$env:WINDIR\explorer.exe"
    $lnk.Arguments  = $URL
  }
  $lnk.IconLocation = "$Icono,0"
  $lnk.Description  = 'Calendario, carruseles, clientes y guiones de APARDIAN STUDIO'
  $lnk.Save()
}

Write-Host ''
Write-Host '  Listo: "Centro APARDIAN" quedo en el Escritorio y en el menu Inicio.' -ForegroundColor Green
if ($Nav) { Write-Host "  Se abre con: $Nav" } else { Write-Host '  Se abre en tu navegador.' }
Write-Host '  Abriendo la app...'
Start-Process -FilePath (Join-Path ([Environment]::GetFolderPath('Desktop')) "$Nombre.lnk")
