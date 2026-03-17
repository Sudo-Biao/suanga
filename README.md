<div align="center">

# ☯ 八卦推演系统
# BaGua Divination System

**传统中国命理学 × 多模型 AI 的全栈融合平台**  
**A Full-Stack Platform Where Traditional Chinese Metaphysics Meets Multi-LLM AI**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?style=flat-square&logo=node.js&logoColor=white)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React_19-Vite-61DAFB?style=flat-square&logo=react&logoColor=black)](https://vitejs.dev/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Multi-LLM](https://img.shields.io/badge/LLM-13%2B_Providers-7C3AED?style=flat-square)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

<br/>

> 以《穷通宝鉴》《滴天髓》《增删卜易》《奇门遁甲统宗》等经典古籍为知识底座，  
> 结合 BM25 RAG 检索引擎与 13+ 大语言模型流式解读，构建有深度的命理推演平台。
>
> *Grounded in classical texts such as* Qiong Tong Bao Jian*,* Di Tian Sui*,* Zeng Shan Bu Yi*, and* Qi Men Dun Jia Tong Zong*, this platform combines a BM25 RAG retrieval engine with 13+ LLM providers for streaming interpretation, delivering authentic Chinese metaphysics analysis.*

</div>

---

## 目录 · Table of Contents

1. [项目简介 · Introduction](#1-项目简介--introduction)
2. [功能亮点 · Key Features](#2-功能亮点--key-features)
3. [系统架构 · Architecture](#3-系统架构--architecture)
4. [命理模块详解 · Module Deep Dive](#4-命理模块详解--module-deep-dive)
5. [快速开始 · Quick Start](#5-快速开始--quick-start)
6. [配置说明 · Configuration](#6-配置说明--configuration)
7. [依赖说明 · Dependencies](#7-依赖说明--dependencies)
8. [API 参考 · API Reference](#8-api-参考--api-reference)
9. [项目结构 · Project Structure](#9-项目结构--project-structure)
10. [开发指南 · Development Guide](#10-开发指南--development-guide)
11. [常见问题 · Troubleshooting](#11-常见问题--troubleshooting)
12. [路线图 · Roadmap](#12-路线图--roadmap)
13. [贡献指南 · Contributing](#13-贡献指南--contributing)
14. [许可证 · License](#14-许可证--license)

---

## 1. 项目简介 · Introduction

### 中文

**八卦推演系统**是一套将传统东方命理学与现代软件工程深度融合的开源全栈应用。项目以**纯 Python 计算引擎**为核心，严格依照古籍推算逻辑实现八字四柱、六爻占卜、紫微斗数、奇门遁甲、玄空飞星风水及择日六大子系统，并通过**多供应商 LLM 流式引擎**（支持 Anthropic、OpenAI、DeepSeek、Gemini、Moonshot 等 13+ 供应商）提供古籍级别的 AI 智能解读。

本项目的核心理念：
- **忠于古法**：年柱以立春为界、月柱用五虎遁年起月法、日柱基于经典甲子参考日推算、时柱采五鼠遁日起时法
- **工程严谨**：全量 Pydantic v2 数据校验、清晰的模块边界（计算层与 API 层彻底分离）
- **RAG 赋能**：8,600+ 行经典古籍知识库 + BM25 语义检索引擎（jieba 分词），每次调用动态检索最相关古籍段落作为 LLM 上下文
- **多模型支持**：通过请求头动态切换 AI 供应商与模型，无需修改配置文件
- **一键启动**：Windows / macOS / Linux 三端同等支持，无需手动配置环境

### English

**BaGua Divination System** is an open-source full-stack application that bridges traditional Chinese metaphysical arts with modern software engineering. At its heart lies a **pure Python calculation engine** that implements six major sub-systems — BaZi Four Pillars, LiuYao Six Lines, Zi Wei Dou Shu, QiMen DunJia, Xuan Kong Flying Stars, and Date Selection — following classical textbook algorithms precisely. A **multi-provider LLM streaming engine** (supporting 13+ providers including Anthropic, OpenAI, DeepSeek, Gemini, Moonshot, and major Chinese LLM providers) then delivers AI interpretation grounded in classical source texts via BM25 RAG retrieval.

Core design philosophy:
- **Classical Fidelity**: Year pillars use LiChun as the boundary; month pillars use the Wu Hu Dun Nian Qi Yue method; day pillars reference the canonical 甲戌 1900-01-01 epoch; hour pillars use the Wu Shu Dun Ri Qi Shi method
- **Engineering Rigour**: Full Pydantic v2 validation, strict module separation (calculation layer vs. API layer are fully decoupled)
- **RAG Empowerment**: An 8,600+ line classical knowledge base with BM25 retrieval engine (jieba segmentation) dynamically retrieves the most relevant classical passages for each LLM call
- **Multi-Model Support**: Dynamically switch AI providers and models via request headers — no config file changes needed
- **One-Click Launch**: Native launchers for Windows (PowerShell + cmd.exe), macOS, and Linux — no manual environment setup required

---

## 2. 功能亮点 · Key Features

### ✨ 命理计算引擎 · Calculation Engines

| 功能 Feature | 中文描述 | English Description |
|---|---|---|
| **四柱排盘** | 年月日时四柱完整排盘，含纳音、藏干 | Full four-pillar chart with NaYin and hidden stems |
| **十神分析** | 十神完整矩阵（比肩至正印），全柱覆盖 | Complete Ten Gods matrix across all pillars |
| **格局判定** | 主要格局 + 特殊格局（从格等）自动检测 | Auto-detection of major and special chart patterns |
| **神煞推算** | 包含禄神、羊刃在内的完整神煞表 | Complete Shensha table including LuShen and YangRen |
| **大运流年** | 精确到天的大运起运年龄（传统三日折算法）| DaYun start age exact to the day (3-day conversion) |
| **六爻起卦** | 铜钱摇卦 / 蓍草筮法 / 时间起卦 / 手动输入 | Three-coin / yarrow / time-based / manual entry |
| **纳甲系统** | 完整纳甲装卦，世应、六亲、六兽 | Full NaJia with world line, six relatives, six spirits |
| **紫微排盘** | 十四主星、十二宫位完整排盘（基于 iztro-py）| Full ZiWei chart with 14 major stars and 12 palaces |
| **奇门布局** | 三元九局，九星八门八神完整排盘 | Sanyuan Jiuju: Nine Stars, Eight Doors, Eight Deities |
| **用途分析** | 求财/感情/事业/出行/健康/学业六大主题 | Six-purpose analysis across all major life domains |
| **飞星风水** | 年飞星推算，九宫吉凶及化煞建议 | Annual flying stars with remedies per sector |
| **八宅分析** | 命卦推算，东西四命，宅卦吉凶方位 | Ming Gua, East/West Four Life, Eight Mansion sectors |
| **择日筛选** | 建除十二神，多用途吉日智能筛选 | Twelve Officers, purpose-specific auspicious day selection |

### 🤖 AI 智能解读 · AI Interpretation

- **RAG 检索引擎**：BM25 + jieba 分词的经典古籍语义检索，每次 LLM 调用自动检索 TOP-K 最相关古籍段落，替代传统的固定提示词注入
- **多供应商支持**：通过请求头 `X-LLM-Provider` / `X-LLM-Key` / `X-LLM-Model` 动态切换，支持 13+ AI 供应商
- **流式输出**：Server-Sent Events（SSE）实时流式输出，无需等待全量响应
- **主题匹配**：六爻占问自动匹配 12 大主题（婚姻、求财、官司、求医等），精准调用对应古籍规则
- **结构化解读**：奇门遁甲提供三奇六仪、伏吟反吟、星门神三维组合解读
- **模型列表代理**：实时查询各供应商可用模型列表，支持自定义供应商接入

### 🔌 支持的 AI 供应商 · Supported LLM Providers

| 供应商 Provider | 协议 Protocol | 默认模型 Default Model |
|---|---|---|
| **Anthropic Claude** | Anthropic API | claude-sonnet-4-6 |
| **OpenAI** | OpenAI API | gpt-4o |
| **DeepSeek** | OpenAI-compatible | deepseek-chat |
| **Google Gemini** | Gemini API | gemini-2.0-flash |
| **Moonshot Kimi** | OpenAI-compatible | moonshot-v1-8k |
| **智谱 GLM** | OpenAI-compatible | glm-4-plus |
| **阿里 Qwen** | OpenAI-compatible | qwen-max |
| **零一万物 Yi** | OpenAI-compatible | yi-lightning |
| **百川 Baichuan** | OpenAI-compatible | Baichuan4 |
| **MiniMax** | OpenAI-compatible | abab6.5s-chat |
| **字节 豆包** | OpenAI-compatible | doubao-pro-32k |
| **腾讯 混元** | OpenAI-compatible | hunyuan-turbos |
| **讯飞 星火** | OpenAI-compatible | generalv3 |
| **Ollama (本地)** | OpenAI-compatible | llama3.3:latest |

> 任何 OpenAI-compatible 的自定义供应商均可通过 `X-LLM-Base-Url` 接入。

---

## 3. 系统架构 · Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Browser / Client                         │
│                  React 19 + Vite + Zustand  (Port 5173)          │
│  Agent | BaZi | LiuYao | ZiWei | QiMen | FengShui | DateSel     │
└────────────────────────┬─────────────────────────────────────────┘
                         │  HTTP / SSE (Server-Sent Events)
┌────────────────────────▼─────────────────────────────────────────┐
│                  FastAPI Application  (Port 8888)                 │
│                                                                   │
│  /agent (SSE)  /bazi  /liuyao  /ziwei  /qimen  /fengshui        │
│  /date-sel     /knowledge      /models                            │
│                                                                   │
│          Pydantic v2 Schemas  (models/)                          │
│                                                                   │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐   │
│  │  bazi/   │ liuyao/  │  ziwei/  │  qimen/  │  fengshui/   │   │
│  │ chart    │ divin.   │  chart   │ algorithm│  calculat.   │   │
│  │ analyzer │ najia    │ (iztro)  │ analyzer │  flying_*    │   │
│  │ forecast │ interpret│          │ purpose  │              │   │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘   │
│                  calendar/ (ganzhi + solar_terms)                 │
│                  constants.py (single source of truth)           │
│                                                                   │
│   knowledge/  (8,600+ line Classical Text Library + BM25 RAG)   │
│    穷通宝鉴 · 滴天髓 · 三命通会 · 增删卜易 · 卜筮正宗 · 紫微    │
│    奇门遁甲统宗 · 阳宅三要 · 八宅明镜 · 协纪辨方 …              │
└──────────────────────────────┬───────────────────────────────────┘
                               │  HTTPS  (httpx async)
              ┌────────────────▼────────────────────┐
              │     Multi-Provider LLM Gateway       │
              │  Anthropic / OpenAI / DeepSeek /     │
              │  Gemini / Moonshot / GLM / Qwen …    │
              │     Streaming SSE response           │
              └─────────────────────────────────────┘
```

### 技术选型 · Technology Stack

| 层次 Layer | 技术 Technology | 选型理由 Rationale |
|---|---|---|
| **API 框架** | FastAPI 0.115 | 原生异步支持 SSE，自动 Swagger 文档，Pydantic 深度集成 |
| **数据校验** | Pydantic v2 | 严格类型安全，性能比 v1 提升 5–50×，Python 3.10+ 兼容 |
| **ASGI 服务器** | Uvicorn + standard | 生产级性能，支持 `--reload` 热重载开发 |
| **历法计算** | ephem 4.1.5 + lunar_python | 高精度天文历法 + 扩展农历干支节气 |
| **农历转换** | lunarcalendar 0.0.9 | 农历/公历互转，支持 1900–2100 年 |
| **紫微引擎** | iztro-py | 紫微斗数完整排盘（十四主星、十二宫位）|
| **RAG 检索** | rank-bm25 + jieba | BM25 语义排序 + 中文分词，古籍段落精准检索 |
| **HTTP 客户端** | httpx 0.27.2 | 原生异步，用于多供应商 LLM Streaming API 调用 |
| **前端框架** | React 19 + Vite | 极速 HMR，现代化组件化开发 |
| **状态管理** | Zustand | 轻量级全局状态管理（设置持久化）|
| **前端路由** | React Router v7 | 声明式多页面路由 |
| **配置管理** | pydantic-settings | 类型安全的 `.env` 读取，支持环境变量覆盖 |

---

## 4. 命理模块详解 · Module Deep Dive

### 🀄 八字模块 · BaZi (Four Pillars of Destiny)

**排盘算法 Chart Construction**

| 柱 Pillar | 算法依据 Algorithm |
|---|---|
| 年柱 Year | 以立春（LiChun）为界，跨年生人依实际节气归属正确年份 |
| 月柱 Month | 节（Jié）边界 + 五虎遁年起月法（月干由年干推算）|
| 日柱 Day | 参考日 1900-01-01 = 甲戌（60 甲子第10位），经典验证算法 |
| 时柱 Hour | 五鼠遁日起时法，时干由日干推算 |

**分析功能 Analysis Capabilities**
- 十神矩阵：100 组天干对的完整十神映射（比肩/劫财/食神/伤官/偏财/正财/七杀/正官/偏印/正印）
- 五行强弱：旺/相/休/囚/死 五种季节状态评估
- 格局判定：主要格局 + 从弱/从旺等特殊格局自动识别
- 神煞：完整神煞表含禄神、羊刃（B-12 修正版本）
- 纳音五行：60 甲子纳音全表（海中金至大海水）
- 大运：精确日数 ÷ 3 推算起运年龄（阳男阴女顺行，阴男阳女逆行）
- 流年流月六亲动态推演
- 日主性格特征库（10 种日主完整画像）

---

### ☯ 六爻模块 · LiuYao (Six Lines Divination)

经典依据：《增删卜易》《卜筮正宗》《易隐》《火珠林》《黄金策》

**起卦方式 Divination Methods**

| 方式 Method | 说明 Description |
|---|---|
| `coin` | 铜钱三枚摇卦（三枚铜钱正统方法）|
| `yarrow` | 蓍草筮法（50 根蓍草传统方法）|
| `time` | 时间起卦（年月日时数起卦）|
| `manual` | 手动输入爻值 `[6/7/8/9] × 6`（从初爻到上爻）|

**核心分析 Core Analysis**
- 纳甲装卦（六爻完整天干地支纳入）
- 世爻/应爻确定，六亲（父母/兄弟/子孙/妻财/官鬼），六神（青龙/朱雀/勾陈/腾蛇/白虎/玄武）
- 动爻/变爻，本卦 → 变卦自动生成
- 日月冲克、空亡判断
- 用神确定，12 大主题自动匹配对应古籍规则

**主题关键词自动匹配 Topic Auto-matching**

| 主题 Topic | 用神 Yong Shen |
|---|---|
| 求财 | 妻财爻 |
| 求官仕途 | 官鬼爻、父母爻 |
| 考试功名 | 父母爻、官鬼爻 |
| 婚姻感情 | 妻财爻（男）/ 官鬼爻（女）|
| 求医疾病 | 世爻、子孙爻 |
| 官司诉讼 | 官鬼爻（攻）/ 子孙爻（守）|

---

### 🌟 紫微斗数模块 · Zi Wei Dou Shu (Purple Star Astrology)

基于 **iztro-py** 引擎实现完整紫微排盘。

**核心功能 Core Features**
- **十四主星**：紫微、天机、太阳、武曲、天同、廉贞、天府、太阴、贪狼、巨门、天相、天梁、七杀、破军
- **十二宫位**：命宫、兄弟宫、夫妻宫、子女宫、财帛宫、疾厄宫、迁移宫、交友宫、官禄宫、田宅宫、福德宫、父母宫
- **辅助星曜**：左辅、右弼、文昌、文曲、天魁、天钺等
- **四化飞星**：化禄、化权、化科、化忌
- **宫位分析**：各宫吉凶、星曜组合解读

---

### 🧭 奇门遁甲模块 · QiMen DunJia

基于三元九局（Sanyuan Jiuju）算法，完整实现奇门排盘。

**核心算法 Core Algorithm**
- 阳遁/阴遁判定（冬至→夏至 = 阳遁，夏至→冬至 = 阴遁）
- 局数推算（1–9 局，基于节气位置）
- 元（上/中/下元）确定
- 九宫完整布局：九星 + 八门 + 八神 + 天干

**天干解读矩阵 Stem Interpretation Matrix**

| 天干 Stem | 类别 Category | 性质 Nature | 核心含义 |
|---|---|---|---|
| 戊 | 六仪 | 吉 | 值符之宫，贵人相助，诸事顺遂 |
| 己 | 六仪 | 凶 | 阴柔隐秘，口舌是非，防欺骗 |
| 庚 | 六仪 | 大凶 | 白虎凶险，官非牢狱，诸事阻格 |
| 辛 | 六仪 | 凶 | 刑伤之宿，疾病官司，防刀伤 |
| 壬 | 六仪 | 吉 | 武曲财帛，利商贸经营，智谋过人 |
| 癸 | 六仪 | 凶 | 小耗阴私，防小人消耗 |
| 乙丙丁 | 三奇 | 大吉 | 乙奇/丙奇/丁奇，得奇诸事大吉 |

**用途专项分析 Purpose Analysis**  
6 大主题（求财/感情/事业/出行/健康/学业）各自提供：宫位判断、吉凶星门组合、具体建议。

**特殊格局检测**
- 伏吟（宫与星同，主静滞不动）
- 反吟（相冲之宫，主反复无常）

---

### 🏡 风水模块 · FengShui

融合**八宅风水**与**玄空飞星**两大体系。

**八宅分析 Eight Mansion**
- 命卦推算（传统男减女加公式，2000 年后调整版本）
- 东四命（1/3/4/9 宫）vs 西四命（2/5/6/7/8 宫）
- 八方位吉凶：生气/延年/天医/伏位（四吉）vs 五鬼/绝命/六煞/祸害（四凶）

**玄空飞星 Xuan Kong Flying Stars**

| 星 Star | 五行 | 性质 | 提示 |
|---|---|---|---|
| 一白贪狼 | 水 | 吉 | 利文学求职，桃花旺 |
| 二黑巨门 | 土 | 大凶 | 病符，放铜葫芦化煞 |
| 三碧禄存 | 木 | 凶 | 口舌官非，放红色化解 |
| 四绿文昌 | 木 | 吉 | 学业大吉，宜书房 |
| 五黄廉贞 | 土 | 大凶 | 最凶，绝对不可动土 |
| 六白武曲 | 金 | 吉 | 武曲当旺，利偏财 |
| 七赤破军 | 金 | 凶 | 防盗防争 |
| 八白左辅 | 土 | 大吉 | 财星，利置产 |
| 九紫右弼 | 火 | 吉 | 桃花喜庆 |

---

### 📅 择日模块 · Date Selection

**建除十二神 Twelve Officers**  
建/除/满/平/定/执/破/危/成/收/开/闭 — 依日柱地支与月柱地支关系推算，各有宜忌。

**用途专项筛选 Purpose Criteria**

| 用途 | 宜用地支 | 忌用 |
|---|---|---|
| 婚嫁 | 子丑卯辰未申酉 | 午寅戌 |
| 开业 | 寅午亥子 | 冲日主生肖 |
| 动土 | 辰戌丑未（土旺）| 寅卯（木克土）|
| 搬家 | 子卯午酉（四正）| 冲刑日 |
| 出行 | 寅申巳亥（驿马）| 五黄凶方 |
| 求医 | 子亥酉（天医位）| 午未 |

**三煞方位**：依流年地支推算，动土修缮忌犯三煞方。

---

## 5. 快速开始 · Quick Start

### 前置要求 · Prerequisites

| 依赖 | 最低版本 | 下载地址 |
|---|---|---|
| **Python** | 3.10+ | https://www.python.org/downloads/ |
| **Node.js** | 18+ | https://nodejs.org/ |

> 💡 **Windows 用户**：安装 Python 时务必勾选 ✅ **"Add Python to PATH"**

---

### 克隆与启动 · Clone & Start

#### Windows — PowerShell（推荐）

```powershell
# 克隆项目
git clone https://github.com/your-username/bagua-divination.git
cd bagua-divination

# 首次运行：允许本地脚本执行
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 一键启动（自动安装依赖 + 启动前后端）
.\start.ps1
```

#### Windows — Command Prompt (cmd.exe)

```bat
git clone https://github.com/your-username/bagua-divination.git
cd bagua-divination
start.bat
```

#### macOS / Linux

```bash
git clone https://github.com/your-username/bagua-divination.git
cd bagua-divination
chmod +x start.sh
./start.sh
```

---

### 启动后访问 · Access After Starting

启动成功后，终端将打印如下信息：  
After a successful start, the terminal prints:

```
  ╔══════════════════════════════════════════════════════════════╗
  ║              八 卦 推 演  BaGua System                      ║
  ║  八字 · 六爻 · 紫微 · 奇门遁甲 · 风水 · 择日               ║
  ╚══════════════════════════════════════════════════════════════╝

  ● Backend API  →  http://localhost:8888
  ● API Docs     →  http://localhost:8888/docs
  ● Frontend     →  http://localhost:5173
```

| 服务 Service | 地址 URL | 说明 |
|---|---|---|
| 🖥 前端界面 | http://localhost:5173 | React 交互界面 |
| ⚡ 后端 API | http://localhost:8888 | FastAPI 服务 |
| 📖 Swagger 文档 | http://localhost:8888/docs | 交互式 API 文档 |
| 📋 ReDoc 文档 | http://localhost:8888/redoc | 只读 API 文档 |

---

### 所有命令 · All Commands

| 操作 Action | PowerShell | cmd.exe | macOS/Linux |
|---|---|---|---|
| 启动全部 | `.\start.ps1` | `start.bat` | `./start.sh` |
| 仅后端 | `.\start.ps1 backend` | `start.bat backend` | `./start.sh backend` |
| 仅前端 | `.\start.ps1 frontend` | `start.bat frontend` | `./start.sh frontend` |
| 安装依赖 | `.\start.ps1 install` | `start.bat install` | `./start.sh install` |
| 停止服务 | `.\start.ps1 stop` | `start.bat stop` | `./start.sh stop` |

> **智能缓存**：启动脚本对 `requirements.txt` 和 `package.json` 进行 MD5 哈希比对，内容未变更时跳过重复安装，大幅加快二次启动速度。  
> **Smart caching**: The launcher compares MD5 hashes of `requirements.txt` and `package.json` — dependencies are skipped unless files have changed, making subsequent starts much faster.

---

## 6. 配置说明 · Configuration

```bash
cp .env.example .env
# 然后编辑 .env / Then edit .env
```

### 完整配置项 · All Options

```env
# ─── 服务器 Server ───────────────────────────────────────────────
APP_HOST=0.0.0.0          # 监听地址，0.0.0.0 允许局域网访问
APP_PORT=8888             # 后端端口
DEBUG=false               # true 时开启详细日志
```

### AI 供应商配置 · AI Provider Configuration

本系统的 AI 功能**不依赖 `.env` 文件中的 API Key**，而是通过**前端设置页面**在每次请求的 HTTP Header 中传递：

| Header | 说明 | 示例 |
|---|---|---|
| `X-LLM-Key` | API 密钥 | `sk-ant-...` / `sk-...` |
| `X-LLM-Provider` | 供应商标识 | `anthropic` / `deepseek` / `openai` / `moonshot` / `gemini` |
| `X-LLM-Base-Url` | 自定义 Base URL（可选）| `https://api.deepseek.com` |
| `X-LLM-Model` | 模型名称覆盖（可选）| `claude-sonnet-4-6` |

> ⚠️ **注意**：AI 顾问（`/api/v1/agent/*`）需通过前端设置页面配置有效 API Key。  
> 八字/六爻/紫微/奇门/风水/择日六个计算模块**无需** API Key 即可独立运行。  
> The six calculation modules work **without** an API Key — only the AI streaming features require one.

### 获取 API Key · Getting an API Key

根据您选择的供应商，在对应平台注册：

| 供应商 | 注册地址 | Key 格式 |
|---|---|---|
| Anthropic Claude | [console.anthropic.com](https://console.anthropic.com/) | `sk-ant-...` |
| OpenAI | [platform.openai.com](https://platform.openai.com/) | `sk-...` |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/) | `sk-...` |
| Google Gemini | [aistudio.google.com](https://aistudio.google.com/) | `AIza...` |
| Moonshot Kimi | [platform.moonshot.cn](https://platform.moonshot.cn/) | `sk-...` |

### 生产部署 · Production Deployment

```env
APP_HOST=0.0.0.0
APP_PORT=8888
DEBUG=false
```

建议在 Nginx 前置反向代理，并通过 `systemd` 或 `supervisor` 管理进程。  
Recommended: place Nginx as a reverse proxy and manage the process with `systemd` or `supervisor`.

---

## 7. 依赖说明 · Dependencies

### Python 后端 · Backend (`requirements.txt`)

| 包 Package | 版本 | 用途 Purpose |
|---|---|---|
| `fastapi` | 0.115.0 | Web 框架，原生 SSE 支持 |
| `uvicorn[standard]` | 0.30.6 | ASGI 服务器（含 websockets + uvloop）|
| `pydantic` | 2.9.2 | 请求/响应数据校验，比 v1 快 5–50× |
| `pydantic-settings` | 2.5.2 | 类型安全的 `.env` 配置读取 |
| `python-dotenv` | 1.0.1 | `.env` 文件加载 |
| `python-multipart` | 0.0.12 | 表单数据解析 |
| `ephem` | 4.1.5 | 高精度天文历法，节气精确计算 |
| `lunarcalendar` | 0.0.9 | 公农历互转（1900–2100）|
| `lunar_python` | ≥1.4.8 | 扩展农历库（干支、节气、农历日期）|
| `httpx` | 0.27.2 | 异步 HTTP 客户端，调用多供应商 LLM Streaming API |
| `iztro-py` | ≥0.3.3 | 紫微斗数排盘引擎 |
| `rank-bm25` | ≥0.2.2 | BM25 语义排序，古籍段落检索 |
| `jieba` | ≥0.42.1 | 中文分词，用于 RAG 文本分词索引 |

```bash
pip install -r requirements.txt
```

### 前端 · Frontend

基于 **React 19 + Vite + Zustand + React Router v7**，启动脚本自动安装。手动安装：

```bash
cd frontend
npm install
npm run dev        # 开发模式 Development
npm run build      # 生产构建 Production build
npm run preview    # 预览生产构建 Preview
```

---

## 8. API 参考 · API Reference

完整交互式文档：启动后访问 `http://localhost:8888/docs`

### 健康检查 · Health Check

```
GET /health
```

### 八字 · BaZi

| Method | Endpoint | 功能 |
|---|---|---|
| `POST` | `/api/v1/bazi/chart` | 四柱排盘 |
| `POST` | `/api/v1/bazi/analyze` | 十神/格局/神煞完整分析 |
| `POST` | `/api/v1/bazi/fortune` | 大运/流年/流月推算 |
| `POST` | `/api/v1/bazi/compatibility` | 合婚分析（双人）|

**请求示例 Request Example** — `POST /api/v1/bazi/chart`：
```json
{
  "year": 1990,
  "month": 6,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "gender": "male",
  "name": "张三",
  "use_true_solar_time": false
}
```

---

### 六爻 · LiuYao

| Method | Endpoint | 功能 |
|---|---|---|
| `POST` | `/api/v1/liuyao/divine` | 起卦 |
| `POST` | `/api/v1/liuyao/interpret` | 卦象解读 |
| `GET`  | `/api/v1/liuyao/hexagram/{number}` | 获取第 N 卦详情 |

**请求示例** — `POST /api/v1/liuyao/divine`：
```json
{
  "method": "coin",
  "question": "问近期财运如何？"
}
```

手动输入示例（爻值 6=老阴/7=少阳/8=少阴/9=老阳，从初爻到上爻）：
```json
{
  "method": "manual",
  "question": "问婚姻",
  "yao_values": [7, 8, 9, 7, 6, 8]
}
```

---

### 紫微斗数 · Zi Wei Dou Shu

| Method | Endpoint | 功能 |
|---|---|---|
| `POST` | `/api/v1/ziwei/chart` | 紫微排盘（十四主星、十二宫位）|

---

### 奇门遁甲 · QiMen DunJia

| Method | Endpoint | 功能 |
|---|---|---|
| `POST` | `/api/v1/qimen/chart` | 当前时刻奇门盘 |
| `POST` | `/api/v1/qimen/analyze` | 九宫综合分析 |
| `POST` | `/api/v1/qimen/purpose` | 用途专项分析 |

**用途参数值 Purpose Values**：`求财` / `感情` / `事业` / `出行` / `健康` / `学业`

---

### 风水 · FengShui

| Method | Endpoint | 功能 |
|---|---|---|
| `POST` | `/api/v1/fengshui/ming-gua` | 命卦推算 |
| `POST` | `/api/v1/fengshui/analyze` | 八宅方位分析 |
| `POST` | `/api/v1/fengshui/flying-stars` | 指定年份飞星布局 |

---

### 择日 · Date Selection

| Method | Endpoint | 功能 |
|---|---|---|
| `POST` | `/api/v1/date-selection/select` | 筛选指定月份吉日 |
| `POST` | `/api/v1/date-selection/annotate` | 查询某日建除十二神详情 |

---

### AI 顾问 · AI Agent (SSE)

| Method | Endpoint | 功能 |
|---|---|---|
| `POST` | `/api/v1/agent/consult` | 综合 AI 流式解读 |
| `POST` | `/api/v1/agent/bazi` | 八字 AI 分析（SSE）|
| `POST` | `/api/v1/agent/liuyao` | 六爻 AI 解卦（SSE）|

所有 `/agent/*` 端点返回 `Content-Type: text/event-stream`。

**请求头配置 Request Headers**：
```
X-LLM-Key: sk-ant-...         # API Key
X-LLM-Provider: anthropic     # 供应商 (anthropic/openai/deepseek/moonshot/gemini)
X-LLM-Model: claude-sonnet-4-6  # 模型名（可选）
X-LLM-Base-Url:               # 自定义 Base URL（可选）
```

前端接收示例：
```javascript
const response = await fetch('/api/v1/agent/consult', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-LLM-Key': 'sk-ant-...',
    'X-LLM-Provider': 'anthropic'
  },
  body: JSON.stringify({ query: '...' })
});
const reader = response.body.getReader();
// 逐块读取 SSE 流 / Read SSE stream chunk by chunk
```

---

### 模型列表 · Model List Proxy

| Method | Endpoint | 功能 |
|---|---|---|
| `GET` | `/api/v1/models?provider=anthropic` | 获取指定供应商模型列表（需 `X-LLM-Key`）|
| `GET` | `/api/v1/models/fallback?provider=deepseek` | 获取预置模型列表（无需 Key）|
| `GET` | `/api/v1/models/providers` | 获取所有内置供应商信息 |

> 无 API Key 时返回预置 fallback 列表；有 Key 时实时查询供应商官方 `/models` 端点。

---

### 知识库 · Knowledge Base

| Method | Endpoint | 功能 |
|---|---|---|
| `GET`  | `/api/v1/knowledge/list` | 列出所有古籍条目 |
| `GET`  | `/api/v1/knowledge/{key}` | 获取指定古籍内容 |
| `POST` | `/api/v1/knowledge/search` | 关键词检索古籍 |

---

## 9. 项目结构 · Project Structure

```
bagua_project_build/
│
├── start.ps1              Windows PowerShell 启动器（彩色输出 + 进程管理）
├── start.bat              Windows cmd.exe 启动器（MD5 哈希缓存加速）
├── start.sh               macOS / Linux 启动器（自动创建 .venv）
│
├── main.py                FastAPI 应用入口，路由注册
├── config.py              Pydantic-Settings 配置（读取 .env）
├── requirements.txt       Python 依赖清单
├── .env / .env.example    环境变量模板
│
├── api/                   HTTP 路由层（纯 I/O，不含业务逻辑）
│   ├── agent.py           AI Agent SSE 流式端点（多供应商）      ★
│   ├── models.py          模型列表代理（13+ 供应商实时查询）     ★
│   ├── bazi.py            八字 API 路由
│   ├── liuyao.py          六爻 API 路由
│   ├── ziwei.py           紫微斗数 API 路由                     ★
│   ├── qimen.py           奇门 API 路由
│   ├── fengshui.py        风水 API 路由
│   ├── date_selection.py  择日 API 路由
│   ├── knowledge.py       知识库 API 路由
│   └── knowledge_api.py   知识库扩展 API
│
├── core/                  纯计算引擎（无 HTTP 依赖，可独立单元测试）
│   │
│   ├── constants.py       全局常量库（天干/地支/五行/十神/纳音/神煞等）
│   │
│   ├── bazi/              四柱八字
│   │   ├── chart.py       排盘（立春/五虎遁/五鼠遁算法）
│   │   ├── analyzer.py    十神/格局/神煞分析
│   │   ├── forecaster.py  大运/流年/流月推算（精确日数折算）
│   │   ├── applications.py  命理实际应用建议
│   │   └── day_master_profiles.py  日主性格特征库（10 种日主）
│   │
│   ├── liuyao/            六爻占卜
│   │   ├── divination.py  铜钱/蓍草/时间/手动起卦
│   │   ├── hexagram_data.py  六十四卦完整数据（卦名/卦辞/爻辞）
│   │   ├── interpreter.py    卦象解读（12 主题自动匹配古籍规则）
│   │   └── najia.py       纳甲系统（世应/六亲/六兽）
│   │
│   ├── ziwei/             紫微斗数                               ★
│   │   └── chart.py       紫微排盘（基于 iztro-py）
│   │
│   ├── qimen/             奇门遁甲
│   │   ├── algorithm.py   三元九局核心算法（阳遁/阴遁/局数/九宫布局）
│   │   ├── analyzer.py    九宫综合分析
│   │   └── purpose_analysis.py  用途分析（6 主题 + 三奇六仪矩阵）
│   │
│   ├── fengshui/          风水
│   │   ├── calculator.py  命卦/宅卦/八宅方位吉凶
│   │   └── flying_stars.py  玄空飞星（九星属性/年飞星/化煞建议）
│   │
│   ├── date_selection/    择日
│   │   ├── selector.py    吉日筛选（6 种用途 × 多维条件）
│   │   └── twelve_officers.py  建除十二神推算
│   │
│   └── calendar/          历法工具
│       ├── ganzhi.py      干支推算（60 甲子索引计算）
│       └── solar_terms.py  节气计算（基于 ephem 高精度天文算法）
│
├── models/                Pydantic v2 数据模型
│   ├── common.py          通用基础模型
│   ├── bazi.py            八字模型（含 PillarDetail/DayunPeriod/LiunianDetail 等）
│   ├── liuyao.py          六爻模型（含 YaoDetail/DivinationResponse 等）
│   ├── qimen.py           奇门模型
│   └── fengshui.py        风水模型
│
├── knowledge/             古籍知识库 + RAG 检索引擎（8,600+ 行）  ★
│   ├── rag.py             BM25 + jieba RAG 引擎                   ★
│   ├── manager.py         知识管理器（检索/过滤/格式化）
│   ├── classical_texts.py  经典文本核心库
│   ├── classical_knowledge.py  综合经典知识
│   ├── foundations.py      命理基础理论
│   ├── bazi_classical.py   八字专项古籍
│   ├── liuyao_classical.py  六爻专项古籍
│   ├── najia_complete.py   纳甲完整知识
│   ├── qimen_classical.py  奇门专项古籍
│   ├── fengshui_classical.py  风水专项古籍
│   ├── date_classical.py   择日专项古籍
│   ├── ziwei_classical.py  紫微专项古籍
│   ├── ziwei_deep.py       紫微深度知识
│   ├── bagua_system.py     八卦体系
│   ├── shishen_shensha.py  十神与神煞
│   ├── xingxiu_system.py   星宿体系
│   ├── advanced_systems.py  高级推演体系
│   └── practical_divination.py  实占技法
│
└── frontend/              React 19 + Vite + Zustand 前端
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── pages/
        │   ├── Agent/         AI 顾问聊天（SSE 流式渲染）          ★
        │   ├── Bazi/          八字排盘与分析
        │   ├── LiuYao/        六爻占卜
        │   ├── ZiWei/         紫微斗数                             ★
        │   ├── QiMen/         奇门遁甲
        │   ├── FengShui/      风水分析
        │   ├── DateSelection/ 择日选择
        │   ├── Knowledge/     古籍知识库浏览
        │   └── Settings/      供应商/Key/模型设置                  ★
        ├── components/        公共组件库（UI/Layout）
        ├── store/             Zustand 状态管理（设置持久化）
        └── api/client.js      API 请求封装
```

---

## 10. 开发指南 · Development Guide

### 本地开发模式 · Local Dev Mode

```bash
# 后端（热重载）
cd bagua_project_build
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows
uvicorn main:app --reload --port 8888

# 前端（另开终端）
cd frontend
npm run dev
```

### 分层架构原则 · Layered Architecture Principles

```
api/       ← 只做 HTTP I/O，参数验证，调用 core 层
core/      ← 纯计算，无 HTTP 依赖，返回 dict / dataclass
models/    ← Pydantic schema，api 层用于序列化/反序列化
knowledge/ ← 古籍文本 + RAG 索引，供 core 层和 agent 层引用
```

遵循此分层可确保 `core/` 中的所有计算函数可独立进行单元测试。

### 新增 API 端点 · Adding a New Endpoint

1. 在 `core/` 中实现纯计算逻辑（无任何 HTTP 依赖）
2. 在 `models/` 中定义 Pydantic Request / Response 模型
3. 在 `api/` 中创建路由文件，调用 `core` 层
4. 在 `main.py` 中注册新路由

### 新增 AI 供应商 · Adding a New LLM Provider

1. 在 `api/agent.py` 的 `PROVIDER_DEFAULTS` 中添加供应商配置
2. 在 `api/models.py` 的 `PROVIDER_CONFIG` 和 `FALLBACK_MODELS` 中添加模型列表
3. 如供应商使用 OpenAI-compatible API，无需额外代码

### 扩展古籍知识库 · Extending the Knowledge Base

在 `knowledge/` 目录下创建新的 Python 文件，按现有格式添加知识条目。RAG 引擎会在启动时自动索引 `knowledge/` 下所有模块：

```python
# knowledge/your_new_text.py

YOUR_TEXT_KNOWLEDGE = {
    "title": "古籍名称",
    "source": "书名",
    "content": [
        "原文片段一...",
        "原文片段二...",
    ]
}
```

### 代码规范 · Code Style

- **Python**：PEP 8，类型注解全覆盖，每模块含 docstring
- **命名**：命理术语保留中文拼音（`tiangan`/`dizhi`/`shishen`），方法名英文
- **注释**：关键算法附中英双语注释
- **提交**：遵循 Conventional Commits 规范（见贡献指南）

---

## 11. 常见问题 · Troubleshooting

### Windows

<details>
<summary><b>"running scripts is disabled on this system"</b></summary>

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
</details>

<details>
<summary><b>"python is not recognized" / python 不是内部命令</b></summary>

重新运行 Python 安装程序，勾选 **"Add Python to PATH"**，重启终端。  
验证：`python --version` 或 `python3 --version`
</details>

<details>
<summary><b>"node is not recognized" / node 不是内部命令</b></summary>

从 https://nodejs.org/ 安装 Node.js LTS，重启终端。  
验证：`node --version` 和 `npm --version`
</details>

<details>
<summary><b>端口被占用 · Port already in use (8888 or 5173)</b></summary>

```powershell
netstat -ano | findstr :8888
taskkill /f /pid <PID>
```
</details>

<details>
<summary><b>查看实时日志 · View live logs</b></summary>

```powershell
Get-Content $env:TEMP\bagua_run\backend.log  -Wait
Get-Content $env:TEMP\bagua_run\frontend.log -Wait
```
</details>

---

### macOS / Linux

<details>
<summary><b>Permission denied</b></summary>

```bash
chmod +x start.sh
```
</details>

<details>
<summary><b>Python 版本过低 · Python version too old</b></summary>

```bash
python3 --version   # 需要 3.10+

# macOS (Homebrew)
brew install python@3.11

# Ubuntu / Debian
sudo apt update && sudo apt install python3.11 python3.11-venv
```
</details>

<details>
<summary><b>npm install 失败 · npm install fails</b></summary>

```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```
</details>

<details>
<summary><b>后端启动后立即退出 · Backend exits immediately</b></summary>

直接运行查看完整错误：
```bash
cd bagua_project_build
source .venv/bin/activate
python -m uvicorn main:app --reload --port 8888
```
</details>

<details>
<summary><b>AI 功能无响应 · AI Agent not responding</b></summary>

1. 确认前端设置页面已正确配置 API Key 和供应商
2. 在设置页面点击「测试连接」验证 Key 可用性
3. 确认网络可访问对应供应商的 API 端点
4. 查看浏览器开发者工具 Network 面板，检查 SSE 请求的响应状态
</details>

---

## 12. 路线图 · Roadmap

- [x] ~~**紫微斗数** — 十四主星、十二宫位完整排盘~~ ✅ 已实现
- [x] ~~**多 LLM 供应商** — 支持 13+ AI 供应商动态切换~~ ✅ 已实现
- [x] ~~**RAG 检索引擎** — BM25 + jieba 古籍语义检索~~ ✅ 已实现
- [ ] **梅花易数** — 体用卦，数字/时间起卦
- [ ] **铁板神数** — 结合八字与序数推演
- [ ] **用户账号系统** — 本地命盘保存与历史记录
- [ ] **多语言界面** — 繁体中文 / English UI
- [ ] **移动端优化** — PWA 支持，响应式布局
- [ ] **Docker 镜像** — 一键容器化部署
- [ ] **古籍扩充** — 更多经典文本片段入库
- [ ] **PDF 导出** — 命盘报告导出与分享链接

---

## 13. 贡献指南 · Contributing

欢迎任何形式的贡献：Bug 修复、新功能、文档改进、古籍知识库扩充。  
All contributions are welcome: bug fixes, new features, documentation, or knowledge base additions.

### 贡献流程 · Workflow

```bash
# 1. Fork 并克隆
git clone https://github.com/your-username/bagua-divination.git

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 提交（遵循 Conventional Commits）
git commit -m "feat: add purple star astrology module"
git commit -m "fix: correct DaYun start age for yin-female chart"
git commit -m "docs: add LiuYao topic matching examples to README"

# 4. Push 并创建 Pull Request
git push origin feature/your-feature-name
```

### 提交规范 · Commit Convention

| 前缀 | 用途 |
|---|---|
| `feat:` | 新功能 |
| `fix:` | Bug 修复 |
| `docs:` | 文档更新 |
| `refactor:` | 重构（不影响功能）|
| `test:` | 测试相关 |
| `chore:` | 构建/工具链更新 |

### 报告问题 · Reporting Issues

提交 Issue 请包含：操作系统及版本 · Python/Node.js 版本 · 完整错误日志 · 复现步骤

---

## 14. 许可证 · License

本项目基于 **MIT 许可证** 开源发布。  
This project is released under the **MIT License**.

```
MIT License — Copyright (c) 2024–2025 BaGua Divination System Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

> **免责声明 Disclaimer**：本系统所有命理推演结果仅供文化研究与娱乐参考，不构成任何专业的医疗、法律、财务建议。传统命理学属中华文化遗产，请理性对待推演结果。  
> *All divination results from this system are for cultural research and entertainment purposes only and do not constitute medical, legal, or financial advice. Traditional Chinese metaphysics is part of cultural heritage — please interpret results rationally.*

---

<div align="center">

**以古籍之智，赋 AI 之能 · Empowering Ancient Wisdom with Modern AI**

⭐ 如果这个项目对你有帮助，请点一个 Star！  
⭐ If you find this project useful, please give it a Star!

</div>
