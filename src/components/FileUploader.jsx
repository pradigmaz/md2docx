import React, { useRef, useState } from 'react'

export default function FileUploader({ file, setFile }) {
  const fileInputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile?.name.endsWith('.md')) {
      setFile(droppedFile)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const getContainerClasses = () => {
    const base = "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200"
    
    if (file) {
      return `${base} border-green-400 bg-green-50 hover:border-green-500 hover:bg-green-100`
    }
    
    if (isDragging) {
      return `${base} border-blue-500 bg-blue-100 scale-[1.02] shadow-lg`
    }
    
    return `${base} border-gray-300 hover:border-blue-500 hover:bg-blue-50`
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => fileInputRef.current?.click()}
      className={getContainerClasses()}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".md"
        onChange={handleFileSelect}
        className="hidden"
      />

      {file ? (
        <div className="animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-3">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="font-semibold text-green-800 text-lg">{file.name}</p>
          <p className="text-sm text-green-600 mt-1">
            {(file.size / 1024).toFixed(1)} KB • Готов к конвертации
          </p>
          <button
            onClick={(e) => { e.stopPropagation(); setFile(null); }}
            className="mt-3 px-4 py-1.5 text-red-600 hover:text-white hover:bg-red-500 border border-red-300 hover:border-red-500 rounded-full text-sm transition-colors"
          >
            Удалить
          </button>
        </div>
      ) : isDragging ? (
        <div className="animate-pulse">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-200 rounded-full mb-3">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </div>
          <p className="text-blue-700 font-medium text-lg">Отпустите файл</p>
        </div>
      ) : (
        <div>
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-3 group-hover:bg-blue-100 transition-colors">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <p className="text-gray-700 font-medium">
            Перетащите .md файл сюда
          </p>
          <p className="text-gray-500 text-sm mt-1">
            или нажмите для выбора
          </p>
        </div>
      )}
    </div>
  )
}
