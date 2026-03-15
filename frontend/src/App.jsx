import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useSettingsStore } from './store/settingsStore'
import Layout from './components/Layout/Layout'
import Notifications from './components/UI/Notifications'

import BaziPage       from './pages/Bazi/BaziPage'
import LiuYaoPage     from './pages/LiuYao/LiuYaoPage'
import QiMenPage      from './pages/QiMen/QiMenPage'
import FengShuiPage   from './pages/FengShui/FengShuiPage'
import DateSelectPage from './pages/DateSelection/DateSelectPage'
import KnowledgePage  from './pages/Knowledge/KnowledgePage'
import AgentPage      from './pages/Agent/AgentPage'
import SettingsPage   from './pages/Settings/SettingsPage'

export default function App() {
  const { theme, accentColor } = useSettingsStore()

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.setAttribute('data-accent', accentColor)
  }, [theme, accentColor])

  return (
    <>
      <Notifications />
      <Layout>
        <Routes>
          <Route path="/"              element={<Navigate to="/agent" replace />} />
          <Route path="/agent"         element={<AgentPage />} />
          <Route path="/bazi/*"        element={<BaziPage />} />
          <Route path="/liuyao"        element={<LiuYaoPage />} />
          <Route path="/qimen"         element={<QiMenPage />} />
          <Route path="/fengshui"      element={<FengShuiPage />} />
          <Route path="/date-select"   element={<DateSelectPage />} />
          <Route path="/knowledge"     element={<KnowledgePage />} />
          <Route path="/settings"      element={<SettingsPage />} />
        </Routes>
      </Layout>
    </>
  )
}
