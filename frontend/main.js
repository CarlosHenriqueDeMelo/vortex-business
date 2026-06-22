const { app, BrowserWindow, Menu, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')
const os = require('os')
let backendProcess = null

function getBackendPath() {
  const exeName = process.platform === 'win32' ? 'vortex-backend.exe' : 'vortex-backend'
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend-bin', exeName)
  }
  return path.join(__dirname, 'backend-bin', exeName)
}

function startBackend() {
  const backendPath = getBackendPath()
  if (!fs.existsSync(backendPath)) {
    console.error('Backend nao encontrado em:', backendPath)
    return
  }
  try {
    backendProcess = spawn(backendPath, [], {
      detached: false,
      windowsHide: true,
      cwd: path.dirname(backendPath)
    })
    backendProcess.on('error', (err) => console.error('Erro ao iniciar backend:', err))
  } catch (e) {
    console.error('Excecao ao iniciar backend:', e)
  }
}

function getLocalIP() {
  const interfaces = os.networkInterfaces()
  for (const nome in interfaces) {
    for (const iface of interfaces[nome]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        const nomeMinusculo = nome.toLowerCase()
        if (nomeMinusculo.includes('docker') || nomeMinusculo.includes('vbox') || nomeMinusculo.includes('veth') || nomeMinusculo.includes('virtual')) {
          continue
        }
        return iface.address
      }
    }
  }
  return null
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 700,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#0d0d0f',
    frame: false,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    }
  })
  win.loadFile(path.join(__dirname, 'src/pages/index.html'))
  ipcMain.removeAllListeners('window-minimize')
  ipcMain.removeAllListeners('window-maximize')
  ipcMain.removeAllListeners('window-close')
  ipcMain.removeAllListeners('get-sync-info')
  ipcMain.on('window-minimize', () => win.minimize())
  ipcMain.on('window-maximize', () => {
    if (win.isMaximized()) win.unmaximize()
    else win.maximize()
  })
  ipcMain.on('window-close', () => win.close())
  ipcMain.handle('get-sync-info', () => {
    return {
      ip: getLocalIP(),
      porta: 5000
    }
  })
}

Menu.setApplicationMenu(null)
app.whenReady().then(() => {
  startBackend()
  setTimeout(createWindow, 3000)
})
app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill()
  if (process.platform !== 'darwin') app.quit()
})
app.on('before-quit', () => {
  if (backendProcess) backendProcess.kill()
})
