<template>
  <div class="page">

    <!-- 背景装饰 -->
    <div class="bg-decor">
      <div class="bagua-bg-1">☯</div>
      <div class="bagua-bg-2">☷</div>
    </div>

    <!-- 顶部导航 -->
    <header class="header-section">
      <div class="header-bagua">☯</div>
      <h1 class="header-title">{{ parsed.name || '命盘' }}分析报告</h1>
      <div class="header-tags">
        <span class="tag tag-jin">{{ parsed.gender === '男' ? '乾' : '坤' }}命</span>
        <span class="tag tag-shui">{{ info.year }}年</span>
        <span class="tag tag-mu">{{ info.month }}月{{ info.day }}日</span>
      </div>
      <div class="header-divider"></div>
    </header>

    <!-- 返回首页 -->
    <button class="btn-back" @click="$router.push('/')">← 返回首页</button>

    <!-- ===================== A. 四柱八字 ===================== -->
    <section class="card card-gold-border">
      <div class="card-header">
        <span class="card-icon">☰</span>
        <span class="card-title">四柱八字</span>
        <span class="card-title-en">BAZI</span>
      </div>
      <div class="divider-gold"></div>
      <div class="birth-detail">{{ info.year }}年 {{ info.month }}月{{ info.day }}日 {{ info.hour }}时 ({{ shichenDisplay }})</div>
      <div class="pillar-table">
        <div class="pillar-row pillar-header">
          <div class="pillar-th"></div><div class="pillar-th">年柱</div><div class="pillar-th">月柱</div><div class="pillar-th">日柱</div><div class="pillar-th">时柱</div>
        </div>
        <div class="pillar-row" v-for="row in pillarRows" :key="row.label">
          <div class="pillar-td pillar-label">{{ row.label }}</div>
          <div v-for="col in row.cells" :key="col.key" :class="['pillar-td', col.cls]">{{ col.val }}</div>
        </div>
      </div>
    </section>

    <!-- ===================== B. 五行分析 ===================== -->
    <section class="card">
      <div class="card-header">
        <span class="card-icon">⚖</span>
        <span class="card-title">五行分析</span>
        <span class="card-title-en">WUXING</span>
      </div>
      <div class="divider-gold"></div>
      <div class="wx-bars">
        <div v-for="item in wuxingItems" :key="item.name" class="wx-bar-row">
          <span :class="['tag', 'tag-' + item.cls]">{{ item.name }}</span>
          <div class="wx-bar-track">
            <div :class="['wx-bar-fill', 'wx-bar-' + item.cls]" :style="{ width: item.pct + '%' }"></div>
          </div>
          <span class="wx-score">{{ item.score }}分</span>
        </div>
      </div>
      <div class="strong-meter">
        <span class="meter-label">日主强弱</span>
        <div class="meter-track">
          <div class="meter-indicator" :style="{ left: strongPct + '%' }"></div>
        </div>
        <div class="meter-scale">
          <span>极弱</span><span>偏弱</span><span>中和</span><span>偏强</span><span>极强</span>
        </div>
        <span class="meter-result">{{ wuxing.strong_weak }}</span>
      </div>
      <div class="wuxing-cycle">
        <div class="cycle-row">
          <span class="cycle-label">相生：</span>
          <div class="cycle-items">
            <span class="tag tag-mu">木</span><span class="ca">→</span>
            <span class="tag tag-huo">火</span><span class="ca">→</span>
            <span class="tag tag-tu">土</span><span class="ca">→</span>
            <span class="tag tag-jin">金</span><span class="ca">→</span>
            <span class="tag tag-shui">水</span><span class="ca">→</span>
            <span class="tag tag-mu">木</span>
          </div>
        </div>
        <div class="cycle-row">
          <span class="cycle-label">相克：</span>
          <div class="cycle-items">
            <span class="tag tag-mu">木</span><span class="ca">⊘</span>
            <span class="tag tag-tu">土</span><span class="ca">⊘</span>
            <span class="tag tag-shui">水</span><span class="ca">⊘</span>
            <span class="tag tag-huo">火</span><span class="ca">⊘</span>
            <span class="tag tag-jin">金</span><span class="ca">⊘</span>
            <span class="tag tag-mu">木</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===================== C. 格局十神 ===================== -->
    <section class="card">
      <div class="card-header">
        <span class="card-icon">☵</span>
        <span class="card-title">格局 · 十神</span>
        <span class="card-title-en">GEJU &amp; SHISHEN</span>
      </div>
      <div class="divider-gold"></div>
      <div class="geju-display">
        <div class="geju-main">
          <span class="geju-name">{{ geju.name }}</span>
          <span class="geju-level">{{ geju.level }}级</span>
        </div>
        <p class="geju-desc">{{ geju.desc }}</p>
      </div>
      <div class="divider"></div>
      <div class="shishen-list">
        <div v-for="item in shishenPos" :key="item.position" class="shishen-item">
          <span class="ss-pos">{{ item.position }}</span>
          <div class="ss-detail">
            <span class="ss-gan">{{ item.gan }}</span>
            <span class="ss-arrow">→</span>
            <span :class="['tag', ssClass(item.shishen)]">{{ item.shishen }}</span>
            <span class="ss-wx">({{ item.wuxing }})</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===================== D. 用神忌神 ===================== -->
    <section class="card">
      <div class="card-header">
        <span class="card-icon">◎</span>
        <span class="card-title">用神 · 忌神</span>
        <span class="card-title-en">YONGSHEN</span>
      </div>
      <div class="divider-gold"></div>
      <div class="god-row">
        <div class="god-box god-good">
          <div class="god-badge">↑ 用神</div>
          <div class="god-values">
            <span v-for="v in (wuxing.xiyongshen||[]).slice(0,3)" :key="v" class="tag tag-mu">{{ v }}</span>
            <span v-if="!wuxing.xiyongshen?.length" class="text-dim">待分析</span>
          </div>
          <p class="god-tip">扶抑日主，调和五行</p>
        </div>
        <div class="god-box god-bad">
          <div class="god-badge god-badge-bad">↓ 忌神</div>
          <div class="god-values">
            <span v-for="v in (wuxing.jishen||[]).slice(0,3)" :key="v" class="tag tag-huo">{{ v }}</span>
            <span v-if="!wuxing.jishen?.length" class="text-dim">待分析</span>
          </div>
          <p class="god-tip">克制日主，需化解</p>
        </div>
      </div>
    </section>

    <!-- ===================== E. 大运流年 ===================== -->
    <section class="card">
      <div class="card-header">
        <span class="card-icon">⛵</span>
        <span class="card-title">大运 · 流年</span>
        <span class="card-title-en">DAYUN</span>
      </div>
      <div class="divider-gold"></div>
      <div class="yun-tabs">
        <button
          v-for="(d, i) in dayunDisplay.slice(0,8)" :key="i"
          :class="['yun-tab', yunIdx === i && 'active']"
          @click="yunIdx = i"
        >{{ d.age_start }}岁</button>
      </div>
      <div v-if="dayunDisplay[yunIdx]" class="yun-current">
        <div class="yun-info-row">
          <div class="yun-ganzhi-box">
            <span class="yun-ganzhi">{{ dayunDisplay[yunIdx].ganzhi }}</span>
            <span class="yun-step">第{{ dayunDisplay[yunIdx].step }}步大运</span>
          </div>
          <div class="yun-right">
            <span class="yun-range">{{ dayunDisplay[yunIdx].age_start }}~{{ dayunDisplay[yunIdx].age_end }}岁</span>
            <span :class="['tag', 'tag-' + wxClass(dayunDisplay[yunIdx].wuxing?.[0] || '')]">{{ dayunDisplay[yunIdx].wuxing }}</span>
          </div>
        </div>
        <p class="yun-desc">{{ dayunDisplay[yunIdx].desc }}</p>
      </div>
      <div v-if="liunianDisplay.length" class="liunian-wrap">
        <p class="liunian-label">流年（近5年）</p>
        <div class="liunian-grid">
          <div
            v-for="item in liunianDisplay"
            :key="item.year"
            :class="['liunian-cell', liunianClass(item.jixiong)]"
          >
            <span class="liunian-year">{{ item.year }}</span>
            <span class="liunian-ganzhi">{{ item.ganzhi }}</span>
            <span class="liunian-status">{{ item.jixiong }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===================== F. 婚姻姻缘 ===================== -->
    <section v-if="marriage" class="card">
      <div class="card-header">
        <span class="card-icon">♀</span>
        <span class="card-title">婚姻姻缘</span>
        <span class="card-title-en">MARRIAGE</span>
      </div>
      <div class="divider-gold"></div>
      <div class="info-rows">
        <div class="info-row"><span class="info-key">配偶星</span><span class="info-val text-gold">{{ marriage.spouse_star }}</span></div>
        <div class="info-row"><span class="info-key">五行匹配</span><span class="info-val">{{ marriage.wuxing_match }}</span></div>
        <div class="info-row"><span class="info-key">婚姻宫</span><span class="info-val">{{ marriage.marriage_palace }}</span></div>
        <div class="marriage-suggest">
          <span class="suggest-icon">💡</span>
          <span>{{ marriage.suggestion }}</span>
        </div>
      </div>
    </section>

    <!-- ===================== G. 健康养生 ===================== -->
    <section v-if="health" class="card">
      <div class="card-header">
        <span class="card-icon">☘</span>
        <span class="card-title">健康养生</span>
        <span class="card-title-en">HEALTH</span>
      </div>
      <div class="divider-gold"></div>
      <div class="health-section">
        <p class="health-section-title">五行缺失</p>
        <div class="health-lack">
          <span v-for="v in (health.lack_wuxing||[])" :key="v" class="tag tag-mu">{{ v }}</span>
          <span v-if="!health.lack_wuxing?.length" class="text-dim">五行俱全</span>
        </div>
      </div>
      <div class="health-section">
        <p class="health-section-title">养生重点</p>
        <div class="health-tips">
          <div v-for="tip in healthTips" :key="tip" class="health-tip">
            <span>☘</span><span>{{ tip }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===================== H. 六爻卦象 ===================== -->
    <section v-if="data.gua?.symbol" class="card">
      <div class="card-header">
        <span class="card-icon">☲</span>
        <span class="card-title">六爻卦象</span>
        <span class="card-title-en">LIUYAO</span>
      </div>
      <div class="divider-gold"></div>
      <div class="gua-display">
        <span class="gua-symbol-large">{{ data.gua.symbol }}</span>
        <div class="gua-info-col">
          <p class="gua-name">{{ data.gua.original_gua }}</p>
          <p class="text-dim">变卦：{{ data.gua.change_gua }}</p>
          <div class="gua-tags">
            <span :class="['tag', 'tag-' + wxClass(data.gua.element?.[0]||'')]">{{ data.gua.element }}行</span>
            <span class="tag tag-shui">动爻：{{ data.gua.dong_pos }}爻动</span>
          </div>
          <p class="text-dim">{{ data.gua.analysis }}</p>
        </div>
      </div>
    </section>

    <!-- ===================== I. 紫微斗数 ===================== -->
    <section v-if="ziwei" class="card card-gold-border">
      <div class="card-header">
        <span class="card-icon">☆</span>
        <span class="card-title">紫微斗数</span>
        <span class="card-title-en">ZIWEI</span>
      </div>
      <div class="divider-gold"></div>
      <div class="ziwei-minggong">
        <div class="zg-item"><span class="text-dim">命宫</span><span class="text-gold">{{ ziwei.minggong }}</span></div>
        <div class="zg-divider"></div>
        <div class="zg-item"><span class="text-dim">身宫</span><span class="text-gold">{{ ziwei.shengong }}</span></div>
      </div>
      <div class="stars-section">
        <p class="text-dim" style="margin-bottom:8px">十四主星</p>
        <div class="stars-grid">
          <div v-for="s in ziweiMainStars" :key="s.name||s" class="star-cell">
            <span>{{ s.name || s }}</span>
            <span class="tag tag-jin">{{ s.position || '' }}</span>
          </div>
        </div>
      </div>
      <div class="palace-section">
        <p class="text-dim" style="margin-bottom:8px">十二宫位</p>
        <div class="palace-grid">
          <div v-for="p in ziweiPalaces" :key="p.name||p" class="palace-cell">
            <span>{{ p.name || p }}</span>
            <span class="text-dim" style="font-size:11px">{{ p.main_stars || '' }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===================== J. 奇门遁甲 ===================== -->
    <section v-if="qimen" class="card card-gold-border">
      <div class="card-header">
        <span class="card-icon">☰</span>
        <span class="card-title">奇门遁甲</span>
        <span class="card-title-en">QIMEN</span>
      </div>
      <div class="divider-gold"></div>
      <div class="qimen-grid-wrap">
        <div class="qimen-grid">
          <div v-for="(cell, i) in qimenGrid" :key="i" class="qimen-cell">
            <span class="qc-gua">{{ cell.gua }}</span>
            <span class="qc-men">{{ cell.men }}</span>
            <span class="qc-shen">{{ cell.shen }}</span>
          </div>
        </div>
        <div class="qimen-legend">
          <div class="legend-item"><span class="text-dim">值符</span><span class="text-gold">{{ qimen.zhifu }}</span></div>
          <div class="legend-item"><span class="text-dim">值使</span><span class="text-gold">{{ qimen.zhishi }}</span></div>
          <div class="legend-item"><span class="text-dim">用神</span><span>{{ qimen.yongshen }}</span></div>
        </div>
      </div>
      <div v-if="qimenMen.length" class="bamen-row">
        <span class="text-dim" style="min-width:40px">八门</span>
        <div class="bamen-items">
          <span v-for="m in qimenMen" :key="m" :class="['tag', bamenClass(m)]">{{ m }}</span>
        </div>
      </div>
      <div v-if="qimenShen.length" class="bamen-row">
        <span class="text-dim" style="min-width:40px">八神</span>
        <div class="bamen-items">
          <span v-for="s in qimenShen" :key="s" class="tag tag-jin">{{ s }}</span>
        </div>
      </div>
    </section>

    <!-- ===================== K. 古籍引经据典 ===================== -->
    <section v-if="classicList.length" class="card card-gold-border">
      <div class="card-header">
        <span class="card-icon">📜</span>
        <span class="card-title">古籍引经据典</span>
        <span class="card-title-en">CLASSICS</span>
      </div>
      <div class="divider-gold"></div>
      <div class="classic-list">
        <div v-for="item in classicList" :key="item.source" class="classic-item">
          <div class="classic-source">
            <span class="text-gold">{{ item.source }}</span>
            <span class="text-dim">{{ item.chapter }}</span>
          </div>
          <p class="classic-quote">「{{ item.quote }}」</p>
        </div>
      </div>
    </section>

    <!-- ===================== L. LLM 智能解读 ===================== -->
    <section class="card llm-card">
      <div class="card-header">
        <span class="card-icon">✦</span>
        <span class="card-title">LLM 智能解读</span>
        <span class="card-title-en">AI INTERPRETATION</span>
      </div>
      <div class="divider-gold"></div>

      <div v-if="!llmLoading && !llmAnswer && !llmError" class="llm-pre">
        <p v-if="parsed.ask" class="ask-preview">
          <span class="ask-label">您的问题：</span><span>{{ parsed.ask }}</span>
        </p>
        <button class="btn-llm" @click="onLLMInterpret">
          <span>☯</span><span>请求 LLM 解读</span>
        </button>
      </div>

      <div v-if="llmLoading" class="loading-wrap">
        <span class="bagua-loading">☯</span><span>LLM 正在解读，请稍候...</span>
      </div>

      <div v-if="llmAnswer" class="llm-output">
        <div v-for="(content, key) in llmSections" :key="key" class="llm-section">
          <div class="llm-section-header">
            <span>{{ sectionIcon(key) }}</span>
            <span>{{ sectionTitle(key) }}</span>
          </div>
          <p class="llm-text">{{ content }}</p>
        </div>
        <div v-if="!Object.keys(llmSections).length && llmAnswer" class="llm-raw">
          <p class="llm-text">{{ llmAnswer }}</p>
        </div>
      </div>

      <div v-if="llmError" class="llm-error">⚠ {{ llmError }}</div>
    </section>

    <!-- 底部 -->
    <footer class="page-footer">
      <p>☯ 易学命理 · 仅供娱乐参考</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// ========== 解析传入数据 ==========
const parsed = ref({})
const data = computed(() => parsed.value.data || {})
const info = computed(() => data.value.birth_info || {})
const pillar = computed(() => data.value.pillar || {})
const wuxing = computed(() => data.value.wuxing || {})
const geju = computed(() => data.value.geju || {})
const shishenPos = computed(() => data.value.shishen?.positions || [])

const SHICHEN_MAP = [
  { name:'子',gua:'坎' },{ name:'丑',gua:'艮' },{ name:'寅',gua:'艮' },
  { name:'卯',gua:'震' },{ name:'辰',gua:'巽' },{ name:'巳',gua:'巽' },
  { name:'午',gua:'离' },{ name:'未',gua:'坤' },{ name:'申',gua:'坤' },
  { name:'酉',gua:'兑' },{ name:'戌',gua:'乾' },{ name:'亥',gua:'乾' },
]
const shichenDisplay = computed(() => {
  const h = info.value.hour || 0
  const sc = SHICHEN_MAP[h % 12]
  return sc ? `${sc.name}时（${sc.gua}卦）` : ''
})

// ========== 四柱表格 ==========
const WX_MAP = { '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水' }
const WX_CLS  = { '木':'mu','火':'huo','土':'tu','金':'jin','水':'shui' }

const pillarRows = computed(() => {
  const p = pillar.value
  const cells = (zhi) => {
    const w = WX_MAP[zhi] || ''
    return WX_CLS[w] || ''
  }
  return [
    {
      label: '干支',
      cells: [
        { key:'y', val: p.year||'', cls: '' },
        { key:'m', val: p.month||'', cls: '' },
        { key:'d', val: p.day||'', cls: '' },
        { key:'t', val: p.time||'', cls: '' },
      ]
    },
    {
      label: '天干',
      cells: [
        { key:'y', val: (p.year||'')[0]||'', cls: '' },
        { key:'m', val: (p.month||'')[0]||'', cls: '' },
        { key:'d', val: (p.day||'')[0]||'', cls: '' },
        { key:'t', val: (p.time||'')[0]||'', cls: '' },
      ]
    },
    {
      label: '地支',
      cells: [
        { key:'y', val: (p.year||'')[1]||'', cls: 'tag-'+(WX_CLS[WX_MAP[(p.year||'')[1]||'']] || '') },
        { key:'m', val: (p.month||'')[1]||'', cls: 'tag-'+(WX_CLS[WX_MAP[(p.month||'')[1]||'']] || '') },
        { key:'d', val: (p.day||'')[1]||'', cls: 'tag-'+(WX_CLS[WX_MAP[(p.day||'')[1]||'']] || '') },
        { key:'t', val: (p.time||'')[1]||'', cls: 'tag-'+(WX_CLS[WX_MAP[(p.time||'')[1]||'']] || '') },
      ]
    },
    {
      label: '五行',
      cells: [
        { key:'y', val: WX_MAP[(p.year||'')[1]||'']||'', cls: 'tag-'+(WX_CLS[WX_MAP[(p.year||'')[1]||'']] || '') },
        { key:'m', val: WX_MAP[(p.month||'')[1]||'']||'', cls: 'tag-'+(WX_CLS[WX_MAP[(p.month||'')[1]||'']] || '') },
        { key:'d', val: WX_MAP[(p.day||'')[1]||'']||'', cls: 'tag-'+(WX_CLS[WX_MAP[(p.day||'')[1]||'']] || '') },
        { key:'t', val: WX_MAP[(p.time||'')[1]||'']||'', cls: 'tag-'+(WX_CLS[WX_MAP[(p.time||'')[1]||'']] || '') },
      ]
    },
  ]
})

// ========== 五行柱状图 ==========
const wuxingItems = computed(() => {
  const score = wuxing.value.score || {}
  return ['木','火','土','金','水'].map(wx => ({
    name: wx,
    score: score[wx] || 0,
    pct: Math.min((score[wx] || 0) * 8, 100),
    cls: WX_CLS[wx] || '',
  }))
})

const strongPct = computed(() => {
  const sw = wuxing.value.strong_weak || ''
  if (sw.includes('极强')) return 90
  if (sw.includes('偏强') || sw.includes('旺')) return 72
  if (sw.includes('中和')) return 50
  if (sw.includes('偏弱') || sw.includes('衰')) return 28
  if (sw.includes('极弱')) return 10
  return 50
})

// ========== 大运 ==========
const dayunDisplay = computed(() => (data.value.dayun || []).slice(0, 10))
const yunIdx = ref(0)
const liunianDisplay = computed(() => {
  const d = dayunDisplay.value[yunIdx.value]
  return d?.liunian?.slice(0, 5) || []
})

// ========== 插件数据 ==========
const marriage = computed(() => data.value.plugins?.marriage?.details || null)
const health   = computed(() => data.value.plugins?.health?.details || null)
const ziwei    = computed(() => data.value.plugins?.ziwei?.details || null)
const qimen    = computed(() => data.value.plugins?.qimen?.details || null)

const healthTips = computed(() => {
  const tips = health.value?.health_tips || ''
  return tips.split(/[；;。\n]/).filter(t => t.trim()).slice(0, 5)
})

const ziweiMainStars = computed(() => {
  const stars = ziwei.value?.main_stars || []
  return stars.slice(0, 14).map(s => typeof s === 'string' ? { name: s, position: '' } : s)
})
const ziweiPalaces = computed(() => {
  const ps = ziwei.value?.palaces || ziwei.value?.gongs || []
  return ps.slice(0, 12).map(p => typeof p === 'string' ? { name: p, main_stars: '' } : p)
})

const qimenGrid = computed(() => {
  const g = qimen.value?.grid || qimen.value?.gongs || []
  return g.slice(0, 9).map(item => ({
    gua: item.gua || item.g || '',
    men: item.men || item.door || '',
    shen: item.shen || item.god || '',
  }))
})
const qimenMen  = computed(() => {
  const m = qimen.value?.men
  return m ? Object.values(m).slice(0, 8) : (qimen.value?.bamen || [])
})
const qimenShen = computed(() => {
  const s = qimen.value?.shen
  return s ? Object.values(s).slice(0, 8) : (qimen.value?.bashen || [])
})

// ========== 古籍引用 ==========
const classicList = computed(() => {
  const cd = data.value.plugins?.llm_rag?.book_sources || []
  return cd.map(r => ({
    source: r.source || '',
    chapter: r.chapter || '',
    quote: r.segment || r.quote || '',
  })).filter(r => r.quote)
})

// ========== LLM ==========
const llmLoading = ref(false)
const llmAnswer  = ref('')
const llmError  = ref('')
const llmSections = ref({})

function wxClass(w) {
  return WX_CLS[w] || ''
}
function ssClass(ss) {
  const m = { '正官':'tag-jin','七杀':'tag-huo','正印':'tag-shui','偏印':'tag-shui','正财':'tag-tu','偏财':'tag-tu','食神':'tag-mu','伤官':'tag-huo','比肩':'tag-mu','劫财':'tag-mu' }
  return m[ss] || 'tag-tu'
}
function liunianClass(s) {
  if (!s) return 'neutral'
  if (['吉','大吉','上吉','旺','好运'].some(k => s.includes(k))) return 'good'
  if (['凶','大凶','衰','败'].some(k => s.includes(k))) return 'bad'
  return 'neutral'
}
function bamenClass(m) {
  return ['开','生','休'].includes(m) ? 'tag-mu' : 'tag-huo'
}
function sectionIcon(k) {
  return { personality:'🧠', career:'📈', relationship:'💑', health:'☘' }[k] || '✦'
}
function sectionTitle(k) {
  return { personality:'性格分析', career:'事业财运', relationship:'婚姻感情', health:'健康养生' }[k] || ''
}

function parseSections(text) {
  const sections = {}
  const patterns = [
    { key:'personality',  labels:['性格','个性','禀性','为人'] },
    { key:'career',        labels:['事业','财运','财富','工作'] },
    { key:'relationship',  labels:['婚姻','感情','姻缘','爱情'] },
    { key:'health',        labels:['健康','养生','身体'] },
  ]
  for (const { key, labels } of patterns) {
    for (const label of labels) {
      const idx = text.indexOf(label)
      if (idx !== -1) {
        const start = idx + label.length
        let end = text.length
        patterns.forEach(({ labels: ls2 }) => {
          ls2.forEach(l3 => {
            if (l3 === label) return
            const i3 = text.indexOf(l3, start)
            if (i3 !== -1 && i3 < end) end = i3
          })
        })
        const content = text.substring(start, end).trim()
        if (content) sections[key] = content
        break
      }
    }
  }
  llmSections.value = sections
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

let typewriterTimer = null
let typewriterFull = ''
let typewriterIdx = 0

function startTypewriter() {
  if (typewriterIdx >= typewriterFull.length) {
    parseSections(typewriterFull)
    return
  }
  typewriterIdx += 3
  llmAnswer.value = typewriterFull.substring(0, typewriterIdx)
  typewriterTimer = setTimeout(startTypewriter, 40)
}

async function onLLMInterpret() {
  if (typewriterTimer) clearTimeout(typewriterTimer)
  llmLoading.value = true
  llmAnswer.value = ''
  llmError.value = ''
  llmSections.value = {}
  try {
    const res = await fetch(`${API_BASE}/api/llm/interpret`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pillar_json: data.value,
        question: parsed.value.ask || '',
        style: parsed.value.style || 'professional',
      }),
    })
    const json = await res.json()
    llmLoading.value = false
    if (json.code === 200) {
      typewriterFull = json.data?.answer || ''
      typewriterIdx = 0
      startTypewriter()
    } else {
      llmError.value = json.msg || '解读失败'
    }
  } catch (e) {
    llmLoading.value = false
    llmError.value = '网络请求失败，请确保后端服务已启动'
  }
}

onMounted(() => {
  try {
    parsed.value = JSON.parse(decodeURIComponent(atob(route.query.d)))
  } catch (e) {
    parsed.value = {}
  }
})

onUnmounted(() => {
  if (typewriterTimer) clearTimeout(typewriterTimer)
})
</script>

<style scoped>
.page {
  min-height: 100vh; background: #0D0F14; padding: 0 16px 80px;
  position: relative; overflow-x: hidden; max-width: 600px; margin: 0 auto;
}
.bg-decor { position: fixed; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 0; }
.bagua-bg-1, .bagua-bg-2 { position: absolute; font-size: 200px; color: #C9A84C; opacity: 0.04; font-weight: 100; }
.bagua-bg-1 { top: -40px; left: -40px; transform: rotate(15deg); }
.bagua-bg-2 { bottom: 200px; right: -40px; transform: rotate(-20deg); font-size: 280px; }

.header-section { position: relative; z-index: 1; text-align: center; padding: 40px 0 20px; }
.header-bagua { font-size: 40px; color: #C9A84C; margin-bottom: 8px; }
.header-title { font-size: 20px; color: #C9A84C; letter-spacing: 3px; }
.header-tags { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }
.header-divider { width: 60px; height: 2px; background: linear-gradient(90deg,transparent,#C9A84C,transparent); margin: 12px auto 0; }

.btn-back {
  display: inline-flex; align-items: center; gap: 4px; padding: 6px 14px;
  background: rgba(201,168,76,0.08); border: 1px solid rgba(201,168,76,0.2);
  border-radius: 20px; color: #C9A84C; font-size: 12px; cursor: pointer;
  margin: 0 0 16px 16px; transition: all 0.3s;
}
.btn-back:hover { background: rgba(201,168,76,0.15); }

.card {
  position: relative; z-index: 1; background: rgba(255,255,255,0.03);
  border: 1px solid rgba(201,168,76,0.12); border-radius: 16px;
  padding: 18px; margin-bottom: 14px; backdrop-filter: blur(8px);
}
.card-gold-border { border-color: rgba(201,168,76,0.3); }

.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.card-icon { font-size: 18px; color: #C9A84C; }
.card-title { color: #C9A84C; font-size: 15px; font-weight: 600; letter-spacing: 1px; }
.card-title-en { color: #555; font-size: 11px; margin-left: auto; letter-spacing: 1px; }
.divider-gold { height: 1px; background: linear-gradient(90deg,transparent,rgba(201,168,76,0.4),transparent); margin-bottom: 14px; }
.divider { height: 1px; background: rgba(255,255,255,0.05); margin: 14px 0; }

/* Tag */
.tag {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 11px; font-weight: 500; line-height: 1.6;
}
.tag-mu   { background: rgba(76,175,80,0.15);  color: #66BB6A; }
.tag-huo  { background: rgba(244,67,54,0.15);  color: #EF9A9A; }
.tag-tu   { background: rgba(255,193,7,0.15);  color: #FFD54F; }
.tag-jin  { background: rgba(255,255,255,0.1);  color: #E0E0E0; }
.tag-shui { background: rgba(33,150,243,0.15); color: #64B5F6; }
.text-gold { color: #C9A84C; }
.text-dim  { color: #666; font-size: 13px; }

/* 四柱 */
.birth-detail { text-align: center; color: #888; font-size: 13px; margin-bottom: 12px; }
.pillar-table { border: 1px solid rgba(201,168,76,0.15); border-radius: 10px; overflow: hidden; }
.pillar-row { display: grid; grid-template-columns: 60px repeat(4,1fr); }
.pillar-header { background: rgba(201,168,76,0.06); }
.pillar-th { text-align: center; color: #666; font-size: 11px; padding: 6px 2px; }
.pillar-td { text-align: center; font-size: 13px; padding: 8px 2px; color: #C0B498; border-top: 1px solid rgba(255,255,255,0.04); }
.pillar-label { color: #555; font-size: 11px; display: flex; align-items: center; justify-content: center; }

/* 五行 */
.wx-bars { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.wx-bar-row { display: flex; align-items: center; gap: 8px; }
.wx-bar-row > .tag { min-width: 28px; text-align: center; }
.wx-bar-track { flex: 1; height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; }
.wx-bar-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
.wx-bar-mu   { background: linear-gradient(90deg,#4CAF50,#66BB6A); }
.wx-bar-huo  { background: linear-gradient(90deg,#F44336,#EF9A9A); }
.wx-bar-tu   { background: linear-gradient(90deg,#FF9800,#FFD54F); }
.wx-bar-jin  { background: linear-gradient(90deg,#9E9E9E,#E0E0E0); }
.wx-bar-shui { background: linear-gradient(90deg,#2196F3,#64B5F6); }
.wx-score { color: #888; font-size: 11px; min-width: 32px; text-align: right; }

.strong-meter { margin: 16px 0; }
.meter-label { display: block; color: #666; font-size: 12px; margin-bottom: 6px; }
.meter-track { position: relative; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; }
.meter-indicator { position: absolute; top: -3px; width: 12px; height: 12px; background: #C9A84C; border-radius: 50%; transform: translateX(-50%); box-shadow: 0 0 8px rgba(201,168,76,0.5); transition: left 0.6s ease; }
.meter-scale { display: flex; justify-content: space-between; margin-top: 4px; }
.meter-scale span { color: #555; font-size: 10px; }
.meter-result { display: block; text-align: center; color: #C9A84C; font-size: 14px; margin-top: 6px; font-weight: 600; }

.wuxing-cycle { margin-top: 12px; }
.cycle-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }
.cycle-label { color: #555; font-size: 11px; min-width: 40px; }
.cycle-items { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.ca { color: #555; font-size: 10px; }

/* 格局 */
.geju-display { text-align: center; margin-bottom: 8px; }
.geju-main { display: flex; align-items: baseline; justify-content: center; gap: 8px; }
.geju-name { font-size: 22px; color: #C9A84C; font-weight: 700; }
.geju-level { font-size: 12px; color: #888; padding: 2px 8px; border: 1px solid rgba(201,168,76,0.2); border-radius: 10px; }
.geju-desc { color: #777; font-size: 12px; margin-top: 4px; line-height: 1.5; }

.shishen-list { display: flex; flex-direction: column; gap: 8px; }
.shishen-item { display: flex; align-items: center; gap: 10px; }
.ss-pos { color: #555; font-size: 11px; min-width: 30px; }
.ss-detail { display: flex; align-items: center; gap: 6px; }
.ss-gan { color: #C0B498; font-size: 13px; }
.ss-arrow { color: #555; font-size: 11px; }
.ss-wx { color: #555; font-size: 11px; }

/* 用神忌神 */
.god-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.god-box { padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); }
.god-good { background: rgba(76,175,80,0.05); border-color: rgba(76,175,80,0.15); }
.god-bad  { background: rgba(244,67,54,0.05); border-color: rgba(244,67,54,0.15); }
.god-badge { font-size: 12px; font-weight: 600; margin-bottom: 8px; }
.god-badge-bad { color: #EF9A9A; }
.god-values { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6px; }
.god-v { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
.god-tip { font-size: 11px; color: #555; }

/* 大运 */
.yun-tabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.yun-tab {
  padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);
  color: #666; font-size: 11px; cursor: pointer; background: transparent; transition: all 0.3s;
}
.yun-tab.active { border-color: #C9A84C; color: #C9A84C; background: rgba(201,168,76,0.08); }
.yun-current { background: rgba(201,168,76,0.04); border-radius: 10px; padding: 12px; margin-bottom: 12px; }
.yun-info-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.yun-ganzhi-box { display: flex; flex-direction: column; gap: 2px; }
.yun-ganzhi { font-size: 20px; color: #C9A84C; font-weight: 700; }
.yun-step { color: #555; font-size: 11px; }
.yun-right { text-align: right; }
.yun-range { color: #555; font-size: 11px; display: block; }
.yun-desc { color: #777; font-size: 12px; line-height: 1.5; }

.liunian-wrap { margin-top: 8px; }
.liunian-label { color: #555; font-size: 12px; margin-bottom: 8px; }
.liunian-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }
.liunian-cell {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 8px 2px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);
  background: rgba(255,255,255,0.02);
}
.liunian-cell.good { border-color: rgba(76,175,80,0.2); background: rgba(76,175,80,0.05); }
.liunian-cell.bad  { border-color: rgba(244,67,54,0.2); background: rgba(244,67,54,0.05); }
.liunian-year { color: #888; font-size: 10px; }
.liunian-ganzhi { color: #C0B498; font-size: 11px; }
.liunian-status { font-size: 10px; }
.liunian-cell.good .liunian-status { color: #66BB6A; }
.liunian-cell.bad  .liunian-status { color: #EF9A9A; }
.liunian-cell.neutral .liunian-status { color: #888; }

/* 信息列表 */
.info-rows { display: flex; flex-direction: column; gap: 8px; }
.info-row { display: flex; justify-content: space-between; align-items: center; }
.info-key { color: #555; font-size: 13px; }
.info-val { color: #C0B498; font-size: 13px; }
.marriage-suggest { margin-top: 8px; display: flex; align-items: flex-start; gap: 6px; font-size: 13px; color: #999; line-height: 1.5; }

/* 健康 */
.health-section { margin-bottom: 12px; }
.health-section-title { color: #555; font-size: 12px; margin-bottom: 8px; }
.health-lack { display: flex; gap: 6px; flex-wrap: wrap; }
.health-tips { display: flex; flex-direction: column; gap: 6px; }
.health-tip { display: flex; align-items: center; gap: 6px; color: #888; font-size: 13px; }

/* 六爻 */
.gua-display { display: flex; align-items: flex-start; gap: 16px; }
.gua-symbol-large { font-size: 56px; color: #C9A84C; line-height: 1; }
.gua-info-col { flex: 1; }
.gua-name { color: #C9A84C; font-size: 18px; font-weight: 600; margin-bottom: 4px; }
.gua-tags { display: flex; gap: 6px; flex-wrap: wrap; margin: 6px 0; }

/* 紫微 */
.ziwei-minggong { display: flex; justify-content: center; gap: 0; margin-bottom: 16px; }
.zg-item { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.zg-divider { width: 1px; background: rgba(255,255,255,0.06); }
.stars-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.star-cell { display: flex; flex-direction: column; align-items: center; gap: 3px; font-size: 12px; color: #C0B498; padding: 6px 2px; background: rgba(255,255,255,0.02); border-radius: 6px; }
.palace-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.palace-cell { display: flex; flex-direction: column; align-items: center; gap: 2px; font-size: 12px; color: #C0B498; padding: 6px 2px; }

/* 奇门 */
.qimen-grid-wrap { display: flex; flex-direction: column; gap: 12px; margin-bottom: 12px; }
.qimen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; }
.qimen-cell {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 8px 4px; background: rgba(255,255,255,0.03); border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.05);
}
.qc-gua { font-size: 16px; color: #C9A84C; }
.qc-men { font-size: 12px; color: #C0B498; }
.qc-shen { font-size: 10px; color: #555; }
.qimen-legend { display: flex; justify-content: space-around; }
.legend-item { display: flex; gap: 8px; align-items: center; font-size: 13px; }
.bamen-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.bamen-items { display: flex; gap: 6px; flex-wrap: wrap; }

/* 古籍 */
.classic-list { display: flex; flex-direction: column; gap: 12px; }
.classic-item { padding: 12px; background: rgba(201,168,76,0.03); border-radius: 10px; border: 1px solid rgba(201,168,76,0.08); }
.classic-source { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
.classic-quote { color: #999; font-size: 13px; line-height: 1.7; font-style: italic; }

/* LLM */
.llm-pre { text-align: center; }
.ask-preview { color: #777; font-size: 13px; margin-bottom: 12px; text-align: left; }
.ask-label { color: #555; margin-right: 4px; }
.btn-llm {
  display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px;
  background: linear-gradient(135deg, rgba(201,168,76,0.15), rgba(201,168,76,0.08));
  border: 1px solid rgba(201,168,76,0.3); border-radius: 24px;
  color: #C9A84C; font-size: 14px; cursor: pointer; transition: all 0.3s;
}
.btn-llm:hover { background: rgba(201,168,76,0.2); }
.loading-wrap { display: flex; align-items: center; justify-content: center; gap: 10px; color: #888; padding: 20px; }
.bagua-loading { display: inline-block; font-size: 24px; color: #C9A84C; animation: spin 2s linear infinite; }
@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }

.llm-output { display: flex; flex-direction: column; gap: 16px; }
.llm-section { background: rgba(255,255,255,0.02); border-radius: 12px; padding: 14px; border: 1px solid rgba(255,255,255,0.05); }
.llm-section-header { display: flex; align-items: center; gap: 6px; color: #C9A84C; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.llm-text { color: #B0A898; font-size: 14px; line-height: 1.8; white-space: pre-wrap; }
.llm-raw { background: rgba(255,255,255,0.02); border-radius: 12px; padding: 14px; }
.llm-error { color: #EF9A9A; font-size: 13px; padding: 10px; background: rgba(244,67,54,0.05); border-radius: 8px; }

.page-footer { text-align: center; color: #444; font-size: 12px; padding: 24px 0; }
</style>
