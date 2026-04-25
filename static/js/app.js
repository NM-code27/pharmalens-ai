'use strict';

let priceChart = null;
let _lastAnalysis = null;

// ── DOM refs ──
const drugInput   = document.getElementById('drugInput');
const priceInput  = document.getElementById('priceInput');
const marginInput = document.getElementById('marginInput');
const analyzeBtn  = document.getElementById('analyzeBtn');
const btnText     = document.getElementById('btnText');
const btnLoader   = document.getElementById('btnLoader');
const results     = document.getElementById('results');
const overlay     = document.getElementById('loadingOverlay');

// ── Quick fill chips ──
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    drugInput.value  = chip.dataset.drug;
    priceInput.value = chip.dataset.price || '';
    drugInput.focus();
  });
});

// ── Sidebar toggle ──
document.getElementById('sidebarToggle')?.addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('open');
});

// ── Nav items ──
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', e => {
    e.preventDefault();
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    item.classList.add('active');
    const sec = item.dataset.section;
    const el = document.getElementById(sec);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

// ── Analyze ──
analyzeBtn.addEventListener('click', analyze);
drugInput.addEventListener('keydown', e => { if (e.key === 'Enter') analyze(); });

async function analyze() {
  const drug = drugInput.value.trim();
  if (!drug) { showError('Please enter a drug name.'); return; }

  setLoading(true);
  showOverlay();

  try {
    const payload = {
      drug,
      my_price: parseFloat(priceInput.value) || null,
      target_margin: parseFloat(marginInput.value) || 25
    };

    const res = await fetch('/api/analyze-pricing', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Server error');
    }

    const data = await res.json();
    _lastAnalysis = data;

    renderDashboard(data);

  } catch (err) {
    showError(err.message || 'Failed to analyze. Please try again.');
  } finally {
    setLoading(false);
    hideOverlay();
  }
}

// ── Loader ──
const LOAD_STEPS = [
  '🔍 Querying RxNav drug database...',
  '🏪 Benchmarking 6 competitor pharmacies...',
  '🤖 Running AI pricing agents...',
  '⚡ Groq LLaMA generating final recommendation...',
];

let loaderInterval = null;

function showOverlay() {
  overlay.classList.remove('hidden');
  let step = 0;
  const stepsEl = document.getElementById('loaderSteps');
  stepsEl.innerHTML = `<div class="loader-step active">${LOAD_STEPS[0]}</div>`;
  loaderInterval = setInterval(() => {
    step = (step + 1) % LOAD_STEPS.length;
    stepsEl.innerHTML = LOAD_STEPS.map((s, i) =>
      `<div class="loader-step${i === step ? ' active' : ''}">${s}</div>`
    ).join('');
  }, 800);
}

function hideOverlay() {
  clearInterval(loaderInterval);
  overlay.classList.add('hidden');
}

function setLoading(on) {
  analyzeBtn.disabled = on;
  btnText.classList.toggle('hidden', on);
  btnLoader.classList.toggle('hidden', !on);
}

// ── RENDER DASHBOARD ──
function renderDashboard(data) {
  const { drug, my_price, market, kpis, agents, final_recommendation: final } = data;

  renderDrugBanner(drug, my_price);
  renderKPIs(kpis);
  renderCompetitors(market.competitors, my_price, agents.margin.suggested_price);

  results.classList.remove('hidden');

  // Reset chat to empty state first
  const chatMessages = document.getElementById('chatMessages');
  chatMessages.innerHTML = '<div class="chat-empty" id="chatEmpty"><div class="chat-empty-icon">🤖</div><p class="chat-empty-title">AI Intelligence Ready</p><p class="chat-empty-sub">Run an analysis above to see multi-agent insights and Groq LLaMA recommendations</p></div>';

  document.getElementById('chatInput').disabled = true;
  document.getElementById('chatSendBtn').disabled = true;

  results.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Start chatbot animation after scroll
  setTimeout(() => {
    document.getElementById('chatEmpty')?.remove();
    renderChatSequence(agents, final);
  }, 600);
}

// ── DRUG BANNER ──
function renderDrugBanner(drug, my_price) {
  const items = [
    { label: 'Analyzed Drug', value: drug.matched_name || drug.searched, cls: '' },
    { label: 'Generic (Salt)', value: drug.generic_name || '—', cls: 'accent' },
    { label: 'RxCUI', value: drug.rxcui || 'N/A', cls: 'mono' },
    { label: 'Your Price', value: `$${Number(my_price).toFixed(2)}${drug.price_estimated ? ' (est.)' : ''}`, cls: 'green' },
    { label: 'Data Source', value: drug.source === 'rxnav' ? '✅ RxNav API' : '📦 Drug Database', cls: '' },
  ];

  const html = items.map((item, i) => `
    ${i > 0 ? '<div class="db-sep"></div>' : ''}
    <div class="drug-banner-item">
      <span class="db-label">${item.label}</span>
      <span class="db-value ${item.cls}">${item.value}</span>
    </div>
  `).join('');

  document.getElementById('drugBannerItems').innerHTML = html;
}

// ── KPI CARDS ──
function renderKPIs(kpis) {
  const posColor = { OVERPRICED: '#ef4444', UNDERPRICED: '#f59e0b', COMPETITIVE: '#10b981' };
  const posTrend = {
    OVERPRICED:  { cls: 'down', label: 'High' },
    UNDERPRICED: { cls: 'warn', label: 'Low' },
    COMPETITIVE: { cls: 'up',   label: 'Optimal' }
  };
  const posProgress = { OVERPRICED: 22, UNDERPRICED: 55, COMPETITIVE: 85 };

  const gap = kpis.competitor_gap;
  const gapColor = Math.abs(gap) < 2 ? '#10b981' : gap > 0 ? '#ef4444' : '#f59e0b';
  const gapTrend = Math.abs(gap) < 2 ? { cls: 'up', label: 'Even' } : gap > 0 ? { cls: 'down', label: 'Above' } : { cls: 'warn', label: 'Below' };

  const mopp = kpis.margin_opportunity;
  const oppColor  = mopp >= 0 ? '#10b981' : '#f59e0b';
  const oppTrend  = mopp > 2 ? { cls: 'up', label: `+${mopp.toFixed(1)}%` } : mopp < -2 ? { cls: 'down', label: `${mopp.toFixed(1)}%` } : { cls: 'neu', label: 'Flat' };

  const cards = [
    {
      icon: '📊',
      label: 'Market Average Price',
      value: `$${kpis.market_avg.toFixed(2)}`,
      sub: 'Across 6 pharmacies',
      color: '#00d4ff',
      trend: { cls: 'neu', label: 'Live' },
      progress: 65,
      isText: false,
    },
    {
      icon: '🎯',
      label: 'Your Price Position',
      value: kpis.position,
      sub: `vs $${kpis.market_avg.toFixed(2)} market avg`,
      color: posColor[kpis.position] || '#94a3b8',
      trend: posTrend[kpis.position] || { cls: 'neu', label: '—' },
      progress: posProgress[kpis.position] || 50,
      isText: true,
    },
    {
      icon: '💊',
      label: 'Generic Savings',
      value: `${kpis.generic_savings_pct}%`,
      sub: 'vs brand price',
      color: '#7c3aed',
      trend: kpis.generic_savings_pct >= 20 ? { cls: 'up', label: 'HIGH' } : { cls: 'neu', label: 'MED' },
      progress: Math.min(100, kpis.generic_savings_pct),
      isText: false,
    },
    {
      icon: '💡',
      label: 'Suggested Price',
      value: `$${kpis.suggested_price.toFixed(2)}`,
      sub: 'Margin-optimized target',
      color: '#10b981',
      trend: { cls: 'up', label: 'AI Pick' },
      progress: 78,
      isText: false,
    },
    {
      icon: '📈',
      label: 'Margin Opportunity',
      value: `${mopp > 0 ? '+' : ''}${mopp.toFixed(1)}%`,
      sub: 'Vs current pricing',
      color: oppColor,
      trend: oppTrend,
      progress: Math.min(100, Math.max(5, 50 + mopp * 2)),
      isText: false,
    },
    {
      icon: '⚖️',
      label: 'Competitor Gap',
      value: `${gap > 0 ? '+' : ''}$${gap.toFixed(2)}`,
      sub: 'Your price vs market avg',
      color: gapColor,
      trend: gapTrend,
      progress: Math.min(100, Math.max(5, 50 + gap * 3)),
      isText: false,
    },
  ];

  const grid = document.getElementById('kpiGrid');
  grid.innerHTML = cards.map((c, i) => `
    <div class="kpi-card" style="--kpi-color:${c.color}; animation-delay:${i * 70}ms">
      <div class="kpi-header">
        <div class="kpi-icon-wrap">${c.icon}</div>
        <div class="kpi-trend ${c.trend.cls}">${c.trend.label}</div>
      </div>
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value${c.isText ? ' kpi-text' : ''}">${c.value}</div>
      <div class="kpi-sub">${c.sub}</div>
      <div class="kpi-progress-wrap">
        <div class="kpi-progress" style="width:${c.progress}%"></div>
      </div>
    </div>
  `).join('');
}

// ── COMPETITOR MAP ──
function renderCompetitors(competitors, my_price, suggested) {
  const cardsEl = document.getElementById('competitorCards');
  cardsEl.innerHTML = competitors.map((c, i) => {
    const diff = c.price - my_price;
    const diffStr = diff > 0 ? `+$${diff.toFixed(2)} vs you` : `-$${Math.abs(diff).toFixed(2)} vs you`;
    const diffClass = diff > 0 ? 'diff-pos' : 'diff-neg';
    return `
      <div class="comp-card" style="animation-delay:${i * 50}ms">
        <div class="comp-icon">${c.icon}</div>
        <div class="comp-info">
          <div class="comp-name">${c.name}</div>
          <div class="comp-offer">${c.offer}</div>
        </div>
        <div class="comp-right">
          <span class="comp-price">$${c.price.toFixed(2)}</span>
          <span class="comp-badge badge-${c.position}">${c.position}</span>
          <div class="comp-diff ${diffClass}">${diffStr}</div>
        </div>
      </div>
    `;
  }).join('');

  renderChart(competitors, my_price, suggested);
}

function renderChart(competitors, my_price, suggested) {
  if (priceChart) { priceChart.destroy(); priceChart = null; }
  const ctx = document.getElementById('priceChart').getContext('2d');
  const labels = [...competitors.map(c => c.name), 'Your Price', 'Suggested'];
  const values = [...competitors.map(c => c.price), my_price, suggested];
  const bgColors = competitors.map(c =>
    c.position === 'premium' ? 'rgba(239,68,68,0.45)' :
    c.position === 'discount' ? 'rgba(0,212,255,0.45)' :
    'rgba(16,185,129,0.45)'
  );
  bgColors.push('rgba(245,158,11,0.65)', 'rgba(124,58,237,0.65)');
  const borderColors = bgColors.map(c => c.replace(/0\.\d+\)/, '1)'));

  priceChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Price ($)',
        data: values,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(11,16,34,0.95)',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#e2e8f0',
          bodyColor: '#94a3b8',
          callbacks: { label: ctx => ` $${ctx.raw.toFixed(2)}` }
        }
      },
      scales: {
        x: {
          ticks: { color: '#64748b', font: { size: 10 }, maxRotation: 30 },
          grid: { color: 'rgba(255,255,255,0.04)' }
        },
        y: {
          ticks: { color: '#64748b', font: { size: 10 }, callback: v => `$${v}` },
          grid: { color: 'rgba(255,255,255,0.04)' }
        }
      }
    }
  });
}

// ── CHAT: AGENT + CLAUDE SEQUENCE ──
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const AGENT_COLORS = {
  'Price Benchmark':     '#00d4ff',
  'Generic Substitution':'#7c3aed',
  'Margin Optimization': '#10b981',
  'Competitive Strategy':'#f59e0b',
};

async function renderChatSequence(agents, final) {
  const chatEl = document.getElementById('chatMessages');

  // System message
  appendToChat(chatEl, createSystemMsg('✅ Analysis complete — 4 AI agents processed · Groq LLaMA recommendation ready'));
  await delay(300);

  const agentList = [
    agents.benchmark,
    agents.generic,
    agents.margin,
    agents.strategy,
  ];

  for (let i = 0; i < agentList.length; i++) {
    const agent = agentList[i];
    const color = AGENT_COLORS[agent.agent] || '#00d4ff';
    const tid = `typing-${i}`;

    // Add typing indicator
    appendToChat(chatEl, createTypingBubble(tid, agent.icon, agent.agent, color));
    chatEl.scrollTop = chatEl.scrollHeight;
    await delay(500 + i * 100);

    // Replace typing with actual message
    const typingEl = document.getElementById(tid);
    if (typingEl) {
      typingEl.outerHTML = createAgentMessage(agent, color);
    }
    chatEl.scrollTop = chatEl.scrollHeight;
    await delay(150);
  }

  // Claude typing
  await delay(400);
  const claudeTid = 'typing-claude';
  appendToChat(chatEl, createTypingBubble(claudeTid, '⚡', 'Groq LLaMA 3.3', '#7c3aed'));
  chatEl.scrollTop = chatEl.scrollHeight;
  await delay(1000);

  const claudeTypingEl = document.getElementById(claudeTid);
  if (claudeTypingEl) {
    claudeTypingEl.outerHTML = createClaudeMessage(final);
  }
  chatEl.scrollTop = chatEl.scrollHeight;

  // Enable follow-up input
  const chatInput = document.getElementById('chatInput');
  const chatSendBtn = document.getElementById('chatSendBtn');
  chatInput.disabled = false;
  chatSendBtn.disabled = false;
  chatInput.focus();
}

function appendToChat(container, html) {
  const div = document.createElement('div');
  div.innerHTML = html;
  while (div.firstChild) container.appendChild(div.firstChild);
}

function createSystemMsg(text) {
  return `<div class="chat-msg system-msg"><div class="sys-bubble">${text}</div></div>`;
}

function createTypingBubble(id, icon, name, color) {
  return `
    <div id="${id}" class="chat-msg">
      <div class="msg-avatar" style="border-color:${color}22">${icon}</div>
      <div class="msg-content">
        <div class="msg-sender">${name}</div>
        <div class="typing-content">
          <span class="typing-sender">${name}</span>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    </div>`;
}

function createAgentMessage(data, color) {
  const severity = data.severity || data.opportunity || 'neutral';
  const tagLabel = data.position || data.opportunity || severity || '';
  const tagClass = `tag-${(tagLabel || 'neutral').toLowerCase()}`;

  return `
    <div class="chat-msg" style="--agent-color:${color}">
      <div class="msg-avatar" style="border-color:${color}33; background:${color}11">${data.icon}</div>
      <div class="msg-content">
        <div class="msg-sender">${data.agent} Agent</div>
        <div class="msg-bubble">
          <div class="agent-bubble-header">
            <div class="agent-bubble-name">
              <span class="abn-icon">${data.icon}</span>
              <span class="abn-label">${data.agent}</span>
              ${tagLabel ? `<span class="agent-status-tag ${tagClass}">${tagLabel}</span>` : ''}
            </div>
            <div class="agent-score-chip">
              <div class="score-circle">${data.score}</div>
            </div>
          </div>
          <div class="agent-bubble-insight">${data.insight}</div>
          <div class="agent-bubble-action">
            <span class="aba-label">→</span>
            <span class="aba-text">${data.action}</span>
          </div>
        </div>
      </div>
    </div>`;
}

function createClaudeMessage(final) {
  const decWord = (final.decision || 'KEEP').split(' ')[0];
  const decClass = `decision-${decWord}`;

  const actions = (final.top3_actions || []).map((a, i) => `
    <div class="claude-action-item">
      <div class="ca-num">${i + 1}</div>
      <div class="ca-text">${a}</div>
    </div>`).join('');

  return `
    <div class="chat-msg">
      <div class="msg-avatar claude-avatar">⚡</div>
      <div class="msg-content" style="max-width:82%">
        <div class="msg-sender">Groq LLaMA 3.3 · Final Recommendation</div>
        <div class="claude-bubble">
          <div class="claude-pill-row">
            <span class="claude-pill-badge">⚡ Groq LLaMA 3.3 70B · llama-3.3-70b-versatile</span>
          </div>
          <div class="claude-decision-row">
            <div class="claude-decision-badge ${decClass}">⚡ ${final.decision}</div>
            <div class="confidence-wrap">
              <span class="confidence-label">Confidence</span>
              <div class="confidence-bar-wrap">
                <div class="confidence-bar" style="width:${final.confidence}%"></div>
              </div>
              <span class="confidence-pct">${final.confidence}%</span>
            </div>
          </div>
          <div class="claude-rationale">${final.rationale}</div>
          <div class="claude-metrics">
            <div class="claude-metric">
              <div class="cm-label">Suggested Price</div>
              <div class="cm-value">$${Number(final.suggested_price).toFixed(2)}</div>
            </div>
            <div class="claude-metric">
              <div class="cm-label">Monthly Impact</div>
              <div class="cm-value">${final.impact_label || '—'}</div>
            </div>
            <div class="claude-metric">
              <div class="cm-label">Offer Strategy</div>
              <div class="cm-value purple" style="font-size:14px;line-height:1.3">${final.offer_strategy}</div>
            </div>
            <div class="claude-metric">
              <div class="cm-label">Decision</div>
              <div class="cm-value purple" style="font-size:14px;line-height:1.3">${final.decision}</div>
            </div>
          </div>
          <div class="claude-actions-header">Top 3 Priority Actions</div>
          <div class="claude-actions-list">${actions}</div>
          <div class="claude-scenario">
            <div class="cs-label">💼 Business Scenario</div>
            <div class="cs-text">${final.business_scenario}</div>
          </div>
        </div>
      </div>
    </div>`;
}

// ── FOLLOW-UP CHAT ──
document.getElementById('chatSendBtn').addEventListener('click', sendFollowUp);
document.getElementById('chatInput').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) sendFollowUp();
});

async function sendFollowUp() {
  const input = document.getElementById('chatInput');
  const btn   = document.getElementById('chatSendBtn');
  const msg   = input.value.trim();
  if (!msg || !_lastAnalysis) return;

  const chatEl = document.getElementById('chatMessages');

  // Add user message
  appendToChat(chatEl, `
    <div class="chat-msg user-msg">
      <div class="msg-avatar user-avatar">👤</div>
      <div class="msg-content">
        <div class="msg-sender">You</div>
        <div class="msg-bubble">${escapeHtml(msg)}</div>
      </div>
    </div>`);

  input.value = '';
  input.disabled = true;
  btn.disabled = true;
  chatEl.scrollTop = chatEl.scrollHeight;

  // Show typing
  const tid = `typing-followup-${Date.now()}`;
  appendToChat(chatEl, createTypingBubble(tid, '⚡', 'Groq LLaMA 3.3', '#7c3aed'));
  chatEl.scrollTop = chatEl.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, context: _lastAnalysis })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'AI response failed');
    }

    const data = await res.json();
    const typingEl = document.getElementById(tid);
    if (typingEl) {
      typingEl.outerHTML = `
        <div class="chat-msg">
          <div class="msg-avatar claude-avatar">⚡</div>
          <div class="msg-content">
            <div class="msg-sender">Groq LLaMA 3.3</div>
            <div class="claude-bubble" style="padding:14px 18px">
              <div style="font-size:13.5px;color:var(--text-dim);line-height:1.75">${escapeHtml(data.response).replace(/\n/g, '<br>')}</div>
            </div>
          </div>
        </div>`;
    }
  } catch (err) {
    const typingEl = document.getElementById(tid);
    if (typingEl) typingEl.remove();
    showError(err.message || 'Failed to get AI response.');
  } finally {
    input.disabled = false;
    btn.disabled = false;
    chatEl.scrollTop = chatEl.scrollHeight;
    input.focus();
  }
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showError(msg) {
  document.getElementById('errorMsg').textContent = msg;
  document.getElementById('errorToast').classList.remove('hidden');
  setTimeout(() => document.getElementById('errorToast').classList.add('hidden'), 6000);
}
