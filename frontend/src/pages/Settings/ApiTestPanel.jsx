import React, { useState } from 'react'
import { useSettingsStore } from '../../store/settingsStore'

const TESTS = [
  { id: 'health',   label: '后端健康',     method: 'GET',  path: '/health' },
  { id: 'bazi',     label: '八字推算',     method: 'POST', path: '/api/v1/bazi/chart',
    body: { year:1990, month:6, day:15, hour:8, minute:0, gender:'male' } },
  { id: 'qimen',    label: '奇门起局',     method: 'GET',  path: '/api/v1/qimen/now' },
  { id: 'liuyao',   label: '六爻起卦',     method: 'POST', path: '/api/v1/liuyao/divine',
    body: { method:'coin', question:'测试' } },
  { id: 'fengshui', label: '风水分析',     method: 'POST', path: '/api/v1/fengshui/analysis',
    body: { birth_year:1990, gender:'male', house_facing:'南' } },
  { id: 'datesel',  label: '择日选时',     method: 'POST', path: '/api/v1/date-selection/select',
    body: { purpose:'婚嫁', year:2026, month:3 } },
  { id: 'knowledge',label: '知识库',       method: 'GET',  path: '/api/v1/knowledge/classical/shishen' },
  { id: 'agent',    label: 'AI顾问（流式）', method: 'STREAM', path: '/api/v1/agent/consult',
    body: { question:'你好，简单介绍一下八字命理。' } },
]

export default function ApiTestPanel() {
  const { apiBaseUrl, llmKey, llmProvider, llmModel } = useSettingsStore()
  const [results, setResults] = useState({})
  const [running, setRunning] = useState({})

  const PROVIDER_DEFAULTS = { anthropic:'claude-sonnet-4-6', deepseek:'deepseek-chat', openai:'gpt-4o', moonshot:'moonshot-v1-8k' }
  const effectiveModel = llmModel || PROVIDER_DEFAULTS[llmProvider] || 'claude-sonnet-4-6'

  const runTest = async (test) => {
    setRunning(r => ({ ...r, [test.id]: true }))
    setResults(r => ({ ...r, [test.id]: { status: 'running', msg: '测试中…' } }))
    const start = Date.now()

    try {
      if (test.method === 'STREAM') {
        // Test streaming agent
        if (!llmKey) {
          setResults(r => ({ ...r, [test.id]: { status: 'skip', msg: '未配置 API Key — 跳过 AI 测试' } }))
          setRunning(r => ({ ...r, [test.id]: false }))
          return
        }
        const resp = await fetch(`${apiBaseUrl}${test.path}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-LLM-Key': llmKey,
            'X-LLM-Provider': llmProvider || 'anthropic',
            'X-LLM-Model': effectiveModel,
            'X-LLM-Base-Url': '',
          },
          body: JSON.stringify(test.body),
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const reader = resp.body.getReader()
        const decoder = new TextDecoder()
        let chunks = 0, text = ''
        while (chunks < 5) {  // read first 5 SSE chunks
          const { done, value } = await reader.read()
          if (done) break
          const raw = decoder.decode(value, { stream: true })
          for (const line of raw.split('\n')) {
            if (!line.startsWith('data:')) continue
            const d = line.slice(5).trim()
            if (d === '[DONE]') break
            try { text += JSON.parse(d).text || '' } catch {}
            chunks++
          }
        }
        reader.cancel()
        const ms = Date.now() - start
        if (text) {
          setResults(r => ({ ...r, [test.id]: {
            status: 'ok',
            msg: `✓ 流式响应正常 (${ms}ms) — AI回复前缀: "${text.slice(0,40)}…"`,
          }}))
        } else {
          throw new Error('收到空响应 — 检查 API Key 和模型名称')
        }
      } else {
        const resp = await fetch(`${apiBaseUrl}${test.path}`, {
          method: test.method,
          headers: { 'Content-Type': 'application/json' },
          body: test.method === 'POST' ? JSON.stringify(test.body) : undefined,
        })
        const ms = Date.now() - start
        const json = await resp.json()
        if (!resp.ok || json.success === false) {
          throw new Error(`HTTP ${resp.status}: ${json.detail || json.message || '未知错误'}`)
        }
        // Spot-check key fields
        const d = json.data || json
        let detail = ''
        if (test.id === 'health')    detail = `v${d.version} · ${d.modules?.length} 模块`
        if (test.id === 'bazi')      detail = `日主: ${d.day_master} · 格局: ${d.pattern}`
        if (test.id === 'qimen')     detail = `${d.ju_type} ${d.ju_number}局`
        if (test.id === 'liuyao')    detail = `第${d.original?.number}卦 ${d.original?.name}`
        if (test.id === 'fengshui')  detail = `命卦${d.ming_gua} · ${d.compatibility}`
        if (test.id === 'datesel')   detail = `吉日 ${d.auspicious_days?.length} 天`
        if (test.id === 'knowledge') detail = `共 ${Object.keys(d).length} 个十神`
        setResults(r => ({ ...r, [test.id]: {
          status: 'ok', msg: `✓ ${ms}ms — ${detail}`
        }}))
      }
    } catch (e) {
      setResults(r => ({ ...r, [test.id]: { status: 'err', msg: `✗ ${e.message}` } }))
    }
    setRunning(r => ({ ...r, [test.id]: false }))
  }

  const runAll = async () => {
    for (const t of TESTS) await runTest(t)
  }

  const STATUS_COLOR = { ok:'#3de088', err:'var(--red-light)', running:'var(--accent)', skip:'var(--text-muted)' }

  return (
    <div className="card">
      <div className="card-title">🧪 API 连通性测试</div>
      <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginBottom:'0.75rem' }}>
        直接从浏览器测试每个后端接口和 AI 顾问 · 当前后端: <code style={{ color:'var(--accent)' }}>{apiBaseUrl}</code>
      </div>

      <button className="btn btn-primary btn-sm" onClick={runAll} style={{ marginBottom:'0.75rem' }}>
        ▶ 全部测试
      </button>

      <div style={{ display:'flex', flexDirection:'column', gap:'0.35rem' }}>
        {TESTS.map(t => {
          const r = results[t.id]
          const isRunning = running[t.id]
          return (
            <div key={t.id} style={{
              display:'flex', alignItems:'center', gap:'0.6rem',
              padding:'0.5rem 0.75rem',
              background:'var(--bg-raised)', borderRadius:'var(--r-sm)',
              border:`1px solid ${r?.status==='ok' ? 'rgba(61,224,136,0.25)' : r?.status==='err' ? 'rgba(200,64,42,0.3)' : 'var(--border)'}`,
            }}>
              <button className="btn btn-sm" onClick={() => runTest(t)}
                disabled={isRunning}
                style={{ padding:'0.2rem 0.6rem', fontSize:'var(--text-xs)', minWidth:'44px' }}>
                {isRunning ? '…' : '测试'}
              </button>
              <span style={{ width:'80px', fontSize:'var(--text-sm)', fontWeight:500, color:'var(--text-primary)', flexShrink:0 }}>
                {t.label}
              </span>
              <span style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', width:'30px', flexShrink:0 }}>
                {t.method === 'STREAM' ? 'SSE' : t.method}
              </span>
              <span style={{ flex:1, fontSize:'var(--text-sm)', fontFamily:'var(--font-mono)',
                color: r ? STATUS_COLOR[r.status] : 'var(--text-muted)',
                overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                {r ? r.msg : '点击测试'}
              </span>
            </div>
          )
        })}
      </div>

      {Object.values(results).some(r => r.status === 'err') && (
        <div style={{ marginTop:'0.75rem', padding:'0.6rem 0.8rem',
          background:'var(--red-glow)', border:'1px solid rgba(200,64,42,0.3)',
          borderRadius:'var(--r-sm)', fontSize:'var(--text-sm)', color:'var(--text-secondary)',
          fontFamily:'var(--font-serif)', lineHeight:1.7 }}>
          常见排查：① 确认 start.bat 已启动且后端显示"API is up" ② AI顾问测试需先在上方配置 API Key ③ 检查防火墙是否阻止 8888 端口
        </div>
      )}
    </div>
  )
}
