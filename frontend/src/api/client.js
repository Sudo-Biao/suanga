/**
 * api/client.js
 * Centralised fetch wrapper for all backend calls.
 * Base URL is read from the settings store.
 */
import { useSettingsStore } from '../store/settingsStore';

async function request(method, path, body = null) {
  const { apiBaseUrl } = useSettingsStore.getState();
  const url = `${apiBaseUrl}${path}`;

  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const data = await res.json();

  if (!res.ok || data.success === false) {
    throw new Error(data.detail || data.message || `HTTP ${res.status}`);
  }
  return data.data;
}

const get  = (path)        => request('GET',  path);
const post = (path, body)  => request('POST', path, body);

// ── BaZi ──────────────────────────────────────────────────
export const baziApi = {
  chart:         (birth)  => post('/api/v1/bazi/chart', birth),
  fortune:       (req)    => post('/api/v1/bazi/fortune', req),
  career:        (birth)  => post('/api/v1/bazi/career', birth),
  marriage:      (birth)  => post('/api/v1/bazi/marriage', birth),
  health:        (birth)  => post('/api/v1/bazi/health', birth),
  wealth:        (birth)  => post('/api/v1/bazi/wealth', birth),
  compatibility: (req)    => post('/api/v1/bazi/compatibility', req),
};

// ── LiuYao ────────────────────────────────────────────────
export const liuyaoApi = {
  divine:     (req)    => post('/api/v1/liuyao/divine', req),
  hexagrams:  ()       => get('/api/v1/liuyao/hexagrams'),
  hexagram:   (num)    => get(`/api/v1/liuyao/hexagram/${num}`),
};

// ── QiMen ─────────────────────────────────────────────────
export const qimenApi = {
  layout: (req) => post('/api/v1/qimen/layout', req),
  now:    ()    => get('/api/v1/qimen/now'),
};

// ── FengShui ──────────────────────────────────────────────
export const fengshuiApi = {
  analysis: (req) => post('/api/v1/fengshui/analysis', req),
};

// ── ZiWei ────────────────────────────────────────────
export const ziweiApi = {
  chart: (req) => post('/api/v1/ziwei/chart', req),
  hours: ()    => get('/api/v1/ziwei/hours'),
};

// ── DateSelection ─────────────────────────────────────────
export const dateApi = {
  select: (req) => post('/api/v1/date-selection/select', req),
};

// ── Knowledge ─────────────────────────────────────────────
export const knowledgeApi = {
  search:     (keyword, category) =>
    get(`/api/v1/knowledge/search?keyword=${encodeURIComponent(keyword)}${category ? `&category=${encodeURIComponent(category)}` : ''}`),
  categories: () => get('/api/v1/knowledge/categories'),
  smartSearch: (keyword) => post('/api/v1/knowledge/smart-search', { keyword }),
};

// ── Health ────────────────────────────────────────────────
export const systemApi = {
  // Health returns { success, data: { status, version, modules, port } }
  // Use raw fetch so we don't go through the ApiResponse unwrapper
  health: async () => {
    const { apiBaseUrl } = useSettingsStore.getState();
    try {
      const res = await fetch(`${apiBaseUrl}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) return { status: 'offline' };
      const json = await res.json();
      // Handle both old format { status:'ok' } and new { success:true, data:{ status:'ok' } }
      if (json.data?.status === 'ok') return json.data;
      if (json.status === 'ok') return json;
      return { status: 'offline' };
    } catch {
      return { status: 'offline' };
    }
  },
};

// ── Classical Knowledge ────────────────────────────────────
export const classicalApi = {
  shishen:      ()     => get('/api/v1/knowledge/classical/shishen'),
  shishenDetail:(name) => get(`/api/v1/knowledge/classical/shishen/${name}`),
  pillars:      ()     => get('/api/v1/knowledge/classical/pillars'),
  dizhi:        ()     => get('/api/v1/knowledge/classical/dizhi'),
  liuyaoTopics: ()     => get('/api/v1/knowledge/classical/liuyao-topics'),
  liuyaoRules:  ()     => get('/api/v1/knowledge/classical/liuyao-rules'),
  qimenMatrix:  ()     => get('/api/v1/knowledge/classical/qimen-matrix'),
  formulas:     ()     => get('/api/v1/knowledge/classical/formulas'),
  mountains:    ()     => get('/api/v1/knowledge/classical/24mountains'),
};
