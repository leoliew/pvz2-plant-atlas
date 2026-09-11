import plants from '../plants_egypt.json';
import { bindA4PdfExport, setPageRangeInputs } from './export-a4-pdf.js';
import { assetUrl } from './asset-url.js';

const book = document.querySelector('#book');
const fromInput = document.querySelector('#export-from');
const toInput = document.querySelector('#export-to');
const totalLabel = document.querySelector('#export-total');

const CHIP_LABELS = {
  SUNCOST: ['Sun', '阳光'],
  RECHARGE: ['Recharge', '冷却'],
  TOUGHNESS: ['Toughness', '生命'],
  DAMAGE: ['Damage', '伤害'],
  SUNPRODUCTION: ['Sun/cycle', '产阳'],
  GROWTIME: ['Grow time', '生长'],
  ARMINGTIME: ['Arming', '装填'],
  DURATION: ['Duration', '持续'],
};
const CHIP_KEYS = Object.keys(CHIP_LABELS);
const PER_PAGE = 4;

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[char]));
}

function plain(value) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const en = value.en ?? value.EN ?? '';
    const zh = value.zh ?? value.ZH ?? '';
    return [en, zh].filter(Boolean).join(' · ');
  }
  if (Array.isArray(value)) return value.map(plain).join(' / ');
  return String(value ?? '');
}

function part(value) {
  if (value == null || value === '—') return '';
  return String(value).trim();
}

function bilingual(en, zh, zhOnly) {
  const english = part(en);
  const chinese = part(zh);
  if (zhOnly) return chinese;
  return [english, chinese].filter(Boolean).join(' ');
}

function bilingualValue(value, zhOnly) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return bilingual(value.en ?? value.EN, value.zh ?? value.ZH, zhOnly);
  }
  if (Array.isArray(value)) return value.map((item) => bilingualValue(item, zhOnly)).filter(Boolean).join(' / ');
  return part(value);
}

function stripWiki(text) {
  return String(text || '').replace(/\[\[([^|\]]+)(?:\|[^\]]*)?\]\]/g, '$1');
}

function overflowing(el, pad = 1.5) {
  return Boolean(el) && el.scrollHeight > el.clientHeight + pad;
}

function fitOverflow(el, minPx = 6.5) {
  if (!el) return;
  let size = Number.parseFloat(getComputedStyle(el).fontSize);
  while (overflowing(el) && size > minPx) {
    size -= 0.25;
    el.style.fontSize = `${size}px`;
  }
}

function fitCard(card, plant) {
  const def = card.querySelector('.definition');
  const trivia = card.querySelector('.trivia');
  const unlock = card.querySelector('.unlock');
  if (def) {
    def.style.fontSize = '';
    def.innerHTML = definitionHtml(plant, false);
  }
  if (trivia) {
    trivia.style.fontSize = '';
    trivia.style.flex = '';
    trivia.innerHTML = triviaHtml(plant);
  }
  if (unlock) unlock.innerHTML = unlockHtml(plant, false);

  if (overflowing(def)) def.innerHTML = definitionHtml(plant, true);
  if (overflowing(unlock)) unlock.innerHTML = unlockHtml(plant, true);

  fitOverflow(def);
  fitOverflow(trivia);
  if (overflowing(def) && trivia) {
    trivia.style.flex = '0 1 22%';
    def.style.fontSize = '';
    trivia.style.fontSize = '';
    if (overflowing(def)) def.innerHTML = definitionHtml(plant, true);
    fitOverflow(def);
    fitOverflow(trivia);
  }
}

function hexToRgb(value) {
  const hex = String(value || '#4e9f66').replace('#', '');
  if (hex.length !== 6) return '78,159,102';
  return [0, 2, 4].map((index) => Number.parseInt(hex.slice(index, index + 2), 16)).join(',');
}

function chipBlock(plant) {
  const elements = plant.elements || {};
  return CHIP_KEYS.flatMap((key) => {
    const value = elements[key];
    if (value == null || value === '' || value === '—') return [];
    const [en, zh] = CHIP_LABELS[key];
    return [`<div class="chip"><b>${esc(en)}<small>${esc(zh)}</small></b><div class="v">${esc(plain(value))}</div></div>`];
  }).join('');
}

function definitionItems(plant, zhOnly) {
  const items = [];
  const intro = bilingual(plant.description, plant.description_zh, zhOnly);
  if (intro) items.push([zhOnly ? '简介' : '简介·Intro', esc(intro)]);

  const range = bilingualValue(plant.elements?.RANGE, zhOnly);
  if (range) items.push([zhOnly ? '索敌' : '索敌·Range', esc(range)]);

  const food = bilingual(plant.plant_food, plant.plant_food_zh, zhOnly);
  if (food) items.push([zhOnly ? '叶绿素' : '叶绿素·Plant Food', esc(food)]);

  for (const item of plant.special || []) {
    if (!item || typeof item !== 'object') continue;
    const description = bilingualValue(item.DESCRIPTION, zhOnly);
    if (!description) continue;
    const name = bilingualValue(item.NAME, zhOnly) || (zhOnly ? '特点' : 'Special');
    items.push([`特点·${esc(name)}`, esc(description)]);
  }
  return items;
}

function definitionHtml(plant, zhOnly = false) {
  return definitionItems(plant, zhOnly)
    .map(([label, text]) => `<div class="def-item"><b>${label}</b><span>${text}</span></div>`)
    .join('');
}

function triviaHtml(plant) {
  const text = part(plant.chat_zh);
  if (!text) return '';
  return `<span class="lines"><b>趣闻</b> ${esc(text)}</span>`;
}

function unlockHtml(plant, zhOnly = false) {
  const english = stripWiki(plant.unlock || '');
  const chinese = part(plant.unlock_zh);
  if (zhOnly) return esc(chinese || english);
  return `${esc(english)}${chinese ? ` · ${esc(chinese)}` : ''}`;
}

function familyIconCode(family) {
  if (!family || family === 'Nope' || family === 'None') return 'None';
  return family;
}

function plantCard(plant) {
  const family = familyIconCode(plant.family);
  const color = plant.color || '#4e9f66';
  const file = plant.pvzg_file || plant.file || '';
  return `<article class="plant-card" style="--accent:${esc(color)};--soft:rgba(${hexToRgb(color)},.18)">
  <div class="head">
    <div class="head-top"><div class="name">${esc(plant.en)}<span class="zh">${esc(plant.zh)}</span></div><div class="world">${esc(plant.world || 'Ancient Egypt')}</div></div>
    <div class="unlock">${unlockHtml(plant, false)}</div>
  </div>
  <div class="media-row">
    <div class="pic"><img class="art" src="${assetUrl(`images/${esc(file)}`)}" onerror="this.onerror=null;this.src='${esc(plant.img || '')}'" alt="${esc(plant.en)}"><img class="fam" src="${assetUrl(`images/families/${esc(family)}_familyicon.webp`)}" onerror="this.onerror=null;this.src='${assetUrl('images/families/None_familyicon.webp')}'" alt="${esc(plant.family_zh || family)}" title="${esc(plant.family_zh || family)} · ${esc(family)}"></div>
    <div class="chip-grid">${chipBlock(plant)}</div>
  </div>
  <div class="definition">${definitionHtml(plant, false)}</div>
  <p class="trivia">${triviaHtml(plant)}</p>
</article>`;
}

const total = Math.ceil(plants.length / PER_PAGE);
setPageRangeInputs({ fromInput, toInput, totalLabel, pageCount: total });

book.innerHTML = Array.from({ length: total }, (_, index) => {
  const group = plants.slice(index * PER_PAGE, (index + 1) * PER_PAGE);
  return `<section class="page">
    <div class="plant-grid">${group.map(plantCard).join('')}</div>
    <div class="footer"><span>Data: pvzg_site · Printable A4 portrait almanac</span><span class="page-no">${index + 1} / ${total}</span></div>
  </section>`;
}).join('');

async function fitCards() {
  await document.fonts.ready.catch(() => {});
  document.querySelectorAll('.plant-card').forEach((card, index) => fitCard(card, plants[index]));
}
fitCards();

bindA4PdfExport({
  button: document.querySelector('#export-pdf'),
  statusEl: document.querySelector('#export-status'),
  fromInput,
  toInput,
  filename: 'PvZ2_Plant_Attributes',
});
