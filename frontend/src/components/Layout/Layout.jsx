import React, { useState, useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { systemApi } from '../../api/client'
import { useSettingsStore } from '../../store/settingsStore'
import './Layout.css'

const NAV = [
  { path: '/agent',      icon: '🔮', label: 'AI顾问',   en: 'Agent' },
  { path: '/bazi',       icon: '☰',  label: '八字',     en: 'BaZi' },
  { path: '/liuyao',     icon: '☷',  label: '六爻',     en: 'LiuYao' },
  { path: '/qimen',      icon: '✦',  label: '奇门',     en: 'QiMen' },
  { path: '/fengshui',   icon: '◎',  label: '风水',     en: 'FengShui' },
  { path: '/date-select',icon: '◈',  label: '择日',     en: 'DateSelect' },
  { path: '/ziwei',      icon: '☆',  label: '紫微',     en: 'ZiWei' },
  { path: '/knowledge',  icon: '⊞',  label: '知识库',   en: 'Knowledge' },
]

export default function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [status, setStatus]         = useState('checking')
  const { apiBaseUrl }              = useSettingsStore()
  const location                    = useLocation()

  useEffect(() => {
    let mounted = true
    const check = async () => {
      try {
        const r = await systemApi.health()
        if (mounted) setStatus(r.status === 'ok' ? 'online' : 'offline')
      } catch { if (mounted) setStatus('offline') }
    }
    check()
    const id = setInterval(check, 30_000)
    return () => { mounted = false; clearInterval(id) }
  }, [apiBaseUrl])

  return (
    <div className="app-shell">
      {/* ── Top Navigation Bar ── */}
      <header className="topnav">
        {/* Left: Brand */}
        <div className="topnav-brand">
          <span className="brand-glyph">☯</span>
          <div className="brand-text">
            <span className="brand-name">八卦推演</span>
            <span className="brand-tagline">Chinese Metaphysics</span>
          </div>
        </div>

        {/* Centre: Nav links */}
        <nav className="topnav-links">
          {NAV.map(n => (
            <NavLink
              key={n.path}
              to={n.path}
              className={({ isActive }) => `tnav-item ${isActive ? 'active' : ''}`}
            >
              <span className="tnav-icon">{n.icon}</span>
              <span className="tnav-label">{n.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Right: Status + Settings */}
        <div className="topnav-right">
          <div className="api-status">
            <span className={`status-dot ${status}`} />
            <span className="status-text">
              {status === 'online' ? 'API 在线'
                : status === 'offline' ? 'API 离线'
                : '连接中'}
            </span>
          </div>
          <NavLink
            to="/settings"
            className={({ isActive }) => `settings-btn ${isActive ? 'active' : ''}`}
          >
            <span>⚙</span>
            <span>设置</span>
          </NavLink>
        </div>

        {/* Mobile hamburger */}
        <button className="mobile-toggle" onClick={() => setMobileOpen(o => !o)}>
          {mobileOpen ? '✕' : '☰'}
        </button>
      </header>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="mobile-drawer" onClick={() => setMobileOpen(false)}>
          <nav className="mobile-nav" onClick={e => e.stopPropagation()}>
            {NAV.map(n => (
              <NavLink
                key={n.path}
                to={n.path}
                className={({ isActive }) => `mnav-item ${isActive ? 'active' : ''}`}
                onClick={() => setMobileOpen(false)}
              >
                <span>{n.icon}</span>
                <span>{n.label}</span>
                <span className="mnav-en">{n.en}</span>
              </NavLink>
            ))}
            <NavLink to="/settings" className="mnav-item" onClick={() => setMobileOpen(false)}>
              <span>⚙</span><span>设置</span>
            </NavLink>
          </nav>
        </div>
      )}

      {/* ── Main content ── */}
      <main className="main-area">
        {children}
      </main>
    </div>
  )
}
