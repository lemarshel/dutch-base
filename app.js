const state = {
  data: [],
  filtered: [],
  search: '',
  levels: new Set(),
  pos: new Set(),
  showEnglish: true,
  slowAudio: false,
  spellAudio: false,
  voiceName: '',
};

const posOrder = ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'numeral', 'determiner', 'preposition', 'conjunction', 'interjection', 'other'];

const posLabels = {
  noun: 'Noun',
  verb: 'Verb',
  adjective: 'Adjective',
  adverb: 'Adverb',
  pronoun: 'Pronoun',
  numeral: 'Numeral',
  determiner: 'Determiner',
  preposition: 'Preposition',
  conjunction: 'Conjunction',
  interjection: 'Interjection',
  other: 'Other'
};

const levelTargets = [1,2,3,4,5,6,7];

function createChip(label, onClick, active = true) {
  const btn = document.createElement('button');
  btn.className = 'chip' + (active ? ' active' : '');
  btn.textContent = label;
  btn.addEventListener('click', () => {
    btn.classList.toggle('active');
    onClick(btn.classList.contains('active'));
  });
  return btn;
}

function renderStats() {
  const stats = document.getElementById('stats');
  stats.innerHTML = '';
  const total = state.filtered.length;
  const totalCard = document.createElement('div');
  totalCard.className = 'stat-card';
  totalCard.innerHTML = `<strong>${total}</strong> entries shown`;
  stats.appendChild(totalCard);
}

function renderTable() {
  const table = document.getElementById('wordTable');
  table.innerHTML = '';

  state.filtered.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.rank}</td>
      <td class="word">
        <div class="wordcell">
          <button class="tts-btn" data-tts="${item.lemma}">▶</button>
          <span>${item.lemma}</span>
        </div>
      </td>
      <td class="col-english">${state.showEnglish ? (item.english || '') : ''}</td>
      <td>${posLabels[item.pos] || item.pos}</td>
      <td>${item.level}</td>
    `;
    table.appendChild(tr);
  });

  table.querySelectorAll('.tts-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const text = btn.getAttribute('data-tts');
      if (!text) return;
      speakDutch(text);
    });
  });
}

let dutchVoice = null;
function loadDutchVoice() {
  const voices = window.speechSynthesis.getVoices();
  const nlVoices = voices.filter(v => v.lang && v.lang.toLowerCase().startsWith('nl'));
  if (!nlVoices.length) return;
  const preferred = nlVoices.find(v =>
    (v.lang && v.lang.toLowerCase() === 'nl-nl') &&
    /xander|frank|google|microsoft|netherlands|nederlands/i.test(v.name)
  );
  dutchVoice = preferred || nlVoices[0];
  if (!state.voiceName) state.voiceName = dutchVoice.name;
}

function speakDutch(text) {
  if (!window.speechSynthesis) return;
  if (!dutchVoice) loadDutchVoice();
  const voices = window.speechSynthesis.getVoices();
  if (state.voiceName) {
    const chosen = voices.find(v => v.name === state.voiceName);
    if (chosen) dutchVoice = chosen;
  }
  let speakText = text;
  if (state.spellAudio) {
    speakText = text.split('').join(' ');
  }
  const utter = new SpeechSynthesisUtterance(text);
  utter.text = speakText;
  if (dutchVoice) utter.voice = dutchVoice;
  utter.lang = dutchVoice ? dutchVoice.lang : 'nl-NL';
  utter.rate = state.slowAudio ? 0.85 : 1.0;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
}

function applyFilters() {
  const term = state.search.trim().toLowerCase();
  const levelSet = state.levels;
  const posSet = state.pos;

  state.filtered = state.data.filter(item => {
    const matchLevel = levelSet.size === 0 || levelSet.has(item.level);
    const matchPos = posSet.size === 0 || posSet.has(item.pos);
    if (!matchLevel || !matchPos) return false;
    if (!term) return true;
    return (
      item.lemma.toLowerCase().includes(term) ||
      (item.english && item.english.toLowerCase().includes(term))
    );
  });

  renderStats();
  renderTable();
}

function initFilters() {
  const levelContainer = document.getElementById('levelFilters');
  levelTargets.forEach(level => {
    const chip = createChip(`L${level}`, active => {
      if (active) state.levels.add(level); else state.levels.delete(level);
      applyFilters();
    }, false);
    levelContainer.appendChild(chip);
  });

  const posContainer = document.getElementById('posFilters');
  posOrder.forEach(pos => {
    const label = posLabels[pos] || pos;
    const chip = createChip(label, active => {
      if (active) state.pos.add(pos); else state.pos.delete(pos);
      applyFilters();
    }, false);
    posContainer.appendChild(chip);
  });

  document.getElementById('toggleEnglish').addEventListener('click', (e) => {
    state.showEnglish = !state.showEnglish;
    e.target.classList.toggle('active', state.showEnglish);
    applyFilters();
  });

  const slowBtn = document.getElementById('toggleSlow');
  const spellBtn = document.getElementById('toggleSpell');
  slowBtn.addEventListener('click', () => {
    state.slowAudio = !state.slowAudio;
    slowBtn.classList.toggle('active', state.slowAudio);
  });
  spellBtn.addEventListener('click', () => {
    state.spellAudio = !state.spellAudio;
    spellBtn.classList.toggle('active', state.spellAudio);
  });

  const voiceSelect = document.getElementById('voiceSelect');
  if (voiceSelect) {
    voiceSelect.addEventListener('change', () => {
      state.voiceName = voiceSelect.value;
      loadDutchVoice();
    });
  }
}

function initSearch() {
  const input = document.getElementById('search');
  input.addEventListener('input', () => {
    state.search = input.value;
    applyFilters();
  });
  document.getElementById('clearSearch').addEventListener('click', () => {
    input.value = '';
    state.search = '';
    applyFilters();
  });
}

async function boot() {
  const res = await fetch('data/words.json');
  const data = await res.json();
  state.data = data;
  state.filtered = data;
  if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = () => {
      loadDutchVoice();
      populateVoiceSelect();
    };
    loadDutchVoice();
    populateVoiceSelect();
  }
  initFilters();
  initSearch();
  renderStats();
  renderTable();
}

function populateVoiceSelect() {
  const voiceSelect = document.getElementById('voiceSelect');
  if (!voiceSelect || !window.speechSynthesis) return;
  const voices = window.speechSynthesis.getVoices();
  const nlVoices = voices.filter(v => v.lang && v.lang.toLowerCase().startsWith('nl'));
  voiceSelect.innerHTML = '';
  nlVoices.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v.name;
    opt.textContent = `${v.name} (${v.lang})`;
    if (state.voiceName && v.name === state.voiceName) opt.selected = true;
    voiceSelect.appendChild(opt);
  });
}

boot();
