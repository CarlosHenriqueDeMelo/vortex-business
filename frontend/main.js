const { app, BrowserWindow, Menu, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')

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
  backendProcess = spawn(backendPath, [], { detached: false })
  backendProcess.stdout.on('data', (data) => console.log(`Backend: ${data}`))
  backendProcess.stderr.on('data', (data) => console.error(`Backend erro: ${data}`))
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

  win.webContents.on('did-finish-load', () => {
    win.webContents.insertCSS(`
      .titlebar-button, .window-controls, [class*="traffic-light"] { opacity: 0 !important; pointer-events: none !important; }
    `)
  })

  win.loadFile(path.join(__dirname, 'src/pages/index.html'))

  ipcMain.removeAllListeners('window-minimize')
  ipcMain.removeAllListeners('window-maximize')
  ipcMain.removeAllListeners('window-close')

  ipcMain.on('window-minimize', () => win.minimize())
  ipcMain.on('window-maximize', () => {
    if (win.isMaximized()) win.unmaximize()
    else win.maximize()
  })
  ipcMain.on('window-close', () => win.close())
}

Menu.setApplicationMenu(null)

app.whenReady().then(() => {
  startBackend()
  setTimeout(createWindow, 1500)
})

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill()
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => {
  if (backendProcess) backendProcess.kill()
})
