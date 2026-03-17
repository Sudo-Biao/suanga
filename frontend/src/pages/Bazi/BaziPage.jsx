import React, { useState, Component } from 'react'
import BirthForm    from '../../components/UI/BirthForm'
import PillarCard   from '../../components/UI/PillarCard'
import AiInterpretPanel from '../../components/UI/AiInterpretPanel'
import { baziApi }  from '../../api/client'
import { useNotifyStore, useSettingsStore } from '../../store/settingsStore'

/* ── Error Boundary — prevents blank screen on any render crash ── */
class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { error: null } }
  static getDerivedStateFromError(e) { return { error: e } }
  componentDidCatch(e, info) { console.error('BaZi render error:', e, info) }
  render() {
    if (this.state.error) return (
      <div className="card card-danger" style={{ textAlign:'center', padding:'2rem' }}>
        <div style={{ fontSize:'1.5rem', marginBottom:'0.75rem' }}>⚠</div>
        <p style={{ color:'var(--red-light)', fontFamily:'var(--font-serif)', marginBottom:'0.75rem' }}>
          显示结果时发生错误，请重新点击推算。
        </p>
        <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', fontFamily:'var(--font-mono)' }}>
          {this.state.error.message}
        </div>
        <button className="btn btn-sm" style={{ marginTop:'1rem' }}
          onClick={() => this.setState({ error: null })}>重试</button>
      </div>
    )
    return this.props.children
  }
}

const TABS = [
  { id: 'chart',    label: '命盘' },
  { id: 'profile',  label: '日主' },
  { id: 'fortune',  label: '运势' },
  { id: 'career',   label: '事业' },
  { id: 'marriage', label: '婚姻' },
  { id: 'health',   label: '健康' },
  { id: 'wealth',   label: '财运' },
  { id: 'compat',   label: '合婚' },
]

const WX_COLOR = { 木:'#27ae60', 火:'#e74c3c', 土:'#f39c12', 金:'#95a5a6', 水:'#3498db' }
const defaultBirth = () => ({ year:1990, month:6, day:15, hour:8, minute:0, gender:'male' })

export default function BaziPage() {
  const [tab, setTab]       = useState('chart')
  const [birth, setBirth]   = useState(defaultBirth())
  const [birth2, setBirth2] = useState({ ...defaultBirth(), year:1992, month:3, day:8, gender:'female' })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)
  const { notify }          = useNotifyStore()

  const run = async () => {
    setLoading(true); setError(null)
    try {
      let data
      if (tab === 'chart' || tab === 'profile') data = await baziApi.chart(birth)
      else if (tab === 'fortune') data = await baziApi.fortune({ birth, query_year: new Date().getFullYear() })
      else if (tab === 'career')  data = await baziApi.career(birth)
      else if (tab === 'marriage') data = await baziApi.marriage(birth)
      else if (tab === 'health')  data = await baziApi.health(birth)
      else if (tab === 'wealth')  data = await baziApi.wealth(birth)
      else if (tab === 'compat')  data = await baziApi.compatibility({ person_a: birth, person_b: birth2 })
      setResult(data)
      notify('计算完成', 'success')
    } catch (e) { setError(e.message); notify(e.message, 'error') }
    finally { setLoading(false) }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <div className="page-title">八字推演</div>
          <div className="page-subtitle">四柱命理 · 干支五行 · 十神格局 · 大运流年</div>
        </div>
      </div>
      <div className="page-body">
        <div className="page-cols">
          {/* Left: input form */}
          <div style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
            {/* Tab selector — vertical pill list */}
            <div className="card" style={{ padding:'0.75rem 0.65rem' }}>
              <div style={{ fontSize:'10px', textTransform:'uppercase', letterSpacing:'0.08em',
                color:'var(--text-faint)', fontWeight:700, marginBottom:'0.5rem', paddingLeft:'0.2rem' }}>
                分析类型
              </div>
              <div style={{ display:'flex', flexDirection:'column', gap:'2px' }}>
                {TABS.map(t => (
                  <button key={t.id} onClick={() => { setTab(t.id); setResult(null) }}
                    style={{
                      padding:'0.52rem 0.75rem', borderRadius:'var(--r-md)',
                      border:`1px solid ${tab===t.id?'var(--accent-dim)':'transparent'}`,
                      background:tab===t.id?'var(--accent-bg)':'transparent',
                      color:tab===t.id?'var(--accent)':'var(--text-secondary)',
                      fontSize:'var(--text-sm)', fontWeight:tab===t.id?600:500,
                      cursor:'pointer', textAlign:'left', transition:'all var(--t-fast)',
                    }}>{t.label}</button>
                ))}
              </div>
            </div>
            <BirthForm values={birth} onChange={setBirth} title={tab==='compat'?'当事人 A':'出生信息'} />
            {tab === 'compat' && <BirthForm values={birth2} onChange={setBirth2} title="当事人 B" />}
            <button className="btn btn-primary btn-full btn-lg" onClick={run} disabled={loading}>
              {loading ? '推算中…' : '开始推算 ▶'}
            </button>
            {error && <div className="error-box">⚠ {error}</div>}
          </div>
          {/* Right: results */}
          <div>
            {loading && <div className="loading"><div className="spinner"/><p>正在推演命盘…</p></div>}
            {!loading && (
              <ErrorBoundary key={tab}>
                {result
                  ? <BaziResult tab={tab} data={result} birth={birth} />
                  : <BaziPlaceholder tab={tab} />}
              </ErrorBoundary>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function BaziPlaceholder({ tab }) {
  const descs = {
    chart:   '输入出生信息，推算四柱八字命盘、十神分布、格局神煞',
    profile: '深度解析日主性格特质、用神喜忌、幸运方向',
    fortune: '推算大运（十年周期）、流年运势、流月走向',
    career:  '根据命局五行分析最适合的职业方向与工作风格',
    marriage:'分析婚姻宫、配偶星，论断感情婚缘吉凶',
    health:  '五行偏枯分析，了解易患疾病与养生建议',
    wealth:  '财星分析，评估财富积累能力与理财方向',
    compat:  '两人八字对比，五行生克合冲，论断合婚吉凶',
  }
  return (
    <div className="card result-placeholder">
      <div className="result-placeholder-icon">☰</div>
      <p className="result-placeholder-text">{descs[tab]}</p>
    </div>
  )
}

function BaziResult({ tab, data, birth }) {
  if (tab === 'chart')    return <><ChartResult data={data} /><AiInterpretPanel module="bazi" data={data} extraContext="命盘" /></>
  if (tab === 'profile')  return <><ProfileResult data={data} /><AiInterpretPanel module="bazi" data={data} extraContext="日主性格" /></>
  if (tab === 'fortune')  return <><FortuneResult data={data} /><AiInterpretPanel module="bazi" data={data} extraContext="运势" /></>
  if (tab === 'career')   return <><CareerResult data={data} /><AiInterpretPanel module="bazi" data={data} extraContext="事业" /></>
  if (tab === 'marriage') return <><MarriageResult data={data} /><AiInterpretPanel module="bazi" data={data} extraContext="婚姻" /></>
  if (tab === 'health')   return <><HealthResult data={data} /><AiInterpretPanel module="bazi" data={data} extraContext="健康" /></>
  if (tab === 'wealth')   return <><WealthResult data={data} /><AiInterpretPanel module="bazi" data={data} extraContext="财运" /></>
  if (tab === 'compat')   return <><CompatResult data={data} /><AiInterpretPanel module="bazi" data={data} extraContext="合婚" /></>
  return null
}

/* ── Chart ── */
function ChartResult({ data }) {
  const q = data.strength_info?.monthly_status
  const shensha = data.shensha || []
  return (
    <div className="result-section">
      <div className="card">
        <div className="card-title">四柱八字命盘</div>
        <div className="pillar-row">
          {['year_pillar','month_pillar','day_pillar','hour_pillar'].map(k => (
            <PillarCard key={k} pillar={data[k]} highlight={k==='day_pillar'} />
          ))}
        </div>
        <div style={{ marginTop:'1.25rem' }}>
          <div className="kv-grid">
            <span className="kv-label">日主</span>
            <span className="kv-value accent">{data.day_master}（{data.day_master_wuxing}）</span>
            <span className="kv-label">身强弱</span>
            <span className="kv-value">
              {data.strength}
              {q && <span className="badge badge-muted" style={{ marginLeft:'0.5rem', fontSize:'var(--text-xs)' }}>{q}</span>}
            </span>
            <span className="kv-label">月令</span>
            <span className="kv-value">{data.strength_info?.deling ? '✓ 得令' : '✗ 不得令'}</span>
            <span className="kv-label">格局</span>
            <span className="kv-value accent">{data.pattern}</span>
            <span className="kv-label">格局解</span>
            <span className="kv-value" style={{ fontSize:'var(--text-sm)', color:'var(--text-secondary)' }}>{data.pattern_desc}</span>
          </div>
        </div>
      </div>

      {shensha.length > 0 && (
        <div className="card">
          <div className="card-title">神煞 · 特殊星曜</div>
          <div style={{ display:'flex', flexWrap:'wrap', gap:'0.5rem', marginBottom:'0.75rem' }}>
            {shensha.map((s, i) => (
              <span key={i} className="badge badge-gold">{s.name} · {s.pillar}</span>
            ))}
          </div>
          <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', fontFamily:'var(--font-serif)', lineHeight:1.7 }}>
            {shensha.some(s=>s.name==='天乙贵人') && <div>◆ 天乙贵人：一生贵人相助，化险为夷，遇难呈祥</div>}
            {shensha.some(s=>s.name==='文昌贵人') && <div>◆ 文昌贵人：智慧聪颖，学业顺遂，利于考试功名</div>}
            {shensha.some(s=>s.name==='驿马') && <div>◆ 驿马星：主动荡奔波，利出行、移居、外出求财</div>}
            {shensha.some(s=>s.name==='华盖') && <div>◆ 华盖星：孤高有才，利文艺宗教，但有孤独之象</div>}
            {shensha.some(s=>s.name==='羊刃') && <div>◆ 羊刃星：性格刚猛，有武职之才，但需防意外血光</div>}
          </div>
        </div>
      )}

      {data.shishen_summary?.length > 0 && (
        <div className="card">
          <div className="card-title">十神分布 · 五行力量</div>
          <div style={{ display:'flex', flexDirection:'column', gap:'0.5rem' }}>
            {data.shishen_summary?.map((s, i) => {
              const SHISHEN_MEANING = {
                '比肩':'同类帮扶，主自立独立', '劫财':'竞争争财，主决断魄力',
                '食神':'发泄才华，主口福享乐', '伤官':'才华过人，主创新突破',
                '正财':'踏实求财，主正职薪资', '偏财':'意外之财，主投资偏业',
                '正官':'约束规范，主仕途地位', '七杀':'权威魄力，主竞争压力',
                '正印':'学问贵人，主文化修养', '偏印':'偏门技艺，主独特才能',
              }
              return (
                <div key={i} style={{ padding:'0.5rem 0.75rem', background:'var(--bg-raised)', borderRadius:'var(--radius-sm)', border:'1px solid var(--border)' }}>
                  <div style={{ display:'flex', alignItems:'center', gap:'0.75rem', marginBottom:'0.25rem' }}>
                    <span style={{ width:'48px', color:'var(--accent)', fontFamily:'var(--font-display)', fontWeight:600 }}>{s.shishen}</span>
                    <div style={{ flex:1, background:'var(--bg-overlay)', borderRadius:'4px', height:'6px', overflow:'hidden' }}>
                      <div style={{ width:`${Math.min(100,s.count*22)}%`, height:'100%', background:'var(--accent)', borderRadius:'4px' }} />
                    </div>
                    <span style={{ width:'24px', textAlign:'right', color:'var(--text-muted)', fontSize:'var(--text-sm)' }}>{s.count}</span>
                    <span className="badge badge-muted" style={{ fontSize:'var(--text-xs)' }}>{s.strength}</span>
                  </div>
                  <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', paddingLeft:'56px' }}>{SHISHEN_MEANING[s.shishen]||''}</div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Profile (日主深度) ── */
function ProfileResult({ data }) {
  const p = data.day_master_profile || {}
  const y = data.yong_shen || {}
  const rec = y.recommendations || {}
  const WX_COLOR = { 木:'#27ae60', 火:'#e74c3c', 土:'#f39c12', 金:'#95a5a6', 水:'#3498db' }
  const lucky = p.lucky || {}
  const health = p.health || {}
  const rels = p.relationships || {}

  return (
    <div className="result-section">
      <div className="card" style={{ borderColor:'var(--accent-dim)', background:'var(--accent-glow)' }}>
        <div style={{ display:'flex', alignItems:'center', gap:'1rem', marginBottom:'1rem' }}>
          <div style={{ fontSize:'2.5rem', fontFamily:'var(--font-display)', color:'var(--accent)', lineHeight:1 }}>{data.day_master}</div>
          <div>
            <div style={{ fontFamily:'var(--font-display)', fontSize:'1.1rem', color:'var(--accent)' }}>{p.title}</div>
            <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginTop:'0.2rem' }}>
              {data.day_master_wuxing} · {data.strength} · {data.pattern}
            </div>
          </div>
        </div>
        <p style={{ fontFamily:'var(--font-serif)', lineHeight:1.8, color:'var(--text-secondary)' }}>{p.personality_detail}</p>
      </div>

      <div className="card">
        <div className="card-title">性格特质</div>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.5rem' }}>
          <div>
            <div style={{ fontSize:'var(--text-sm)', color:'#27ae60', marginBottom:'0.35rem', fontWeight:600 }}>✦ 优势</div>
            {(p.strengths||[]).map((s,i) => (
              <div key={i} style={{ fontSize:'var(--text-sm)', color:'var(--text-secondary)', display:'flex', gap:'0.4rem', marginBottom:'0.2rem' }}>
                <span style={{ color:'#27ae60', flexShrink:0 }}>◆</span>{s}
              </div>
            ))}
          </div>
          <div>
            <div style={{ fontSize:'var(--text-sm)', color:'var(--red-light)', marginBottom:'0.35rem', fontWeight:600 }}>✦ 注意</div>
            {(p.weaknesses||[]).map((s,i) => (
              <div key={i} style={{ fontSize:'var(--text-sm)', color:'var(--text-secondary)', display:'flex', gap:'0.4rem', marginBottom:'0.2rem' }}>
                <span style={{ color:'var(--red-light)', flexShrink:0 }}>◆</span>{s}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">用神喜忌分析</div>
        <div style={{ display:'flex', gap:'0.5rem', flexWrap:'wrap', marginBottom:'0.75rem' }}>
          {[['用神',y.yong_shen_wx,'#27ae60'],['喜神',y.xi_shen_wx,'#3498db'],
            ['忌神',y.ji_shen_wx,'var(--red-light)'],['仇神',y.chou_shen_wx,'#e67e22']].map(([label,wx,color]) => wx && (
            <div key={label} style={{ padding:'0.5rem 0.85rem', borderRadius:'var(--radius-md)',
              background:'var(--bg-raised)', border:`1px solid ${color}44`, textAlign:'center', minWidth:'80px' }}>
              <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>{label}</div>
              <div style={{ fontFamily:'var(--font-display)', fontSize:'1.3rem', color }}>
                {wx}
              </div>
            </div>
          ))}
        </div>
        <p style={{ fontSize:'var(--text-sm)', color:'var(--text-secondary)', fontFamily:'var(--font-serif)', lineHeight:1.7, marginBottom:'0.75rem' }}>
          {y.analysis}
        </p>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.5rem', fontSize:'var(--text-sm)' }}>
          {[
            ['✦ 幸运方向', rec.lucky_direction, '#27ae60'],
            ['✦ 幸运颜色', rec.lucky_color, '#27ae60'],
            ['✦ 幸运行业', rec.lucky_career, '#27ae60'],
            ['✦ 幸运数字', rec.lucky_number, '#27ae60'],
            ['✗ 回避方向', rec.avoid_direction, 'var(--red-light)'],
            ['✗ 回避颜色', rec.avoid_color, 'var(--red-light)'],
          ].map(([label,val,color]) => val && (
            <div key={label} style={{ padding:'0.35rem 0.5rem', background:'var(--bg-raised)', borderRadius:'var(--radius-sm)' }}>
              <span style={{ color, marginRight:'0.3rem' }}>{label.slice(0,1)}</span>
              <span style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)' }}>{label.slice(1)}</span>
              <div style={{ color:'var(--text-primary)', marginTop:'0.15rem' }}>{val}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-title">健康注意事项</div>
        <div className="kv-grid">
          <span className="kv-label">关注脏腑</span>
          <span className="kv-value accent">{health.vulnerable_organs?.join('、')}</span>
          <span className="kv-label">常见问题</span>
          <span className="kv-value">{health.common_issues}</span>
          <span className="kv-label">养生建议</span>
          <span className="kv-value" style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)' }}>{health.health_advice}</span>
        </div>
      </div>

      <div className="card">
        <div className="card-title">感情婚姻特质</div>
        <p style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-base)', color:'var(--text-secondary)', lineHeight:1.8 }}>{rels.style}</p>
        <div style={{ marginTop:'0.5rem', fontSize:'var(--text-sm)', color:'var(--text-muted)' }}>
          理想配偶五行：<span style={{ color:'var(--accent)' }}>{rels.ideal_partner_wx}</span>
        </div>
      </div>

      <div className="card">
        <div className="card-title">幸运元素</div>
        <div className="kv-grid">
          <span className="kv-label">幸运颜色</span>
          <span className="kv-value">{(lucky.colors||[]).join('、')}</span>
          <span className="kv-label">幸运方位</span>
          <span className="kv-value accent">{(lucky.directions||[]).join('、')}</span>
          <span className="kv-label">幸运数字</span>
          <span className="kv-value">{(lucky.numbers||[]).join('、')}</span>
          <span className="kv-label">旺盛季节</span>
          <span className="kv-value">{lucky.season}</span>
        </div>
      </div>
    </div>
  )
}

/* ── Fortune ── */
function FortuneResult({ data }) {
  const [view, setView] = useState('dayun')
  const Q_COLOR = { 吉:'#27ae60', 凶:'var(--red-light)', 平:'var(--text-muted)' }
  return (
    <div className="result-section">
      <div className="tab-bar">
        {[['dayun','大运'],['liunian','流年'],['liuyue','流月']].map(([v,l]) => (
          <button key={v} className={`tab ${view===v?'active':''}`} onClick={() => setView(v)}>{l}</button>
        ))}
      </div>

      {view === 'dayun' && (
        <div className="card">
          <div className="card-title">大运十年周期</div>
          <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginBottom:'0.75rem', fontFamily:'var(--font-serif)' }}>
            大运每10年一换，决定人生各阶段整体运势基调。
          </div>
          <div style={{ display:'flex', flexDirection:'column', gap:'0.5rem' }}>
            {data.dayun?.map((dy, i) => (
              <div key={i} style={{
                display:'flex', alignItems:'center', gap:'1rem',
                padding:'0.65rem 0.9rem',
                background: dy.quality==='吉' ? 'var(--accent-glow)' : dy.quality==='凶' ? 'var(--red-glow)' : 'var(--bg-raised)',
                borderRadius:'var(--radius-sm)',
                border:`1px solid ${dy.quality==='吉'?'var(--accent-dim)':dy.quality==='凶'?'var(--red-glow)':'var(--border)'}`,
              }}>
                <span style={{ fontFamily:'var(--font-display)', fontSize:'1.25rem', color:'var(--accent)', width:'44px' }}>
                  {dy.tiangan}{dy.dizhi}
                </span>
                <div style={{ flex:1 }}>
                  <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)' }}>
                    {dy.start_year}–{dy.end_year}年 · {Math.floor(dy.start_age)}岁起
                  </div>
                  <div style={{ fontSize:'var(--text-sm)', color:'var(--text-secondary)', marginTop:'0.1rem' }}>
                    {dy.dm_shishen} · {dy.quality==='吉'?'运势顺遂，宜积极进取':dy.quality==='凶'?'运势有阻，宜守成待机':'运势平稳，宜稳中求进'}
                  </div>
                </div>
                <span className={`badge ${dy.quality==='吉'?'badge-jade':dy.quality==='凶'?'badge-red':'badge-muted'}`}>{dy.quality}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {view === 'liunian' && (
        <div className="card">
          <div className="card-title">流年运势</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(110px,1fr))', gap:'0.4rem' }}>
            {data.liunian?.slice(0,40).map((ly,i) => (
              <div key={i} style={{
                padding:'0.5rem 0.4rem', textAlign:'center',
                background: ly.quality==='吉'?'var(--accent-glow)':ly.quality==='凶'?'var(--red-glow)':'var(--bg-raised)',
                borderRadius:'var(--radius-sm)',
                border:`1px solid ${ly.quality==='吉'?'var(--accent-dim)':ly.quality==='凶'?'var(--red-glow)':'var(--border)'}`,
              }}>
                <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>{ly.year}年</div>
                <div style={{ fontFamily:'var(--font-display)', color:'var(--accent)', fontSize:'1rem' }}>{ly.tiangan}{ly.dizhi}</div>
                <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>{ly.age}岁</div>
                <div style={{ fontSize:'var(--text-xs)', color: Q_COLOR[ly.quality]||'var(--text-muted)', marginTop:'2px' }}>{ly.shishen_gan}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {view === 'liuyue' && data.liuyue && (
        <div className="card">
          <div className="card-title">流月运势</div>
          {data.liuyue.map((lm,i) => (
            <div key={i} style={{
              display:'flex', alignItems:'center', gap:'0.75rem',
              padding:'0.5rem 0.75rem', borderBottom:'1px solid var(--border)',
            }}>
              <span style={{ width:'32px', color:'var(--text-muted)', fontSize:'var(--text-sm)' }}>{lm.month_num}月</span>
              <span style={{ fontFamily:'var(--font-display)', color:'var(--accent)', width:'40px' }}>{lm.tiangan}{lm.dizhi}</span>
              <span style={{ flex:1, fontSize:'var(--text-sm)', color:'var(--text-secondary)' }}>{lm.summary}</span>
              <span style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>{lm.season_status}</span>
              <span className={`badge ${lm.quality==='吉'?'badge-jade':lm.quality==='凶'?'badge-red':'badge-muted'}`}>{lm.quality}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ── Career ── */
function CareerResult({ data }) {
  const pc = data.profile_career || {}
  return (
    <div className="result-section">
      <div className="card">
        <div className="card-title">事业运势分析</div>
        <p style={{ fontFamily:'var(--font-serif)', lineHeight:1.85, marginBottom:'1rem' }}>{data.analysis}</p>
        {data.career_fields?.length > 0 && (
          <div style={{ marginBottom:'1rem' }}>
            <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginBottom:'0.4rem' }}>推荐行业</div>
            <div style={{ display:'flex', flexWrap:'wrap', gap:'0.4rem' }}>
              {data.career_fields?.map((f,i) => <span key={i} className="badge badge-gold">{f}</span>)}
            </div>
          </div>
        )}
        {data.shishen_advice?.map((a,i) => (
          <div key={i} style={{ display:'flex', gap:'0.5rem', fontSize:'var(--text-base)', color:'var(--text-secondary)', marginTop:'0.4rem' }}>
            <span style={{ color:'var(--accent)', flexShrink:0 }}>◆</span><span>{a}</span>
          </div>
        ))}
      </div>
      {pc.best_fields && (
        <div className="card">
          <div className="card-title">日主性格与职场风格</div>
          <div style={{ marginBottom:'0.75rem' }}>
            <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginBottom:'0.35rem' }}>适合行业</div>
            <div style={{ display:'flex', flexWrap:'wrap', gap:'0.4rem' }}>
              {pc.best_fields?.map((f,i) => <span key={i} className="badge badge-muted">{f}</span>)}
            </div>
          </div>
          <p style={{ fontSize:'var(--text-sm)', color:'var(--text-secondary)', fontFamily:'var(--font-serif)', lineHeight:1.7 }}>{pc.work_style}</p>
          <p style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginTop:'0.5rem' }}>财富观：{pc.wealth_approach}</p>
        </div>
      )}
      {data.personality_traits?.length > 0 && (
        <div className="card">
          <div className="card-title">核心性格优势</div>
          {data.personality_traits?.map((t,i) => (
            <div key={i} style={{ display:'flex', gap:'0.5rem', fontSize:'var(--text-base)', color:'var(--text-secondary)', marginBottom:'0.35rem' }}>
              <span style={{ color:'#27ae60', flexShrink:0 }}>✦</span><span>{t}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ── Marriage ── */
function MarriageResult({ data }) {
  return (
    <div className="result-section">
      <div className="card">
        <div className="card-title">婚姻感情分析</div>
        <div style={{ display:'flex', gap:'0.5rem', marginBottom:'0.75rem', flexWrap:'wrap' }}>
          {data.clash_present && <span className="badge badge-red">日支受冲 · 婚姻有波折</span>}
          {data.harmony_present && <span className="badge badge-jade">日支六合 · 婚缘和谐</span>}
          {data.spouse_stars?.length > 0 && <span className="badge badge-gold">配偶星 {data.spouse_stars.join('·')}</span>}
        </div>
        <div className="kv-grid">
          <span className="kv-label">婚姻宫（日支）</span>
          <span className="kv-value accent">{data.spouse_palace}</span>
          <span className="kv-label">配偶星</span>
          <span className="kv-value">{data.spouse_stars?.join('、') || '未见'}</span>
          <span className="kv-label">综合论断</span>
          <span className="kv-value" style={{ fontFamily:'var(--font-serif)', color:'var(--text-secondary)' }}>{data.quality}</span>
        </div>
      </div>
      {data.advice?.length > 0 && (
        <div className="card">
          <div className="card-title">感情建议</div>
          {data.advice?.filter(Boolean).map((a,i) => (
            <div key={i} style={{ display:'flex', gap:'0.5rem', fontSize:'var(--text-base)', color:'var(--text-secondary)', marginBottom:'0.4rem' }}>
              <span style={{ color:'var(--accent)', flexShrink:0 }}>◆</span><span>{a}</span>
            </div>
          ))}
          <div style={{ marginTop:'0.75rem', padding:'0.75rem', background:'var(--bg-raised)', borderRadius:'var(--radius-sm)',
            fontSize:'var(--text-sm)', color:'var(--text-muted)', fontFamily:'var(--font-serif)', lineHeight:1.7 }}>
            注：婚姻宫（日支）为观察配偶宫位。日支与年支、时支六合，婚姻更易和谐；若遭月支、时支六冲，则婚姻多有波折，需多包容沟通。
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Health ── */
function HealthResult({ data }) {
  const wx = data.wx_distribution || {}
  const total = Object.values(wx).reduce((a,b)=>a+b,0) || 1
  const WX_COLOR = { 木:'#27ae60', 火:'#e74c3c', 土:'#f39c12', 金:'#95a5a6', 水:'#3498db' }
  const ph = data.profile_health || {}
  return (
    <div className="result-section">
      <div className="card">
        <div className="card-title">五行健康分析</div>
        <p style={{ fontFamily:'var(--font-serif)', lineHeight:1.85, marginBottom:'1rem' }}>{data.analysis}</p>
        <div style={{ marginBottom:'1rem' }}>
          <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginBottom:'0.5rem' }}>命局五行分布</div>
          <div style={{ display:'flex', gap:'3px', height:'28px', borderRadius:'6px', overflow:'hidden' }}>
            {Object.entries(wx).map(([el,cnt]) => cnt > 0 && (
              <div key={el} title={`${el}: ${cnt}`}
                style={{ flex:cnt, background:WX_COLOR[el], display:'flex', alignItems:'center',
                  justifyContent:'center', fontSize:'var(--text-xs)', color:'#fff', fontWeight:600 }}>
                {cnt >= 2 ? el : ''}
              </div>
            ))}
          </div>
          <div style={{ display:'flex', gap:'1rem', marginTop:'0.4rem', flexWrap:'wrap' }}>
            {Object.entries(wx).map(([el,cnt]) => (
              <span key={el} style={{ fontSize:'var(--text-sm)', color:WX_COLOR[el], fontWeight:600 }}>{el}：{cnt}</span>
            ))}
          </div>
        </div>
        <div className="kv-grid">
          <span className="kv-label">日主脏腑</span>
          <span className="kv-value accent">{data.dm_organ}</span>
          <span className="kv-label">注意症状</span>
          <span className="kv-value">{data.dm_condition}</span>
          <span className="kv-label">最弱五行</span>
          <span className="kv-value" style={{ color:WX_COLOR[data.weak_element] }}>{data.weak_element}</span>
          <span className="kv-label">弱势脏腑</span>
          <span className="kv-value">{data.weak_organ}</span>
        </div>
      </div>
      <div className="card">
        <div className="card-title">日主健康细则</div>
        {ph.vulnerable_organs && (
          <div style={{ marginBottom:'0.5rem' }}>
            <span style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)' }}>重点关注：</span>
            <span style={{ color:'var(--accent)', fontWeight:600 }}>{ph.vulnerable_organs?.join('、')}</span>
          </div>
        )}
        {data.advice?.filter(Boolean).map((a,i) => (
          <div key={i} style={{ display:'flex', gap:'0.5rem', fontSize:'var(--text-base)', color:'var(--text-secondary)', marginBottom:'0.35rem' }}>
            <span style={{ color:'#27ae60', flexShrink:0 }}>◆</span><span>{a}</span>
          </div>
        ))}
        {ph.health_advice && (
          <div style={{ marginTop:'0.75rem', padding:'0.75rem', background:'var(--accent-glow)',
            border:'1px solid var(--accent-dim)', borderRadius:'var(--radius-sm)',
            fontSize:'var(--text-sm)', fontFamily:'var(--font-serif)', color:'var(--text-secondary)', lineHeight:1.7 }}>
            {ph.health_advice}
          </div>
        )}
      </div>
    </div>
  )
}

/* ── Wealth ── */
function WealthResult({ data }) {
  const LEVEL_COLOR = { '财运丰厚':'var(--accent)', '财运稳健':'#27ae60', '财来财去':'#e67e22', '财运平稳':'var(--text-muted)' }
  return (
    <div className="result-section">
      <div className="card" style={{ textAlign:'center' }}>
        <div className="card-title">财运评估</div>
        <div style={{ fontSize:'2rem', fontFamily:'var(--font-display)', color:LEVEL_COLOR[data.level]||'var(--accent)',
          margin:'0.5rem 0', textShadow:'0 0 20px currentColor' }}>
          {data.level}
        </div>
        <p style={{ fontFamily:'var(--font-serif)', color:'var(--text-secondary)', lineHeight:1.8, marginBottom:'1rem' }}>
          {data.analysis}
        </p>
        <div style={{ display:'flex', gap:'0.5rem', justifyContent:'center', flexWrap:'wrap' }}>
          {data.wealth_stems?.map((s,i) => <span key={i} className="badge badge-gold">{s}</span>)}
        </div>
      </div>
      <div className="card">
        <div className="card-title">财运建议</div>
        {data.advice?.filter(Boolean).map((a,i) => (
          <div key={i} style={{ display:'flex', gap:'0.5rem', fontSize:'var(--text-base)', color:'var(--text-secondary)', marginBottom:'0.4rem' }}>
            <span style={{ color:'var(--accent)', flexShrink:0 }}>◆</span><span>{a}</span>
          </div>
        ))}
        <div style={{ marginTop:'0.75rem', padding:'0.75rem', background:'var(--bg-raised)',
          borderRadius:'var(--radius-sm)', fontSize:'var(--text-sm)', color:'var(--text-muted)', fontFamily:'var(--font-serif)', lineHeight:1.7 }}>
          正财（正财星）主稳定薪资与本业收入；偏财（偏财星）主投资、偏业与意外之财。
          身强者更能驾驭财星，身弱则财星重时反成负担。
        </div>
      </div>
    </div>
  )
}

/* ── Compat ── */
function CompatResult({ data }) {
  const score = data.score || 0
  const color = score>=80?'var(--accent)':score>=65?'#27ae60':'var(--red-light)'
  return (
    <div className="result-section">
      <div className="card" style={{ textAlign:'center' }}>
        <div className="card-title">合婚分析</div>
        <div style={{ fontSize:'5rem', fontFamily:'var(--font-display)', color, lineHeight:1.1,
          textShadow:`0 0 30px ${color}44`, margin:'0.5rem 0' }}>{score}</div>
        <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)', marginBottom:'1rem' }}>合婚评分 / 100</div>
        <p style={{ fontFamily:'var(--font-serif)', color:'var(--text-secondary)', lineHeight:1.8 }}>{data.summary}</p>
        <div style={{ display:'flex', gap:'2rem', justifyContent:'center', marginTop:'1.5rem' }}>
          {['person_a','person_b'].map((k,i) => (
            <div key={k} style={{ textAlign:'center' }}>
              <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)' }}>{i===0?'甲方':'乙方'}</div>
              <div style={{ fontFamily:'var(--font-display)', fontSize:'1.2rem', color:'var(--accent)' }}>{data[k]?.day_master}</div>
              <div style={{ fontSize:'var(--text-sm)', color:'var(--text-muted)' }}>{data[k]?.pattern}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="card">
        <div className="card-title">合婚详解</div>
        <div style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-base)', color:'var(--text-secondary)', lineHeight:1.8 }}>
          <p>合婚以五行生克为基础。五行相生（木生火、火生土）为最佳，表明双方能互相扶持滋养；五行相同为同类，志同道合但需保持各自空间；五行相克则性格差异明显，需多磨合理解。</p>
          <p style={{ marginTop:'0.5rem' }}>此外还需参考日柱六合六冲：日支相合，夫妻宫和谐；日支相冲，婚姻多有摩擦，需双方主动化解。</p>
        </div>
      </div>
    </div>
  )
}
