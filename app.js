const state = {
  data: [],
  filtered: [],
  search: '',
  levels: new Set(),
  pos: new Set(),
  showEnglish: true,
  rate: 1.0,
  volume: 1.0,
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
const audioCache = new Map();
let currentAudio = null;

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
          <button class="tts-btn" data-tts="${item.lemma}" data-rank="${item.rank}">▶</button>
          <span>${item.lemma}</span>
        </div>
      </td>
      <td class="col-english">${state.showEnglish ? (item.english || '') : ''}</td>
      <td class="example-cell">
        <div class="wordcell">
          <button class="tts-btn" data-exrank="${item.rank}" data-extext="${item.example || ''}">▶</button>
          <span>${item.example || ''}</span>
        </div>
      </td>
      <td>${posLabels[item.pos] || item.pos}</td>
      <td>${item.level}</td>
    `;
    table.appendChild(tr);
  });

  table.querySelectorAll('.tts-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const text = btn.getAttribute('data-tts');
      const rank = parseInt(btn.getAttribute('data-rank') || '0', 10);
      const exText = btn.getAttribute('data-extext');
      const exRank = parseInt(btn.getAttribute('data-exrank') || '0', 10);
      if (exRank && exText) {
        playExampleAudio(exRank, exText);
        return;
      }
      if (!text) return;
      playAudio(rank, text);
    });
  });
}

function audioFilename(rank) {
  const safeRank = String(rank || 0).padStart(4, '0');
  return `audio/${safeRank}.mp3`;
}

function exampleAudioFilename(rank) {
  const safeRank = String(rank || 0).padStart(4, '0');
  return `audio_examples/${safeRank}.mp3`;
}

function playAudio(rank, text) {
  const url = audioFilename(rank);
  let audio = audioCache.get(url);
  if (!audio) {
    audio = new Audio(url);
    audio.preload = 'auto';
    audioCache.set(url, audio);
  }
  if (currentAudio && currentAudio !== audio) {
    currentAudio.pause();
  }
  currentAudio = audio;
  audio.currentTime = 0;
  audio.playbackRate = state.rate;
  audio.volume = state.volume;
  audio.play().catch(() => {
    console.warn('Audio missing for', text, url);
  });
}

function playExampleAudio(rank, text) {
  const url = exampleAudioFilename(rank);
  let audio = audioCache.get(url);
  if (!audio) {
    audio = new Audio(url);
    audio.preload = 'auto';
    audioCache.set(url, audio);
  }
  if (currentAudio && currentAudio !== audio) {
    currentAudio.pause();
  }
  currentAudio = audio;
  audio.currentTime = 0;
  audio.playbackRate = state.rate;
  audio.volume = state.volume;
  audio.play().catch(() => {
    console.warn('Example audio missing for', text, url);
  });
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

  const speedSlider = document.getElementById('speedSlider');
  const speedValue = document.getElementById('speedValue');
  if (speedSlider && speedValue) {
    speedValue.textContent = state.rate.toFixed(2);
    speedSlider.addEventListener('input', () => {
      state.rate = parseFloat(speedSlider.value);
      speedValue.textContent = state.rate.toFixed(2);
    });
  }

  const volumeSlider = document.getElementById('volumeSlider');
  const volumeValue = document.getElementById('volumeValue');
  if (volumeSlider && volumeValue) {
    volumeValue.textContent = state.volume.toFixed(2);
    volumeSlider.addEventListener('input', () => {
      state.volume = parseFloat(volumeSlider.value);
      volumeValue.textContent = state.volume.toFixed(2);
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
  initFilters();
  initSearch();
  renderStats();
  renderTable();
}

boot();
