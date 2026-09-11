import plants from '../plants_egypt.json';
import { highlightSentence, WORD_COLORS } from './learning.js';
import { resolveWorldBackgroundFile } from './world-backgrounds.js';
import { bindA4PdfExport, setPageRangeInputs } from './export-a4-pdf.js';
import { assetUrl } from './asset-url.js';

const book = document.querySelector('#book');
const fromInput = document.querySelector('#export-from');
const toInput = document.querySelector('#export-to');
const totalLabel = document.querySelector('#export-total');

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[char]));
}

function background(plant) {
  const file = resolveWorldBackgroundFile(plant.obtain_world_code);
  return `<img class="bg" src="${assetUrl(`images/backgrounds/${file}.webp`)}" alt="" loading="lazy">`;
}

function image(plant) {
  const file = plant.pvzg_file || plant.file;
  return `<img class="art" src="${assetUrl(`images/${esc(file)}`)}" onerror="this.onerror=null;this.src='${esc(plant.img || '')}'" alt="${esc(plant.en)}">`;
}

function familyBadge(plant) {
  const family = plant.family;
  if (!family || family === 'Nope' || family === 'None') return '';
  return `<img class="family-badge" src="${assetUrl(`images/families/${esc(family)}_familyicon.webp`)}" alt="${esc(plant.family_zh || family)}" title="${esc(plant.family_zh || family)}" loading="lazy">`;
}

function paintedSentence(sentence, words) {
  return highlightSentence(sentence, words).map((part) => {
    if (part.colorIndex == null) return esc(part.text);
    const color = WORD_COLORS[part.colorIndex];
    return `<mark style="color:${color};background:${color}24">${esc(part.text)}</mark>`;
  }).join('');
}

function card(plant) {
  const words = (plant.words || []).slice(0, 3);
  const chips = words.map(([en], index) => (
    `<div class="word" style="--wc:${WORD_COLORS[index]}"><div class="en">${esc(en)}</div></div>`
  )).join('');
  const answers = words.map(([, zh]) => `<span>${esc(zh)}</span>`).join('');
  return `<article class="card" style="--c:${esc(plant.color || '#5da33b')}">
    <div class="pic">${background(plant)}${image(plant)}${familyBadge(plant)}
      <div class="sunbadge">☀${esc(plant.sun)}</div>
      <div class="label"><div class="en">${esc(plant.en)}</div><div class="zh">${esc(plant.zh)}</div></div>
    </div>
    <div class="body">
      <div class="say">${paintedSentence(plant.sentence, words)}</div>
      <div class="words">${chips}</div>
      <div class="answer">
        <div class="hint">Cover the Chinese · 用手盖住中文</div>
        <div class="zh-row">${answers}</div>
      </div>
    </div>
  </article>`;
}

const perPage = 4;
const total = Math.ceil(plants.length / perPage);
setPageRangeInputs({ fromInput, toInput, totalLabel, pageCount: total });
book.innerHTML = Array.from({ length: total }, (_, index) => `
  <section class="page">
    <div class="hdr">
      <div class="t">Plants vs. Zombies 2 · Word Cards<span class="zh">英语单词卡</span></div>
      <div class="p">${index + 1} / ${total}</div>
    </div>
    <div class="grid">${plants.slice(index * perPage, (index + 1) * perPage).map(card).join('')}</div>
    <div class="ftr">先读英文，用手盖住底边中文再读 · 沿虚线裁下即为单词卡</div>
  </section>
`).join('');

bindA4PdfExport({
  button: document.querySelector('#export-pdf'),
  statusEl: document.querySelector('#export-status'),
  fromInput,
  toInput,
  filename: 'PvZ2_Plant_Seed_Packets',
});
