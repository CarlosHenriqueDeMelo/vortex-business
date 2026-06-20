const { app, BrowserWindow } = require('electron')
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
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    }
  })

  win.loadFile(path.join(__dirname, 'src/pages/index.html'))
}

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
