# 八卦推演 Frontend

React + Vite frontend for the Chinese metaphysics platform.

## Quick start

```bash
npm install
npm run dev        # → http://localhost:5173
npm run build      # production build → dist/
```

Backend must be running at `http://localhost:8888`:
```bash
cd ../bagua_backend && uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

The API URL can be changed at runtime in **Settings → API 连接**.

## Pages

| Route | 模块 | Backend APIs |
|---|---|---|
| `/bazi` | 八字 | chart, fortune, career, marriage, health, wealth, compatibility |
| `/liuyao` | 六爻 | divine (coin/yarrow/time/manual), hexagram library |
| `/qimen` | 奇门遁甲 | layout, /now |
| `/fengshui` | 风水 | analysis |
| `/date-select` | 择日 | select |
| `/knowledge` | 知识库 | search, categories, smart-search |
| `/settings` | 设置 | — |

## Settings (persisted to localStorage)

`apiBaseUrl` · `theme` (dark/light) · `accentColor` (gold/red/jade)  
`defaultGender` · `compactMode` · `animationsEnabled`

## Stack

React 18 · Vite · React Router v6 · Zustand · Pure CSS design system
