import React from 'react'

export default function PillarCard({ pillar, highlight }) {
  if (!pillar) return null
  const { label, tiangan, dizhi, nayin, shishen_gan, wuxing_gan, wuxing_zhi } = pillar

  return (
    <div className="gz-pill" style={highlight ? { borderColor: 'var(--accent)', boxShadow: 'var(--shadow-glow)' } : {}}>
      <span className="gz-label">{label}</span>
      <span className="gz-gan">{tiangan}</span>
      <span className="gz-zhi">{dizhi}</span>
      {shishen_gan && <span className="gz-nayin">{shishen_gan}</span>}
      {nayin && <span className="gz-nayin" style={{ color: 'var(--text-muted)', fontSize: '0.65rem' }}>{nayin}</span>}
    </div>
  )
}
