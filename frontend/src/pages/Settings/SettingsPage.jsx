import React, { useState, useEffect, useCallback } from 'react'
import { useSettingsStore, useNotifyStore } from '../../store/settingsStore'
import { systemApi } from '../../api/client'
import ApiTestPanel from './ApiTestPanel'
import './SettingsPage.css'

const BUILTIN_PROVIDERS = [
  { id: 'anthropic', name: 'Anthropic Claude', color: '#c8a04a', icon: '✦',
    placeholder: 'sk-ant-api03-…', hint: 'console.anthropic.com',
    defaultModel: 'claude-sonnet-4-6', style: 'anthropic' },
  { id: 'openai',    name: 'OpenAI',            color: '#10a37f', icon: '◎',
    placeholder: 'sk-…',            hint: 'platform.openai.com',
    defaultModel: 'gpt-4o',          style: 'openai' },
  { id: 'deepseek',  name: 'DeepSeek',           color: '#3498db', icon: '◈',
    placeholder: 'sk-…',            hint: 'platform.deepseek.com',
    defaultModel: 'deepseek-chat',   style: 'openai' },
  { id: 'moonshot',  name: 'Moonshot Kimi',       color: '#9b59b6', icon: '☽',
    placeholder: 'sk-…',            hint: 'platform.moonshot.cn',
    defaultModel: 'moonshot-v1-8k',  style: 'openai' },
  { id: 'gemini',    name: 'Google Gemini',        color: '#4285f4', icon: '✧',
    placeholder: 'AIza…',           hint: 'aistudio.google.com',
    defaultModel: 'gemini-2.0-flash', style: 'gemini' },
]

const QUICK_CUSTOM = [
  { id: 'glm',      name: '智谱 GLM',      color: '#00aaff', icon: '智',
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    placeholder: 'sk-…', hint: 'open.bigmodel.cn', defaultModel: 'glm-4-plus', style: 'openai' },
  { id: 'qwen',     name: '阿里 Qwen',     color: '#ff6a00', icon: '通',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    placeholder: 'sk-…', hint: 'dashscope.aliyuncs.com', defaultModel: 'qwen-max', style: 'openai' },
  { id: 'yi',       name: '零一万物 Yi',   color: '#6c63ff', icon: 'Yi',
    baseUrl: 'https://api.lingyiwanwu.com/v1',
    placeholder: 'sk-…', hint: 'platform.lingyiwanwu.com', defaultModel: 'yi-lightning', style: 'openai' },
  { id: 'baichuan', name: '百川',           color: '#e07b39', icon: '百',
    baseUrl: 'https://api.baichuan-ai.com/v1',
    placeholder: 'sk-…', hint: 'platform.baichuan-ai.com', defaultModel: 'Baichuan4', style: 'openai' },
  { id: 'doubao',   name: '字节 豆包',     color: '#1664ff', icon: '豆',
    baseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
    placeholder: 'sk-…', hint: 'console.volcengine.com', defaultModel: 'doubao-pro-32k', style: 'openai' },
  { id: 'hunyuan',  name: '腾讯 混元',     color: '#07c160', icon: '元',
    baseUrl: 'https://api.hunyuan.cloud.tencent.com/v1',
    placeholder: 'sk-…', hint: 'cloud.tencent.com', defaultModel: 'hunyuan-turbos', style: 'openai' },
  { id: 'spark',    name: '讯飞 星火',     color: '#0066ff', icon: '火',
    baseUrl: 'https://spark-api-open.xf-yun.com/v1',
    placeholder: 'sk-…', hint: 'xinghuo.xfyun.cn', defaultModel: '4.0Ultra', style: 'openai' },
  { id: 'minimax',  name: 'MiniMax',        color: '#8b5cf6', icon: 'M',
    baseUrl: 'https://api.minimaxi.com/v1',
    placeholder: 'sk-…', hint: 'minimaxi.com', defaultModel: 'abab6.5s-chat', style: 'openai' },
  { id: 'ollama',   name: 'Ollama (本地)',  color: '#555', icon: '⬡',
    baseUrl: 'http://localhost:11434/v1',
    placeholder: '（无需 Key）', hint: 'localhost:11434', defaultModel: 'llama3.3:latest', style: 'openai' },
]

const ACCENT_OPTIONS = [
  { value: 'red',  label: '朱砂红', hex: '#b5361e', desc: '朱砂正色，驱邪辟煞' },
  { value: 'gold', label: '琥珀橙', hex: '#b85c00', desc: '橙红暖色，活力进取' },
  { value: 'jade', label: '青碧绿', hex: '#1a7a52', desc: '青绿生机，清新雅致' },
]

const SETTING_TABS = [
  { id: 'api',   label: 'API 连接', icon: '🔗' },
  { id: 'model', label: 'AI 模型',  icon: '🧠' },
  { id: 'theme', label: '外观主题', icon: '🎨' },
  { id: 'test',  label: '接口测试', icon: '🧪' },
]

function useModelList(provider, apiKey, baseUrl, apiStyle, apiBaseUrl) {
  const [models,    setModels]    = useState([])
  const [loading,   setLoading]   = useState(false)
  const [source,    setSource]    = useState('')
  const [message,   setMessage]   = useState('')
  const [lastFetch, setLastFetch] = useState(null)

  useEffect(() => {
    if (!provider) return
    ;(async () => {
      try {
        const res  = await window.fetch(
          apiBaseUrl + '/api/v1/models/fallback?provider=' + encodeURIComponent(provider)
        )
        const json = await res.json()
        const list = (json.data && json.data[provider]) || []
        if (list.length) {
          setModels(list)
          setSource('fallback')
          setMessage('预置列表（点击「拉取最新」获取官方列表）')
        }
      } catch (_) {}
    })()
    setLastFetch(null)
  }, [provider, apiBaseUrl])

  const refresh = useCallback(async () => {
    if (!provider) return
    setLoading(true)
    try {
      const res  = await window.fetch(
        apiBaseUrl + '/api/v1/models?provider=' + encodeURIComponent(provider),
        {
          headers: {
            'X-LLM-Key':      apiKey  || '',
            'X-LLM-Base-Url': baseUrl || '',
            'X-LLM-Style':    apiStyle || 'openai',
          },
        }
      )
      const json = await res.json()
      if (json.success && json.data && json.data.models && json.data.models.length) {
        setModels(json.data.models)
        setSource(json.data.source || 'live')
        setMessage(json.data.message || '')
        setLastFetch(new Date())
      } else {
        setMessage((json.data && json.data.message) || '未获取到模型列表')
      }
    } catch (e) {
      setMessage('无法连接后端：' + e.message)
    } finally {
      setLoading(false)
    }
  }, [provider, apiKey, baseUrl, apiStyle, apiBaseUrl])

  return { models, loading, source, message, lastFetch, refresh }
}

export default function SettingsPage() {
  const s = useSettingsStore()
  const { notify } = useNotifyStore()

  const [apiStatus, setApiStatus] = useState(null)
  const [urlDraft,  setUrlDraft]  = useState(s.apiBaseUrl)
  const [showKey,   setShowKey]   = useState(false)
  const [tab,       setTab]       = useState('api')
  const [providerPane, setProviderPane] = useState('builtin')

  const [customForm, setCustomForm] = useState({
    name:    s.llmCustomName || '',
    baseUrl: s.llmBaseUrl    || '',
    style:   s.llmStyle      || 'openai',
    model:   s.llmModel      || '',
  })
  const [customModelInput, setCustomModelInput] = useState('')

  const builtinMeta = BUILTIN_PROVIDERS.find(function(p) { return p.id === s.llmProvider })
  const quickMeta   = QUICK_CUSTOM.find(function(p) { return p.id === s.llmProvider })
  const isBuiltin   = !!builtinMeta
  const effectiveStyle = s.llmStyle || (builtinMeta && builtinMeta.style) || (quickMeta && quickMeta.style) || 'openai'

  const { models, loading: modelLoading, source, message: modelMsg, lastFetch, refresh } =
    useModelList(s.llmProvider, s.llmKey, s.llmBaseUrl, effectiveStyle, s.apiBaseUrl)

  function applyBuiltin(p) {
    s.setLlmProvider(p.id)
    s.setLlmModel(p.defaultModel)
    s.setLlmBaseUrl('')
    s.setLlmStyle(p.style)
    s.setLlmCustomName('')
    setCustomModelInput('')
    setProviderPane('builtin')
  }

  function applyQuick(p) {
    s.setLlmProvider(p.id)
    s.setLlmModel(p.defaultModel)
    s.setLlmBaseUrl(p.baseUrl)
    s.setLlmStyle(p.style)
    s.setLlmCustomName(p.name)
    setCustomModelInput('')
    setCustomForm({ name: p.name, baseUrl: p.baseUrl, style: p.style, model: p.defaultModel })
    setProviderPane('quick')
  }

  function applyManual() {
    var name = customForm.name, baseUrl = customForm.baseUrl,
        style = customForm.style, model = customForm.model
    if (!baseUrl.trim()) { notify('请填写 Base URL', 'error'); return }
    if (!model.trim())   { notify('请填写模型名称', 'error'); return }
    var id = (name.toLowerCase().replace(/\s+/g, '-')) || 'custom'
    s.setLlmProvider(id)
    s.setLlmModel(model.trim())
    s.setLlmBaseUrl(baseUrl.trim())
    s.setLlmStyle(style)
    s.setLlmCustomName(name.trim() || '自定义供应商')
    setCustomModelInput('')
    notify('已应用自定义供应商：' + (name || baseUrl), 'success')
  }

  function selectModel(m) {
    s.setLlmModel(m)
    setCustomModelInput('')
  }

  function applyCustomModel() {
    var m = customModelInput.trim()
    if (!m) return
    s.setLlmModel(m)
    setCustomModelInput('')
    notify('模型已设为 ' + m, 'success')
  }

  async function testApi() {
    try {
      var r = await systemApi.health()
      setApiStatus(r.status === 'ok' ? 'ok' : 'fail')
      notify(r.status === 'ok' ? '后端连接正常 ✓' : '后端异常', r.status === 'ok' ? 'success' : 'error')
    } catch (_) {
      setApiStatus('fail'); notify('无法连接后端', 'error')
    }
  }

  var currentLabel = (builtinMeta && builtinMeta.name)
    || (quickMeta && quickMeta.name)
    || s.llmCustomName || s.llmProvider || '未选择'

  var keyHint = (builtinMeta && builtinMeta.hint)
    || (quickMeta && quickMeta.hint)
    || (s.llmBaseUrl ? s.llmBaseUrl.replace(/https?:\/\//, '').split('/')[0] : '')

  return (
    React.createElement('div', { className: 'page sp-page' },
      React.createElement('div', { className: 'page-header' },
        React.createElement('div', null,
          React.createElement('div', { className: 'page-title' }, '系统设置'),
          React.createElement('div', { className: 'page-subtitle' }, 'Settings — 后端连接 · AI模型 · 外观主题')
        )
      ),
      React.createElement('div', { className: 'sp-body' },
        React.createElement('aside', { className: 'sp-tabs' },
          SETTING_TABS.map(function(t) {
            return React.createElement('button', {
              key: t.id,
              className: 'sp-tab-btn' + (tab === t.id ? ' active' : ''),
              onClick: function() { setTab(t.id) }
            },
              React.createElement('span', null, t.icon),
              React.createElement('span', null, t.label)
            )
          })
        ),
        React.createElement('div', { className: 'sp-content' },
          tab === 'api' && ApiSection({ urlDraft, setUrlDraft, s, notify, testApi, apiStatus }),
          tab === 'model' && ModelSection({
            s, notify, providerPane, setProviderPane,
            customForm, setCustomForm,
            customModelInput, setCustomModelInput,
            builtinMeta, quickMeta, isBuiltin,
            effectiveStyle, models, modelLoading, source, modelMsg, lastFetch, refresh,
            showKey, setShowKey,
            applyBuiltin, applyQuick, applyManual, selectModel, applyCustomModel,
            currentLabel, keyHint,
          }),
          tab === 'theme' && ThemeSection({ s }),
          tab === 'test'  && React.createElement('div', { className: 'sp-section' },
            React.createElement('div', { className: 'sp-section-title' }, '接口测试'),
            React.createElement('div', { className: 'sp-section-desc' }, '测试各模块 API 端点是否正常工作'),
            React.createElement(ApiTestPanel)
          )
        )
      )
    )
  )
}

function ApiSection({ urlDraft, setUrlDraft, s, notify, testApi, apiStatus }) {
  return React.createElement('div', { className: 'sp-section' },
    React.createElement('div', { className: 'sp-section-title' }, '后端 API 连接'),
    React.createElement('div', { className: 'sp-section-desc' }, '八卦推演系统后端地址（默认本地 8888 端口）'),
    React.createElement('div', { className: 'sp-field-group' },
      React.createElement('label', null, 'API 地址'),
      React.createElement('div', { className: 'sp-input-row' },
        React.createElement('input', {
          value: urlDraft,
          onChange: function(e) { setUrlDraft(e.target.value) },
          placeholder: 'http://localhost:8888'
        }),
        React.createElement('button', {
          className: 'btn btn-primary',
          onClick: function() { s.setApiBaseUrl(urlDraft); notify('已保存', 'success') }
        }, '保存'),
        React.createElement('button', { className: 'btn', onClick: testApi }, '测试连接')
      ),
      apiStatus && React.createElement('div', { className: 'sp-status ' + apiStatus },
        apiStatus === 'ok' ? '✓ 连接正常' : '✕ 连接失败，请检查后端服务'
      ),
      React.createElement('div', { className: 'sp-hint' },
        React.createElement('code', null, s.apiBaseUrl), ' 当前地址'
      )
    )
  )
}

function ModelSection(props) {
  var {
    s, notify, providerPane, setProviderPane,
    customForm, setCustomForm, customModelInput, setCustomModelInput,
    builtinMeta, quickMeta, isBuiltin, effectiveStyle,
    models, modelLoading, source, modelMsg, lastFetch, refresh,
    showKey, setShowKey,
    applyBuiltin, applyQuick, applyManual, selectModel, applyCustomModel,
    currentLabel, keyHint,
  } = props

  return React.createElement('div', { className: 'sp-section' },
    React.createElement('div', { className: 'sp-section-title' }, 'AI 模型配置'),
    React.createElement('div', { className: 'sp-section-desc' },
      '选择内置供应商或添加任意自定义供应商（GLM、Qwen、Yi、Ollama 等）'
    ),

    // Provider pane selector
    React.createElement('div', { className: 'sp-field-group' },
      React.createElement('label', null, '供应商来源'),
      React.createElement('div', { style: { display: 'flex', gap: '0.4rem', marginBottom: '0.75rem' } },
        [
          { id: 'builtin', label: '内置供应商' },
          { id: 'quick',   label: '国内/常用' },
          { id: 'manual',  label: '手动配置' },
        ].map(function(p) {
          return React.createElement('button', {
            key: p.id,
            className: 'btn btn-sm' + (providerPane === p.id ? ' btn-primary' : ''),
            onClick: function() { setProviderPane(p.id) }
          }, p.label)
        })
      ),

      // Built-in grid
      providerPane === 'builtin' && React.createElement('div', { className: 'sp-provider-grid' },
        BUILTIN_PROVIDERS.map(function(p) {
          return React.createElement('button', {
            key: p.id,
            className: 'sp-provider-card' + (s.llmProvider === p.id ? ' active' : ''),
            style: { '--pc': p.color },
            onClick: function() { applyBuiltin(p) }
          },
            React.createElement('span', { className: 'sp-prov-icon' }, p.icon),
            React.createElement('span', { className: 'sp-prov-name' }, p.name),
            s.llmProvider === p.id && React.createElement('span', { className: 'sp-prov-check' }, '✓')
          )
        })
      ),

      // Quick custom grid
      providerPane === 'quick' && React.createElement('div', {
        className: 'sp-provider-grid',
        style: { gridTemplateColumns: 'repeat(3, 1fr)' }
      },
        QUICK_CUSTOM.map(function(p) {
          return React.createElement('button', {
            key: p.id,
            className: 'sp-provider-card' + (s.llmProvider === p.id ? ' active' : ''),
            style: { '--pc': p.color },
            onClick: function() { applyQuick(p) }
          },
            React.createElement('span', {
              className: 'sp-prov-icon',
              style: { fontSize: '0.7rem', fontWeight: 700 }
            }, p.icon),
            React.createElement('span', {
              className: 'sp-prov-name',
              style: { fontSize: 'var(--text-xs)' }
            }, p.name),
            s.llmProvider === p.id && React.createElement('span', { className: 'sp-prov-check' }, '✓')
          )
        })
      ),

      // Manual form
      providerPane === 'manual' && React.createElement('div', {
        style: {
          display: 'flex', flexDirection: 'column', gap: '0.65rem',
          padding: '0.75rem', background: 'var(--bg-subtle)',
          border: '1px solid var(--border)', borderRadius: 'var(--r-sm)'
        }
      },
        React.createElement('div', { className: 'form-row-2' },
          React.createElement('div', { className: 'form-group' },
            React.createElement('label', null, '供应商名称（展示用）'),
            React.createElement('input', {
              value: customForm.name,
              onChange: function(e) { setCustomForm(function(f) { return Object.assign({}, f, { name: e.target.value }) }) },
              placeholder: '如：My LLM'
            })
          ),
          React.createElement('div', { className: 'form-group' },
            React.createElement('label', null, 'API 风格'),
            React.createElement('select', {
              value: customForm.style,
              onChange: function(e) { setCustomForm(function(f) { return Object.assign({}, f, { style: e.target.value }) }) }
            },
              React.createElement('option', { value: 'openai' }, 'OpenAI 兼容（绝大多数）'),
              React.createElement('option', { value: 'anthropic' }, 'Anthropic 原生'),
              React.createElement('option', { value: 'gemini' }, 'Google Gemini')
            )
          )
        ),
        React.createElement('div', { className: 'form-group' },
          React.createElement('label', null,
            'Base URL ',
            React.createElement('span', { style: { color: 'var(--accent)', fontSize: '0.7rem' } }, '必填')
          ),
          React.createElement('input', {
            value: customForm.baseUrl,
            onChange: function(e) { setCustomForm(function(f) { return Object.assign({}, f, { baseUrl: e.target.value }) }) },
            placeholder: 'https://open.bigmodel.cn/api/paas/v4'
          }),
          React.createElement('div', { className: 'sp-hint' },
            'OpenAI 兼容接口填到 /v1 层级，不含 /chat/completions'
          )
        ),
        React.createElement('div', { className: 'form-group' },
          React.createElement('label', null,
            '默认模型名称 ',
            React.createElement('span', { style: { color: 'var(--accent)', fontSize: '0.7rem' } }, '必填')
          ),
          React.createElement('input', {
            value: customForm.model,
            onChange: function(e) { setCustomForm(function(f) { return Object.assign({}, f, { model: e.target.value }) }) },
            placeholder: '如：glm-4-plus'
          })
        ),
        React.createElement('button', {
          className: 'btn btn-primary',
          onClick: applyManual,
          style: { alignSelf: 'flex-start' }
        }, '✓ 应用配置')
      )
    ),

    // API Key
    React.createElement('div', { className: 'sp-field-group' },
      React.createElement('label', null,
        'API Key',
        keyHint && React.createElement('span', {
          style: { fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginLeft: '0.5rem' }
        }, '— ' + keyHint)
      ),
      React.createElement('div', { className: 'sp-input-row' },
        React.createElement('input', {
          type: showKey ? 'text' : 'password',
          value: s.llmKey,
          onChange: function(e) { s.setLlmKey(e.target.value) },
          placeholder: (builtinMeta && builtinMeta.placeholder)
            || (QUICK_CUSTOM.find(function(p) { return p.id === s.llmProvider }) || {}).placeholder
            || 'API Key'
        }),
        React.createElement('button', {
          className: 'btn btn-icon',
          onClick: function() { setShowKey(function(v) { return !v }) }
        }, showKey ? '🙈' : '👁')
      ),
      isBuiltin && builtinMeta && React.createElement('div', { className: 'sp-hint' },
        '从 ',
        React.createElement('a', { href: 'https://' + builtinMeta.hint, target: '_blank', rel: 'noreferrer' }, builtinMeta.hint),
        ' 获取'
      ),
      !isBuiltin && s.llmBaseUrl && React.createElement('div', { className: 'sp-hint' },
        'Base URL：',
        React.createElement('code', { style: { wordBreak: 'break-all' } }, s.llmBaseUrl)
      )
    ),

    // Proxy URL (built-in only)
    isBuiltin && React.createElement('div', { className: 'sp-field-group' },
      React.createElement('label', null, '代理 / 镜像地址（可选）'),
      React.createElement('input', {
        value: s.llmBaseUrl,
        onChange: function(e) { s.setLlmBaseUrl(e.target.value) },
        placeholder: '留空使用官方地址；填写可用于国内代理或自建镜像'
      })
    ),

    // Model selector
    React.createElement('div', { className: 'sp-field-group' },
      React.createElement('div', {
        style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }
      },
        React.createElement('label', { style: { margin: 0 } }, '模型版本'),
        React.createElement('button', {
          className: 'btn btn-sm',
          onClick: refresh,
          disabled: modelLoading,
          style: { display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: 'var(--text-xs)' }
        },
          modelLoading
            ? React.createElement(React.Fragment, null,
                React.createElement('span', { className: 'btn-spinner', style: { width: '10px', height: '10px' } }),
                '获取中…'
              )
            : '🔄 拉取最新列表'
        )
      ),

      modelMsg && React.createElement('div', {
        style: {
          fontSize: 'var(--text-xs)',
          color: source === 'live' ? 'var(--jade)' : 'var(--text-muted)',
          marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.35rem'
        }
      },
        React.createElement('span', null, source === 'live' ? '✓' : '○'),
        React.createElement('span', null, modelMsg),
        lastFetch && React.createElement('span', { style: { marginLeft: 'auto', opacity: 0.5 } },
          lastFetch.toLocaleTimeString()
        )
      ),

      models.length > 0 && React.createElement('select', {
        value: s.llmModel,
        onChange: function(e) { selectModel(e.target.value) },
        style: { marginBottom: '0.5rem' }
      },
        models.map(function(m) { return React.createElement('option', { key: m, value: m }, m) })
      ),

      // Free-text override
      React.createElement('div', {
        style: {
          display: 'flex', gap: '0.5rem', alignItems: 'center',
          padding: '0.55rem 0.75rem',
          background: 'var(--bg-subtle)',
          border: '1px solid ' + (customModelInput ? 'var(--accent-dim)' : 'var(--border)'),
          borderRadius: 'var(--r-sm)',
        }
      },
        React.createElement('input', {
          value: customModelInput,
          onChange: function(e) { setCustomModelInput(e.target.value) },
          placeholder: '直接输入任意模型 ID（优先级最高）',
          style: {
            flex: 1, background: 'transparent', border: 'none',
            outline: 'none', fontSize: 'var(--text-sm)', color: 'var(--text-primary)'
          },
          onKeyDown: function(e) { if (e.key === 'Enter') applyCustomModel() }
        }),
        customModelInput && React.createElement('button', {
          className: 'btn btn-sm btn-primary',
          onClick: applyCustomModel
        }, '应用')
      ),
      React.createElement('div', { className: 'sp-hint', style: { marginTop: '0.3rem' } },
        '手动输入任意模型 ID 后按 Enter 或点「应用」，可覆盖下拉选项'
      )
    ),

    // Config summary
    React.createElement('div', { className: 'sp-config-preview' },
      ...[
        ['供应商', currentLabel, null],
        ['当前模型', s.llmModel || '未设置', 'var(--accent)'],
        ['API Key', s.llmKey ? s.llmKey.slice(0, 8) + '…' + s.llmKey.slice(-4) : '未配置', null],
        ['Base URL', s.llmBaseUrl || (isBuiltin ? '官方默认' : '未填写'), null],
        ['API 风格', effectiveStyle, null],
        ['模型来源', source === 'live' ? '官方 API 实时' : '预置列表',
          source === 'live' ? 'var(--jade)' : 'var(--text-muted)'],
      ].map(function(row) {
        return React.createElement('div', { key: row[0], className: 'sp-cfg-row' },
          React.createElement('span', null, row[0]),
          React.createElement('code', {
            style: row[2] ? { color: row[2], wordBreak: 'break-all', fontSize: '0.68rem' } : { wordBreak: 'break-all', fontSize: '0.68rem' }
          }, row[1])
        )
      })
    )
  )
}

function ThemeSection({ s }) {
  return React.createElement('div', { className: 'sp-section' },
    React.createElement('div', { className: 'sp-section-title' }, '外观主题'),
    React.createElement('div', { className: 'sp-section-desc' }, '调整界面配色和显示模式'),
    React.createElement('div', { className: 'sp-field-group' },
      React.createElement('label', null, '主题色'),
      React.createElement('div', { className: 'sp-accent-grid' },
        ACCENT_OPTIONS.map(function(a) {
          return React.createElement('button', {
            key: a.value,
            className: 'sp-accent-card' + (s.accentColor === a.value ? ' active' : ''),
            style: { '--ac': a.hex },
            onClick: function() {
              s.setAccentColor(a.value)
              document.documentElement.setAttribute('data-accent', a.value)
            }
          },
            React.createElement('span', { className: 'sp-accent-dot' }),
            React.createElement('div', null,
              React.createElement('div', { className: 'sp-accent-name' }, a.label),
              React.createElement('div', { className: 'sp-accent-desc' }, a.desc)
            ),
            s.accentColor === a.value && React.createElement('span', { className: 'sp-accent-check' }, '✓')
          )
        })
      )
    ),
    React.createElement('div', { className: 'sp-field-group' },
      React.createElement('label', null, '颜色主题'),
      React.createElement('div', { className: 'sp-theme-toggle' },
        [{ v: '', l: '自动' }, { v: 'light', l: '浅色 宣纸' }, { v: 'dark', l: '深色 靛青' }].map(function(t) {
          return React.createElement('button', {
            key: t.v,
            className: 'sp-theme-btn' + ((s.theme || '') === t.v ? ' active' : ''),
            onClick: function() {
              s.setTheme(t.v)
              document.documentElement.setAttribute('data-theme', t.v)
            }
          }, t.l)
        })
      )
    )
  )
}
