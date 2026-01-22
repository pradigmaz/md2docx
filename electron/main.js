const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const isDev = require('electron-is-dev')

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    resizable: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    autoHideMenuBar: false,
    titleBarStyle: 'default'
  })

  const startUrl = isDev
    ? 'http://localhost:5173'
    : `file://${path.join(__dirname, '../dist/index.html')}`

  mainWindow.loadURL(startUrl)

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// IPC handlers
ipcMain.handle('convert-file', async (event, filePath, settings) => {
  return new Promise((resolve, reject) => {
    const pythonDir = path.join(__dirname, '../python')
    const venvPython = path.join(__dirname, '../venv/bin/python')
    const outputDir = path.dirname(filePath)
    const outputFile = path.join(outputDir, path.basename(filePath, '.md') + '.docx')

    const args = [
      '-m', 'md2docx',
      filePath,
      outputFile,
      '--settings', JSON.stringify(settings)
    ]

    // Check if venv exists, log which python we're using
    const fs = require('fs')
    let pythonCmd
    if (fs.existsSync(venvPython)) {
      pythonCmd = venvPython
      console.log('Using venv python:', pythonCmd)
    } else {
      pythonCmd = 'python3.14'
      console.log('Venv not found at', venvPython, ', using python3.14')
    }

    const pythonProcess = spawn(pythonCmd, args, {
      cwd: pythonDir,
      stdio: ['pipe', 'pipe', 'pipe']
    })

    let stdout = ''
    let stderr = ''

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ outputPath: outputFile })
      } else {
        reject(new Error(`Conversion failed: ${stderr}`))
      }
    })
  })
})

ipcMain.handle('open-file', async (event, filePath) => {
  await shell.openPath(filePath)
})

ipcMain.handle('open-folder', async (event, filePath) => {
  await shell.showItemInFolder(filePath)
})
