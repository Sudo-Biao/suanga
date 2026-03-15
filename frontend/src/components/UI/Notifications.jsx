import React from 'react'
import { useNotifyStore } from '../../store/settingsStore'

export default function Notifications() {
  const { notifications } = useNotifyStore()
  return (
    <div className="notifications">
      {notifications.map(n => (
        <div key={n.id} className={`toast ${n.type}`}>{n.message}</div>
      ))}
    </div>
  )
}
