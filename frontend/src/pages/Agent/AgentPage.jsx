import React, { useState, useRef, useEffect } from 'react'
import BirthForm from '../../components/UI/BirthForm'
import { baziApi, liuyaoApi, qimenApi, fengshuiApi } from '../../api/client'
import { useSettingsStore, useNotifyStore } from '../../store/settingsStore'
import './AgentPage.css'

const MODES = [
  { id:'consult',  label:'命理顾问', icon:'🔮', desc:'自由问答综合解读',    color:'#b5361e' },
  { id:'bazi',     label:'八字解读', icon:'🀄', desc:'先起八字盘再AI深析', color:'#1e5c96' },
  { id:'liuyao',   label:'六爻占卜', icon:'☯',  desc:'先起卦再AI深度解读', color:'#1a7a52' },
  { id:'qimen',    label:'奇门策略', icon:'🧭', desc:'先起奇门盘再AI分析', color:'#b85c00' },
  { id:'fengshui', label:'风水建议', icon:'🏡', desc:'先分析宅卦再AI建议', color:'#6a3d8a' },
]

const QUICK_PROMPTS = {
  consult: ['今年整体运势如何？', '我适合什么行业？', '如何提升财运？', '感情发展前景？'],
  bazi:    ['请解读八字格局和用神', '分析事业运程重点', '婚姻宫和感情缘分', '大运流年如何预测'],
  liuyao:  ['此次创业是否顺利？', '感情是否可以发展？', '这次投资能否盈利？', '求职能否成功？'],
  qimen:   ['当前谈判形势如何？', '今天适合签合同吗？', '哪个方向发展最有利？', '此事最终能否成功？'],
  fengshui:['主卧如何提升感情运？', '书房最佳方位建议', '财位在哪里如何布局？', '厨房凶方怎么化解？'],
}

// Status labels for each step
const STEP_LABELS = {
  bazi:     ['正在排八字命盘…', '起盘完成，AI深度解读中…'],
  liuyao:   ['正在起卦…', '卦象已成，AI深度解读中…'],
  qimen:    ['正在起奇门遁甲盘…', '排盘完成，AI战略分析中…'],
  fengshui: ['正在分析风水格局…', '分析完成，AI布局建议中…'],
}

export default function AgentPage() {
  const { apiBaseUrl, llmProvider, llmKey, llmBaseUrl, llmModel } = useSettingsStore()
  const PROVIDER_DEFAULTS = { anthropic:'claude-sonnet-4-6', deepseek:'deepseek-chat', openai:'gpt-4o', moonshot:'moonshot-v1-8k' }
  const effectiveModel = llmModel || PROVIDER_DEFAULTS[llmProvider] || 'claude-sonnet-4-6'
  const { notify } = useNotifyStore()

  const [mode, setMode]         = useState('consult')
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [streaming, setStreaming] = useState(false)
  const [moduleData, setModuleData] = useState(null)   // computed result from feature module
  const [moduleLoading, setModuleLoading] = useState(false)  // step 1 loading
  const [birth, setBirth]       = useState({ year:1990, month:6, day:15, hour:8, minute:0, gender:'male' })
  const [focus, setFocus]       = useState('')
  const [liuyaoMethod, setLiuyaoMethod] = useState('time')
  const [houseFacing, setHouseFacing]   = useState('南')
  const [birthYear, setBirthYear]       = useState(1990)
  const bottomRef = useRef(null)
  const abortRef  = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior:'smooth' }) }, [messages])

  // When mode changes, reset computed data
  const switchMode = (m) => { setMode(m); setMessages([]); setModuleData(null); setQuestion('') }

  // ── Step 1: Call the feature module to get real computed data ──
  const computeModuleData = async () => {
    if (mode === 'consult') return null  // no module needed
    setModuleLoading(true)
    try {
      let result = null
      switch (mode) {
        case 'bazi':
          result = await baziApi.chart(birth)
          break
        case 'liuyao':
          result = await liuyaoApi.divine({ method: liuyaoMethod, question: question || '请占问' })
          break
        case 'qimen':
          result = await qimenApi.now()
          break
        case 'fengshui':
          result = await fengshuiApi.analysis({ birth_year: birthYear, gender: birth.gender, house_facing: houseFacing })
          break
        default:
          result = null
      }
      setModuleData(result)
      return result
    } catch (e) {
      notify('起盘失败: ' + e.message, 'error')
      return null
    } finally {
      setModuleLoading(false)
    }
  }

  // ── Step 2: Send to AI with computed data ──
  const sendToAI = async (q, data) => {
    setStreaming(true)
    if (!llmKey.trim()) {
      setMessages(p => [...p, { role:'assistant', ts:Date.now(),
        content:'⚠️ 请先在【设置】页面配置 API Key 才能使用 AI 顾问功能。', error:true }])
      setStreaming(false); return
    }
    setMessages(p => [...p, { role:'assistant', content:'', ts:Date.now() }])
    try {
      abortRef.current = new AbortController()
      const body = buildBody(q, data)
      const resp = await fetch(`${apiBaseUrl}/api/v1/agent/${mode}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-LLM-Key': llmKey.trim(),
          'X-LLM-Provider': llmProvider || 'anthropic',
          'X-LLM-Base-Url': llmBaseUrl.trim() || '',
          'X-LLM-Model': effectiveModel,
        },
        body: JSON.stringify(body),
        signal: abortRef.current.signal,
      })
      if (!resp.ok) { const e = await resp.json().catch(() => ({ detail:'请求失败' })); throw new Error(e.detail || `HTTP ${resp.status}`) }
      const reader = resp.body.getReader(); const decoder = new TextDecoder(); let buf = ''
      while (true) {
        const { done, value } = await reader.read(); if (done) break
        buf += decoder.decode(value, { stream:true })
        const lines = buf.split('\n'); buf = lines.pop()
        for (const line of lines) {
          if (!line.startsWith('data:')) continue
          const d = line.slice(5).trim(); if (d === '[DONE]') break
          try {
            const p = JSON.parse(d)
            if (p.text) setMessages(prev => {
              const u = [...prev]; u[u.length-1] = { ...u[u.length-1], content: u[u.length-1].content + p.text }; return u
            })
          } catch (_) {}
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        notify(e.message, 'error')
        setMessages(prev => { const u = [...prev]; u[u.length-1] = { ...u[u.length-1], content:`⚠️ 出错：${e.message}`, error:true }; return u })
      }
    } finally { setStreaming(false); abortRef.current = null }
  }

  // ── Main send handler: Step1 → Step2 ──
  const sendMessage = async () => {
    if (streaming || moduleLoading) return
    const q = question.trim() || buildDefault()
    setMessages(p => [...p, { role:'user', content: buildUserDisplay(q), ts:Date.now() }])
    setQuestion('')

    if (mode === 'consult') {
      // Direct AI query, no module needed
      await sendToAI(q, null)
      return
    }

    // Modes that need computed data first
    // Check if we already have fresh data (user can reuse existing data)
    let data = moduleData
    if (!data) {
      setMessages(p => [...p, {
        role:'system', content: STEP_LABELS[mode]?.[0] || '正在起盘…', ts:Date.now(), step:1
      }])
      data = await computeModuleData()
      if (!data) {
        setMessages(p => [...p, { role:'assistant', content:'⚠️ 起盘失败，请检查参数后重试。', ts:Date.now(), error:true }])
        return
      }
      setMessages(p => [...p, {
        role:'system', content: STEP_LABELS[mode]?.[1] || '起盘完成，AI解读中…', ts:Date.now(), step:2
      }])
    }

    await sendToAI(q, data)
  }

  const stopStream = () => { abortRef.current?.abort(); setStreaming(false) }
  const clearChat  = () => { setMessages([]); setModuleData(null); notify('对话已清空', 'info') }

  const buildDefault = () => ({
    consult: '请综合解读',
    bazi:    focus ? `请重点分析${focus}方面` : '请深度解读此八字命盘',
    liuyao:  '请深度解读此卦象',
    qimen:   '请分析当前奇门遁甲盘的局势',
    fengshui:'请给出详细的风水布局建议',
  }[mode] || '请分析')

  const buildUserDisplay = (q) => {
    if (mode === 'consult') return q
    const labels = {
      bazi:     `📅 ${birth.year}年${birth.month}月${birth.day}日${birth.hour}时 · ${birth.gender==='male'?'男':'女'}命\n❓ ${q}`,
      liuyao:   `🎲 ${liuyaoMethod==='time'?'时间起卦':liuyaoMethod==='coin'?'铜钱起卦':'蓍草起卦'}\n❓ ${q}`,
      qimen:    `⏰ 即时起局\n❓ ${q}`,
      fengshui: `🏠 ${houseFacing}向宅 · ${birth.gender==='male'?'男':'女'} ${birthYear}年生\n❓ ${q}`,
    }
    return labels[mode] || q
  }

  const buildBody = (q, data) => {
    switch (mode) {
      case 'consult': return { question:q, session_history:messages.slice(-10).map(m=>({role:m.role,content:m.content})) }
      case 'bazi':    return { ...birth, question:q, focus:focus||null, precomputed:data }
      case 'liuyao':  return { method:liuyaoMethod, question:q, precomputed:data }
      case 'qimen':   return { question:q, precomputed:data }
      case 'fengshui':return { birth_year:birthYear, gender:birth.gender, house_facing:houseFacing, question:q, precomputed:data }
      default:        return { question:q }
    }
  }

  const activeMode = MODES.find(m => m.id === mode)
  const isReady = mode === 'consult' || moduleData !== null

  return (
    <div className="page agent-page">
      <div className="page-header">
        <div>
          <div className="page-title">AI 命理顾问</div>
          <div className="page-subtitle">引用《穷通宝鉴》·《滴天髓》·《三命通会》·《奇门遁甲统宗》</div>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={clearChat}>清空对话</button>
      </div>

      <div className="agent-layout">
        {/* ─── LEFT SIDEBAR ─── */}
        <aside className="agent-sidebar">
          <div className="agent-sidebar-section">
            <div className="agent-sidebar-label">咨询模式</div>
            <div className="agent-modes">
              {MODES.map(m => (
                <button key={m.id} className={`agent-mode-btn ${mode===m.id?'active':''}`}
                  style={{ '--mc': m.color }}
                  onClick={() => switchMode(m.id)}>
                  <span className="agent-mode-icon">{m.icon}</span>
                  <div className="agent-mode-text">
                    <span className="agent-mode-name">{m.label}</span>
                    <span className="agent-mode-desc">{m.desc}</span>
                  </div>
                  {mode===m.id && <span className="agent-mode-active-dot"/>}
                </button>
              ))}
            </div>
          </div>

          {/* Context inputs */}
          {mode !== 'consult' && (
            <div className="agent-sidebar-section">
              <div className="agent-sidebar-label">起盘参数</div>
              <ModeInputs mode={mode} birth={birth} setBirth={setBirth}
                focus={focus} setFocus={setFocus}
                liuyaoMethod={liuyaoMethod} setLiuyaoMethod={setLiuyaoMethod}
                houseFacing={houseFacing} setHouseFacing={setHouseFacing}
                birthYear={birthYear} setBirthYear={setBirthYear} />

              {/* Module status indicator */}
              <div className="agent-module-status">
                {moduleLoading ? (
                  <span className="agent-status computing">
                    <span className="agent-status-dot pulse"/>
                    {STEP_LABELS[mode]?.[0]}
                  </span>
                ) : moduleData ? (
                  <span className="agent-status ready">
                    <span className="agent-status-dot green"/>
                    盘已起好，可直接提问
                  </span>
                ) : (
                  <span className="agent-status pending">
                    <span className="agent-status-dot"/>
                    发送问题时自动起盘
                  </span>
                )}
              </div>

              {/* Re-compute button if data exists */}
              {moduleData && !moduleLoading && (
                <button className="btn btn-sm btn-ghost" style={{ width:'100%', marginTop:'0.35rem', fontSize:'var(--text-xs)' }}
                  onClick={async () => { setModuleData(null); const d = await computeModuleData(); if (d) notify('重新起盘完成','success') }}>
                  🔄 重新起盘
                </button>
              )}
            </div>
          )}

          {/* Quick prompts */}
          <div className="agent-sidebar-section">
            <div className="agent-sidebar-label">快速问题</div>
            <div className="agent-quick-prompts">
              {(QUICK_PROMPTS[mode]||[]).map(p => (
                <button key={p} className="agent-quick-btn"
                  onClick={() => setQuestion(p)}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* ─── MAIN CHAT AREA ─── */}
        <div className="agent-main">
          <div className="agent-messages">
            {messages.length === 0 && (
              <div className="agent-empty">
                <div className="agent-empty-icon">{activeMode?.icon}</div>
                <div className="agent-empty-title">{activeMode?.label}</div>
                <div className="agent-empty-hint">
                  {mode === 'consult'
                    ? '在下方输入问题，直接开始咨询'
                    : '填写左侧参数后输入问题，系统将自动起盘再由AI深度解读'}
                </div>
                {mode !== 'consult' && (
                  <div className="agent-flow-hint">
                    <span className="agent-flow-step">① 填写参数</span>
                    <span className="agent-flow-arrow">→</span>
                    <span className="agent-flow-step">② 输入问题</span>
                    <span className="agent-flow-arrow">→</span>
                    <span className="agent-flow-step">③ 自动起盘</span>
                    <span className="agent-flow-arrow">→</span>
                    <span className="agent-flow-step">④ AI深度解读</span>
                  </div>
                )}
              </div>
            )}
            {messages.map((msg, i) => (
              <MessageBubble key={i} msg={msg}
                isLast={i===messages.length-1} streaming={streaming} />
            ))}
            <div ref={bottomRef}/>
          </div>

          <div className="agent-input-wrap">
            <textarea className="agent-input" value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => { if (e.key==='Enter' && (e.ctrlKey||e.metaKey)) sendMessage() }}
              placeholder={mode==='consult' ? '输入问题… （Ctrl+Enter 发送）' : `输入您关于${activeMode?.label}的问题… （Ctrl+Enter 发送）`}
              rows={2} disabled={moduleLoading} />
            {streaming
              ? <button className="agent-send-btn stop" onClick={stopStream}>⏹<span>停止</span></button>
              : <button className="agent-send-btn" onClick={sendMessage}
                  disabled={moduleLoading || (mode==='consult' && !question.trim())}>
                  {moduleLoading ? <span className="btn-spinner"/> : '✨'}
                  <span>{moduleLoading ? '起盘中' : '发送'}</span>
                </button>
            }
          </div>
        </div>
      </div>
    </div>
  )
}

function ModeInputs({ mode, birth, setBirth, focus, setFocus, liuyaoMethod, setLiuyaoMethod, houseFacing, setHouseFacing, birthYear, setBirthYear }) {
  if (mode === 'bazi') return (
    <div className="agent-input-section">
      <BirthForm values={birth} onChange={setBirth} />
      <div className="form-group" style={{ marginTop:'0.65rem' }}>
        <label>分析重点</label>
        <select value={focus} onChange={e => setFocus(e.target.value)}>
          <option value="">综合分析</option>
          {['事业','婚姻','健康','财运','运程'].map(f => <option key={f} value={f}>{f}</option>)}
        </select>
      </div>
    </div>
  )
  if (mode === 'liuyao') return (
    <div className="agent-input-section">
      <div className="form-group">
        <label>起卦方式</label>
        <div style={{ display:'flex', gap:'0.4rem', flexWrap:'wrap' }}>
          {['time','coin','yarrow'].map(m => (
            <button key={m} className={`btn btn-sm ${liuyaoMethod===m?'btn-primary':''}`}
              onClick={() => setLiuyaoMethod(m)}>
              {{ time:'时间起卦', coin:'铜钱起卦', yarrow:'蓍草起卦' }[m]}
            </button>
          ))}
        </div>
      </div>
      <p style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', marginTop:'0.5rem',
        fontFamily:'var(--font-serif)', lineHeight:1.65 }}>
        选择起卦方式后，在聊天框输入占问事项，系统将自动起卦并由AI深度解读。
      </p>
    </div>
  )
  if (mode === 'fengshui') return (
    <div className="agent-input-section">
      <div className="form-row-2">
        <div className="form-group">
          <label>出生年份</label>
          <input type="number" value={birthYear} onChange={e => setBirthYear(parseInt(e.target.value))} />
        </div>
        <div className="form-group">
          <label>性别</label>
          <select value={birth.gender} onChange={e => setBirth(p=>({...p,gender:e.target.value}))}>
            <option value="male">男</option><option value="female">女</option>
          </select>
        </div>
      </div>
      <div className="form-group" style={{ marginTop:'0.5rem' }}>
        <label>大门朝向</label>
        <select value={houseFacing} onChange={e => setHouseFacing(e.target.value)}>
          {['东','南','西','北','东南','东北','西南','西北'].map(d => <option key={d}>{d}</option>)}
        </select>
      </div>
    </div>
  )
  if (mode === 'qimen') return (
    <div className="agent-input-section">
      <p style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', fontFamily:'var(--font-serif)', lineHeight:1.7 }}>
        将以<strong>当前时间</strong>自动起奇门遁甲盘，九宫星门神配合分析，在右侧输入您的占问事项。
      </p>
    </div>
  )
  return null
}

function MessageBubble({ msg, isLast, streaming }) {
  const isUser   = msg.role === 'user'
  const isSystem = msg.role === 'system'
  const isStreaming = isLast && !isUser && !isSystem && streaming

  if (isSystem) return (
    <div className="agent-system-msg">
      <span className="agent-system-dot"/>
      {msg.step === 1 && <span className="agent-spinner"/>}
      {msg.step === 2 && <span style={{ color:'var(--jade)' }}>✓</span>}
      {msg.content}
    </div>
  )

  return (
    <div className={`agent-msg ${isUser?'user':'ai'} ${msg.error?'error':''}`}>
      {!isUser && <div className="agent-avatar">🔮</div>}
      <div className="agent-bubble">
        {msg.content || (isStreaming ? <span className="agent-thinking">正在思考…</span> : '')}
        {isStreaming && <span className="agent-cursor">▊</span>}
      </div>
    </div>
  )
}
