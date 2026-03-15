import React, { useState } from 'react'
import AiInterpretPanel from '../../components/UI/AiInterpretPanel'
import { qimenApi } from '../../api/client'
import { useNotifyStore } from '../../store/settingsStore'

/*洛书九宫顺序：4巽、9离、2坤、3震、5中、7兑、8艮、1坎、6乾 */
const GRID_ORDER = [4, 9, 2, 3, 5, 7, 8, 1, 6]
const PALACE_NAME = {
  1:'坎一宫',2:'坤二宫',3:'震三宫',4:'巽四宫',5:'中五宫',
  6:'乾六宫',7:'兑七宫',8:'艮八宫',9:'离九宫',
}
const PALACE_DIR = {
  1:'北',2:'西南',3:'东',4:'东南',5:'中',6:'西北',7:'西',8:'东北',9:'南',
}

const QUALITY_STYLE = {
  '大吉': { bg:'rgba(26,138,90,0.10)',  border:'rgba(26,138,90,0.40)',  text:'#1a8a5a', dot:'#1a8a5a' },
  '吉':   { bg:'rgba(26,138,90,0.06)',  border:'rgba(26,138,90,0.25)',  text:'#2aaa70', dot:'#2aaa70' },
  '小吉': { bg:'rgba(34,112,168,0.07)', border:'rgba(34,112,168,0.28)', text:'#2270a8', dot:'#2270a8' },
  '平':   { bg:'rgba(100,100,100,0.04)',border:'rgba(100,100,100,0.15)',text:'var(--text-muted)', dot:'#aaa' },
  '凶':   { bg:'rgba(196,88,10,0.07)',  border:'rgba(196,88,10,0.28)',  text:'#c4580a', dot:'#c4580a' },
  '大凶': { bg:'rgba(200,64,42,0.09)',  border:'rgba(200,64,42,0.40)',  text:'#c8402a', dot:'#c8402a' },
}

const STEM_COLOR = {
  '乙':'#1a8a5a','丙':'#c4580a','丁':'#c8402a',
  '戊':'#2270a8','壬':'#2270a8',
  '庚':'#c8402a','辛':'#c8402a','己':'#8a6a50','癸':'#8a6a50',
}

const PURPOSES = [
  { id:'求财', icon:'💰', desc:'经商投资' },
  { id:'求官', icon:'🏆', desc:'仕途升职' },
  { id:'感情', icon:'❤️', desc:'婚嫁感情' },
  { id:'出行', icon:'🧭', desc:'远行出国' },
  { id:'健康', icon:'🏥', desc:'求医问病' },
  { id:'考试', icon:'📚', desc:'学业考试' },
]


const QIMEN_THEORY = [
  { icon:'✦', t:'三奇得使', d:'乙丙丁三奇遇值符相生，为奇门最吉格局。三奇得使主出行大利、谋事必成。' },
  { icon:'⚡', t:'三吉门', d:'开门（万事通达）·休门（蓄积待机）·生门（财富生发）为三吉，出行谈判选此三门。' },
  { icon:'⚠', t:'三凶门', d:'死门·惊门·伤门为三凶，动兵用军可取，日常谋事大忌。杜门中平宜静守。' },
  { icon:'🌀', t:'伏吟反吟', d:'值符与宫同干为伏吟（主停滞），与宫相冲为反吟（主大变动），两者均为大凶格局。' },
  { icon:'☰', t:'值符值使', d:'值符管长远（天盘天干），值使管近期（地盘八门）。符生使大吉，使克符主困难。' },
]

export default function QiMenPage() {
  const [form, setForm] = useState({
    year: new Date().getFullYear(), month: new Date().getMonth()+1,
    day: new Date().getDate(), hour: new Date().getHours(),
    question: '',
  })
  const [useNow, setUseNow] = useState(true)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null)  // selected palace
  const [tab, setTab] = useState('chart')          // chart | analysis | yongshen | timing
  const [purpose, setPurpose] = useState('求财')
  const { notify } = useNotifyStore()

  const run = async () => {
    setLoading(true); setSelected(null); setTab('chart')
    try {
      const payload = useNow
        ? { question: form.question }
        : { ...form }
      const data = useNow ? await qimenApi.now(payload) : await qimenApi.layout(payload)
      setResult(data)
      notify('排盘完成', 'success')
    } catch (e) { notify(e.message, 'error') }
    finally { setLoading(false) }
  }

  const setF = (k, v) => setForm(f => ({ ...f, [k]: isNaN(Number(v)) ? v : Number(v) }))

  const palaceMap = {}
  result?.palaces?.forEach(p => { palaceMap[p.position] = p })

  const TABS = [
    { id:'chart',    label:'九宫盘', desc:'四盘全局' },
    { id:'analysis', label:'值符值使', desc:'核心断法' },
    { id:'yongshen', label:'用神分析', desc:'14类用法' },
    { id:'timing',   label:'应期推算', desc:'《奇门法穷》' },
  ]

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <div className="page-title">奇门遁甲</div>
          <div className="page-subtitle">
            三元九局 · 四盘体系（天地人神）· 值符值使 · 三奇六仪 · 趋吉避凶
          </div>
        </div>
      </div>

      <div className="page-body">
        <div className="page-cols">
          {/* ── Left: Input ── */}
          <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
            <div className="card">
              <div className="card-title">起局方式</div>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.5rem', marginBottom:'0.85rem' }}>
                <button className={`btn ${useNow ? 'btn-primary' : ''}`}
                  onClick={() => setUseNow(true)}>⚡ 即时起局</button>
                <button className={`btn ${!useNow ? 'btn-primary' : ''}`}
                  onClick={() => setUseNow(false)}>🗓 指定时间</button>
              </div>

              {!useNow && (
                <div style={{ display:'flex', flexDirection:'column', gap:'0.55rem', marginBottom:'0.75rem' }}>
                  <div className="form-row-2">
                    <div className="form-group"><label>年</label>
                      <input type="number" value={form.year} onChange={e=>setF('year',e.target.value)} /></div>
                    <div className="form-group"><label>月</label>
                      <input type="number" min="1" max="12" value={form.month} onChange={e=>setF('month',e.target.value)} /></div>
                  </div>
                  <div className="form-row-2">
                    <div className="form-group"><label>日</label>
                      <input type="number" min="1" max="31" value={form.day} onChange={e=>setF('day',e.target.value)} /></div>
                    <div className="form-group"><label>时 (0–23)</label>
                      <input type="number" min="0" max="23" value={form.hour} onChange={e=>setF('hour',e.target.value)} /></div>
                  </div>
                </div>
              )}

              <div className="form-group">
                <label>占问事项（可选）</label>
                <textarea value={form.question}
                  onChange={e => setF('question', e.target.value)}
                  placeholder="如：此次求职是否顺利？投资某项目吉凶？" rows={2} />
              </div>
            </div>

            <button className="btn btn-primary btn-full btn-lg" onClick={run} disabled={loading}>
              {loading ? '布局中…' : '起局排盘 ▶'}
            </button>

            {/* Purpose selector */}
            <div className="card">
              <div className="card-title">占问类型</div>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.4rem' }}>
                {PURPOSES.map(p => (
                  <button key={p.id}
                    onClick={() => setPurpose(p.id)}
                    style={{
                      padding:'0.5rem 0.6rem', borderRadius:'var(--r-sm)',
                      border:`1px solid ${purpose===p.id ? 'var(--accent-dim)' : 'var(--border)'}`,
                      background: purpose===p.id ? 'var(--accent-bg)' : 'var(--bg-subtle)',
                      cursor:'pointer', display:'flex', alignItems:'center', gap:'0.4rem',
                      fontSize:'var(--text-sm)', color: purpose===p.id ? 'var(--accent)' : 'var(--text-muted)',
                    }}>
                    <span>{p.icon}</span>
                    <span style={{ fontWeight:500 }}>{p.id}</span>
                    <span style={{ fontSize:'var(--text-xs)', marginLeft:'auto' }}>{p.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Quick theory reference */}
            <div className="card">
              <div className="card-title">四盘体系</div>
              {[
                { icon:'⭐', name:'天盘·九星', color:'#c4580a', desc:'天时 — 辅禽心任吉，蓬芮柱凶' },
                { icon:'🚪', name:'人盘·八门', color:'#1a8a5a', desc:'人和 — 开休生吉，死惊伤凶' },
                { icon:'🏔', name:'地盘·九宫', color:'#2270a8', desc:'地利 — 九宫方位，造葬迁移首重' },
                { icon:'👁', name:'神盘·八神', color:'#c8402a', desc:'神助 — 值符吉首，玄武凶煞' },
              ].map(item => (
                <div key={item.name} style={{
                  display:'flex', gap:'0.6rem', alignItems:'center',
                  padding:'0.42rem 0', borderBottom:'1px solid var(--border)',
                  fontSize:'var(--text-xs)',
                }}>
                  <span style={{ fontSize:'0.9rem' }}>{item.icon}</span>
                  <span style={{ color:item.color, fontWeight:600, width:'70px', flexShrink:0 }}>{item.name}</span>
                  <span style={{ color:'var(--text-muted)' }}>{item.desc}</span>
                </div>
              ))}
              <div style={{ marginTop:'0.6rem', fontSize:'var(--text-xs)', color:'var(--text-muted)',
                fontFamily:'var(--font-serif)', lineHeight:1.7 }}>
                《秘籍大全》：星克门吉，门克星凶。《统宗》：静看值符值使，动看方向。
              </div>
            </div>
          </div>

          {/* ── Right: Result ── */}
          <div>
            {loading && (
              <div className="loading"><div className="spinner"/><p>演算九宫八门中…</p></div>
            )}

            {!loading && !result && (
              <div className="card" style={{ textAlign:'center', padding:'3.5rem 2rem' }}>
                <div style={{ fontSize:'3.5rem', marginBottom:'1rem', opacity:0.25 }}>✦</div>
                <p style={{ fontFamily:'var(--font-serif)', color:'var(--text-muted)', fontSize:'var(--text-base)' }}>
                  以当前时刻或指定时间起局，观四盘星门神奇仪
                </p>
                <p style={{ fontSize:'var(--text-xs)', color:'var(--text-faint)', marginTop:'0.5rem', fontFamily:'var(--font-serif)' }}>
                  《奇门遁甲统宗》：趋吉避凶，知时识势，方为上策
                </p>
              </div>
            )}

            {!loading && result && (
              <>
                {/* Header summary card */}
                <div className="card card-glow" style={{ marginBottom:'1rem' }}>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', flexWrap:'wrap', gap:'0.75rem' }}>
                    <div>
                      <div style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-lg)',
                        color:'var(--accent)', letterSpacing:'0.06em', lineHeight:1.2 }}>
                        {result.ju_type} 第{result.ju_number}局
                        <span style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)',
                          fontFamily:'var(--font-sans)', fontWeight:400, marginLeft:'0.6rem' }}>
                          {result.yuan}
                        </span>
                      </div>
                      <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)',
                        marginTop:'0.3rem', fontFamily:'var(--font-mono)' }}>
                        {result.datetime}
                      </div>
                    </div>
                    <div style={{ display:'flex', gap:'0.5rem', flexWrap:'wrap' }}>
                      {result.auspicious_directions?.slice(0,3).map((d,i) => (
                        <span key={i} className="badge badge-jade">{d}</span>
                      ))}
                      {result.patterns?.filter(p => p.level === '大凶').map((p,i) => (
                        <span key={i} className="badge badge-red">{p.name}</span>
                      ))}
                    </div>
                  </div>
                  {form.question && (
                    <div style={{ marginTop:'0.65rem', padding:'0.42rem 0.75rem',
                      background:'var(--bg-subtle)', borderRadius:'var(--r-sm)',
                      fontSize:'var(--text-xs)', color:'var(--text-muted)', fontStyle:'italic',
                      fontFamily:'var(--font-serif)' }}>
                      占问：{form.question || result.question}
                    </div>
                  )}
                </div>

                {/* Tab bar */}
                <div className="tab-bar">
                  {TABS.map(t => (
                    <button key={t.id} className={`tab ${tab===t.id?'active':''}`}
                      onClick={() => setTab(t.id)}>
                      {t.label}
                      <span style={{ fontSize:'var(--text-xs)', color:'var(--text-faint)',
                        marginLeft:'0.3rem', display:'none' /* mobile */ }}>{t.desc}</span>
                    </button>
                  ))}
                </div>

                {/* ═══ TAB: 九宫盘 ═══ */}
                {tab === 'chart' && (
                  <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
                    {/* 9-palace grid */}
                    <div className="card">
                      <div className="card-title">九宫排局 · 四盘叠合</div>
                      <div style={{
                        display:'grid', gridTemplateColumns:'repeat(3,1fr)',
                        gap:'5px', maxWidth:'520px', margin:'0 auto',
                      }}>
                        {GRID_ORDER.map(pos => {
                          const p = palaceMap[pos]
                          if (!p) return <div key={pos} />
                          const qs = QUALITY_STYLE[p.quality] || QUALITY_STYLE['平']
                          const isZhifu  = p.is_zhifu
                          const isZhishi = p.is_zhishi
                          const isCenter = pos === 5

                          return (
                            <div key={pos}
                              onClick={() => setSelected(selected?.position===pos ? null : p)}
                              style={{
                                background: qs.bg,
                                border:`1.5px solid ${selected?.position===pos ? 'var(--accent)' : qs.border}`,
                                borderRadius:'var(--r-md)',
                                padding:'0.55rem 0.5rem 0.45rem',
                                cursor:'pointer',
                                transition:'all 0.15s',
                                position:'relative',
                                minHeight:'110px',
                                display:'flex', flexDirection:'column', gap:'2px',
                                boxShadow: selected?.position===pos ? '0 0 0 2px var(--accent-bg)' : 'var(--shadow-sm)',
                              }}>
                              {/* Palace header */}
                              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center',
                                marginBottom:'3px' }}>
                                <span style={{ fontSize:'var(--text-xs)', color:'var(--text-faint)',
                                  fontFamily:'var(--font-mono)' }}>
                                  {PALACE_DIR[pos]}
                                </span>
                                <div style={{ display:'flex', gap:'2px' }}>
                                  {isZhifu  && <span style={{ fontSize:'9px', background:'#c8402a',
                                    color:'#fff', padding:'1px 4px', borderRadius:'3px', fontWeight:700 }}>符</span>}
                                  {isZhishi && <span style={{ fontSize:'9px', background:'#2270a8',
                                    color:'#fff', padding:'1px 4px', borderRadius:'3px', fontWeight:700 }}>使</span>}
                                </div>
                              </div>

                              {/* Star (天盘) */}
                              <div style={{ fontWeight:700, fontSize:'var(--text-sm)', color: qs.text }}>
                                {p.star}
                              </div>

                              {/* Door (人盘) */}
                              <div style={{ fontSize:'var(--text-xs)', color:'var(--text-secondary)', fontWeight:500 }}>
                                {p.door}
                              </div>

                              {/* Stem (奇仪) */}
                              <div style={{ fontSize:'var(--text-xs)',
                                color: STEM_COLOR[p.stem] || 'var(--text-muted)', fontFamily:'var(--font-display)',
                                fontSize:'0.9rem' }}>
                                {p.stem}
                              </div>

                              {/* Deity (神盘) */}
                              <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)',
                                marginTop:'auto' }}>
                                {p.deity}
                              </div>

                              {/* Quality dot */}
                              <div style={{ position:'absolute', top:'6px', right:'6px',
                                width:'7px', height:'7px', borderRadius:'50%',
                                background: qs.dot }} />
                            </div>
                          )
                        })}
                      </div>

                      {/* Legend */}
                      <div style={{ display:'flex', gap:'1rem', marginTop:'0.85rem', flexWrap:'wrap',
                        fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>
                        <div>上行：九星（天盘·天时）</div>
                        <div>中行：八门（人盘·人和）</div>
                        <div>奇仪：三奇六仪（天干）</div>
                        <div>下行：八神（神盘·神助）</div>
                        <span className="badge badge-red" style={{ fontSize:'9px' }}>符</span>
                        <span style={{ color:'var(--text-muted)' }}>值符宫</span>
                        <span className="badge badge-cyan" style={{ fontSize:'9px' }}>使</span>
                        <span style={{ color:'var(--text-muted)' }}>值使门宫</span>
                      </div>
                    </div>

                    {/* Palace detail on click */}
                    {selected && <PalaceDetail palace={selected} />}

                    {/* Overall summary */}
                    <div className="card">
                      <div className="card-title">局势总述</div>
                      <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-base)',
                        color:'var(--text-secondary)', lineHeight:1.88 }}>
                        {result.summary}
                      </p>
                      {result.advice && (
                        <div style={{ marginTop:'0.75rem', padding:'0.8rem 1rem',
                          background:'var(--accent-bg)', border:'1px solid var(--accent-dim)',
                          borderRadius:'var(--r-md)', fontFamily:'var(--font-serif)',
                          fontSize:'var(--text-sm)', color:'var(--text-primary)', lineHeight:1.82 }}>
                          {result.advice}
                        </div>
                      )}
                    </div>

                    {/* Yanbo notes */}
                    {result.yanbo_notes?.length > 0 && (
                      <div className="card">
                        <div className="card-title">《烟波钓叟赋》相关口诀</div>
                        {result.yanbo_notes.map((note, i) => (
                          <div key={i} style={{ display:'flex', gap:'0.6rem',
                            padding:'0.4rem 0', borderBottom:'1px solid var(--border)',
                            fontSize:'var(--text-sm)', fontFamily:'var(--font-serif)',
                            color:'var(--text-secondary)', lineHeight:1.7 }}>
                            <span style={{ color:'var(--accent)', flexShrink:0 }}>「</span>
                            {note}
                            <span style={{ color:'var(--accent)' }}>」</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* ═══ TAB: 值符值使 ═══ */}
                {tab === 'analysis' && (
                  <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
                    {result.zhifu_analysis ? (
                      <ZhifuZhishiPanel data={result.zhifu_analysis} />
                    ) : (
                      <div className="card"><p style={{ color:'var(--text-muted)' }}>值符值使数据加载中…</p></div>
                    )}

                    {/* Patterns */}
                    {result.patterns?.length > 0 && (
                      <div className="card">
                        <div className="card-title">格局检测</div>
                        {result.patterns.map((pat, i) => {
                          const qs = QUALITY_STYLE[pat.level] || QUALITY_STYLE['平']
                          return (
                            <div key={i} style={{ marginBottom:'0.75rem', padding:'0.75rem',
                              background: qs.bg, border:`1px solid ${qs.border}`,
                              borderRadius:'var(--r-md)' }}>
                              <div style={{ display:'flex', gap:'0.5rem', alignItems:'center',
                                marginBottom:'0.35rem' }}>
                                <span style={{ fontWeight:700, color: qs.text, fontFamily:'var(--font-title)',
                                  fontSize:'var(--text-md)' }}>{pat.name}</span>
                                <span className={`badge ${pat.level.includes('吉') ? 'badge-jade' : 'badge-red'}`}>
                                  {pat.level}</span>
                              </div>
                              <p style={{ fontSize:'var(--text-sm)', color:'var(--text-secondary)',
                                fontFamily:'var(--font-serif)', lineHeight:1.78 }}>{pat.desc}</p>
                              {pat.kou && (
                                <div style={{ marginTop:'0.4rem', fontSize:'var(--text-xs)',
                                  color:'var(--accent)', fontFamily:'var(--font-serif)',
                                  fontStyle:'italic' }}>「{pat.kou}」</div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )}

                    {/* 4-panel interaction rules */}
                    <div className="card">
                      <div className="card-title">四盘断事要诀</div>
                      {[
                        { rule:'星克门吉', desc:'天盘星五行克人盘门五行 → 天时助人和，主吉', level:'吉', src:'《秘籍大全》' },
                        { rule:'门克星凶', desc:'人盘门五行克天盘星五行 → 逆天时，有阻', level:'凶', src:'《秘籍大全》' },
                        { rule:'门生宫吉', desc:'人盘门生地盘宫五行 → 人和生地利，顺', level:'吉', src:'《秘籍大全》' },
                        { rule:'宫克门凶', desc:'地盘宫克人盘门 → 地利压人和，阻', level:'凶', src:'《秘籍大全》' },
                        { rule:'天生地吉', desc:'天盘奇仪生地盘宫 → 天时助地利，顺', level:'小吉', src:'《奇门一得》' },
                      ].map((item, i) => (
                        <div key={i} style={{ display:'flex', gap:'0.75rem', alignItems:'flex-start',
                          padding:'0.45rem 0', borderBottom:'1px solid var(--border)',
                          fontSize:'var(--text-sm)' }}>
                          <span className={`badge ${item.level.includes('吉') ? 'badge-jade' : 'badge-red'}`}
                            style={{ flexShrink:0, marginTop:'1px' }}>{item.rule}</span>
                          <div>
                            <span style={{ color:'var(--text-secondary)', fontFamily:'var(--font-serif)' }}>{item.desc}</span>
                            <span style={{ fontSize:'var(--text-xs)', color:'var(--text-faint)',
                              marginLeft:'0.5rem' }}>—{item.src}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ═══ TAB: 用神分析 ═══ */}
                {tab === 'yongshen' && (
                  <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
                    {result.yong_shen && (
                      <div className="card card-glow">
                        <div className="card-title">用神 · {result.yong_shen.topic}</div>
                        <div style={{ display:'grid', gridTemplateColumns:'auto 1fr',
                          gap:'0.5rem 1rem', fontSize:'var(--text-sm)', marginBottom:'0.85rem' }}>
                          <span style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', fontWeight:600 }}>用神</span>
                          <span style={{ color:'var(--accent)', fontFamily:'var(--font-serif)', fontWeight:500 }}>
                            {result.yong_shen.name}
                          </span>
                          <span style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', fontWeight:600 }}>所在宫</span>
                          <span style={{ color:'var(--text-primary)' }}>{result.yong_shen.palace}</span>
                          <span style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', fontWeight:600 }}>格局</span>
                          <span style={{ color: QUALITY_STYLE[result.yong_shen.quality]?.text || 'var(--text-muted)' }}>
                            {result.yong_shen.quality}
                          </span>
                        </div>
                        {result.yong_shen.rules && (
                          <div style={{ padding:'0.65rem 0.85rem', background:'var(--bg-subtle)',
                            borderRadius:'var(--r-sm)', fontSize:'var(--text-sm)',
                            fontFamily:'var(--font-serif)', color:'var(--text-secondary)', lineHeight:1.82 }}>
                            {result.yong_shen.rules}
                          </div>
                        )}
                        {result.yong_shen.best && (
                          <div style={{ marginTop:'0.6rem', padding:'0.55rem 0.75rem',
                            background:'rgba(26,138,90,0.07)', border:'1px solid rgba(26,138,90,0.25)',
                            borderRadius:'var(--r-sm)', fontSize:'var(--text-xs)',
                            color:'var(--jade)', fontFamily:'var(--font-serif)' }}>
                            最吉格局：{result.yong_shen.best}
                          </div>
                        )}
                      </div>
                    )}

                    {/* 14-purpose quick reference */}
                    <div className="card">
                      <div className="card-title">14类用神速查表</div>
                      {[
                        { topic:'求财经商', shen:'生门·壬水', tip:'生门旺相，壬水见吉门则财旺' },
                        { topic:'求官仕途', shen:'开门·天心', tip:'开门旺相，值符临吉宫，三奇见大吉' },
                        { topic:'婚嫁感情', shen:'六合神·休门', tip:'六合临吉门，日干与配偶干生合则吉' },
                        { topic:'出行远足', shen:'行人方位宫', tip:'所去方向宫位吉，生开门临之' },
                        { topic:'疾病求医', shen:'天心·休门', tip:'天心旺相，休门临吉神则病可愈' },
                        { topic:'求学考试', shen:'天辅·景门', tip:'天辅旺，景门临文方，丙奇见则吉' },
                        { topic:'经商谈判', shen:'生门·六合', tip:'生门壬水吉，六合临谈判方则成' },
                        { topic:'官司诉讼', shen:'日干宫强弱', tip:'己方宫强于对方宫则胜' },
                        { topic:'投资置业', shen:'天任·生门', tip:'天任临生门，方位宫吉，置业有利' },
                        { topic:'寻人失踪', shen:'生门方位宫', tip:'生开门临所去方，可寻回' },
                        { topic:'预测来意', shen:'日干宫四盘', tip:'日干宫的门星神代表来人事情' },
                      ].map((item, i) => (
                        <div key={i} style={{ display:'grid', gridTemplateColumns:'80px 90px 1fr',
                          gap:'0.5rem', padding:'0.42rem 0',
                          borderBottom:'1px solid var(--border)',
                          fontSize:'var(--text-xs)', alignItems:'start' }}>
                          <span style={{ fontWeight:600, color:'var(--accent)' }}>{item.topic}</span>
                          <span style={{ color:'var(--cyan)', fontFamily:'var(--font-serif)' }}>{item.shen}</span>
                          <span style={{ color:'var(--text-muted)', fontFamily:'var(--font-serif)', lineHeight:1.6 }}>{item.tip}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ═══ TAB: 应期推算 ═══ */}
                {tab === 'timing' && (
                  <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
                    {result.timing && (
                      <>
                        <div className="card card-glow">
                          <div className="card-title">应期总判</div>
                          <div style={{ padding:'0.75rem 1rem', background:'var(--accent-bg)',
                            border:'1px solid var(--accent-dim)', borderRadius:'var(--r-md)',
                            fontFamily:'var(--font-serif)', fontSize:'var(--text-base)',
                            color:'var(--text-primary)', lineHeight:1.88 }}>
                            {result.timing.speed}
                          </div>
                          <div style={{ marginTop:'0.6rem', fontSize:'var(--text-xs)',
                            color:'var(--text-muted)', fontFamily:'var(--font-serif)' }}>
                            原因：{result.timing.speed_reason}
                          </div>
                        </div>

                        <div className="card">
                          <div className="card-title">值符推算法</div>
                          <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)',
                            color:'var(--text-secondary)', lineHeight:1.82 }}>
                            {result.timing.fu_method}
                          </p>
                          <p style={{ marginTop:'0.5rem', fontFamily:'var(--font-serif)',
                            fontSize:'var(--text-sm)', color:'var(--text-secondary)', lineHeight:1.82 }}>
                            {result.timing.shi_method}
                          </p>
                        </div>

                        <div className="card">
                          <div className="card-title">《奇门法穷》三法</div>
                          {Object.entries(result.timing.three_methods || {}).map(([k, v]) => (
                            <div key={k} style={{ marginBottom:'0.7rem', padding:'0.65rem 0.85rem',
                              background:'var(--bg-subtle)', borderRadius:'var(--r-sm)',
                              borderLeft:'2px solid var(--accent-dim)' }}>
                              <div style={{ fontWeight:600, color:'var(--accent)',
                                marginBottom:'0.3rem', fontSize:'var(--text-sm)' }}>{k}</div>
                              <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)',
                                color:'var(--text-secondary)', lineHeight:1.78 }}>{v}</p>
                            </div>
                          ))}
                        </div>

                        <div className="card">
                          <div className="card-title">应期总则</div>
                          <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)',
                            color:'var(--text-secondary)', lineHeight:1.88 }}>
                            {result.timing.general}
                          </p>
                          <div style={{ marginTop:'0.75rem', padding:'0.55rem 0.75rem',
                            background:'rgba(196,88,10,0.06)', border:'1px solid rgba(196,88,10,0.22)',
                            borderRadius:'var(--r-sm)', fontSize:'var(--text-xs)',
                            color:'var(--orange)', fontFamily:'var(--font-serif)' }}>
                            {result.timing.fu_shi_order}
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                )}

                {/* AI Interpret */}
                <div style={{ marginTop:'1rem' }}>
                  <AiInterpretPanel module="qimen" data={result} extraContext={purpose} />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/* ── Palace Detail Card (on click) ── */
function PalaceDetail({ palace: p }) {
  const qs = QUALITY_STYLE[p.quality] || QUALITY_STYLE['平']
  return (
    <div className="card" style={{ border:`1.5px solid ${qs.border}`, background: qs.bg }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'0.75rem' }}>
        <div style={{ fontFamily:'var(--font-title)', fontSize:'var(--text-md)', color: qs.text }}>
          {p.palace_name} · {PALACE_DIR[p.position]}方
        </div>
        <span className={`badge ${p.is_auspicious ? 'badge-jade' : p.quality==='大凶' ? 'badge-red' : 'badge-muted'}`}>
          {p.quality}
        </span>
      </div>

      {/* Four-panel breakdown */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:'0.5rem', marginBottom:'0.85rem' }}>
        {[
          { label:'天·九星', val:p.star, sub:p.star_meaning, color:'#c4580a' },
          { label:'人·八门', val:p.door, sub:p.door_meaning, color:'#1a8a5a' },
          { label:'地·宫位', val:p.gong_wx||'', sub:p.palace_name?.slice(0,2), color:'#2270a8' },
          { label:'神·八神', val:p.deity, sub:p.deity_meaning, color:'#c8402a' },
        ].map(item => (
          <div key={item.label} style={{ textAlign:'center', padding:'0.5rem 0.3rem',
            background:'var(--surface)', borderRadius:'var(--r-sm)', border:'1px solid var(--border)' }}>
            <div style={{ fontSize:'var(--text-xs)', color:'var(--text-faint)', marginBottom:'4px' }}>{item.label}</div>
            <div style={{ fontWeight:700, color:item.color, fontSize:'var(--text-sm)' }}>{item.val}</div>
            <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', lineHeight:1.4, marginTop:'2px' }}>{item.sub}</div>
          </div>
        ))}
      </div>

      {/* Stem info */}
      {p.stem && (
        <div style={{ display:'flex', gap:'0.5rem', alignItems:'center', marginBottom:'0.6rem' }}>
          <span style={{ fontFamily:'var(--font-display)', fontSize:'1.4rem',
            color: STEM_COLOR[p.stem] || 'var(--text-muted)' }}>{p.stem}</span>
          {p.stem_info && (
            <span style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)',
              fontFamily:'var(--font-serif)' }}>{p.stem_info}</span>
          )}
        </div>
      )}

      {/* Star/door relationship */}
      {p.sd_rel && (
        <div style={{ padding:'0.4rem 0.65rem', borderRadius:'var(--r-sm)',
          background: p.sd_rel.includes('★') ? 'rgba(26,138,90,0.08)' : 'rgba(196,88,10,0.08)',
          border: `1px solid ${p.sd_rel.includes('★') ? 'rgba(26,138,90,0.28)' : 'rgba(196,88,10,0.28)'}`,
          fontSize:'var(--text-xs)', color: p.sd_rel.includes('★') ? '#1a8a5a' : '#c4580a',
          fontFamily:'var(--font-serif)', marginBottom:'0.55rem' }}>
          {p.sd_rel}
        </div>
      )}

      {/* Door yi/ji */}
      {(p.door_yi?.length > 0 || p.door_ji?.length > 0) && (
        <div style={{ display:'flex', gap:'0.75rem', fontSize:'var(--text-xs)',
          color:'var(--text-muted)', flexWrap:'wrap' }}>
          {p.door_yi?.length > 0 && (
            <div>
              <span style={{ color:'#1a8a5a', fontWeight:600 }}>宜：</span>
              {p.door_yi.slice(0,3).join('·')}
            </div>
          )}
          {p.door_ji?.length > 0 && (
            <div>
              <span style={{ color:'#c8402a', fontWeight:600 }}>忌：</span>
              {p.door_ji.slice(0,2).join('·')}
            </div>
          )}
        </div>
      )}

      {/* Yanbo */}
      {p.door_yanbo && (
        <div style={{ marginTop:'0.55rem', fontSize:'var(--text-xs)', color:'var(--accent)',
          fontFamily:'var(--font-serif)', fontStyle:'italic', borderTop:'1px solid var(--border)',
          paddingTop:'0.5rem' }}>
          《烟波》：{p.door_yanbo}
        </div>
      )}
    </div>
  )
}

/* ── Zhifu Zhishi Panel ── */
function ZhifuZhishiPanel({ data: d }) {
  const relStyle = d.relationship?.level === '大凶' ? 'badge-red'
                  : d.relationship?.level?.includes('吉') ? 'badge-jade' : 'badge-muted'
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'0.9rem' }}>
      {/* Verdict */}
      <div className="card card-glow">
        <div className="card-title">值符值使综合判断</div>
        <div style={{ padding:'0.75rem 1rem', background:'var(--accent-bg)',
          border:'1px solid var(--accent-dim)', borderRadius:'var(--r-md)',
          fontFamily:'var(--font-serif)', fontSize:'var(--text-base)',
          color:'var(--text-primary)', lineHeight:1.9 }}>
          {d.verdict}
        </div>
        <div style={{ marginTop:'0.55rem', fontSize:'var(--text-xs)',
          color:'var(--text-faint)', fontFamily:'var(--font-serif)' }}>
          {d.priority}
        </div>
      </div>

      {/* Zhifu + Zhishi side by side */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.85rem' }}>
        {/* 值符 */}
        <div className="card" style={{ borderColor:'rgba(196,88,10,0.28)' }}>
          <div style={{ fontFamily:'var(--font-title)', color:'#c4580a',
            fontSize:'var(--text-md)', marginBottom:'0.65rem', letterSpacing:'0.06em' }}>
            值符（{d.zhifu?.star}）
          </div>
          <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)',
            marginBottom:'0.5rem', fontFamily:'var(--font-serif)' }}>{d.zhifu?.role}</div>
          <div style={{ display:'flex', flexDirection:'column', gap:'0.35rem', fontSize:'var(--text-xs)' }}>
            <div><span style={{ color:'var(--text-faint)' }}>宫位：</span>
              <span style={{ color:'var(--text-primary)' }}>{d.zhifu?.palace}</span></div>
            <div><span style={{ color:'var(--text-faint)' }}>奇仪：</span>
              <span style={{ color: STEM_COLOR[d.zhifu?.stem] || 'var(--text-muted)',
                fontFamily:'var(--font-display)', fontSize:'1rem' }}>{d.zhifu?.stem}</span></div>
            <div><span style={{ color:'var(--text-faint)' }}>八神：</span>
              <span style={{ color:'var(--text-secondary)' }}>{d.zhifu?.deity}</span></div>
            <div><span style={{ color:'var(--text-faint)' }}>旺衰：</span>
              <span style={{ color: d.zhifu?.wangshuai==='旺' ? '#1a8a5a' : '#c8402a' }}>
                {d.zhifu?.wangshuai}</span></div>
          </div>
          {d.zhifu?.desc && (
            <div style={{ marginTop:'0.55rem', fontSize:'var(--text-xs)', color:'var(--text-muted)',
              fontFamily:'var(--font-serif)', lineHeight:1.7,
              borderTop:'1px solid var(--border)', paddingTop:'0.45rem' }}>
              {d.zhifu?.desc}
            </div>
          )}
        </div>

        {/* 值使 */}
        <div className="card" style={{ borderColor:'rgba(34,112,168,0.28)' }}>
          <div style={{ fontFamily:'var(--font-title)', color:'#2270a8',
            fontSize:'var(--text-md)', marginBottom:'0.65rem', letterSpacing:'0.06em' }}>
            值使（{d.zhishi?.door}）
          </div>
          <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)',
            marginBottom:'0.5rem', fontFamily:'var(--font-serif)' }}>{d.zhishi?.role}</div>
          <div style={{ display:'flex', flexDirection:'column', gap:'0.35rem', fontSize:'var(--text-xs)' }}>
            <div><span style={{ color:'var(--text-faint)' }}>宫位：</span>
              <span style={{ color:'var(--text-primary)' }}>{d.zhishi?.palace}</span></div>
            <div><span style={{ color:'var(--text-faint)' }}>奇仪：</span>
              <span style={{ color: STEM_COLOR[d.zhishi?.stem] || 'var(--text-muted)',
                fontFamily:'var(--font-display)', fontSize:'1rem' }}>{d.zhishi?.stem}</span></div>
            <div><span style={{ color:'var(--text-faint)' }}>九星：</span>
              <span style={{ color:'var(--text-secondary)' }}>{d.zhishi?.star}</span></div>
            <div><span style={{ color:'var(--text-faint)' }}>吉凶：</span>
              <span style={{ color: d.zhishi?.auspicious ? '#1a8a5a' : '#c8402a' }}>
                {d.zhishi?.auspicious ? '值使吉门' : '值使凶门'}</span></div>
          </div>
          {d.zhishi?.yanbo && (
            <div style={{ marginTop:'0.55rem', fontSize:'var(--text-xs)', color:'var(--accent)',
              fontFamily:'var(--font-serif)', fontStyle:'italic',
              borderTop:'1px solid var(--border)', paddingTop:'0.45rem' }}>
              《烟波》：{d.zhishi?.yanbo}
            </div>
          )}
        </div>
      </div>

      {/* Relationship card */}
      <div className="card">
        <div className="card-title">符使关系</div>
        <div style={{ display:'flex', gap:'0.65rem', alignItems:'center', marginBottom:'0.65rem' }}>
          <span className={`badge ${relStyle}`} style={{ fontSize:'var(--text-sm)', padding:'0.2rem 0.65rem' }}>
            {d.relationship?.name}
          </span>
          <span className={`badge ${relStyle}`}>{d.relationship?.level}</span>
        </div>
        <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)',
          color:'var(--text-secondary)', lineHeight:1.85 }}>
          {d.relationship?.detail}
        </p>
        <div style={{ marginTop:'0.6rem', padding:'0.5rem 0.75rem',
          background:'var(--bg-subtle)', borderRadius:'var(--r-sm)',
          fontSize:'var(--text-xs)', color:'var(--text-muted)', fontFamily:'var(--font-serif)' }}>
          引：{d.classical_ref}
        </div>
      </div>

      {/* Zhifu-zhishi rules table */}
      <div className="card">
        <div className="card-title">符使断法要诀</div>
        {[
          { cond:'符使同宫', level:'大吉', desc:'方向与执行一致，大事可成' },
          { cond:'符生使',   level:'吉',   desc:'贵人支持执行，顺' },
          { cond:'使生符',   level:'次吉', desc:'费力可成，需主动推动' },
          { cond:'符克使',   level:'吉',   desc:'有阻力但正常，可成' },
          { cond:'使克符',   level:'大凶', desc:'执行逆方向，极难成功' },
          { cond:'值使逢空', level:'凶',   desc:'执行无力，停滞不了了之' },
        ].map((item, i) => {
          const isGood = item.level.includes('吉') && item.level !== '大凶'
          return (
            <div key={i} style={{ display:'grid', gridTemplateColumns:'72px 48px 1fr',
              gap:'0.6rem', padding:'0.42rem 0', borderBottom:'1px solid var(--border)',
              fontSize:'var(--text-xs)', alignItems:'center' }}>
              <span style={{ fontWeight:600, color: isGood ? '#1a8a5a' : '#c8402a' }}>{item.cond}</span>
              <span className={`badge ${isGood ? 'badge-jade' : 'badge-red'}`}>{item.level}</span>
              <span style={{ color:'var(--text-muted)', fontFamily:'var(--font-serif)' }}>{item.desc}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
