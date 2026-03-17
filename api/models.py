"""
api/models.py
=============
Proxy: fetch official model lists from any LLM provider.

Known providers have pre-configured endpoints and fallback lists.
Custom providers (GLM, Qwen, Yi, Baichuan, etc.) are supported via
X-LLM-Base-Url — we call {base_url}/models with Bearer auth.

All providers that use OpenAI-compatible APIs work automatically.
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/models", tags=["模型列表"])

# ─────────────────────────────────────────────────────────────
# Known provider configurations
# ─────────────────────────────────────────────────────────────

PROVIDER_CONFIG: Dict[str, Dict[str, Any]] = {
    "anthropic": {
        "url":          "https://api.anthropic.com/v1/models",
        "auth_header":  "x-api-key",
        "auth_prefix":  "",
        "extra_headers":{"anthropic-version": "2023-06-01"},
        "data_path":    "data",
        "id_field":     "id",
        "filter_prefix":["claude-"],
        "filter_exclude":[],
    },
    "openai": {
        "url":          "https://api.openai.com/v1/models",
        "auth_header":  "Authorization",
        "auth_prefix":  "Bearer ",
        "extra_headers":{},
        "data_path":    "data",
        "id_field":     "id",
        "filter_prefix":["gpt-", "o1", "o3", "o4"],
        "filter_exclude":["instruct","realtime","audio","tts","whisper",
                          "dall-e","embedding","babbage","davinci","moderation"],
    },
    "deepseek": {
        "url":          "https://api.deepseek.com/models",
        "auth_header":  "Authorization",
        "auth_prefix":  "Bearer ",
        "extra_headers":{},
        "data_path":    "data",
        "id_field":     "id",
        "filter_prefix":["deepseek-"],
        "filter_exclude":[],
    },
    "moonshot": {
        "url":          "https://api.moonshot.cn/v1/models",
        "auth_header":  "Authorization",
        "auth_prefix":  "Bearer ",
        "extra_headers":{},
        "data_path":    "data",
        "id_field":     "id",
        "filter_prefix":["moonshot-"],
        "filter_exclude":[],
    },
    "gemini": {
        "url":          "https://generativelanguage.googleapis.com/v1beta/models",
        "auth_header":  "x-goog-api-key",
        "auth_prefix":  "",
        "extra_headers":{},
        "data_path":    "models",
        "id_field":     "name",           # returns "models/gemini-1.5-pro"
        "filter_prefix":["models/gemini-"],
        "filter_exclude":["embedding","aqa","text-","bison"],
    },
}

# ─────────────────────────────────────────────────────────────
# Fallback / preset model lists (shown before live fetch)
# ─────────────────────────────────────────────────────────────

FALLBACK_MODELS: Dict[str, List[str]] = {
    "anthropic": [
        "claude-opus-4-6",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
        "claude-opus-4-5",
        "claude-sonnet-4-5",
        "claude-haiku-4-5",
    ],
    "openai": [
        "o3", "o4-mini",
        "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
        "gpt-4o", "gpt-4o-mini",
        "gpt-4-turbo",
    ],
    "deepseek": [
        "deepseek-chat",
        "deepseek-reasoner",
    ],
    "moonshot": [
        "moonshot-v1-8k",
        "moonshot-v1-32k",
        "moonshot-v1-128k",
        "moonshot-v1-auto",
    ],
    "gemini": [
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ],
    # Well-known custom providers — pre-filled for convenience
    "glm": [
        "glm-4-plus",
        "glm-4-air",
        "glm-4-flash",
        "glm-4v-plus",
        "glm-zero-preview",
    ],
    "qwen": [
        "qwen-max",
        "qwen-plus",
        "qwen-turbo",
        "qwen-long",
        "qwen2.5-72b-instruct",
        "qwq-32b",
    ],
    "yi": [
        "yi-lightning",
        "yi-large",
        "yi-medium",
        "yi-spark",
    ],
    "baichuan": [
        "Baichuan4",
        "Baichuan3-Turbo",
        "Baichuan2-Turbo",
    ],
    "minimax": [
        "abab6.5s-chat",
        "abab6.5-chat",
        "abab5.5-chat",
    ],
    "spark": [
        "lite",
        "generalv3",
        "pro-128k",
        "max-32k",
        "4.0Ultra",
    ],
    "doubao": [
        "doubao-pro-32k",
        "doubao-pro-4k",
        "doubao-lite-32k",
        "doubao-lite-4k",
    ],
    "hunyuan": [
        "hunyuan-turbos",
        "hunyuan-pro",
        "hunyuan-standard",
        "hunyuan-lite",
    ],
    "ollama": [
        "llama3.3:latest",
        "qwen2.5:7b",
        "deepseek-r1:7b",
        "mistral:latest",
        "gemma2:9b",
    ],
}

# ─────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────

def _matches_filter(model_id: str, cfg: Dict[str, Any]) -> bool:
    prefixes = cfg.get("filter_prefix", [])
    excludes = cfg.get("filter_exclude", [])
    if prefixes and not any(model_id.startswith(p) for p in prefixes):
        return False
    if excludes:
        lo = model_id.lower()
        if any(ex in lo for ex in excludes):
            return False
    return True


def _extract_id(item: Any, id_field: str) -> str:
    raw = item.get(id_field, "") if isinstance(item, dict) else str(item)
    # Gemini returns "models/gemini-1.5-pro" — strip prefix
    if raw.startswith("models/"):
        raw = raw[len("models/"):]
    return raw


async def _fetch_known(provider: str, api_key: str, custom_base: str) -> List[str]:
    """Fetch model list from a known provider's official endpoint."""
    cfg = PROVIDER_CONFIG[provider]

    headers: Dict[str, str] = {"Content-Type": "application/json"}
    headers.update(cfg.get("extra_headers", {}))

    # Gemini uses query-param auth
    if provider == "gemini":
        base = (custom_base or cfg["url"].rsplit("/models", 1)[0])
        url  = f"{base}/v1beta/models?key={api_key}"
    else:
        prefix = cfg.get("auth_prefix", "")
        headers[cfg["auth_header"]] = f"{prefix}{api_key}"
        if custom_base:
            from urllib.parse import urlparse
            path = urlparse(cfg["url"]).path
            url  = custom_base + path
        else:
            url = cfg["url"]

    async with httpx.AsyncClient(timeout=12.0) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code == 401:
        raise HTTPException(401, "API Key 无效或已过期")
    if resp.status_code == 403:
        raise HTTPException(403, "API Key 权限不足")
    if not resp.is_success:
        raise HTTPException(resp.status_code,
            f"{provider} API 返回 {resp.status_code}: {resp.text[:200]}")

    raw   = resp.json()
    items = raw.get(cfg.get("data_path", "data"), [])
    if not isinstance(items, list):
        items = []

    models = []
    for item in items:
        mid = _extract_id(item, cfg.get("id_field", "id"))
        if mid and _matches_filter(mid, cfg):
            models.append(mid)

    models.sort(reverse=True)
    return models


async def _fetch_custom(base_url: str, api_key: str) -> List[str]:
    """
    Fetch model list from any OpenAI-compatible /models endpoint.
    Used for custom providers: GLM, Qwen, Yi, Baichuan, Ollama, etc.
    """
    # Try both /models and /v1/models
    candidates = []
    for suffix in ["/models", "/v1/models"]:
        if not base_url.endswith(suffix):
            candidates.append(base_url.rstrip("/") + suffix)
    if not candidates:
        candidates = [base_url]

    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    last_err = None
    async with httpx.AsyncClient(timeout=12.0) as client:
        for url in candidates:
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 401:
                    raise HTTPException(401, "API Key 无效或已过期")
                if not resp.is_success:
                    last_err = f"HTTP {resp.status_code}"
                    continue

                raw   = resp.json()
                # OpenAI-compatible: { "data": [ { "id": "..." } ] }
                # Some providers: { "models": [...] } or bare list
                items = (raw.get("data")
                         or raw.get("models")
                         or raw.get("result")
                         or (raw if isinstance(raw, list) else []))

                models: List[str] = []
                for item in items:
                    if isinstance(item, dict):
                        mid = item.get("id") or item.get("name") or item.get("model_name", "")
                        if mid.startswith("models/"):
                            mid = mid[len("models/"):]
                    else:
                        mid = str(item)
                    if mid:
                        models.append(mid)

                if models:
                    models.sort(reverse=True)
                    return models

            except HTTPException:
                raise
            except Exception as e:
                last_err = str(e)
                continue

    raise Exception(last_err or "无法获取模型列表")


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────

@router.get("", summary="获取模型列表（内置供应商 + 任意自定义供应商）")
async def list_models(
    provider: str = Query(...,
        description="供应商 id。内置: anthropic|openai|deepseek|moonshot|gemini。"
                    "自定义: 任意名称（需同时传 X-LLM-Base-Url）"),
    x_llm_key: str = Header("", alias="X-LLM-Key"),
    x_llm_base_url: str = Header("", alias="X-LLM-Base-Url",
        description="自定义供应商必填；内置供应商可留空或填代理地址"),
):
    """
    Unified model-list proxy.
    - Known providers: calls official /models endpoint.
    - Custom providers: calls {base_url}/models or {base_url}/v1/models.
    - No API key: returns the preset fallback list immediately.
    - Network error / timeout: returns preset fallback gracefully.
    """
    provider   = provider.lower().strip()
    api_key    = x_llm_key.strip()
    custom_base = x_llm_base_url.strip().rstrip("/")
    is_known   = provider in PROVIDER_CONFIG

    # Always have a fallback to return
    fallback = FALLBACK_MODELS.get(provider, [])

    if not api_key:
        return {
            "success": True,
            "data": {
                "models":  fallback,
                "source":  "fallback",
                "message": "未提供 API Key，返回预置列表",
            },
        }

    try:
        if is_known:
            models = await _fetch_known(provider, api_key, custom_base)
        elif custom_base:
            models = await _fetch_custom(custom_base, api_key)
        else:
            # Unknown provider, no base URL → return fallback
            return {
                "success": True,
                "data": {
                    "models":  fallback,
                    "source":  "fallback",
                    "message": "自定义供应商需填写 Base URL 才能获取模型列表",
                },
            }

        if not models:
            return {
                "success": True,
                "data": {
                    "models":  fallback,
                    "source":  "fallback",
                    "message": "供应商未返回有效模型，返回预置列表",
                },
            }

        return {
            "success": True,
            "data": {
                "models":  models,
                "source":  "live",
                "message": f"已从 {provider} 获取 {len(models)} 个模型",
            },
        }

    except HTTPException:
        raise
    except httpx.TimeoutException:
        return {
            "success": True,
            "data": {
                "models":  fallback,
                "source":  "fallback",
                "message": "请求超时，返回预置列表",
            },
        }
    except Exception as e:
        return {
            "success": True,
            "data": {
                "models":  fallback,
                "source":  "fallback",
                "message": f"获取失败（{str(e)[:80]}），返回预置列表",
            },
        }


@router.get("/fallback", summary="获取预置模型列表（无需 API Key）")
async def list_fallback(
    provider: Optional[str] = Query(None, description="不传则返回所有供应商"),
):
    """Return preset model lists. No API key needed. Includes custom provider presets."""
    if provider:
        p = provider.lower().strip()
        models = FALLBACK_MODELS.get(p, [])
        return {
            "success": True,
            "data": {p: models, "source": "fallback"},
        }
    return {
        "success": True,
        "data": {"providers": FALLBACK_MODELS, "source": "fallback"},
    }


@router.get("/providers", summary="获取所有内置供应商信息")
async def list_providers():
    """Return metadata for all built-in providers."""
    built_in = {
        "anthropic": {"name": "Anthropic Claude", "hint": "console.anthropic.com",
                      "placeholder": "sk-ant-api03-…", "style": "anthropic"},
        "openai":    {"name": "OpenAI",            "hint": "platform.openai.com",
                      "placeholder": "sk-…",         "style": "openai"},
        "deepseek":  {"name": "DeepSeek",          "hint": "platform.deepseek.com",
                      "placeholder": "sk-…",         "style": "openai"},
        "moonshot":  {"name": "Moonshot Kimi",     "hint": "platform.moonshot.cn",
                      "placeholder": "sk-…",         "style": "openai"},
        "gemini":    {"name": "Google Gemini",     "hint": "aistudio.google.com",
                      "placeholder": "AIza…",        "style": "gemini"},
    }
    common_custom = {
        "glm":      {"name": "智谱 GLM",    "hint": "open.bigmodel.cn",
                     "base_url": "https://open.bigmodel.cn/api/paas/v4",
                     "placeholder": "sk-…", "style": "openai"},
        "qwen":     {"name": "阿里 Qwen",   "hint": "dashscope.aliyuncs.com",
                     "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                     "placeholder": "sk-…", "style": "openai"},
        "yi":       {"name": "零一万物 Yi", "hint": "platform.lingyiwanwu.com",
                     "base_url": "https://api.lingyiwanwu.com/v1",
                     "placeholder": "sk-…", "style": "openai"},
        "baichuan": {"name": "百川 Baichuan","hint": "platform.baichuan-ai.com",
                     "base_url": "https://api.baichuan-ai.com/v1",
                     "placeholder": "sk-…", "style": "openai"},
        "minimax":  {"name": "MiniMax",     "hint": "minimaxi.com",
                     "base_url": "https://api.minimaxi.com/v1",
                     "placeholder": "sk-…", "style": "openai"},
        "doubao":   {"name": "字节 豆包",   "hint": "console.volcengine.com",
                     "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                     "placeholder": "sk-…", "style": "openai"},
        "hunyuan":  {"name": "腾讯 混元",   "hint": "cloud.tencent.com",
                     "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
                     "placeholder": "sk-…", "style": "openai"},
        "spark":    {"name": "讯飞 星火",   "hint": "xinghuo.xfyun.cn",
                     "base_url": "https://spark-api-open.xf-yun.com/v1",
                     "placeholder": "sk-…", "style": "openai"},
        "ollama":   {"name": "Ollama (本地)","hint": "localhost:11434",
                     "base_url": "http://localhost:11434/v1",
                     "placeholder": "(无需 Key)",  "style": "openai"},
    }
    return {
        "success": True,
        "data": {
            "built_in": built_in,
            "common_custom": common_custom,
        },
    }
