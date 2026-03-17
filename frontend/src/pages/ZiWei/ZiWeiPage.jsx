import React, { useState } from 'react'
import { useNotifyStore } from '../../store/settingsStore'
import { useSettingsStore } from '../../store/settingsStore'
import AiInterpretPanel from '../../components/UI/AiInterpretPanel'

const HOUR_OPTIONS = [
  { label: '子时 23:00–01:00', value: 23 },
  { label: '丑时 01:00–03:00', value: 1  },
  { label: '寅时 03:00–05:00', value: 3  },
  { label: '卯时 05:00–07:00', value: 5  },
  { label: '辰时 07:00–09:00', value: 7  },
  { label: '巳时 09:00–11:00', value: 9  },
  { label: '午时 11:00–13:00', value: 11 },
  { label: '未时 13:00–15:00', value: 13 },
  { label: '申时 15:00–17:00', value: 15 },
  { label: '酉时 17:00–19:00', value: 17 },
  { label: '戌时 19:00–21:00', value: 19 },
  { label: '亥时 21:00–23:00', value: 21 },
]

// Brightness color
const BRIGHT_COLOR = { '庙': '#c8a04a', '旺': '#f39c12', '得地': '#3498db', '利': '#27ae60', '平和': '#7f8c8d', '不得地': '#e67e22', '落陷': '#e74c3c', '陷': '#e74c3c' }

// Palace display order (clockwise from top-right, traditional layout)
// Standard 12-palace layout indices for a 4×3 grid
const PALACE_LAYOUT = [
  // row 0: top (right to left)
  [11, 10, 9, 8],
  // row 1: sides
  [0, null, null, 7],
  // row 2: sides
  [1, null, null, 6],
  // row 3: bottom (left to right)
  [2, 3, 4, 5],
]

function PalaceCell({ palace, isSoul, isBody, onSelect, selected }) {
  if (!palace) {
    return (
      <div style={{
        gridColumn: 'span 2', gridRow: 'span 2',
        border: '1px solid var(--border)',
        background: 'var(--bg-subtle)',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        gap: '0.3rem',
      }}>
        <div style={{ fontSize: '0.65rem', color: 'var(--text-faint)', fontFamily: 'var(--font-serif)' }}>命盘中宫</div>
      </div>
    )
  }

  const borderColor = selected ? 'var(--accent)' : isSoul ? 'var(--jade)' : isBody ? 'var(--cyan-b, #3498db)' : 'var(--border)'
  const bgColor = selected ? 'var(--accent-bg)' : isSoul ? 'rgba(26,122,82,0.07)' : 'var(--bg-card)'

  return (
    <div
      onClick={() => onSelect(palace)}
      style={{
        border: `1.5px solid ${borderColor}`,
        background: bgColor,
        padding: '0.35rem 0.4rem',
        cursor: 'pointer',
        display: 'flex', flexDirection: 'column', gap: '3px',
        minHeight: '90px', transition: 'all 0.12s',
        position: 'relative',
      }}
    >
      {/* Palace name + stem+branch */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: isSoul ? 'var(--jade)' : 'var(--text-primary)' }}>
          {palace.name}
        </span>
        <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', fontFamily: 'var(--font-serif)' }}>
          {palace.heavenly_stem}{palace.earthly_branch}
        </span>
      </div>

      {/* Major stars */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px' }}>
        {palace.major_stars.map((s, i) => (
          <span key={i} style={{
            fontSize: '0.68rem', fontWeight: 600,
            color: BRIGHT_COLOR[s.brightness] || 'var(--accent)',
            background: 'rgba(181,54,30,0.06)',
            padding: '1px 4px', borderRadius: '3px',
          }}>
            {s.name}{s.brightness ? `(${s.brightness})` : ''}
          </span>
        ))}
      </div>

      {/* Minor stars (smaller) */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px' }}>
        {palace.minor_stars.slice(0, 4).map((s, i) => (
          <span key={i} style={{ fontSize: '0.58rem', color: 'var(--text-muted)' }}>
            {s.name}
          </span>
        ))}
      </div>

      {/* Decadal range */}
      {palace.decadal_range && palace.decadal_range.length === 2 && (
        <div style={{ fontSize: '0.58rem', color: 'var(--text-faint)', marginTop: 'auto' }}>
          大限 {palace.decadal_range[0]}–{palace.decadal_range[1]}岁
        </div>
      )}

      {/* 长生十二 */}
      {palace.changsheng12 && (
        <div style={{
          position: 'absolute', bottom: 3, right: 4,
          fontSize: '0.55rem', color: 'var(--text-faint)',
        }}>{palace.changsheng12}</div>
      )}

      {/* 命/身 badge */}
      {(isSoul || isBody) && (
        <div style={{
          position: 'absolute', top: 2, right: 3,
          fontSize: '0.55rem', fontWeight: 700,
          color: isSoul ? 'var(--jade)' : 'var(--cyan-b, #3498db)',
        }}>{isSoul ? '命' : '身'}</div>
      )}
    </div>
  )
}

export default function ZiWeiPage() {
  const { apiBaseUrl } = useSettingsStore()
  const { notify } = useNotifyStore()
  const now = new Date()

  const [form, setForm] = useState({
    year: 1990, month: 6, day: 15, hour: 7, gender: '男', name: '',
  })
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const run = async () => {
    setLoading(true)
    setSelected(null)
    try {
      const res  = await fetch(`${apiBaseUrl}/api/v1/ziwei/chart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, year: +form.year, month: +form.month, day: +form.day, hour: +form.hour }),
      })
      const json = await res.json()
      if (!json.success) throw new Error(json.message || '排盘失败')
      setResult(json.data)
      notify('紫微排盘完成', 'success')
    } catch (e) {
      notify(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const palaces = result?.palaces || []
  const meta    = result?.metadata || {}
  const soul    = result?.soul_palace
  const body    = result?.body_palace

  // Build index map for grid
  const palaceByIndex = {}
  palaces.forEach(p => { palaceByIndex[p.index] = p })

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <div className="page-title">紫微斗数</div>
          <div className="page-subtitle">十四主星 · 十二宫位 · 三方四正 · 大小限流年</div>
        </div>
      </div>

      <div className="page-body">
        <div className="page-cols">
          {/* ── LEFT ── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="card">
              <div className="card-title">出生信息</div>
              <div className="form-row-2">
                <div className="form-group"><label>年</label>
                  <input type="number" min="1800" max="2100" value={form.year} onChange={e => set('year', e.target.value)} />
                </div>
                <div className="form-group"><label>月</label>
                  <input type="number" min="1" max="12" value={form.month} onChange={e => set('month', e.target.value)} />
                </div>
              </div>
              <div className="form-row-2">
                <div className="form-group"><label>日</label>
                  <input type="number" min="1" max="31" value={form.day} onChange={e => set('day', e.target.value)} />
                </div>
                <div className="form-group"><label>性别</label>
                  <select value={form.gender} onChange={e => set('gender', e.target.value)}>
                    <option value="男">男</option>
                    <option value="女">女</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>出生时辰</label>
                <select value={form.hour} onChange={e => set('hour', +e.target.value)}>
                  {HOUR_OPTIONS.map(h => (
                    <option key={h.value} value={h.value}>{h.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>姓名（可选）</label>
                <input value={form.name} onChange={e => set('name', e.target.value)} placeholder="仅作标注" />
              </div>
            </div>

            <button className="btn btn-primary btn-full btn-lg" onClick={run} disabled={loading}>
              {loading ? '起盘中…' : '起紫微斗数盘 ▶'}
            </button>

            {/* Metadata card */}
            {meta.five_elements && (
              <div className="card card-glow">
                <div className="card-title">命盘基本信息</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.35rem 0.75rem', fontSize: 'var(--text-sm)' }}>
                  {[
                    ['四柱', meta.chinese_date],
                    ['五行局', meta.five_elements],
                    ['农历', meta.lunar_date],
                    ['生肖', meta.zodiac],
                    ['时辰', meta.birth_hour_name + ' ' + meta.birth_hour_range],
                    ['星座', meta.sign],
                  ].map(([k, v]) => (
                    <React.Fragment key={k}>
                      <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                      <span style={{ fontFamily: 'var(--font-serif)' }}>{v}</span>
                    </React.Fragment>
                  ))}
                </div>
                {soul && (
                  <div style={{ marginTop: '0.6rem', borderTop: '1px solid var(--border)', paddingTop: '0.5rem' }}>
                    <div style={{ display: 'flex', gap: '1.5rem', fontSize: 'var(--text-sm)' }}>
                      <div>
                        <span style={{ color: 'var(--text-muted)' }}>命宫 </span>
                        <span style={{ color: 'var(--jade)', fontWeight: 700 }}>
                          {soul.stem_branch} {soul.major_stars.join('·') || '无主星'}
                        </span>
                      </div>
                      <div>
                        <span style={{ color: 'var(--text-muted)' }}>身宫 </span>
                        <span style={{ color: 'var(--cyan-b, #3498db)', fontWeight: 700 }}>
                          {body?.name} {body?.major_stars?.join('·') || ''}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Three-direction info */}
            {result?.sanjiao_sizheng?.length > 0 && (
              <div className="card">
                <div className="card-title">命宫三方四正</div>
                {result.sanjiao_sizheng.map((p, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between',
                    padding: '0.3rem 0', borderBottom: '1px solid var(--border)',
                    fontSize: 'var(--text-sm)' }}>
                    <span style={{ color: 'var(--text-muted)' }}>{p.name}</span>
                    <span style={{ color: 'var(--accent)', fontFamily: 'var(--font-serif)' }}>
                      {p.major_stars.join(' ') || '无主星'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ── RIGHT ── */}
          <div>
            {loading && (
              <div className="loading"><div className="spinner"/><p>排盘中…</p></div>
            )}

            {!loading && !result && (
              <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.15 }}>☆</div>
                <p style={{ fontFamily: 'var(--font-serif)', color: 'var(--text-muted)', lineHeight: 1.9 }}>
                  紫微斗数，以北斗紫微星为主，<br/>统御十四主星布十二宫，<br/>论命运起伏，知人生格局
                </p>
              </div>
            )}

            {!loading && result && (
              <>
                {/* ── 12-palace grid ── */}
                <div className="card" style={{ padding: '0.5rem' }}>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gridTemplateRows: 'repeat(4, auto)',
                    gap: '2px',
                  }}>
                    {PALACE_LAYOUT.map((row, ri) =>
                      row.map((pidx, ci) => {
                        if (pidx === null) {
                          // Center cells — show metadata
                          if (ri === 1 && ci === 1) {
                            return (
                              <div key={`c${ri}${ci}`} style={{
                                gridColumn: 'span 2', gridRow: 'span 2',
                                border: '1px solid var(--border)',
                                background: 'var(--bg-subtle)',
                                display: 'flex', flexDirection: 'column',
                                alignItems: 'center', justifyContent: 'center',
                                gap: '0.3rem', padding: '0.5rem',
                              }}>
                                <div style={{ fontSize: '1.1rem', color: 'var(--accent)', fontFamily: 'var(--font-display)' }}>
                                  {meta.five_elements}
                                </div>
                                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textAlign: 'center', fontFamily: 'var(--font-serif)' }}>
                                  {meta.chinese_date}
                                </div>
                                <div style={{ fontSize: '0.62rem', color: 'var(--text-faint)' }}>
                                  {meta.zodiac} · {meta.gender}
                                </div>
                              </div>
                            )
                          }
                          return null
                        }
                        const p = palaceByIndex[pidx]
                        if (!p) return <div key={`e${ri}${ci}`} style={{ minHeight: 80, border: '1px solid var(--border)' }} />
                        return (
                          <PalaceCell
                            key={p.index}
                            palace={p}
                            isSoul={p.is_soul}
                            isBody={p.is_body}
                            selected={selected?.index === p.index}
                            onSelect={setSelected}
                          />
                        )
                      })
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem',
                    fontSize: 'var(--text-xs)', color: 'var(--text-faint)' }}>
                    <span><span style={{ color: 'var(--jade)', fontWeight: 700 }}>命</span> 命宫</span>
                    <span><span style={{ color: 'var(--cyan-b, #3498db)', fontWeight: 700 }}>身</span> 身宫</span>
                    <span>点击宫位查看详情</span>
                  </div>
                </div>

                {/* ── Selected palace detail ── */}
                {selected && (
                  <div className="card card-glow" style={{ marginTop: '0.85rem' }}>
                    <div className="card-title">
                      {selected.name}（{selected.heavenly_stem}{selected.earthly_branch}）
                      {selected.is_soul && <span style={{ color: 'var(--jade)', marginLeft: '0.4rem', fontSize: 'var(--text-xs)' }}>命宫</span>}
                      {selected.is_body && <span style={{ color: 'var(--cyan-b, #3498db)', marginLeft: '0.4rem', fontSize: 'var(--text-xs)' }}>身宫</span>}
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '0.65rem' }}>
                      <div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginBottom: '3px' }}>主星</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                          {selected.major_stars.length > 0
                            ? selected.major_stars.map((s, i) => (
                                <span key={i} style={{
                                  padding: '2px 8px', borderRadius: 4,
                                  background: 'var(--accent-bg)',
                                  color: BRIGHT_COLOR[s.brightness] || 'var(--accent)',
                                  fontSize: 'var(--text-sm)', fontWeight: 700,
                                  border: '1px solid var(--accent-dim)',
                                }}>
                                  {s.name} {s.brightness || ''}
                                </span>
                              ))
                            : <span style={{ color: 'var(--text-faint)', fontSize: 'var(--text-sm)' }}>空宫</span>
                          }
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginBottom: '3px' }}>辅星</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px' }}>
                          {selected.minor_stars.map((s, i) => (
                            <span key={i} style={{
                              fontSize: '0.68rem', color: 'var(--text-secondary)',
                              background: 'var(--bg-subtle)', padding: '1px 5px',
                              borderRadius: 3,
                            }}>{s.name}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '1.5rem', fontSize: 'var(--text-sm)',
                      color: 'var(--text-secondary)', fontFamily: 'var(--font-serif)' }}>
                      {selected.decadal_range?.length === 2 && (
                        <span>大限 {selected.decadal_range[0]}–{selected.decadal_range[1]}岁</span>
                      )}
                      {selected.changsheng12 && <span>长生十二：{selected.changsheng12}</span>}
                      {selected.boshi12 && <span>博士十二：{selected.boshi12}</span>}
                    </div>
                  </div>
                )}

                {/* ── AI Interpret ── */}
                <div style={{ marginTop: '1rem' }}>
                  <AiInterpretPanel
                    module="ziwei"
                    data={result}
                    extraContext={`${form.year}年${form.month}月${form.day}日 ${HOUR_OPTIONS.find(h=>h.value===+form.hour)?.label||''} ${form.gender}`}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
