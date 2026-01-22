import React, { useState } from 'react'

export default function Converter({ file, isConverting, outputFile, onConvert }) {
  const [copied, setCopied] = useState(false)

  const handleCopyPath = async () => {
    if (outputFile) {
      await navigator.clipboard.writeText(outputFile)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleOpenFile = () => {
    if (outputFile && window.electronAPI) {
      window.electronAPI.openFile(outputFile)
    }
  }

  const handleOpenFolder = () => {
    if (outputFile && window.electronAPI) {
      window.electronAPI.openFolder(outputFile)
    }
  }

  return (
    <div className="text-center">
      <button
        onClick={onConvert}
        disabled={!file || isConverting}
        className={`px-8 py-3 rounded-lg font-medium text-lg transition-all ${
          !file || isConverting
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
        }`}
      >
        {isConverting ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Конвертация...
          </span>
        ) : (
          '🔄 Конвертировать в DOCX'
        )}
      </button>

      {/* Progress Bar */}
      {isConverting && (
        <div className="mt-4">
          <div className="w-full max-w-md mx-auto bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
          </div>
          <p className="text-sm text-gray-500 mt-2">Обработка документа...</p>
        </div>
      )}

      {/* Success Result */}
      {outputFile && !isConverting && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg animate-fade-in">
          <div className="flex items-center justify-center gap-2 text-green-800 font-medium mb-3">
            <span className="text-xl">✅</span>
            <span>Файл успешно сохранён!</span>
          </div>

          <div className="flex items-center gap-2 bg-white rounded-lg p-2 border border-green-200">
            <code className="text-sm text-gray-600 flex-1 truncate font-mono">
              {outputFile}
            </code>
            <button
              onClick={handleCopyPath}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                copied
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
              title="Копировать путь"
            >
              {copied ? '✓' : '📋'}
            </button>
          </div>

          <div className="flex gap-2 justify-center mt-4">
            <button
              onClick={handleOpenFile}
              className="flex items-center gap-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-colors"
            >
              📂 Открыть файл
            </button>
            <button
              onClick={handleOpenFolder}
              className="flex items-center gap-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg text-sm transition-colors"
            >
              📁 Показать в папке
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
