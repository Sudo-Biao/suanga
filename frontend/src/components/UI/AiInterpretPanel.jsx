/**
 * AiInterpretPanel — reusable streaming AI interpretation panel
 * 
 * Usage:
 *   <AiInterpretPanel
 *     module="bazi"           // module name
 *     data={resultData}       // computed result to interpret
 *     extraContext="命盘"     // optional: tab name, purpose, etc.
 *   />
 */
import React, { useState, useRef, useEffect } from 'react'
import { useSettingsStore } from '../../store/settingsStore'

const PROVIDER_DEFAULTS = {
  anthropic: 'claude-sonnet-4-6',
  deepseek:  'deepseek-chat',
  openai:    'gpt-4o',
  moonshot:  'moonshot-v1-8k',
}

const MODULE_LABELS = {
  bazi:      '八字命理',
  liuyao:    '六爻卦象',
  qimen:     '奇门遁甲',
  fengshui:  '八宅风水',
  date:      '择日选时',
  knowledge: '命理知识',
}

export default function AiInterpretPanel({ module, data, extraContext = '', disabled = false }) {
  const { apiBaseUrl, llmProvider, llmKey, llmBaseUrl, llmModel } = useSettingsStore()
  const effectiveModel = llmModel || PROVIDER_DEFAULTS[llmProvider] || 'claude-sonnet-4-6'

  const [open, setOpen]         = useState(false)
  const [streaming, setStreaming] = useState(false)
  const [text, setText]          = useState('')
  const [question, setQuestion]  = useState('')
  const [error, setError]        = useState(null)
  const abortRef = useRef(null)
  const textRef  = useRef(null)

  // Auto-scroll
  useEffect(() => {
    if (streaming && textRef.current) {
      textRef.current.scrollTop = textRef.current.scrollHeight
    }
  }, [text, streaming])

  // Reset when data changes (new calculation)
  useEffect(() => {
    setText('')
    setError(null)
    setOpen(false)
  }, [data])

  const start = async (customQ = '') => {
    if (!llmKey) {
      setError('请先在【设置】页面配置 API Key')
      setOpen(true)
      return
    }
    if (!data) return

    setOpen(true)
    setStreaming(true)
    setText('')
    setError(null)

    try {
      abortRef.current = new AbortController()
      const resp = await fetch(`${apiBaseUrl}/api/v1/agent/interpret`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-LLM-Key':      llmKey.trim(),
          'X-LLM-Provider': llmProvider || 'anthropic',
          'X-LLM-Model':    effectiveModel,
          'X-LLM-Base-Url': llmBaseUrl.trim() || '',
        },
        body: JSON.stringify({
          module,
          data,
          question: customQ || question || null,
          extra_context: extraContext,
        }),
        signal: abortRef.current.signal,
      })

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

      const reader  = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()
        for (const line of lines) {
          if (!line.startsWith('data:')) continue
          const raw = line.slice(5).trim()
          if (raw === '[DONE]') break
          try {
            const chunk = JSON.parse(raw)
            if (chunk.text) setText(prev => prev + chunk.text)
          } catch {}
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') setError(e.message)
    } finally {
      setStreaming(false)
      abortRef.current = null
    }
  }

  const stop = () => {
    abortRef.current?.abort()
    setStreaming(false)
  }

  const hasKey = !!llmKey

  return (
    <div style={{ marginTop:'1rem' }}>
      {/* Trigger bar */}
      <div style={{
        display:'flex', alignItems:'center', gap:'0.75rem',
        padding:'0.65rem 1rem',
        background: open ? 'var(--accent-glow)' : 'var(--bg-raised)',
        border:`1px solid ${open ? 'var(--accent-dim)' : 'var(--border)'}`,
        borderRadius: open ? 'var(--r-md) var(--r-md) 0 0' : 'var(--r-md)',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition:'all var(--t-mid)',
        opacity: disabled ? 0.5 : 1,
      }} onClick={() => !disabled && !streaming && (open ? setOpen(false) : (text ? setOpen(!open) : start()))}>
        <span style={{ fontSize:'1rem' }}>🤖</span>
        <span style={{ fontSize:'var(--text-base)', fontWeight:500,
          color: open ? 'var(--accent)' : 'var(--text-secondary)' }}>
          AI {MODULE_LABELS[module] || ''}解读
        </span>
        {streaming && (
          <span style={{ fontSize:'var(--text-xs)', color:'var(--accent)', marginLeft:'0.25rem' }}>
            ● 生成中…
          </span>
        )}
        {text && !streaming && (
          <span className="badge badge-gold" style={{ fontSize:'var(--text-xs)', marginLeft:'auto' }}>已完成</span>
        )}
        {!hasKey && (
          <span className="badge badge-red" style={{ fontSize:'var(--text-xs)', marginLeft:'auto' }}>需配置 Key</span>
        )}
        {hasKey && !text && !streaming && (
          <span style={{ marginLeft:'auto', fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>
            {open ? '▲' : '▼ 点击解读'}
          </span>
        )}
        {text && !streaming && (
          <span style={{ marginLeft: hasKey ? '0.25rem' : 'auto', fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>
            {open ? '▲' : '▼'}
          </span>
        )}
      </div>

      {/* Content panel */}
      {open && (
        <div style={{
          border:'1px solid var(--accent-dim)',
          borderTop:'none',
          borderRadius:'0 0 var(--r-md) var(--r-md)',
          background:'var(--bg-card)',
          overflow:'hidden',
        }}>
          {/* Error */}
          {error && (
            <div style={{ padding:'0.75rem 1rem', background:'var(--red-glow)',
              fontSize:'var(--text-sm)', color:'var(--red-light)', fontFamily:'var(--font-serif)' }}>
              ⚠ {error}
              {!hasKey && (
                <span style={{ marginLeft:'0.5rem' }}>
                  → <a href="#" onClick={e=>{e.preventDefault(); window.location.hash='#settings'}}
                    style={{ color:'var(--accent)' }}>前往设置配置 API Key</a>
                </span>
              )}
            </div>
          )}

          {/* Streaming text */}
          {(text || streaming) && (
            <div ref={textRef} style={{
              padding:'1rem 1.25rem',
              maxHeight:'400px', overflowY:'auto',
              fontSize:'var(--text-base)', lineHeight:'1.85',
              color:'var(--text-secondary)', fontFamily:'var(--font-serif)',
              whiteSpace:'pre-wrap', wordBreak:'break-word',
            }}>
              {text}
              {streaming && (
                <span style={{
                  display:'inline-block', width:'2px', height:'1em',
                  background:'var(--accent)', marginLeft:'2px', verticalAlign:'text-bottom',
                  animation:'blink-cursor 0.8s step-end infinite',
                }}>
                  <style>{`@keyframes blink-cursor{0%,100%{opacity:1}50%{opacity:0}}`}</style>
                </span>
              )}
            </div>
          )}

          {/* Ask a follow-up question */}
          {!streaming && (
            <div style={{ padding:'0.75rem 1rem', borderTop:'1px solid var(--border)',
              display:'flex', gap:'0.5rem', alignItems:'flex-end' }}>
              <textarea
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && e.ctrlKey) { start(question); setQuestion('') } }}
                placeholder={text ? '追问（Ctrl+Enter发送）…' : '输入具体问题（可留空直接解读）…'}
                rows={1}
                style={{
                  flex:1, resize:'none', padding:'0.4rem 0.7rem',
                  background:'var(--bg-raised)', border:'1px solid var(--border)',
                  borderRadius:'var(--r-sm)', color:'var(--text-primary)',
                  fontSize:'var(--text-sm)', fontFamily:'var(--font-sans)',
                }}
              />
              {streaming
                ? <button className="btn btn-danger btn-sm" onClick={stop}>停止</button>
                : <button className="btn btn-primary btn-sm"
                    onClick={() => { start(question); setQuestion('') }}
                    disabled={!hasKey}>
                    {text ? '追问' : '解读'}
                  </button>
              }
              {text && !streaming && (
                <button className="btn btn-sm" onClick={() => { setText(''); start('') }}>
                  重新解读
                </button>
              )}
            </div>
          )}

          {/* Provider info */}
          <div style={{ padding:'0.3rem 1rem', borderTop:'1px solid var(--border)',
            fontSize:'var(--text-xs)', color:'var(--text-muted)', fontFamily:'var(--font-mono)',
            display:'flex', gap:'1rem' }}>
            <span>{llmProvider} / {effectiveModel}</span>
            {llmBaseUrl && <span style={{ color:'var(--accent-dim)' }}>自定义地址</span>}
          </div>
        </div>
      )}
    </div>
  )
}
