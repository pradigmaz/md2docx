const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  convertFile: (filePath, settings) => ipcRenderer.invoke('convert-file', filePath, settings),
  openFile: (filePath) => ipcRenderer.invoke('open-file', filePath),
  openFolder: (filePath) => ipcRenderer.invoke('open-folder', filePath)
})
