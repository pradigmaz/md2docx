import React from 'react'

export default function Settings({ settings, setSettings }) {
  const handleChange = (key, value) => {
    setSettings({ ...settings, [key]: parseFloat(value) })
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Размер шрифта (pt)
        </label>
        <input
          type="number"
          value={settings.fontSize}
          onChange={(e) => handleChange('fontSize', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Шрифт
        </label>
        <select
          value={settings.fontFamily}
          onChange={(e) => handleChange('fontFamily', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="Times New Roman">Times New Roman</option>
          <option value="Arial">Arial</option>
          <option value="Calibri">Calibri</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Межстрочный интервал
        </label>
        <select
          value={settings.lineSpacing}
          onChange={(e) => handleChange('lineSpacing', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="1.0">Одинарный</option>
          <option value="1.5">Полуторный</option>
          <option value="2.0">Двойной</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Красная строка (см)
        </label>
        <input
          type="number"
          step="0.1"
          value={settings.firstLineIndent}
          onChange={(e) => handleChange('firstLineIndent', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Поле сверху (см)
        </label>
        <input
          type="number"
          step="0.1"
          value={settings.marginTop}
          onChange={(e) => handleChange('marginTop', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Поле снизу (см)
        </label>
        <input
          type="number"
          step="0.1"
          value={settings.marginBottom}
          onChange={(e) => handleChange('marginBottom', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Поле слева (см)
        </label>
        <input
          type="number"
          step="0.1"
          value={settings.marginLeft}
          onChange={(e) => handleChange('marginLeft', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Поле справа (см)
        </label>
        <input
          type="number"
          step="0.1"
          value={settings.marginRight}
          onChange={(e) => handleChange('marginRight', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  )
}
