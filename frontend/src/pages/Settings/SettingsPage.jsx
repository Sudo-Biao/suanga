import React, { useState } from 'react'
import { useSettingsStore, useNotifyStore } from '../../store/settingsStore'
import { systemApi } from '../../api/client'
import ApiTestPanel from './ApiTestPanel'
import './SettingsPage.css'

const PROVIDERS = [
  { id:'anthropic', name:'Anthropic Claude', color:'#c8a04a', icon:'✦',
    models:['claude-sonnet-4-6','claude-opus-4-6','claude-haiku-4-5-20251001'],
    default:'claude-sonnet-4-6', placeholder:'sk-ant-api03-…', hint:'console.anthropic.com' },
  { id:'deepseek', name:'DeepSeek', color:'#3498db', icon:'◈',
    models:['deepseek-chat','deepseek-reasoner'],
    default:'deepseek-chat', placeholder:'sk-…', hint:'platform.deepseek.com' },
  { id:'openai', name:'OpenAI GPT', color:'#10a37f', icon:'◎',
    models:['gpt-4o','gpt-4o-mini','gpt-4-turbo'],
    default:'gpt-4o', placeholder:'sk-…', hint:'platform.openai.com' },
  { id:'moonshot', name:'Moonshot Kimi', color:'#9b59b6', icon:'☽',
    models:['moonshot-v1-8k','moonshot-v1-32k','moonshot-v1-128k'],
    default:'moonshot-v1-8k', placeholder:'sk-…', hint:'platform.moonshot.cn' },
]

const ACCENT_OPTIONS = [
  { value:'red',  label:'朱砂红', hex:'#b5361e', desc:'朱砂正色，驱邪辟煞' },
  { value:'gold', label:'琥珀橙', hex:'#b85c00', desc:'橙红暖色，活力进取' },
  { value:'jade', label:'青碧绿', hex:'#1a7a52', desc:'青绿生机，清新雅致' },
]

export default function SettingsPage() {
  const s = useSettingsStore()
  const { notify } = useNotifyStore()
  const [apiStatus, setApiStatus] = useState(null)
  const [urlDraft, setUrlDraft]   = useState(s.apiBaseUrl)
  const [showKey, setShowKey]     = useState(false)
  const [tab, setTab]             = useState('api')

  const prov = PROVIDERS.find(p => p.id === s.llmProvider) || PROVIDERS[0]

  const testApi = async () => {
    try {
      const r = await systemApi.health()
      setApiStatus(r.status === 'ok' ? 'ok' : 'fail')
      notify(r.status === 'ok' ? '后端连接正常 ✓' : '后端异常', r.status==='ok'?'success':'error')
    } catch { setApiStatus('fail'); notify('无法连接后端', 'error') }
  }

  const SETTING_TABS = [
    { id:'api',     label:'API 连接', icon:'🔗' },
    { id:'model',   label:'AI 模型',  icon:'🧠' },
    { id:'theme',   label:'外观主题', icon:'🎨' },
    { id:'test',    label:'接口测试', icon:'🧪' },
  ]

  return (
    <div className="page sp-page">
      <div className="page-header">
        <div>
          <div className="page-title">系统设置</div>
          <div className="page-subtitle">Settings — 后端连接 · AI模型 · 外观主题</div>
        </div>
      </div>

      <div className="sp-body">
        {/* ── Vertical tab sidebar ── */}
        <aside className="sp-tabs">
          {SETTING_TABS.map(t => (
            <button key={t.id} className={`sp-tab-btn ${tab===t.id?'active':''}`}
              onClick={() => setTab(t.id)}>
              <span>{t.icon}</span><span>{t.label}</span>
            </button>
          ))}
        </aside>

        {/* ── Content panel ── */}
        <div className="sp-content">

          {tab === 'api' && (
            <div className="sp-section">
              <div className="sp-section-title">后端 API 连接</div>
              <div className="sp-section-desc">八卦推演系统后端服务地址（默认本地 8888 端口）</div>

              <div className="sp-field-group">
                <label>API 地址</label>
                <div className="sp-input-row">
                  <input value={urlDraft} onChange={e => setUrlDraft(e.target.value)}
                    placeholder="http://localhost:8888" />
                  <button className="btn btn-primary" onClick={() => { s.setApiBaseUrl(urlDraft); notify('已保存','success') }}>
                    保存
                  </button>
                  <button className="btn" onClick={testApi}>测试连接</button>
                </div>
                {apiStatus && (
                  <div className={`sp-status ${apiStatus}`}>
                    {apiStatus==='ok' ? '✓ 连接正常' : '✕ 连接失败，请检查后端服务'}
                  </div>
                )}
                <div className="sp-hint">
                  <code>{s.apiBaseUrl}</code>
                  <span> 当前地址 · 默认端口 8888</span>
                </div>
              </div>
            </div>
          )}

          {tab === 'model' && (
            <div className="sp-section">
              <div className="sp-section-title">AI 模型配置</div>
              <div className="sp-section-desc">选择用于命理解读的 AI 提供商和模型</div>

              {/* Provider cards */}
              <div className="sp-field-group">
                <label>AI 供应商</label>
                <div className="sp-provider-grid">
                  {PROVIDERS.map(p => (
                    <button key={p.id}
                      className={`sp-provider-card ${s.llmProvider===p.id?'active':''}`}
                      style={{ '--pc': p.color }}
                      onClick={() => { s.setLlmProvider(p.id); s.setLlmModel(p.default) }}>
                      <span className="sp-prov-icon">{p.icon}</span>
                      <span className="sp-prov-name">{p.name}</span>
                      {s.llmProvider===p.id && <span className="sp-prov-check">✓</span>}
                    </button>
                  ))}
                </div>
              </div>

              {/* Model select */}
              <div className="sp-field-group">
                <label>模型版本</label>
                <select value={s.llmModel || prov.default}
                  onChange={e => s.setLlmModel(e.target.value)}>
                  {prov.models.map(m => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>

              {/* API Key */}
              <div className="sp-field-group">
                <label>API Key</label>
                <div className="sp-input-row">
                  <input type={showKey?'text':'password'} value={s.llmKey}
                    onChange={e => s.setLlmKey(e.target.value)}
                    placeholder={prov.placeholder} />
                  <button className="btn btn-icon" onClick={() => setShowKey(v => !v)}>
                    {showKey ? '🙈' : '👁'}
                  </button>
                </div>
                <div className="sp-hint">从 <a href={`https://${prov.hint}`} target="_blank" rel="noreferrer">{prov.hint}</a> 获取</div>
              </div>

              {/* Custom base URL */}
              <div className="sp-field-group">
                <label>自定义 Base URL（可选）</label>
                <input value={s.llmBaseUrl} onChange={e => s.setLlmBaseUrl(e.target.value)}
                  placeholder="留空使用官方默认地址" />
                <div className="sp-hint">用于代理或国内镜像地址</div>
              </div>

              {/* Current config */}
              <div className="sp-config-preview">
                <div className="sp-cfg-row"><span>供应商</span><code>{s.llmProvider || '未设置'}</code></div>
                <div className="sp-cfg-row"><span>模型</span><code>{s.llmModel || prov.default}</code></div>
                <div className="sp-cfg-row"><span>Key</span><code>{s.llmKey ? s.llmKey.slice(0,8)+'…' : '未配置'}</code></div>
              </div>
            </div>
          )}

          {tab === 'theme' && (
            <div className="sp-section">
              <div className="sp-section-title">外观主题</div>
              <div className="sp-section-desc">调整界面配色和显示模式</div>

              {/* Accent color */}
              <div className="sp-field-group">
                <label>主题色</label>
                <div className="sp-accent-grid">
                  {ACCENT_OPTIONS.map(a => (
                    <button key={a.value}
                      className={`sp-accent-card ${s.accentColor===a.value?'active':''}`}
                      style={{ '--ac': a.hex }}
                      onClick={() => { s.setAccentColor(a.value); document.documentElement.setAttribute('data-accent', a.value) }}>
                      <span className="sp-accent-dot"/>
                      <div>
                        <div className="sp-accent-name">{a.label}</div>
                        <div className="sp-accent-desc">{a.desc}</div>
                      </div>
                      {s.accentColor===a.value && <span className="sp-accent-check">✓</span>}
                    </button>
                  ))}
                </div>
              </div>

              {/* Theme toggle */}
              <div className="sp-field-group">
                <label>颜色主题</label>
                <div className="sp-theme-toggle">
                  {[{v:'',l:'自动'},{v:'light',l:'浅色 宣纸'},{v:'dark',l:'深色 靛青'}].map(t => (
                    <button key={t.v}
                      className={`sp-theme-btn ${(s.theme||'')===t.v?'active':''}`}
                      onClick={() => { s.setTheme(t.v); document.documentElement.setAttribute('data-theme', t.v) }}>
                      {t.l}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab === 'test' && (
            <div className="sp-section">
              <div className="sp-section-title">接口测试</div>
              <div className="sp-section-desc">测试各模块 API 端点是否正常工作</div>
              <ApiTestPanel />
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
