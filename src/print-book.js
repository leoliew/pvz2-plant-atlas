import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import plants from '../plants_egypt.json';
import { resolveWorldBackgroundFile } from './world-backgrounds.js';

const book = document.querySelector('#book');
const exportButton = document.querySelector('#export-pdf');
const exportStatus = document.querySelector('#export-status');
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
  return `<img class="bg" src="/images/backgrounds/${file}.webp" alt="" loading="lazy">`;
}

function image(plant) {
  const file = plant.pvzg_file || plant.file;
  return `<img class="art" src="/images/${esc(file)}" onerror="this.onerror=null;this.src='${esc(plant.img || '')}'" alt="${esc(plant.en)}">`;
}

function familyBadge(plant) {
  const family = plant.family;
  if (!family || family === 'Nope' || family === 'None') return '';
  return `<img class="family-badge" src="/images/families/${esc(family)}_familyicon.webp" alt="${esc(plant.family_zh || family)}" title="${esc(plant.family_zh || family)}" loading="lazy">`;
}

function card(plant) {
  const words = (plant.words || []).slice(0, 3).map(([en, zh]) => (
    `<div class="word"><div class="en">${esc(en)}</div><div class="zh">${esc(zh)}</div></div>`
  )).join('');
  return `<article class="card" style="--c:${esc(plant.color || '#5da33b')}">
    <div class="pic">${background(plant)}${image(plant)}${familyBadge(plant)}
      <div class="sunbadge">☀${esc(plant.sun)}</div>
      <div class="label"><div class="en">${esc(plant.en)}</div><div class="zh">${esc(plant.zh)}</div></div>
    </div>
    <div class="body">
      <div class="stats">
        <div class="stat"><div class="ic">◷</div><div class="v">${esc(plant.recharge)}</div><div class="k">Recharge<small>冷却</small></div></div>
        <div class="stat"><div class="ic">♥</div><div class="v">${esc(plant.toughness)}</div><div class="k">Toughness<small>生命</small></div></div>
        <div class="stat"><div class="ic">ϟ</div><div class="v">${esc(plant.damage)}</div><div class="k">Damage<small>攻击</small></div></div>
      </div>
      <div class="range"><span class="ic">➜</span>${esc(plant.range)} <span class="zh">${esc(plant.range_zh)}</span></div>
      <div class="say"><div class="en">${esc(plant.sentence)}</div><div class="zh">${esc(plant.sentence_zh)}</div></div>
      <div class="words">${words}</div>
    </div>
  </article>`;
}

const perPage = 4;
const total = Math.ceil(plants.length / perPage);
fromInput.max = String(total);
toInput.max = String(total);
toInput.value = String(total);
totalLabel.textContent = `of ${total} pages · 共 ${total} 页`;
book.innerHTML = Array.from({ length: total }, (_, index) => `
  <section class="page">
    <div class="hdr">
      <div class="t">Plants vs. Zombies 2 · Plant Seed Packets<span class="zh">植物种子卡</span></div>
      <div class="p">${index + 1} / ${total}</div>
    </div>
    <div class="grid">${plants.slice(index * perPage, (index + 1) * perPage).map(card).join('')}</div>
    <div class="ftr">Data &amp; art: PvZ2 Gardendless · 沿虚线裁下即为单词卡</div>
  </section>
`).join('');

function setStatus(text) {
  exportStatus.hidden = !text;
  exportStatus.textContent = text;
}

function wait(ms = 0) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function clampPage(value, pageCount) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return 1;
  return Math.min(Math.max(1, parsed), pageCount);
}

function readRange(pageCount) {
  let from = clampPage(fromInput.value, pageCount);
  let to = clampPage(toInput.value, pageCount);
  if (from > to) [from, to] = [to, from];
  fromInput.value = String(from);
  toInput.value = String(to);
  return { from, to };
}

async function waitForImages(pages) {
  await document.fonts.ready.catch(() => {});
  const images = pages.flatMap((page) => [...page.querySelectorAll('img')]);
  await Promise.all(images.map((img) => {
    img.loading = 'eager';
    if (img.complete && img.naturalWidth > 0) return null;
    return new Promise((resolve) => {
      img.addEventListener('load', resolve, { once: true });
      img.addEventListener('error', resolve, { once: true });
    });
  }));
}

async function exportPdf() {
  const allPages = [...document.querySelectorAll('.page')];
  if (!allPages.length) return;
  const { from, to } = readRange(allPages.length);
  const pages = allPages.slice(from - 1, to);
  const rangeLabel = from === 1 && to === allPages.length ? '' : `_p${from}-${to}`;

  exportButton.disabled = true;
  fromInput.disabled = true;
  toInput.disabled = true;
  setStatus(`Preparing ${from}–${to} / ${allPages.length}… 准备中`);

  try {
    await waitForImages(pages);
    await wait(50);

    const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4', compress: true });

    for (let index = 0; index < pages.length; index += 1) {
      setStatus(`Exporting ${from + index}–${to} · ${index + 1}/${pages.length}`);
      await wait(0);

      const page = pages[index];
      page.scrollIntoView({ block: 'start' });
      const canvas = await html2canvas(page, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false,
        imageTimeout: 20000,
        width: page.offsetWidth,
        height: page.offsetHeight,
        windowWidth: page.offsetWidth,
        windowHeight: page.offsetHeight,
      });
      const imageData = canvas.toDataURL('image/jpeg', 0.82);
      if (index > 0) pdf.addPage('a4', 'p');
      pdf.addImage(imageData, 'JPEG', 0, 0, 210, 297, undefined, 'FAST');
      canvas.width = 0;
      canvas.height = 0;
    }

    pdf.save(`PvZ2_Plant_Seed_Packets${rangeLabel}.pdf`);
    setStatus(`Saved p${from}–${to} · 已保存`);
  } catch (error) {
    console.error(error);
    setStatus('Export failed · 导出失败');
  } finally {
    exportButton.disabled = false;
    fromInput.disabled = false;
    toInput.disabled = false;
  }
}

exportButton.addEventListener('click', exportPdf);
