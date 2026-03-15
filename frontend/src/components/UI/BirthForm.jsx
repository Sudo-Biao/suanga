import React from 'react'

export default function BirthForm({ values, onChange, showGender = true, title = '出生信息' }) {
  const set = (k, v) => onChange({ ...values, [k]: Number(v) || v })

  return (
    <div className="card">
      <div className="card-title">{title}</div>

      <div className="form-row" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
        <div className="form-group">
          <label>年 Year</label>
          <input type="number" min="1900" max="2100" value={values.year}
            onChange={e => set('year', e.target.value)} />
        </div>
        <div className="form-group">
          <label>月 Month</label>
          <select value={values.month} onChange={e => set('month', e.target.value)}>
            {Array.from({ length: 12 }, (_, i) => (
              <option key={i+1} value={i+1}>{i+1} 月</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>日 Day</label>
          <input type="number" min="1" max="31" value={values.day}
            onChange={e => set('day', e.target.value)} />
        </div>
      </div>

      <div className="form-row" style={{ gridTemplateColumns: '1fr 1fr', marginTop: '0.75rem' }}>
        <div className="form-group">
          <label>时 Hour (0–23)</label>
          <input type="number" min="0" max="23" value={values.hour}
            onChange={e => set('hour', e.target.value)} />
        </div>
        <div className="form-group">
          <label>分 Minute</label>
          <input type="number" min="0" max="59" value={values.minute || 0}
            onChange={e => set('minute', e.target.value)} />
        </div>
      </div>

      {showGender && (
        <div className="form-group" style={{ marginTop: '0.75rem' }}>
          <label>性别 Gender</label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {[['male', '男 Male'], ['female', '女 Female']].map(([v, l]) => (
              <button key={v} className={`btn ${values.gender === v ? 'btn-primary' : ''}`}
                style={{ flex: 1 }}
                onClick={() => onChange({ ...values, gender: v })}>
                {l}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
