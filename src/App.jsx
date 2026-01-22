import React, { useState } from 'react'
import FileUploader from './components/FileUploader'
import Settings from './components/Settings'
import Converter from './components/Converter'

function App() {
  const [file, setFile] = useState(null)
  const [settings, setSettings] = useState({
    fontSize: 14,
    fontFamily: 'Times New Roman',
    lineSpacing: 1.5,
    firstLineIndent: 1.27,
    marginTop: 2,
    marginBottom: 2,
    marginLeft: 3,
    marginRight: 1.5,
  })
  const [outputFile, setOutputFile] = useState(null)
  const [isConverting, setIsConverting] = useState(false)

  const handleConvert = async () => {
    if (!file) return
    setIsConverting(true)
    try {
      const result = await window.electronAPI.convertFile(file.path, settings)
      setOutputFile(result.outputPath)
    } catch (error) {
      console.error('Conversion failed:', error)
    }
    setIsConverting(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Markdown to DOCX
          </h1>
          <p className="text-gray-600">Конвертер с поддержкой LaTeX</p>
        </header>

        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">📁 Выберите файл</h2>
            <FileUploader file={file} setFile={setFile} />
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">⚙️ Настройки</h2>
            <Settings settings={settings} setSettings={setSettings} />
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <Converter
              file={file}
              isConverting={isConverting}
              outputFile={outputFile}
              onConvert={handleConvert}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
