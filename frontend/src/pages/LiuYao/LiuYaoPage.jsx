import React, { useState, useEffect, Component } from 'react'
import { liuyaoApi } from '../../api/client'
import { useNotifyStore } from '../../store/settingsStore'
import AiInterpretPanel from '../../components/UI/AiInterpretPanel'

class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { error: null } }
  static getDerivedStateFromError(e) { return { error: e } }
  render() {
    if (this.state.error) return (
      <div className="card card-danger" style={{ textAlign:'center', padding:'2rem' }}>
        <p style={{ color:'var(--red-light)', fontFamily:'var(--font-serif)' }}>显示出错，请重新起卦。</p>
        <button className="btn btn-sm" style={{ marginTop:'0.75rem' }}
          onClick={() => this.setState({ error: null })}>重试</button>
      </div>
    )
    return this.props.children
  }
}

const SYM  = { 乾:'☰', 兑:'☱', 离:'☲', 震:'☳', 巽:'☴', 坎:'☵', 艮:'☶', 坤:'☷' }
const QIN_COLOR  = { 父母:'#8e44ad', 兄弟:'#e67e22', 子孙:'#27ae60', 妻财:'#d4a040', 官鬼:'#c0392b' }
const SHEN_COLOR = { 青龙:'#27ae60', 朱雀:'#e74c3c', 勾陈:'#d4a040', 腾蛇:'#9b59b6', 白虎:'#bdc3c7', 玄武:'#5d8fa5' }
const STR_COLOR  = { 旺:'#e74c3c', 相:'#e67e22', 休:'#7f8c8d', 囚:'#5d6d7e', 死:'#4a4a4a' }

const METHODS = [
  { id:'coin',   label:'铜钱法', desc:'三枚铜钱摇六次' },
  { id:'yarrow', label:'蓍草法', desc:'传统蓍草概率' },
  { id:'time',   label:'时间法', desc:'以当前时间推算' },
  { id:'manual', label:'手动输入', desc:'自行输入六爻数值' },
]

export default function LiuYaoPage() {
  const [method, setMethod]     = useState('coin')
  const [question, setQuestion] = useState('')
  const [manual, setManual]     = useState([7,8,7,8,7,8])
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [hexList, setHexList]   = useState([])
  const [view, setView]         = useState('divine')
  const [selHex, setSelHex]     = useState(null)
  const { notify }              = useNotifyStore()

  useEffect(() => {
    liuyaoApi.hexagrams().then(setHexList).catch(() => {})
  }, [])

  const divine = async () => {
    setLoading(true)
    try {
      const req = { method, question }
      if (method === 'manual') req.yao_values = manual
      const data = await liuyaoApi.divine(req)
      setResult(data)
      notify('起卦完成', 'success')
    } catch (e) { notify(e.message, 'error') }
    finally { setLoading(false) }
  }

  const loadHex = async (num) => {
    try { const d = await liuyaoApi.hexagram(num); setSelHex(d) }
    catch (e) { notify(e.message, 'error') }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <div className="page-title">六爻占卜</div>
          <div className="page-subtitle">纳甲筮法 · 六亲六神 · 世应爻 · 旺相休囚</div>
        </div>
        <div style={{ display:'flex', gap:'0.5rem' }}>
          <button className={`btn ${view==='divine'?'btn-primary':''}`} onClick={() => setView('divine')}>起卦</button>
          <button className={`btn ${view==='library'?'btn-primary':''}`} onClick={() => setView('library')}>卦象库</button>
          <button className={`btn ${view==='guide'?'btn-primary':''}`} onClick={() => setView('guide')}>用卦指南</button>
        </div>
      </div>

      <div className="page-body">
        {view === 'divine' && (
          <div className="page-cols">
            {/* ── Input panel ── */}
            <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
              <div className="card">
                <div className="card-title">起卦方式</div>
                {METHODS.map(m => (
                  <div key={m.id} onClick={() => setMethod(m.id)} style={{
                    padding:'0.6rem 0.85rem', marginBottom:'0.35rem',
                    borderRadius:'var(--r-md)', cursor:'pointer', transition:'all var(--t-fast)',
                    border:`1px solid ${method===m.id?'var(--accent-dim)':'var(--border)'}`,
                    background: method===m.id ? 'var(--accent-glow)' : 'var(--bg-raised)',
                  }}>
                    <div style={{ fontWeight:500, fontSize:'var(--text-base)',
                      color:method===m.id?'var(--accent)':'var(--text-primary)' }}>{m.label}</div>
                    <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', marginTop:'2px' }}>{m.desc}</div>
                  </div>
                ))}
              </div>

              <div className="card">
                <div className="card-title">占问事项</div>
                <textarea value={question} onChange={e => setQuestion(e.target.value)}
                  placeholder="请输入所占之事，如：此次求职是否顺利？" rows={3} />
                <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', marginTop:'0.4rem' }}>
                  心诚则灵，一次只问一事，方能卦象应验
                </div>
              </div>

              {method === 'manual' && (
                <div className="card">
                  <div className="card-title">手动输入六爻</div>
                  <div style={{ fontSize:'0.73rem', color:'var(--text-muted)', marginBottom:'0.5rem' }}>
                    从初爻（下）到上爻（上）依次输入
                  </div>
                  <div style={{ display:'grid', gridTemplateColumns:'repeat(6,1fr)', gap:'0.35rem' }}>
                    {manual.map((v,i) => (
                      <div key={i} style={{ textAlign:'center' }}>
                        <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', marginBottom:'0.2rem' }}>
                          {['初','二','三','四','五','上'][i]}爻
                        </div>
                        <select value={v} onChange={e => {
                          const arr=[...manual]; arr[i]=Number(e.target.value); setManual(arr)
                        }} style={{ fontSize:'var(--text-sm)', padding:'0.3rem 0.2rem' }}>
                          <option value={6}>6 老阴×</option>
                          <option value={7}>7 少阳—</option>
                          <option value={8}>8 少阴--</option>
                          <option value={9}>9 老阳○</option>
                        </select>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button className="btn btn-primary btn-full btn-lg" onClick={divine} disabled={loading}>
                {loading ? '推算中…' : '开始起卦 ▶'}
              </button>
            </div>

            {/* ── Result panel ── */}
            <div>
              {loading && <div className="loading"><div className="spinner"/><p>正在演算卦象…</p></div>}
              {!loading && (
                <ErrorBoundary key={result?.original?.number}>
                  {result
                    ? <>
                        <HexagramResult data={result} />
                        <AiInterpretPanel module="liuyao" data={result}
                          extraContext={result.topic || result.question || '综合'} />
                      </>
                    : <div className="card" style={{ textAlign:'center', padding:'3rem', color:'var(--text-muted)' }}>
                        <div style={{ fontSize:'3rem', marginBottom:'1rem', opacity:0.3 }}>☵</div>
                        <p style={{ fontFamily:'var(--font-serif)' }}>心存问题，默念三遍，诚心起卦</p>
                      </div>
                  }
                </ErrorBoundary>
              )}
            </div>
          </div>
        )}

        {view === 'library' && (
          <div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(80px,1fr))', gap:'0.4rem', marginBottom:'1.5rem' }}>
              {hexList.map(h => (
                <button key={h.number} onClick={() => loadHex(h.number)}
                  className={`btn ${selHex?.number===h.number?'btn-primary':''}`}
                  style={{ flexDirection:'column', gap:'0.2rem', padding:'0.5rem 0.3rem' }}>
                  <span style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>第{h.number}卦</span>
                  <span style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-base)' }}>{h.name}</span>
                </button>
              ))}
            </div>
            {selHex && <HexagramDetail data={selHex} />}
          </div>
        )}

        {view === 'guide' && <LiuYaoGuide />}
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════════════════
   HEXAGRAM RESULT — full tabbed view
══════════════════════════════════════════════════════════ */
function HexagramResult({ data }) {
  const [tab, setTab] = useState('hexagram')
  const orig    = data.original
  const changed = data.changed
  const yaos    = data.yaos || []
  const kong    = data.kong_wang_branches || []
  const topic   = data.topic || '综合'
  const ta      = data.topic_analysis || {}
  const cp      = data.classical_points || []
  const ca      = data.changing_analysis || []
  const timing  = ta.timing || {}

  const TABS = [
    { id:'hexagram', label:'卦象' },
    { id:'analysis', label:'断法分析', badge: cp.length > 0 },
    { id:'timing',   label:'应期推算', badge: !!timing.general },
  ]

  return (
    <div className="result-section">
      {/* ── Hexagram header ── */}
      <div className="card card-glow" style={{ textAlign:'center' }}>
        <div style={{ display:'flex', justifyContent:'center', alignItems:'center', gap:'1.75rem', marginBottom:'0.85rem' }}>
          {/* Original hexagram symbols */}
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:'0.3rem' }}>
            <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', letterSpacing:'0.06em', textTransform:'uppercase' }}>本卦</div>
            <div style={{ fontSize:'3.5rem', lineHeight:1, color:'var(--accent)',
              textShadow:'0 0 24px var(--accent-glow), 0 0 48px var(--accent-glow2)' }}>
              {SYM[orig.upper?.name]}{SYM[orig.lower?.name]}
            </div>
            <div style={{ fontFamily:'var(--font-display)', fontSize:'1.5rem', color:'var(--accent)', letterSpacing:'0.08em' }}>
              {orig.name}
            </div>
            <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>第{orig.number}卦</div>
          </div>

          {changed && (
            <>
              <div style={{ color:'var(--accent-dim)', fontSize:'1.2rem' }}>→</div>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:'0.3rem', opacity:0.85 }}>
                <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', letterSpacing:'0.06em', textTransform:'uppercase' }}>之卦</div>
                <div style={{ fontSize:'3.5rem', lineHeight:1, color:'var(--text-secondary)' }}>
                  {SYM[changed.upper?.name]}{SYM[changed.lower?.name]}
                </div>
                <div style={{ fontFamily:'var(--font-display)', fontSize:'1.5rem', color:'var(--text-secondary)' }}>
                  {changed.name}
                </div>
                <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>第{changed.number}卦</div>
              </div>
            </>
          )}
        </div>

        {/* Palace + world/app info */}
        <div style={{ display:'flex', justifyContent:'center', gap:'1rem', flexWrap:'wrap',
          fontSize:'var(--text-xs)', color:'var(--text-muted)', marginBottom:'0.75rem' }}>
          {data.palace_trigram && <span>{data.palace_trigram}宫 · {data.palace_element}行</span>}
          <span>世爻第{data.world_line}爻</span>
          <span>应爻第{data.application_line}爻</span>
          {kong.length > 0 && <span style={{ color:'var(--red-light)' }}>旬空：{kong.join('、')}</span>}
        </div>

        {/* Judgment */}
        <div style={{ fontSize:'var(--text-base)', fontFamily:'var(--font-serif)', color:'var(--text-secondary)',
          lineHeight:1.85, maxWidth:'500px', margin:'0 auto 0.75rem' }}>
          {orig.judgment}
        </div>

        {/* Topic badge + question */}
        <div style={{ display:'flex', justifyContent:'center', gap:'0.5rem', flexWrap:'wrap' }}>
          <span className="badge badge-gold">{topic}</span>
          {data.question && (
            <span style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', fontStyle:'italic' }}>
              「{data.question}」
            </span>
          )}
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="tab-bar">
        {TABS.map(t => (
          <button key={t.id} className={`tab ${tab===t.id?'active':''}`} onClick={() => setTab(t.id)}>
            {t.label}
            {t.badge && <span style={{ marginLeft:'0.3rem', display:'inline-block',
              width:'6px', height:'6px', borderRadius:'50%', background:'var(--accent)',
              verticalAlign:'middle', marginBottom:'1px' }} />}
          </button>
        ))}
      </div>

      {/* ══ TAB: 卦象 ══ */}
      {tab === 'hexagram' && (
        <div style={{ display:'flex', flexDirection:'column', gap:'0.9rem' }}>
          {/* Six yao table */}
          <div className="card">
            <div className="card-title">六爻纳甲详表</div>

            {/* Table header */}
            <div style={{ display:'grid', gridTemplateColumns:'28px 70px 16px 38px 26px 36px 24px auto',
              gap:'0.3rem', padding:'0.3rem 0.5rem',
              fontSize:'var(--text-xs)', color:'var(--text-muted)', letterSpacing:'0.06em',
              borderBottom:'1px solid var(--border)', marginBottom:'0.3rem' }}>
              <span>爻位</span>
              <span style={{ textAlign:'center' }}>爻象</span>
              <span></span>
              <span>六亲</span>
              <span>地支</span>
              <span>六神</span>
              <span>旺衰</span>
              <span style={{ textAlign:'right' }}>标记</span>
            </div>

            {/* Rows — display from top (上爻) to bottom (初爻) */}
            <div style={{ display:'flex', flexDirection:'column', gap:'3px' }}>
              {[...yaos].reverse().map((y, ri) => {
                const i = yaos.length - 1 - ri
                const posLabel = ['初','二','三','四','五','上'][i]
                return (
                  <div key={i} style={{
                    display:'grid', gridTemplateColumns:'28px 70px 16px 38px 26px 36px 24px auto',
                    gap:'0.3rem', padding:'0.4rem 0.5rem', alignItems:'center',
                    borderRadius:'var(--r-sm)',
                    border: y.is_changing ? '1px solid var(--accent-dim)'
                          : y.is_world    ? '1px solid rgba(212,160,64,0.3)'
                          : '1px solid transparent',
                    background: y.is_world       ? 'rgba(212,160,64,0.07)'
                              : y.is_application ? 'rgba(100,120,200,0.06)'
                              : y.is_changing    ? 'var(--accent-glow2)'
                              : 'var(--bg-raised)',
                  }}>
                    {/* 爻位 */}
                    <span style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', textAlign:'center' }}>
                      {posLabel}
                    </span>

                    {/* 爻象 line */}
                    <div style={{ display:'flex', alignItems:'center', gap:'4px' }}>
                      {y.line === '阳'
                        ? <div style={{ flex:1, height:'4px', background:'var(--text-primary)', borderRadius:'2px' }} />
                        : <>
                            <div style={{ flex:1, height:'4px', background:'var(--text-primary)', borderRadius:'2px' }} />
                            <div style={{ width:'8px' }} />
                            <div style={{ flex:1, height:'4px', background:'var(--text-primary)', borderRadius:'2px' }} />
                          </>
                      }
                    </div>

                    {/* 变爻标记 */}
                    <span style={{ fontSize:'var(--text-xs)', color:'var(--accent)', textAlign:'center', fontWeight:700 }}>
                      {y.is_changing ? '▸' : ''}
                    </span>

                    {/* 六亲 */}
                    <span style={{ fontSize:'var(--text-sm)', fontWeight:600,
                      color: QIN_COLOR[y.liu_qin] || 'var(--text-muted)' }}>
                      {y.liu_qin || '—'}
                    </span>

                    {/* 地支 */}
                    <span style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-base)',
                      color: y.kong_wang ? 'var(--red-light)' : 'var(--accent)' }}>
                      {y.branch || '—'}
                      {y.kong_wang && <span style={{ fontSize:'var(--text-xs)', marginLeft:'1px' }}>空</span>}
                    </span>

                    {/* 六神 */}
                    <span style={{ fontSize:'var(--text-xs)',
                      color: SHEN_COLOR[y.liu_shen] || 'var(--text-muted)' }}>
                      {y.liu_shen || '—'}
                    </span>

                    {/* 旺衰 */}
                    <span style={{ fontSize:'var(--text-xs)', fontWeight:500,
                      color: STR_COLOR[y.strength?.label] || 'var(--text-muted)' }}>
                      {y.strength?.label || '—'}
                    </span>

                    {/* 世/应 */}
                    <div style={{ display:'flex', gap:'0.2rem', justifyContent:'flex-end' }}>
                      {y.is_world       && <span className="badge badge-gold" style={{ fontSize:'var(--text-xs)', padding:'0 4px' }}>世</span>}
                      {y.is_application && <span className="badge badge-muted" style={{ fontSize:'var(--text-xs)', padding:'0 4px' }}>应</span>}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Kong wang note */}
            {kong.length > 0 && (
              <div style={{ marginTop:'0.6rem', padding:'0.4rem 0.65rem',
                background:'rgba(212,75,58,0.07)', border:'1px solid rgba(212,75,58,0.2)',
                borderRadius:'var(--r-sm)', fontSize:'var(--text-xs)', color:'var(--text-muted)',
                fontFamily:'var(--font-serif)' }}>
                ⚠ 旬空：{kong.join('、')} — 空亡之爻力量虚化，所代事物难以成就，待出空后再验
              </div>
            )}
          </div>

          {/* Changed hexagram detail */}
          {changed && (
            <div className="card">
              <div className="card-title">之卦 · 第{changed.number}卦 {changed.name}</div>
              <div style={{ display:'flex', gap:'1rem', alignItems:'flex-start' }}>
                <div style={{ fontSize:'2.8rem', color:'var(--text-secondary)', lineHeight:1, flexShrink:0 }}>
                  {SYM[changed.upper?.name]}{SYM[changed.lower?.name]}
                </div>
                <div style={{ flex:1 }}>
                  <p style={{ fontSize:'var(--text-sm)', fontFamily:'var(--font-serif)',
                    color:'var(--text-secondary)', lineHeight:1.82 }}>
                    {changed.interpretation || changed.judgment}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* World / app summary */}
          {data.world_summary && (
            <div className="card" style={{ padding:'0.85rem 1.2rem' }}>
              <div className="card-title">世应概况</div>
              <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)',
                color:'var(--text-secondary)', lineHeight:1.8 }}>
                {data.world_summary}
              </p>
            </div>
          )}
        </div>
      )}

      {/* ══ TAB: 断法分析 ══ */}
      {tab === 'analysis' && (
        <div style={{ display:'flex', flexDirection:'column', gap:'0.9rem' }}>

          {/* Verdict */}
          {ta.verdict && (
            <div className="card card-glow">
              <div className="card-title">综合判断 · {topic}</div>
              <div style={{ padding:'0.75rem 1rem', background:'var(--accent-glow)',
                border:'1px solid var(--accent-dim)', borderRadius:'var(--r-md)',
                fontFamily:'var(--font-serif)', fontSize:'var(--text-base)',
                color:'var(--text-primary)', lineHeight:1.85 }}>
                {ta.verdict}
              </div>
            </div>
          )}

          {/* Classical analysis points from interpreter */}
          {cp.length > 0 && (
            <div className="card">
              <div className="card-title">经典断法要点</div>
              <div style={{ display:'flex', flexDirection:'column', gap:'0.55rem' }}>
                {cp.map((point, i) => (
                  <div key={i} style={{ display:'flex', gap:'0.65rem', alignItems:'flex-start',
                    padding:'0.55rem 0.75rem', background:'var(--bg-raised)',
                    borderRadius:'var(--r-sm)', borderLeft:'2px solid var(--accent-dim)' }}>
                    <span style={{ color:'var(--accent)', fontSize:'var(--text-xs)',
                      flexShrink:0, marginTop:'0.22em', fontWeight:700 }}>{i+1}</span>
                    <span style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)',
                      color:'var(--text-secondary)', lineHeight:1.78 }}>{point}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Topic key points */}
          {ta.key_points?.length > 0 && (
            <div className="card">
              <div className="card-title">《增删卜易》占{topic}规则</div>
              <div style={{ display:'flex', flexDirection:'column', gap:'0.4rem' }}>
                {ta.key_points.map((r, i) => (
                  <div key={i} style={{ display:'flex', gap:'0.5rem', alignItems:'flex-start',
                    fontSize:'var(--text-sm)', color:'var(--text-secondary)', lineHeight:1.75,
                    padding:'0.4rem 0', borderBottom:'1px solid var(--border)' }}>
                    <span style={{ color:'var(--accent)', flexShrink:0, fontSize:'var(--text-xs)', marginTop:'0.4em' }}>◆</span>
                    <span style={{ fontFamily:'var(--font-serif)' }}>{r}</span>
                  </div>
                ))}
              </div>
              {ta.classical_ref && (
                <div style={{ marginTop:'0.65rem', padding:'0.5rem 0.75rem',
                  background:'var(--accent-glow)', border:'1px solid var(--accent-dim)',
                  borderRadius:'var(--r-sm)', fontSize:'var(--text-sm)',
                  color:'var(--accent-light)', fontFamily:'var(--font-serif)', lineHeight:1.7 }}>
                  引典：{ta.classical_ref}
                </div>
              )}
            </div>
          )}

          {/* Changing lines analysis */}
          {ca.length > 0 && (
            <div className="card">
              <div className="card-title">动爻详析（{ca.length}爻动）</div>
              <div style={{ display:'flex', flexDirection:'column', gap:'0.5rem' }}>
                {ca.map((y, i) => {
                  const shenInfo = { 白虎:'主凶险血光', 玄武:'主暗昧欺诈', 青龙:'主喜庆贵人',
                    朱雀:'主口舌文书', 勾陈:'主拖延田土', 腾蛇:'主虚惊怪异' }
                  return (
                    <div key={i} style={{ display:'flex', gap:'0.85rem', alignItems:'center',
                      padding:'0.65rem 0.85rem', borderRadius:'var(--r-md)',
                      background:'var(--accent-glow2)', border:'1px solid var(--accent-dim)' }}>
                      <div style={{ fontFamily:'var(--font-display)', fontSize:'1.4rem',
                        color:'var(--accent)', flexShrink:0 }}>
                        {['初','二','三','四','五','上'][Number(y.line)-1] || y.line}
                      </div>
                      <div style={{ flex:1 }}>
                        <div style={{ display:'flex', gap:'0.4rem', marginBottom:'0.25rem', flexWrap:'wrap' }}>
                          <span style={{ fontWeight:600, fontSize:'var(--text-sm)',
                            color: QIN_COLOR[y.liu_qin] || 'var(--text-primary)' }}>{y.liu_qin}爻</span>
                          <span style={{ fontSize:'var(--text-sm)', color:'var(--accent)',
                            fontFamily:'var(--font-display)' }}>{y.branch}</span>
                          <span style={{ fontSize:'var(--text-sm)',
                            color: SHEN_COLOR[y.liu_shen] || 'var(--text-muted)' }}>{y.liu_shen}</span>
                          {y.jin_tui && (
                            <span className={`badge ${y.jin_tui==='进'?'badge-jade':'badge-red'}`}
                              style={{ fontSize:'var(--text-xs)' }}>化{y.jin_tui}神</span>
                          )}
                          {y.kong_wang && <span className="badge badge-red" style={{ fontSize:'var(--text-xs)' }}>空亡</span>}
                        </div>
                        <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)',
                          fontFamily:'var(--font-serif)', lineHeight:1.6 }}>
                          {shenInfo[y.liu_shen] || ''}
                          {y.jin_tui === '进' && '，化进神主事态好转'}
                          {y.jin_tui === '退' && '，化退神主事态消退'}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
              {ca.length === 1 && (
                <div style={{ marginTop:'0.5rem', fontSize:'var(--text-sm)', color:'var(--text-muted)',
                  fontFamily:'var(--font-serif)' }}>
                  《增删卜易》：独发易取——唯此一爻动，以此爻论断为主，吉凶明确
                </div>
              )}
              {ca.length >= 5 && (
                <div style={{ marginTop:'0.5rem', fontSize:'var(--text-sm)', color:'var(--red-light)',
                  fontFamily:'var(--font-serif)' }}>
                  《增删卜易》：乱动难寻——爻动过多，吉凶交错，宜以之卦为准综合论断
                </div>
              )}
            </div>
          )}

          {/* Full interpretation text */}
          <div className="card">
            <div className="card-title">卦象全解</div>
            {data.question && (
              <div style={{ padding:'0.45rem 0.7rem', background:'var(--bg-raised)',
                borderRadius:'var(--r-sm)', fontSize:'var(--text-sm)',
                color:'var(--text-muted)', marginBottom:'0.75rem', fontStyle:'italic' }}>
                占问：{data.question}
              </div>
            )}
            <p style={{ fontFamily:'var(--font-serif)', lineHeight:1.92,
              whiteSpace:'pre-line', color:'var(--text-secondary)', fontSize:'var(--text-base)' }}>
              {data.interpretation}
            </p>
          </div>
        </div>
      )}

      {/* ══ TAB: 应期推算 ══ */}
      {tab === 'timing' && (
        <div style={{ display:'flex', flexDirection:'column', gap:'0.9rem' }}>

          {/* General principle */}
          {timing.general && (
            <div className="card card-glow">
              <div className="card-title">应期总则 · 病药原则</div>
              <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-base)',
                color:'var(--text-secondary)', lineHeight:1.88 }}>
                {timing.general}
              </p>
            </div>
          )}

          {/* Kong wang timing */}
          {timing.kong_wang_timing && (
            <div className="card">
              <div className="card-title">旬空应期</div>
              <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-base)',
                color:'var(--text-secondary)', lineHeight:1.85 }}>
                {timing.kong_wang_timing}
              </p>
            </div>
          )}

          {/* Rules applied */}
          {timing.rules_applied?.length > 0 && (
            <div className="card">
              <div className="card-title">动爻应期分析</div>
              {timing.rules_applied.map((r, i) => (
                <div key={i} style={{ display:'flex', gap:'0.5rem', alignItems:'flex-start',
                  padding:'0.5rem 0.65rem', marginBottom:'0.35rem',
                  background:'var(--bg-raised)', borderRadius:'var(--r-sm)',
                  borderLeft:'2px solid var(--accent-dim)' }}>
                  <span style={{ color:'var(--accent)', flexShrink:0, fontSize:'var(--text-xs)', marginTop:'0.38em' }}>◆</span>
                  <span style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)',
                    color:'var(--text-secondary)', lineHeight:1.75 }}>{r}</span>
                </div>
              ))}
            </div>
          )}

          {/* Yong shen timing hint */}
          {timing.yong_shen_name && (
            <div className="card">
              <div className="card-title">用神应期</div>
              <div className="kv-grid">
                <span className="kv-label">用神</span>
                <span className="kv-value">{timing.yong_shen_name}</span>
                <span className="kv-label">占事</span>
                <span className="kv-value">{topic}</span>
                <span className="kv-label">应期法则</span>
                <span className="kv-value" style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)', lineHeight:1.75 }}>
                  用神旺相不动，逢冲之日月应验；用神发动，逢合之日应验；用神空亡，出空之日应验；用神入墓，冲开墓库之日应验
                </span>
              </div>
            </div>
          )}

          {/* Advice */}
          {data.advice && (
            <div className="card">
              <div className="card-title">综合建议</div>
              <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-base)',
                color:'var(--text-secondary)', lineHeight:1.88 }}>
                {data.advice}
              </p>
            </div>
          )}

          {/* Classical timing reference table */}
          <div className="card">
            <div className="card-title">《黄金策》期日速查</div>
            <div style={{ display:'flex', flexDirection:'column', gap:'0.3rem', fontSize:'var(--text-sm)' }}>
              {[
                ['用神旺相不动', '逢冲动之月日'],
                ['用神有气发动', '逢合日 / 当日'],
                ['用神受制被克', '制杀（克忌神）之月日'],
                ['用神太旺遇生', '墓库月日（器满则倾）'],
                ['用神无气发动', '逢生扶之月日'],
                ['用神入墓', '冲破墓库之日'],
                ['用神旬空', '出旬 / 冲空之日'],
              ].map(([cond, result], i) => (
                <div key={i} style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.5rem',
                  padding:'0.4rem 0.65rem', background: i%2===0 ? 'var(--bg-raised)' : 'transparent',
                  borderRadius:'var(--r-sm)' }}>
                  <span style={{ color:'var(--text-muted)', fontFamily:'var(--font-serif)' }}>{cond}</span>
                  <span style={{ color:'var(--accent)', fontFamily:'var(--font-serif)' }}>{result}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Hexagram Detail (library) ── */
function HexagramDetail({ data }) {
  return (
    <div className="result-section">
      <div className="card">
        <div style={{ display:'flex', alignItems:'center', gap:'1.5rem', marginBottom:'1rem' }}>
          <div style={{ fontSize:'3.5rem', color:'var(--accent)', lineHeight:1 }}>
            {SYM[data.upper?.name]}{SYM[data.lower?.name]}
          </div>
          <div>
            <div style={{ fontFamily:'var(--font-display)', fontSize:'1.5rem', color:'var(--accent)' }}>
              第{data.number}卦 · {data.name}卦
            </div>
            <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginTop:'0.2rem' }}>
              上{data.upper?.name}（{data.upper?.nature}）下{data.lower?.name}（{data.lower?.nature}）
            </div>
          </div>
        </div>
        {[['卦辞', data.judgment], ['象传', data.image]].map(([label, text]) => text && (
          <div key={label} style={{ background:'var(--bg-raised)', borderRadius:'var(--r-md)',
            padding:'0.85rem', marginBottom:'0.75rem' }}>
            <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', marginBottom:'0.25rem' }}>{label}</div>
            <p style={{ fontFamily:'var(--font-serif)', color:'var(--text-primary)' }}>{text}</p>
          </div>
        ))}
        <div>
          <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginBottom:'0.5rem' }}>爻辞</div>
          {Object.entries(data.lines||{}).reverse().map(([pos, text]) => (
            <div key={pos} style={{ padding:'0.4rem 0.6rem', borderBottom:'1px solid var(--border)',
              fontSize:'var(--text-sm)', fontFamily:'var(--font-serif)', color:'var(--text-secondary)' }}>
              <span style={{ color:'var(--accent)', marginRight:'0.5rem' }}>
                {['初','二','三','四','五','上'][Number(pos)-1]}爻
              </span>
              {text}
            </div>
          ))}
        </div>
        {data.interpretation && (
          <div style={{ marginTop:'0.75rem', padding:'0.75rem', background:'var(--accent-glow)',
            border:'1px solid var(--accent-dim)', borderRadius:'var(--r-md)' }}>
            <p style={{ fontFamily:'var(--font-serif)', color:'var(--text-secondary)', lineHeight:1.85 }}>
              {data.interpretation}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

/* ── LiuYao Guide ── */
function LiuYaoGuide() {
  const LIUQIN = [
    { name:'父母爻', sym:'父', color:'#8e44ad', role:'文书·长辈·房屋·船车', 用神:'问功名学业·文书合同', 喜忌:'旺则文书顺，克则学业受阻' },
    { name:'兄弟爻', sym:'兄', color:'#e67e22', role:'竞争·朋友·兄弟·阻碍', 用神:'独占情境下代表竞争者', 喜忌:'兄弟发动则散财、阻碍' },
    { name:'子孙爻', sym:'子', color:'#27ae60', role:'福气·后代·医药·和平', 用神:'问疾病（药神）·问讼事（和解）', 喜忌:'子孙旺则病愈讼散，克官鬼大吉' },
    { name:'妻财爻', sym:'财', color:'#d4a040', role:'钱财·妻子·财物·享受', 用神:'男问婚姻·问财运', 喜忌:'财旺而身强则财来，身弱则财为祸' },
    { name:'官鬼爻', sym:'官', color:'#c0392b', role:'官府·丈夫·疾病·鬼神', 用神:'女问婚姻·问功名仕途', 喜忌:'官旺身弱则官非疾病，官旺身强则升官' },
  ]

  const LIUSHEN = [
    { name:'青龙', color:'#27ae60', symbol:'龙', nature:'吉', desc:'喜庆·婚嫁·财帛·贵人', 断法:'临父母：文书喜庆；临财：横财；临官：升官有喜' },
    { name:'朱雀', color:'#e74c3c', symbol:'雀', nature:'凶', desc:'口舌·文书·是非·消息', 断法:'临官：官司文书；临兄弟：口舌纷争；临父母：文书有变动' },
    { name:'勾陈', color:'#d4a040', symbol:'陈', nature:'凶', desc:'田土·迟滞·拖延·牢狱', 断法:'临官：官非田土；动则事情拖延不决' },
    { name:'腾蛇', color:'#9b59b6', symbol:'蛇', nature:'凶', desc:'虚惊·怪异·谎言·梦境', 断法:'临官：虚惊官非；临妻财：财来财去；主事情虚假不实' },
    { name:'白虎', color:'#95a5a6', symbol:'虎', nature:'大凶', desc:'血光·伤亡·刚猛·凶险', 断法:'临官：血光官非；临父母：父母有灾；主凶险事件' },
    { name:'玄武', color:'#5d8fa5', symbol:'武', nature:'凶', desc:'盗贼·奸情·暗昧·奸邪', 断法:'临财：财被盗；临妻财：妻有私情；主暗中之事' },
  ]

  const KOUJUE = [
    { t:'用神纲领', c:'凡占须先定用神，用神旺相则事成，休囚克泄则事败——《卜筮正宗》' },
    { t:'月建第一', c:'月建生克最有力，月令生用神则旺，克用神则衰——六爻第一法' },
    { t:'动爻变化', c:'动者变也，变爻为结果；化进神好转，化退神消退，回头克大凶' },
    { t:'旬空之义', c:'空亡之爻力量大减。逢冲则出空，往往在冲空之日应验' },
    { t:'黄金五诀', c:'旺发当日应·空亡出旬应·入墓冲开应·进神越来越好·退神逐渐消退' },
  ]

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:"1rem" }}>
      <div className="card">
        <div className="card-title">六亲爻系 — 六爻核心</div>
        <div style={{ display:"flex", flexDirection:"column", gap:"0.4rem" }}>
          {LIUQIN.map(q => (
            <div key={q.name} style={{ display:"flex", gap:"0.75rem", padding:"0.55rem 0.65rem",
              background:"var(--bg-subtle)", borderRadius:"var(--r-sm)", border:"1px solid var(--border)",
              alignItems:"flex-start" }}>
              <div style={{ width:32, height:32, borderRadius:"50%", flexShrink:0,
                background:q.color+"22", border:`1.5px solid ${q.color}55`,
                display:"flex", alignItems:"center", justifyContent:"center",
                fontFamily:"var(--font-display)", color:q.color, fontWeight:700, fontSize:"var(--text-sm)" }}>
                {q.sym}
              </div>
              <div style={{ flex:1 }}>
                <div style={{ display:"flex", gap:"0.5rem", alignItems:"center", marginBottom:"3px" }}>
                  <span style={{ fontWeight:700, color:q.color, fontSize:"var(--text-sm)" }}>{q.name}</span>
                  <span className="badge" style={{ background:q.color+"15", color:q.color, border:`1px solid ${q.color}40`, borderRadius:"99px", fontSize:"10px", padding:"1px 6px" }}>{q.用神}</span>
                </div>
                <div style={{ fontSize:"var(--text-xs)", color:"var(--text-muted)", lineHeight:1.55, fontFamily:"var(--font-serif)" }}>
                  象意：{q.role} · {q.喜忌}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-title">六神详解 — 天干附神</div>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"0.4rem" }}>
          {LIUSHEN.map(s => (
            <div key={s.name} style={{ padding:"0.55rem 0.7rem",
              background:`${s.color}0d`, borderRadius:"var(--r-sm)",
              border:`1px solid ${s.color}33` }}>
              <div style={{ display:"flex", alignItems:"center", gap:"0.4rem", marginBottom:"4px" }}>
                <div style={{ width:22, height:22, borderRadius:"50%",
                  background:s.color, display:"flex", alignItems:"center", justifyContent:"center",
                  color:"#fff", fontSize:"10px", fontWeight:700, flexShrink:0 }}>{s.symbol}</div>
                <span style={{ fontWeight:700, color:s.color, fontSize:"var(--text-sm)" }}>{s.name}</span>
                <span className="badge" style={{ fontSize:"9px", padding:"1px 5px", marginLeft:"auto",
                  background:s.nature==="吉"?"rgba(26,122,82,0.12)":"rgba(181,54,30,0.1)",
                  color:s.nature==="吉"?"var(--jade)":"var(--accent)", borderRadius:"99px",
                  border:`1px solid ${s.nature==="吉"?"rgba(26,122,82,0.3)":"rgba(181,54,30,0.25)"}` }}>
                  {s.nature}
                </span>
              </div>
              <div style={{ fontSize:"var(--text-xs)", color:"var(--text-muted)", fontFamily:"var(--font-serif)", lineHeight:1.6 }}>
                {s.desc}
              </div>
              <div style={{ fontSize:"var(--text-xs)", color:"var(--text-secondary)", fontFamily:"var(--font-serif)", lineHeight:1.6, marginTop:"3px" }}>
                {s.断法}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-title">断卦核心口诀</div>
        {KOUJUE.map((k, i) => (
          <div key={i} style={{ padding:"0.55rem 0", borderBottom:"1px solid var(--border)" }}>
            <div style={{ fontSize:"var(--text-xs)", fontWeight:700, color:"var(--accent)", marginBottom:"3px", letterSpacing:"0.04em" }}>
              {k.t}
            </div>
            <div style={{ fontSize:"var(--text-xs)", color:"var(--text-secondary)", fontFamily:"var(--font-serif)", lineHeight:1.7 }}>
              {k.c}
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-title">旺相休囚死速查</div>
        <div style={{ fontSize:"var(--text-xs)", color:"var(--text-muted)", marginBottom:"0.5rem", fontFamily:"var(--font-serif)" }}>
          六爻五行旺衰以月令为准，以下为各季对应
        </div>
        {[
          ['春（木旺）', '木旺·火相·水休·金囚·土死'],
          ['夏（火旺）', '火旺·土相·木休·水囚·金死'],
          ['秋（金旺）', '金旺·水相·土休·火囚·木死'],
          ['冬（水旺）', '水旺·木相·金休·土囚·火死'],
          ['四季末（土旺）', '土旺·金相·火休·木囚·水死'],
        ].map(([season, desc]) => (
          <div key={season} style={{ display:"flex", gap:"0.75rem", padding:"0.35rem 0",
            borderBottom:"1px solid var(--border)", fontSize:"var(--text-xs)" }}>
            <span style={{ color:"var(--accent)", fontWeight:600, width:90, flexShrink:0 }}>{season}</span>
            <span style={{ color:"var(--text-secondary)", fontFamily:"var(--font-serif)" }}>{desc}</span>
          </div>
        ))}
      </div>
    </div>
  )
}


