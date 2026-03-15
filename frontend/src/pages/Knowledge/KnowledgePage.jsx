import React, { useState, useEffect, useCallback, Component } from 'react'
import AiInterpretPanel from '../../components/UI/AiInterpretPanel'
import { useNotifyStore } from '../../store/settingsStore'
import './KnowledgePage.css'

/* ─────────────────────────────── ErrorBoundary ─────────────────────────────── */
class ErrorBoundary extends Component {
  constructor(p) { super(p); this.state = { err: null } }
  static getDerivedStateFromError(e) { return { err: e } }
  render() {
    if (this.state.err) return (
      <div className="kp-error">
        <span>⚠</span>
        <p>{this.state.err.message}</p>
        <button onClick={() => this.setState({ err: null })}>重试</button>
      </div>
    )
    return this.props.children
  }
}

/* ─────────────────────────────── Knowledge Catalog ─────────────────────────── */
const CATALOG = [
  // ── 基础理论 ──
  {
    id: 'yinyang', category: '基础理论', icon: '☯', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#0a4c2c 100%)',
    title: '阴阳理论', titleEn: 'Yin-Yang Theory',
    source: '《易传·系辞》', tags: ['哲学基础', '阴阳'], level: '入门', levelNum: 1,
    desc: '一阴一阳之谓道。阴阳对立制约、互根互用、消长转化，是命理学最根本的理论框架。',
    endpoint: '/api/v1/knowledge/foundations/yinyang',
  },
  {
    id: 'wuxing', category: '基础理论', icon: '五', iconBg: 'linear-gradient(135deg,#b5361e 0%,#7c1e0c 100%)',
    title: '五行完整体系', titleEn: 'Five Elements System',
    source: '《洪范》《月令》', tags: ['五行', '生克制化'], level: '入门', levelNum: 1,
    desc: '木火土金水五行：方位·季节·器官·职业·旺相休囚死，及相生相克相侮相乘全论。',
    endpoint: '/api/v1/knowledge/foundations/wuxing',
  },
  {
    id: 'hetu', category: '基础理论', icon: '河', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#0a3260 100%)',
    title: '河图洛书', titleEn: 'He Tu & Luo Shu',
    source: '《易传·系辞》', tags: ['数字', '九宫'], level: '中级', levelNum: 2,
    desc: '河图五行生成之数，洛书九宫幻方。两者是奇门九宫、紫白飞星、命理格局的数理基础。',
    endpoint: '/api/v1/knowledge/foundations/hetu',
  },
  {
    id: 'ganzhi_cal', category: '基础理论', icon: '甲', iconBg: 'linear-gradient(135deg,#b85c00 0%,#7a3600 100%)',
    title: '干支纪年历法', titleEn: 'Stem-Branch Calendar',
    source: '《史记·历书》', tags: ['干支', '历法', '旬空'], level: '入门', levelNum: 1,
    desc: '六十甲子循环，五虎遁年起月，五鼠遁日起时。旬空推算、当代年份对照全表。',
    endpoint: '/api/v1/knowledge/foundations/ganzhi-calendar',
  },
  // ── 天干地支 ──
  {
    id: 'tiangan', category: '天干地支', icon: '干', iconBg: 'linear-gradient(135deg,#b5361e 0%,#cc4428 100%)',
    title: '十天干精解', titleEn: 'Ten Heavenly Stems',
    source: '《滴天髓》', tags: ['天干', '五行', '口诀'], level: '中级', levelNum: 2,
    desc: '甲至癸十干：五行·阴阳·象意·人格·身体·《滴天髓》原文口诀·喜忌·十二长生·六合。',
    endpoint: '/api/v1/knowledge/foundations/tiangan',
  },
  {
    id: 'dizhi', category: '天干地支', icon: '支', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#2878c0 100%)',
    title: '十二地支详解', titleEn: 'Twelve Earthly Branches',
    source: '《三命通会》', tags: ['地支', '藏干', '关系'], level: '中级', levelNum: 2,
    desc: '子至亥：五行·藏干比例·象意·六冲·六合·三合·三刑·六破·六害·墓库全解。',
    endpoint: '/api/v1/knowledge/foundations/dizhi',
  },
  {
    id: 'nayin', category: '天干地支', icon: '音', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#24a070 100%)',
    title: '六十甲子纳音', titleEn: 'Sixty Jiazi Nayin',
    source: '《三命通会》', tags: ['纳音', '甲子'], level: '中级', levelNum: 2,
    desc: '六十甲子纳音五行全表：海中金·炉中火·大林木等三十对，是命理基础知识之一。',
    endpoint: '/api/v1/knowledge/foundations/nayin',
  },
  {
    id: 'canggan', category: '天干地支', icon: '藏', iconBg: 'linear-gradient(135deg,#b85c00 0%,#d47010 100%)',
    title: '十二地支藏干', titleEn: 'Hidden Stems in Branches',
    source: '《京氏易传》', tags: ['藏干', '纳甲'], level: '中级', levelNum: 2,
    desc: '十二支藏干完整表：子藏癸，丑藏己癸辛…是六爻纳甲、八字取神的基础数据。',
    endpoint: '/api/v1/knowledge/foundations/canggan',
  },
  // ── 八卦易学 ──
  {
    id: 'taiji', category: '八卦易学', icon: '☯', iconBg: 'linear-gradient(135deg,#1c1008 0%,#4a3018 100%)',
    title: '太极两仪四象', titleEn: 'Taiji & Four Symbols',
    source: '《易传·系辞》', tags: ['太极', '两仪', '四象'], level: '入门', levelNum: 1,
    desc: '太极→两仪→四象→八卦生成体系，二进制与莱布尼茨，《系辞》原文诠释。',
    endpoint: '/api/v1/knowledge/bagua/taiji',
  },
  {
    id: 'xiantian', category: '八卦易学', icon: '☰', iconBg: 'linear-gradient(135deg,#b5361e 0%,#e05535 100%)',
    title: '先天八卦', titleEn: 'Pre-Heaven Bagua',
    source: '《说卦传》邵雍', tags: ['先天', '伏羲', '数'], level: '中级', levelNum: 2,
    desc: '乾南坤北离东坎西，先天数1-8，先天为体讲对待，《说卦传》"天地定位"原文。',
    endpoint: '/api/v1/knowledge/bagua/xiantian',
  },
  {
    id: 'houtian', category: '八卦易学', icon: '☷', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#2878c0 100%)',
    title: '后天八卦', titleEn: 'Post-Heaven Bagua',
    source: '《说卦传》文王', tags: ['后天', '文王', '方位'], level: '中级', levelNum: 2,
    desc: '震东离南坎北兑西，后天数1-9，节气对应，《说卦传》"帝出乎震"原文，后天为用。',
    endpoint: '/api/v1/knowledge/bagua/houtian',
  },
  {
    id: 'bagua_xiangyi', category: '八卦易学', icon: '象', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#38c888 100%)',
    title: '八卦完整象意', titleEn: 'Eight Trigrams Symbolism',
    source: '《说卦传》', tags: ['象意', '家庭', '身体'], level: '中级', levelNum: 2,
    desc: '乾至兑八卦各含：自然·家庭·五行·身体·职业·《说卦传》原文·卦德（八卦取象歌）。',
    endpoint: '/api/v1/knowledge/bagua/xiangyi',
  },
  {
    id: 'gua64', category: '八卦易学', icon: '卦', iconBg: 'linear-gradient(135deg,#b85c00 0%,#e89040 100%)',
    title: '六十四卦全解', titleEn: 'Sixty-Four Hexagrams',
    source: '《周易》', tags: ['六十四卦', '卦辞', '序卦'], level: '高级', levelNum: 3,
    desc: '全64卦：卦名·符号·上下卦·卦辞·吉凶·核心要义。文王卦序口诀"乾坤屯蒙需讼师…"',
    endpoint: '/api/v1/knowledge/bagua/64gua',
  },
  {
    id: 'jingfang', category: '八卦易学', icon: '京', iconBg: 'linear-gradient(135deg,#6a3d8a 0%,#9b59b6 100%)',
    title: '京房八宫卦', titleEn: 'Jingfang Eight Palaces',
    source: '《京氏易传》', tags: ['八宫', '世应', '六亲'], level: '高级', levelNum: 3,
    desc: '汉代京房创八宫卦体系，64卦分八宫，世应爻，六亲纳甲，六爻预测的核心架构。',
    endpoint: '/api/v1/knowledge/bagua/jingfang',
  },
  {
    id: 'yizhuan', category: '八卦易学', icon: '翼', iconBg: 'linear-gradient(135deg,#1c1008 0%,#8a6840 100%)',
    title: '易经十翼精华', titleEn: 'Ten Wings of I Ching',
    source: '《易传》', tags: ['系辞', '说卦', '文言'], level: '高级', levelNum: 3,
    desc: '彖传·象传·系辞·文言·说卦·序卦·杂卦七种十篇。"天行健君子以自强不息"等经典名言。',
    endpoint: '/api/v1/knowledge/bagua/yizhuan',
  },
  // ── 星宿天文 ──
  {
    id: 'sixiang', category: '星宿天文', icon: '龙', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#4a9ee0 100%)',
    title: '四象体系', titleEn: 'Four Divine Animals',
    source: '《史记·天官书》', tags: ['四象', '四灵', '方位'], level: '中级', levelNum: 2,
    desc: '东方青龙·南方朱雀·西方白虎·北方玄武：七宿·颜色·五行·季节·象征完整体系。',
    endpoint: '/api/v1/knowledge/xingxiu/sixiang',
  },
  {
    id: 'xiu28', category: '星宿天文', icon: '宿', iconBg: 'linear-gradient(135deg,#b5361e 0%,#cc4428 100%)',
    title: '二十八宿全解', titleEn: 'Twenty-Eight Lunar Mansions',
    source: '《步天歌》《开元占经》', tags: ['禽星', '歌诀', '宜忌', '择日'], level: '高级', levelNum: 3,
    desc: '全28宿：禽星（角木蛟…）·五行·七曜·吉凶·吉凶歌诀·宜事忌事·出生命运·天文历史。',
    endpoint: '/api/v1/knowledge/xingxiu/28xiu',
  },
  {
    id: 'sanvuan', category: '星宿天文', icon: '垣', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#0a4c2c 100%)',
    title: '三垣体系', titleEn: 'Three Enclosures',
    source: '《隋书·天文志》', tags: ['紫微垣', '太微', '天市'], level: '高级', levelNum: 3,
    desc: '紫微垣（帝居北斗）·太微垣（朝廷政事）·天市垣（商业财经），与紫微斗数的渊源。',
    endpoint: '/api/v1/knowledge/xingxiu/sanvuan',
  },
  {
    id: 'qizheng', category: '星宿天文', icon: '政', iconBg: 'linear-gradient(135deg,#b85c00 0%,#d47010 100%)',
    title: '七政（日月五星）', titleEn: 'Seven Luminaries',
    source: '《史记·天官书》', tags: ['七政', '占星', '七曜'], level: '高级', levelNum: 3,
    desc: '太阳·太阴·荧惑·辰星·岁星·太白·镇星：命理意义·占星应用·七曜星期制来源。',
    endpoint: '/api/v1/knowledge/xingxiu/qizheng',
  },
  {
    id: 'qinxing', category: '星宿天文', icon: '禽', iconBg: 'linear-gradient(135deg,#6a3d8a 0%,#8e44ad 100%)',
    title: '禽星演禽', titleEn: 'Bird Star System',
    source: '《五星二十八宿神形图》', tags: ['禽星', '七曜', '演禽'], level: '精通', levelNum: 4,
    desc: '28宿配七曜动物（角木蛟·亢金龙…），演禽推命之术，七曜星期与禽星的对应关系。',
    endpoint: '/api/v1/knowledge/xingxiu/qinxing',
  },
  {
    id: 'fenye', category: '星宿天文', icon: '野', iconBg: 'linear-gradient(135deg,#1c1008 0%,#4a3018 100%)',
    title: '分野理论', titleEn: 'Star-Region Correspondence',
    source: '《开元占经》', tags: ['分野', '地域', '星土'], level: '精通', levelNum: 4,
    desc: '二十八宿与中国地域分野对应：角亢→郑，心宿→宋，参宿→晋…天象对地域灾祥的预测。',
    endpoint: '/api/v1/knowledge/xingxiu/fenye',
  },
  // ── 十神神煞 ──
  {
    id: 'shishen_all', category: '十神神煞', icon: '神', iconBg: 'linear-gradient(135deg,#b5361e 0%,#7c1e0c 100%)',
    title: '十神完整体系', titleEn: 'Ten Gods System',
    source: '《子平真诠》', tags: ['十神', '六亲', '断法'], level: '中级', levelNum: 2,
    desc: '比肩至偏印十神：六亲·象意·正负面·职业·财运·感情·断法，《子平真诠》精华。',
    endpoint: '/api/v1/knowledge/shishen/all',
  },
  {
    id: 'shensha', category: '十神神煞', icon: '煞', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#2878c0 100%)',
    title: '重要神煞大全', titleEn: 'Major Divine Influences',
    source: '《神峰通考》《星平会海》', tags: ['天乙', '文昌', '驿马', '空亡'], level: '高级', levelNum: 3,
    desc: '16大神煞：天乙贵人·文昌·太极·将星·华盖·驿马·桃花·孤寡·羊刃·魁罡·天德·月德·空亡。',
    endpoint: '/api/v1/knowledge/shishen/shensha',
  },
  {
    id: 'liuqin', category: '十神神煞', icon: '亲', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#24a070 100%)',
    title: '六亲宫位论断', titleEn: 'Six Relations Analysis',
    source: '《三命通会》', tags: ['六亲', '宫位', '断法'], level: '高级', levelNum: 3,
    desc: '父母·妻子·丈夫·子女·兄弟·上司六亲：取法宫位·旺衰判断·断法口诀全解。',
    endpoint: '/api/v1/knowledge/shishen/liuqin',
  },
  {
    id: 'changsheng', category: '十神神煞', icon: '生', iconBg: 'linear-gradient(135deg,#b85c00 0%,#e89040 100%)',
    title: '十二长生十二宫', titleEn: 'Twelve Growth Stages',
    source: '《渊海子平》', tags: ['长生', '帝旺', '墓绝'], level: '中级', levelNum: 2,
    desc: '长生·沐浴·冠带·临官·帝旺·衰·病·死·墓·绝·胎·养，各阶段象意·断法·人生对应。',
    endpoint: '/api/v1/knowledge/shishen/changsheng',
  },
  {
    id: 'dayun', category: '十神神煞', icon: '运', iconBg: 'linear-gradient(135deg,#6a3d8a 0%,#9b59b6 100%)',
    title: '大运流年断法', titleEn: 'Major & Annual Cycles',
    source: '《滴天髓》', tags: ['大运', '流年', '应期'], level: '高级', levelNum: 3,
    desc: '大运起法·行运吉凶·天干地支分管前后五年·流年太岁·伏吟反吟应期精要。',
    endpoint: '/api/v1/knowledge/shishen/dayun',
  },
  // ── 四柱命理 ──
  {
    id: 'bazi_gejv', category: '四柱命理', icon: '格', iconBg: 'linear-gradient(135deg,#b5361e 0%,#cc4428 100%)',
    title: '八字格局体系', titleEn: 'BaZi Pattern System',
    source: '《子平真诠》', tags: ['格局', '正格', '用神'], level: '高级', levelNum: 3,
    desc: '正官·七杀·正财·偏财·食神·伤官·正印·偏印八格，月令用神，身强弱判断，用神五法。',
    endpoint: '/api/v1/knowledge/classical/bazi-gejv',
  },
  {
    id: 'tiahou', category: '四柱命理', icon: '候', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#4a9ee0 100%)',
    title: '调候用神精解', titleEn: 'Climate-Based God',
    source: '《穷通宝鉴》', tags: ['调候', '寒暖', '燥湿'], level: '精通', levelNum: 4,
    desc: '《穷通宝鉴》寒冬喜丙火炎夏喜壬水，12月份各日干调候用神完整对照，是命理最实用理论之一。',
    endpoint: '/api/v1/knowledge/classical/bazi-tiahou',
  },
  {
    id: 'rizhupan', category: '四柱命理', icon: '主', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#0a4c2c 100%)',
    title: '日主分析体系', titleEn: 'Day Master Analysis',
    source: '《滴天髓》', tags: ['日主', '强弱', '格局'], level: '高级', levelNum: 3,
    desc: '十干日主性格·喜忌用神·经典命例诠释，结合月令强弱判断，专旺从化高级理论。',
    endpoint: '/api/v1/knowledge/classical/rizhupan',
  },
  // ── 六爻占卜 ──
  {
    id: 'liuyao_topics', category: '六爻占卜', icon: '☵', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#0a3260 100%)',
    title: '六爻用神取法', titleEn: 'LiuYao God Selection',
    source: '《增删卜易》', tags: ['用神', '六亲', '断事'], level: '中级', levelNum: 2,
    desc: '12类占事用神：求财·求官·婚嫁·疾病·出行·官司等，各类用神取法和断法要诀。',
    endpoint: '/api/v1/knowledge/classical/liuyao-topics',
  },
  {
    id: 'liuyao_rules', category: '六爻占卜', icon: '典', iconBg: 'linear-gradient(135deg,#b5361e 0%,#7c1e0c 100%)',
    title: '六爻经典口诀', titleEn: 'LiuYao Classic Rules',
    source: '《卜筮正宗》《黄金策》', tags: ['口诀', '断法', '精义'], level: '高级', levelNum: 3,
    desc: '《增删》《卜筮正宗》《黄金策》精华16条断法口诀，用神旺衰·动变·日月建综合运用。',
    endpoint: '/api/v1/knowledge/classical/liuyao-rules',
  },
  {
    id: 'liuyao_gods', category: '六爻占卜', icon: '六', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#24a070 100%)',
    title: '六神详断', titleEn: 'Six Spirits Analysis',
    source: '《京氏易传》', tags: ['六神', '青龙', '白虎'], level: '高级', levelNum: 3,
    desc: '青龙·白虎·朱雀·玄武·勾陈·腾蛇六神：各神象意·人事应象·与六亲结合断法。',
    endpoint: '/api/v1/knowledge/classical/liuyao-gods',
  },
  {
    id: 'liuyao_timing', category: '六爻占卜', icon: '期', iconBg: 'linear-gradient(135deg,#b85c00 0%,#d47010 100%)',
    title: '六爻应期推算', titleEn: 'LiuYao Timing Method',
    source: '《卜筮正宗》', tags: ['应期', '旺衰', '空亡'], level: '精通', levelNum: 4,
    desc: '病药原则·静爻动爻应期·进退神·旬空出空·伏神引发，六爻最难的应期推算全论。',
    endpoint: '/api/v1/knowledge/classical/liuyao-timing',
  },
  // ── 奇门遁甲 ──
  {
    id: 'qm_sibao', category: '奇门遁甲', icon: '✦', iconBg: 'linear-gradient(135deg,#1c1008 0%,#b5361e 100%)',
    title: '四盘体系', titleEn: 'Four Board System',
    source: '《奇门遁甲统宗》', tags: ['九星', '八门', '八神'], level: '中级', levelNum: 2,
    desc: '天（九星）×地（九宫）×人（八门）×神（八神）四盘，核心断法：静看值符值使，动看方向。',
    endpoint: '/api/v1/knowledge/classical/qimen-bamen',
  },
  {
    id: 'qm_jiuxing', category: '奇门遁甲', icon: '星', iconBg: 'linear-gradient(135deg,#b5361e 0%,#e05535 100%)',
    title: '九星详解', titleEn: 'Nine Stars',
    source: '《烟波钓叟赋》', tags: ['九星', '临宫口诀', '断法'], level: '高级', levelNum: 3,
    desc: '天蓬至天英九星：五行·吉凶·人事象意·临宫口诀，辅禽心任为四吉，蓬芮柱为三凶。',
    endpoint: '/api/v1/knowledge/classical/qimen-jiuxing',
  },
  {
    id: 'qm_yanbo', category: '奇门遁甲', icon: '波', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#2878c0 100%)',
    title: '《烟波钓叟赋》', titleEn: 'Yanbo Classical Text',
    source: '《烟波钓叟赋》', tags: ['口诀', '经典', '全文'], level: '精通', levelNum: 4,
    desc: '奇门遁甲最重要的经典口诀集，三奇得使·伏吟反吟·八门吉凶·值符值使，12条核心口诀。',
    endpoint: '/api/v1/knowledge/classical/qimen-yanbo',
  },
  {
    id: 'qm_gejv', category: '奇门遁甲', icon: '格', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#24a070 100%)',
    title: '奇门格局体系', titleEn: 'QiMen Patterns',
    source: '《奇门秘籍大全》', tags: ['格局', '三奇', '伏吟'], level: '精通', levelNum: 4,
    desc: '三奇得使·三奇入墓·六仪击刑·青龙返首·飞鸟跌穴·伏吟·反吟·天网四张等11大格局。',
    endpoint: '/api/v1/knowledge/classical/qimen-gejv',
  },
  // ── 风水地理 ──
  {
    id: 'xuankong', category: '风水地理', icon: '空', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#4a9ee0 100%)',
    title: '玄空飞星', titleEn: 'Xuan Kong Flying Stars',
    source: '《沈氏玄空学》', tags: ['飞星', '旺山旺向', '九运'], level: '高级', levelNum: 3,
    desc: '飞星盘山星向星，旺山旺向·上山下水·双星到向，三元九运（九运2024-2043），紫白飞星。',
    endpoint: '/api/v1/knowledge/classical/fengshui-extended',
  },
  {
    id: 'bayuan', category: '风水地理', icon: '宅', iconBg: 'linear-gradient(135deg,#b5361e 0%,#cc4428 100%)',
    title: '八宅派风水', titleEn: 'Eight Mansions Feng Shui',
    source: '《八宅明镜》', tags: ['八宅', '命卦', '东西四命'], level: '中级', levelNum: 2,
    desc: '东四命坎离震巽，西四命乾坤艮兑。生气·天医·延年·伏位四吉，祸害·五鬼·六煞·绝命四凶。',
    endpoint: '/api/v1/knowledge/classical/bayuan',
  },
  {
    id: 'xingshi', category: '风水地理', icon: '龙', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#0a4c2c 100%)',
    title: '形家风水', titleEn: 'Landscape Feng Shui',
    source: '《葬经》郭璞', tags: ['龙脉', '砂水', '穴法'], level: '精通', levelNum: 4,
    desc: '龙脉识别·砂水格局·明堂·穴法四种（窝钳乳突），"青龙蜿蜒白虎驯顺朱雀翔舞玄武垂头"。',
    endpoint: '/api/v1/knowledge/advanced/xingshi',
  },
  // ── 高级系统 ──
  {
    id: 'ziwei', category: '高级系统', icon: '紫', iconBg: 'linear-gradient(135deg,#6a3d8a 0%,#9b59b6 100%)',
    title: '紫微斗数', titleEn: 'Purple Star Astrology',
    source: '陈希夷《紫微斗数全书》', tags: ['紫微', '十二宫', '四化'], level: '高级', levelNum: 3,
    desc: '十二宫（命宫至父母宫）·主要星曜（紫微至破军）·四化（禄权科忌），南派命理核心体系。',
    endpoint: '/api/v1/knowledge/advanced/ziwei',
  },
  {
    id: 'meihua', category: '高级系统', icon: '梅', iconBg: 'linear-gradient(135deg,#b5361e 0%,#e05535 100%)',
    title: '梅花易数', titleEn: 'Plum Blossom Numerology',
    source: '邵雍《梅花易数》', tags: ['体用', '起卦', '断法'], level: '高级', levelNum: 3,
    desc: '宋代邵雍以先天数起卦，体克用主吉，用克体主凶，心为太极，一念即可起卦断事。',
    endpoint: '/api/v1/knowledge/advanced/meihua',
  },
  {
    id: 'daliuren', category: '高级系统', icon: '壬', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#0a3260 100%)',
    title: '大六壬', titleEn: 'Great Liuren Divination',
    source: '《大六壬指南》', tags: ['四课三传', '天将', '月将'], level: '精通', levelNum: 4,
    desc: '三式之一（与奇门太乙并称），四课三传（初传现在·中传过程·末传结果），十二天将断法。',
    endpoint: '/api/v1/knowledge/advanced/daliuren',
  },
  {
    id: 'bazi_deep', category: '高级系统', icon: '深', iconBg: 'linear-gradient(135deg,#b85c00 0%,#7a3600 100%)',
    title: '八字高级论命', titleEn: 'Advanced BaZi Theory',
    source: '《滴天髓》《三命通会》', tags: ['专旺', '从化', '格局清浊'], level: '精通', levelNum: 4,
    desc: '五行平衡论·有病方贵·格局清浊·通关格·从化真假辨·专旺五局（曲直炎上从革润下稼穑）。',
    endpoint: '/api/v1/knowledge/advanced/bazi-deep',
  },
  // ── 实战断法 ──
  {
    id: 'steps', category: '实战断法', icon: '步', iconBg: 'linear-gradient(135deg,#b5361e 0%,#cc4428 100%)',
    title: '断命实战步骤', titleEn: 'Divination Procedures',
    source: '综合实践', tags: ['步骤', '八字', '六爻', '奇门'], level: '中级', levelNum: 2,
    desc: '八字7步·六爻5步·奇门4步·风水4步，系统的实战操作流程，入门必读。',
    endpoint: '/api/v1/knowledge/practical/steps',
  },
  {
    id: 'caiyun', category: '实战断法', icon: '财', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#24a070 100%)',
    title: '财运断法大全', titleEn: 'Wealth Analysis',
    source: '《三命通会》综合', tags: ['财运', '求财', '风水财位'], level: '高级', levelNum: 3,
    desc: '八字财运·六爻妻财爻·风水财位三法合参，财星旺弱·群劫争财·财库冲开断法精解。',
    endpoint: '/api/v1/knowledge/practical/caiyun',
  },
  {
    id: 'ganqing', category: '实战断法', icon: '情', iconBg: 'linear-gradient(135deg,#6a3d8a 0%,#8e44ad 100%)',
    title: '感情婚姻断法', titleEn: 'Relationship Analysis',
    source: '综合实践', tags: ['婚姻', '感情', '合婚'], level: '高级', levelNum: 3,
    desc: '八字看妻夫·日支配偶宫·六爻官鬼妻财爻·奇门六合神，合婚参考，感情挽回实战。',
    endpoint: '/api/v1/knowledge/practical/ganqing',
  },
  {
    id: 'yingqi', category: '实战断法', icon: '期', iconBg: 'linear-gradient(135deg,#1e5c96 0%,#2878c0 100%)',
    title: '应期推算综合', titleEn: 'Timing Prediction',
    source: '《奇门法穷》综合', tags: ['应期', '三法', '快慢'], level: '精通', levelNum: 4,
    desc: '八字大运流年·六爻用神旺衰法·奇门值符三法（相冲相刑旬空），三种体系的应期精要。',
    endpoint: '/api/v1/knowledge/practical/yingqi',
  },
  {
    id: 'zeri', category: '实战断法', icon: '日', iconBg: 'linear-gradient(135deg,#b85c00 0%,#e89040 100%)',
    title: '择日选时精要', titleEn: 'Auspicious Date Selection',
    source: '《协纪辨方书》', tags: ['择日', '婚嫁', '动土'], level: '中级', levelNum: 2,
    desc: '建除十二神·黄道黑道·天德月德·婚嫁开业动土择日要点，奇门三吉门择时法。',
    endpoint: '/api/v1/knowledge/practical/zeri',
  },
  {
    id: 'mingjia', category: '实战断法', icon: '典', iconBg: 'linear-gradient(135deg,#1c1008 0%,#4a3018 100%)',
    title: '名家论断精华', titleEn: 'Classic Masters Quotes',
    source: '子平真诠·滴天髓等', tags: ['名言', '口诀', '精华'], level: '精通', levelNum: 4,
    desc: '《子平真诠》《滴天髓》《穷通宝鉴》《卜筮正宗》《增删卜易》《烟波钓叟赋》七家精华语录。',
    endpoint: '/api/v1/knowledge/practical/mingjia',
  },

  // ── 深度专题 ──
  {
    id: 'yanbo_full', category: '深度专题', icon: '赋', iconBg: 'linear-gradient(135deg,#b5361e 0%,#7c1e0c 100%)',
    title: '《烟波钓叟赋》全文', titleEn: 'Yanbo Classical Text Full',
    source: '《烟波钓叟赋》', tags: ['完整原文', '逐句解析'], level: '精通', levelNum: 4,
    desc: '奇门入门必背经典全文，逐句原文+现代解析，从阴阳二遁到三奇得使，完整16段精义。',
    endpoint: '/api/v1/knowledge/classical/qimen-yanbo-full',
  },
  {
    id: 'qimen_zhaiji', category: '深度专题', icon: '吉', iconBg: 'linear-gradient(135deg,#1a7a52 0%,#0a4c2c 100%)',
    title: '奇门择吉实战', titleEn: 'QiMen Practical Application',
    source: '《奇门真髓》', tags: ['出行', '谈判', '择时'], level: '高级', levelNum: 3,
    desc: '出行择吉·谈判签约·求财方位·健康调理四大实战场景，逐步操作流程，三吉门应用指南。',
    endpoint: '/api/v1/knowledge/classical/qimen-zhaiji',
  },
  {
    id: 'liushen_full', category: '深度专题', icon: '兽', iconBg: 'linear-gradient(135deg,#6a3d8a 0%,#9b59b6 100%)',
    title: '六神人事象意全解', titleEn: 'Six Spirits Complete Guide',
    source: '《京氏易传》', tags: ['青龙', '白虎', '六亲配合'], level: '高级', levelNum: 3,
    desc: '青龙喜庆·朱雀口舌·勾陈迟滞·腾蛇虚惊·白虎血光·玄武暗昧，六神×六亲结合断法+应期。',
    endpoint: '/api/v1/knowledge/classical/liuyao-gods-full',
  },
  {
    id: 'liuyao_yingqi_deep', category: '深度专题', icon: '黄', iconBg: 'linear-gradient(135deg,#b85c00 0%,#7a3600 100%)',
    title: '《黄金策》应期精要', titleEn: 'Huang Jin Ce Timing',
    source: '《黄金策》《卜筮正宗》', tags: ['应期', '进退神', '空亡'], level: '精通', levelNum: 4,
    desc: '旺相速应·迟慢难应·两动相克·化进退神·回头生克·《黄金策》5条黄金口诀精解。',
    endpoint: '/api/v1/knowledge/classical/liuyao-yingqi-deep',
  },
  {
    id: 'ziwei_zhuxing', category: '深度专题', icon: '主', iconBg: 'linear-gradient(135deg,#6a3d8a 0%,#4a1e6a 100%)',
    title: '紫微十四主星论', titleEn: 'Ziwei 14 Main Stars',
    source: '《紫微斗数全书》', tags: ['主星', '坐命', '四化'], level: '精通', levelNum: 4,
    desc: '紫微至破军十四主星：各星坐命性格·事业·感情·财运·四化（禄权科忌）吉凶变化完整论断。',
    endpoint: '/api/v1/knowledge/classical/ziwei-zhuxing',
  },
  {
    id: 'meihua_qigua', category: '深度专题', icon: '梅', iconBg: 'linear-gradient(135deg,#b5361e 0%,#6a1e0c 100%)',
    title: '梅花七种起卦法', titleEn: 'Meihua Divination Methods',
    source: '邵雍《梅花易数》', tags: ['年月日时', '物数', '体用断法'], level: '高级', levelNum: 3,
    desc: '年月日时法·物数法·字数法·声数法·方位法·时辰法·万物皆可起卦，体用断法五诀精要。',
    endpoint: '/api/v1/knowledge/classical/meihua-qigua',
  },
  {
    id: 'liuyao_yingqi_full', category: '深度专题', icon: '期', iconBg: 'linear-gradient(135deg,#b85c00 0%,#7a3600 100%)',
    title: '六爻应期速查全论', titleEn: 'LiuYao Timing Complete',
    source: '《黄金策》《增删卜易》', tags: ['应期五诀', '干支对应', '快慢'], level: '精通', levelNum: 4,
    desc: '旺相发动当日应·空亡出旬应·入墓冲开应，五行干支应期对应表，《黄金策》应期五诀精要。',
    endpoint: '/api/v1/knowledge/classical/liuyao-yingqi-full',
  },
  {
    id: 'ziwei_deep', category: '深度专题', icon: '命', iconBg: 'linear-gradient(135deg,#6a3d8a 0%,#4a1e6a 100%)',
    title: '紫微斗数深度', titleEn: 'Ziwei Deep Analysis',
    source: '《紫微斗数全书》', tags: ['命宫主星', '四化', '大限', '三方四正'], level: '精通', levelNum: 4,
    desc: '14主星坐命判断·四化深论（化禄权科忌）·三方四正·大限小限流年盘，系统深入论命。',
    endpoint: '/api/v1/knowledge/advanced/ziwei-deep',
  },
  {
    id: 'meihua_deep', category: '深度专题', icon: '心', iconBg: 'linear-gradient(135deg,#b5361e 0%,#6a1e0c 100%)',
    title: '梅花易数深度', titleEn: 'Meihua Numerology Deep',
    source: '邵雍《梅花易数》', tags: ['起卦', '体用', '案例'], level: '精通', levelNum: 4,
    desc: '起卦七法详解·体用精义（克生比和）·互卦变卦·时间应验·邵雍折花案·梅花观雀案经典。',
    endpoint: '/api/v1/knowledge/advanced/meihua-deep',
  },
]

const CATEGORIES = ['全部', '基础理论', '天干地支', '八卦易学', '星宿天文', '十神神煞', '四柱命理', '六爻占卜', '奇门遁甲', '风水地理', '高级系统', '实战断法', '深度专题']

const LEVEL_META = {
  '入门': { color: '#1a7a52', bg: 'rgba(26,122,82,0.12)', num: 1 },
  '中级': { color: '#1e5c96', bg: 'rgba(30,92,150,0.12)', num: 2 },
  '高级': { color: '#b85c00', bg: 'rgba(184,92,0,0.12)',  num: 3 },
  '精通': { color: '#b5361e', bg: 'rgba(181,54,30,0.12)', num: 4 },
}

const CAT_META = {
  '基础理论': { color: '#1a7a52' }, '天干地支': { color: '#b5361e' },
  '八卦易学': { color: '#1e5c96' }, '星宿天文': { color: '#6a3d8a' },
  '十神神煞': { color: '#b85c00' }, '四柱命理': { color: '#b5361e' },
  '六爻占卜': { color: '#1e5c96' }, '奇门遁甲': { color: '#1c1008' },
  '风水地理': { color: '#1a7a52' }, '高级系统': { color: '#6a3d8a' },
  '实战断法': { color: '#b85c00' },
  '深度专题': { color: '#6a3d8a' },
}

/* ─────────────────────────────── Main Page ─────────────────────────────── */
export default function KnowledgePage() {
  const [cat, setCat]         = useState('全部')
  const [search, setSearch]   = useState('')
  const [openCard, setOpenCard] = useState(null)
  const [cardData, setCardData] = useState({})
  const [loading, setLoading]  = useState(false)
  const [levelFilter, setLevel] = useState('全部')
  const { notify } = useNotifyStore()

  const API_BASE = (() => {
    try { return JSON.parse(localStorage.getItem('bagua-settings')||'{}')?.state?.apiBaseUrl || 'http://localhost:8888' }
    catch { return 'http://localhost:8888' }
  })()

  const filtered = CATALOG.filter(c => {
    const matchCat   = cat === '全部' || c.category === cat
    const matchLv    = levelFilter === '全部' || c.level === levelFilter
    const matchSearch = !search || c.title.includes(search) || c.desc.includes(search) || c.tags.some(t => t.includes(search))
    return matchCat && matchLv && matchSearch
  })

  const openDetail = useCallback(async (card) => {
    setOpenCard(card)
    if (cardData[card.id]) return
    setLoading(true)
    try {
      const r = await fetch(API_BASE + card.endpoint)
      if (!r.ok) throw new Error('HTTP ' + r.status)
      const j = await r.json()
      setCardData(d => ({ ...d, [card.id]: j.data }))
    } catch (e) {
      notify('加载失败: ' + e.message, 'error')
    } finally { setLoading(false) }
  }, [cardData, API_BASE, notify])

  return (
    <div className="page kp-page">
      {/* ── Header ── */}
      <div className="kp-header">
        <div className="kp-header-left">
          <h1 className="kp-title">命理知识库</h1>
          <span className="kp-subtitle">Classical Metaphysics Encyclopedia · {CATALOG.length} 个模块</span>
        </div>
        <div className="kp-header-right">
          <div className="kp-search-wrap">
            <span className="kp-search-icon">🔍</span>
            <input className="kp-search" placeholder="搜索知识…" value={search}
              onChange={e => setSearch(e.target.value)} />
          </div>
          <select className="kp-level-select" value={levelFilter} onChange={e => setLevel(e.target.value)}>
            {['全部','入门','中级','高级','精通'].map(l => <option key={l}>{l}</option>)}
          </select>
        </div>
      </div>

      <div className="kp-body">
        {/* ── Category chips ── */}
        <div className="kp-cats">
          {CATEGORIES.map(c => (
            <button key={c} className={`kp-cat-chip ${cat===c?'active':''}`}
              onClick={() => setCat(c)}>{c}</button>
          ))}
        </div>

        {/* ── Results count ── */}
        <div className="kp-results-info">
          <span className="kp-count">{filtered.length}</span> 个模块
          {cat !== '全部' && <span className="kp-tag-pill" style={{ '--c': CAT_META[cat]?.color }}>{cat}</span>}
        </div>

        {/* ── Card grid ── */}
        <div className="kp-grid">
          {filtered.map(card => (
            <KnowledgeCard key={card.id} card={card} onClick={() => openDetail(card)} />
          ))}
        </div>
      </div>

      {/* ── Detail Modal ── */}
      {openCard && (
        <DetailModal
          card={openCard}
          data={cardData[openCard.id]}
          loading={loading}
          onClose={() => setOpenCard(null)}
        />
      )}
    </div>
  )
}

/* ─────────────────────────────── Knowledge Card ─────────────────────────── */
function KnowledgeCard({ card, onClick }) {
  const lv = LEVEL_META[card.level]
  const catColor = CAT_META[card.category]?.color || 'var(--accent)'

  return (
    <div className="kp-card" onClick={onClick}>
      {/* Preview area */}
      <div className="kp-card-preview" style={{ background: card.iconBg }}>
        <div className="kp-preview-glyph">{card.icon}</div>
        <div className="kp-preview-dots">
          {[...Array(6)].map((_,i) => <span key={i} className="kp-dot"/>)}
        </div>
        <div className="kp-preview-source">{card.source}</div>
      </div>

      {/* Content */}
      <div className="kp-card-body">
        <h3 className="kp-card-title">{card.title}</h3>
        <p className="kp-card-en">{card.titleEn}</p>

        {/* Tags row */}
        <div className="kp-card-tags">
          <span className="kp-tag-cat" style={{ '--c': catColor }}>{card.category}</span>
          {card.tags.slice(0, 3).map(t => (
            <span key={t} className="kp-tag-small">{t}</span>
          ))}
          <span className="kp-tag-level" style={{ '--c': lv.color, '--bg': lv.bg }}>
            <span className="kp-lv-num">{lv.num}</span>
            {card.level}
          </span>
        </div>

        {/* Description */}
        <p className="kp-card-desc">{card.desc}</p>

        {/* Footer */}
        <div className="kp-card-footer">
          <span className="kp-card-cta">查看详情 →</span>
        </div>
      </div>
    </div>
  )
}

/* ─────────────────────────────── Detail Modal ─────────────────────────── */
function DetailModal({ card, data, loading, onClose }) {
  const lv = LEVEL_META[card.level]

  return (
    <div className="kp-modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="kp-modal">
        {/* Modal header */}
        <div className="kp-modal-header" style={{ background: card.iconBg }}>
          <div className="kp-modal-header-inner">
            <div className="kp-modal-icon">{card.icon}</div>
            <div>
              <div className="kp-modal-title">{card.title}</div>
              <div className="kp-modal-en">{card.titleEn}</div>
              <div style={{ display:'flex', gap:'0.4rem', marginTop:'0.5rem', flexWrap:'wrap' }}>
                <span className="kp-modal-source">{card.source}</span>
                <span className="kp-tag-level" style={{ '--c': lv.color, '--bg': 'rgba(255,255,255,0.2)' }}>
                  <span className="kp-lv-num">{lv.num}</span> {card.level}
                </span>
              </div>
            </div>
          </div>
          <button className="kp-modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Modal body */}
        <div className="kp-modal-body">
          {loading && <div className="loading"><div className="spinner"/><p>加载知识库…</p></div>}
          {!loading && !data && (
            <div className="kp-modal-placeholder">
              <p style={{ color:'var(--text-muted)', fontFamily:'var(--font-serif)', textAlign:'center', padding:'2rem' }}>
                {card.desc}
              </p>
            </div>
          )}
          {!loading && data && (
            <ErrorBoundary>
              <DataRenderer data={data} card={card} />
              <div style={{ marginTop:'1.5rem' }}>
                <AiInterpretPanel module="knowledge" data={{ [card.id]: data }}
                  extraContext={`${card.category} — ${card.title}`} />
              </div>
            </ErrorBoundary>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─────────────────────────────── Data Renderer ─────────────────────────── */
function DataRenderer({ data, card }) {
  if (!data) return null

  // 64 hexagrams array
  if (Array.isArray(data)) return <ArrayRenderer items={data} card={card} />

  // Nested: gua_list array inside object (64gua endpoint)
  if (data.gua_list && Array.isArray(data.gua_list)) return (
    <div>
      {data.koujue && (
        <div style={{ padding:'0.75rem 1rem', background:'var(--accent-bg)', border:'1px solid var(--accent-dim)',
          borderRadius:'var(--r-md)', marginBottom:'1rem', fontFamily:'var(--font-serif)',
          fontSize:'var(--text-sm)', color:'var(--text-secondary)', lineHeight:1.88, whiteSpace:'pre-line' }}>
          <strong style={{ color:'var(--accent)' }}>文王六十四卦顺序口诀：</strong><br/>
          {data.koujue}
        </div>
      )}
      <ArrayRenderer items={data.gua_list} card={card} />
    </div>
  )

  // 28 mansions object  
  if (card.id === 'xiu28' && typeof data === 'object' && !Array.isArray(data)) {
    const entries = Object.entries(data)
    const [page28, setPage28] = useState(0)
    const PER = 7
    const slice = entries.slice(page28*PER, (page28+1)*PER)
    return (
      <div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(155px,1fr))', gap:'0.65rem' }}>
          {slice.map(([xiu, info]) => {
            const isAusp = info.吉凶?.includes('吉') && !info.吉凶?.includes('大凶')
            return (
              <div key={xiu} className="kp-data-card" style={{ borderLeft:`3px solid ${isAusp?'var(--jade)':'var(--accent)'}` }}>
                <div style={{ display:'flex', justifyContent:'space-between' }}>
                  <div className="kp-dc-title">{xiu}宿</div>
                  <span className={`badge ${isAusp?'badge-jade':'badge-red'}`} style={{ fontSize:'9px' }}>{info.吉凶}</span>
                </div>
                {info.禽星 && <div style={{ fontSize:'10px', color:'var(--cyan)', fontFamily:'var(--font-mono)' }}>{info.禽星}</div>}
                {info.宫 && <div style={{ fontSize:'var(--text-xs)', color:'var(--text-faint)' }}>{info.宫}</div>}
                {info.歌诀 && <p className="kp-dc-text">{info.歌诀.slice(0,50)}</p>}
                {info.出生命运 && <p className="kp-dc-text" style={{ color:'var(--orange)' }}>{info.出生命运.slice(0,30)}</p>}
              </div>
            )
          })}
        </div>
        <div className="kp-pagination">
          {[...Array(Math.ceil(entries.length/PER))].map((_,i) => (
            <button key={i} className={`kp-page-btn ${i===page28?'active':''}`} onClick={() => setPage28(i)}>
              {['青龙','玄武','白虎','朱雀'][i]}
            </button>
          ))}
        </div>
      </div>
    )
  }

  // Bagua xiangyi special renderer
  if (card.id === 'bagua_xiangyi' && data.xiangyi) {
    return (
      <div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(165px,1fr))', gap:'0.65rem', marginBottom:'1rem' }}>
          {Object.entries(data.xiangyi).map(([gua, info]) => (
            <div key={gua} className="kp-data-card" style={{ borderLeft:'3px solid var(--accent-dim)' }}>
              <div style={{ display:'flex', gap:'0.4rem', alignItems:'center', marginBottom:'0.3rem' }}>
                <span style={{ fontFamily:'var(--font-display)', fontSize:'1.4rem', color:'var(--accent)', lineHeight:1 }}>{info.符号}</span>
                <div>
                  <div className="kp-dc-title">{gua}</div>
                  <div style={{ fontSize:'9px', color:'var(--text-faint)' }}>{info.五行} · {info.阴阳}</div>
                </div>
              </div>
              <div style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', fontFamily:'var(--font-serif)', lineHeight:1.6, marginBottom:'0.25rem' }}>
                自然：{info.自然 || '—'} | 家庭：{info.家庭}
              </div>
              <p className="kp-dc-text" style={{ fontStyle:'italic', color:'var(--accent)', borderTop:'1px solid var(--border)', paddingTop:'0.25rem', marginTop:'0.25rem' }}>
                {info.卦德}
              </p>
            </div>
          ))}
        </div>
        {data.jiating && <ObjectRenderer data={data.jiating} card={card} />}
      </div>
    )
  }

  // Object data
  return <ObjectRenderer data={data} card={card} />
}

function ArrayRenderer({ items, card }) {
  const [page, setPage] = useState(0)
  const PER_PAGE = 16
  const total = Math.ceil(items.length / PER_PAGE)
  const slice = items.slice(page * PER_PAGE, (page+1) * PER_PAGE)

  return (
    <div>
      <div className="kp-data-grid">
        {slice.map((item, i) => (
          <div key={i} className="kp-data-card">
            {/* Try to find meaningful fields */}
            {item.名  && <div className="kp-dc-title">{item.名}</div>}
            {item.title && <div className="kp-dc-title">{item.title}</div>}
            {item.宿  && <div className="kp-dc-title">{item.宿}</div>}
            {item.符  && <div className="kp-dc-sym">{item.符}</div>}
            {item.吉凶 && (
              <span className={`badge ${item.吉凶?.includes('大吉')?'badge-jade':item.吉凶?.includes('凶')?'badge-red':'badge-muted'}`}
                style={{ fontSize:'var(--text-xs)' }}>{item.吉凶}</span>
            )}
            {item.卦辞 && <p className="kp-dc-text">{item.卦辞}</p>}
            {item.核心 && <p className="kp-dc-text">{item.核心}</p>}
            {item.歌诀 && <p className="kp-dc-text" style={{ fontFamily:'var(--font-serif)', fontStyle:'italic' }}>{item.歌诀.slice(0,40)}…</p>}
            {item.禽星 && <span className="kp-dc-tag">{item.禽星}</span>}
            {item.desc && <p className="kp-dc-text">{item.desc}</p>}
          </div>
        ))}
      </div>
      {total > 1 && (
        <div className="kp-pagination">
          {[...Array(total)].map((_,i) => (
            <button key={i} className={`kp-page-btn ${i===page?'active':''}`} onClick={() => setPage(i)}>
              {i+1}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function ObjectRenderer({ data }) {
  const entries = Object.entries(data)

  return (
    <div className="kp-obj-sections">
      {entries.map(([key, val]) => (
        <div key={key} className="kp-obj-section">
          <div className="kp-obj-key">
            <span className="kp-obj-key-dot"/>
            {key}
          </div>
          <ObjectValue val={val} />
        </div>
      ))}
    </div>
  )
}

function ObjectValue({ val }) {
  if (val === null || val === undefined) return null
  if (typeof val === 'string') return (
    <p className="kp-val-str">{val}</p>
  )
  if (typeof val === 'number') return (
    <span className="kp-val-num">{val}</span>
  )
  if (Array.isArray(val)) return (
    <div className="kp-val-arr">
      {val.map((item, i) => (
        <div key={i} className="kp-val-arr-item">
          <span className="kp-arr-bullet">·</span>
          <span style={{ fontFamily:'var(--font-serif)', fontSize:'var(--text-sm)', color:'var(--text-secondary)', lineHeight:1.75 }}>
            {typeof item === 'string' ? item : JSON.stringify(item)}
          </span>
        </div>
      ))}
    </div>
  )
  if (typeof val === 'object') return (
    <div className="kp-val-obj">
      {Object.entries(val).map(([k, v]) => (
        <div key={k} className="kp-val-obj-row">
          <span className="kp-val-obj-key">{k}</span>
          <span className="kp-val-obj-val" style={{ fontFamily:'var(--font-serif)' }}>
            {typeof v === 'string' ? v : typeof v === 'object' ? <ObjectValue val={v}/> : String(v)}
          </span>
        </div>
      ))}
    </div>
  )
  return <span className="kp-val-str">{String(val)}</span>
}

/* ─────────────────────────────── Specialized Renderers ─────────────────────── */

// 28 Mansions specialized display
function XiuCard({ key: k, xiu, info }) {
  const isAuspicious = info.吉凶?.includes('吉') && !info.吉凶?.includes('凶')
  return (
    <div className="kp-data-card" style={{
      borderLeft: `3px solid ${isAuspicious ? 'var(--jade)' : 'var(--accent)'}`,
    }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
        <div className="kp-dc-title">{xiu}</div>
        <span className={`badge ${isAuspicious?'badge-jade':'badge-red'}`} style={{ fontSize:'9px' }}>{info.吉凶}</span>
      </div>
      {info.禽星 && <div className="kp-dc-tag">{info.禽星}</div>}
      {info.歌诀 && <p className="kp-dc-text">{info.歌诀.slice(0,50)}…</p>}
    </div>
  )
}

// 64 Gua specialized display
function GuaCard({ gua }) {
  const isGood = gua.吉凶?.includes('大吉') || gua.吉凶 === '吉'
  return (
    <div className="kp-data-card" style={{ borderLeft:`3px solid ${isGood?'var(--jade)':gua.吉凶?.includes('大凶')?'var(--accent)':'var(--border)'}` }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div style={{ display:'flex', gap:'0.3rem', alignItems:'center' }}>
          <span style={{ fontFamily:'var(--font-display)', fontSize:'1.3rem', color:'var(--accent)', lineHeight:1 }}>{gua.符}</span>
          <div className="kp-dc-title">{gua.名}</div>
        </div>
        <span className={`badge ${isGood?'badge-jade':gua.吉凶?.includes('凶')?'badge-red':'badge-muted'}`} style={{ fontSize:'9px' }}>{gua.吉凶}</span>
      </div>
      <p className="kp-dc-text" style={{ fontFamily:'var(--font-serif)', fontStyle:'italic' }}>{gua.卦辞}</p>
      <p className="kp-dc-text">{gua.核心}</p>
    </div>
  )
}
