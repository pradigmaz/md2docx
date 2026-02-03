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
  const [error, setError] = useState(null)

  const handleConvert = async () => {
    if (!file) return
    setIsConverting(true)
    setError(null)
    setOutputFile(null)
    try {
      const result = await window.electronAPI.convertFile(file.path, settings)
      setOutputFile(result.outputPath)
    } catch (err) {
      console.error('Conversion failed:', err)
      setError(err.message || 'Произошла ошибка при конвертации')
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

        {/* Error notification */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl shadow-lg animate-fade-in">
            <div className="flex items-start gap-3">
              <span className="text-2xl">⚠️</span>
              <div className="flex-1">
                <h3 className="font-semibold text-red-800">Ошибка конвертации</h3>
                <p className="text-red-700 mt-1">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-600 text-xl leading-none"
              >
                ×
              </button>
            </div>
          </div>
        )}

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
