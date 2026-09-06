import { StrictMode, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import plants from '../plants_egypt.json';
import './styles.css';
import { resolveWorldBackgroundFile } from './world-backgrounds.js';

const pageSize = 4;
const DEFAULT_WORLD = 'Ancient Egypt';
const ALL_WORLDS = '__all__';

function getWorldBackground(code) {
  return `/images/backgrounds/${resolveWorldBackgroundFile(code)}.webp`;
}

const FAMILY_NONE_ICON = '/images/families/None_familyicon.webp';
const FAMILY_ALL_ICON = '/images/families/All_familyicon.webp';

function normalizeFamily(family) {
  if (!family || family === 'Nope' || family === 'None') return null;
  return family;
}

function getFamilyIcon(family) {
  return `/images/families/${family}_familyicon.webp`;
}

function getWorld(plant) {
  if (plant.world) return plant.world;
  if (/Ancient Egypt|Player's House|Start of the game/i.test(plant.unlock || '')) return DEFAULT_WORLD;
  return 'Other worlds';
}

const WORLD_ORDER = ['Ancient Egypt', 'Pirate Seas', 'Wild West', 'Frostbite Caves', 'Lost City', 'Far Future', 'Dark Ages', 'Jurassic Marsh', 'Big Wave Beach', 'Modern Day', 'Premium & special', 'Mint family', 'Other worlds'];
// Keep the catalog data-driven while preserving the in-game world order.
const worlds = WORLD_ORDER.filter((world) => plants.some((plant) => getWorld(plant) === world));
const worldOptions = [ALL_WORLDS, ...worlds];

// Fields already shown on the card face or explicitly in the detail modal —
// anything else falls through to the generic "More" section below.
const DETAIL_HANDLED_KEYS = new Set([
  'codename', 'id', 'file', 'img', 'pvzg_file', 'color', 'en', 'zh',
  'sun', 'recharge', 'recharge_zh', 'toughness', 'damage', 'range', 'range_zh',
  'sentence', 'sentence_zh', 'words', 'unlock',
  'family', 'family_zh', 'obtain_world_code', 'world',
  'unlock_zh', 'description', 'description_zh', 'plant_food', 'plant_food_zh',
  // duplicates of description/description_zh and sentence/sentence_zh/words for every plant
  'intro_en', 'intro_zh', 'learning_sentences',
]);

function humanizeKey(key) {
  return key.replace(/_zh$/, ' (中文)').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function stringifyField(value) {
  if (Array.isArray(value)) return value.map((v) => (Array.isArray(v) ? v.join(' / ') : String(v))).join(', ');
  if (value && typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function Image({ plant, className = '' }) {
  const primary = plant.pvzg_file || plant.file;
  return (
    <img
      className={className}
      src={`/images/${primary}`}
      data-local-fallback={plant.file !== primary ? `/images/${plant.file}` : ''}
      data-remote-fallback={plant.img}
      onError={(event) => {
        const image = event.currentTarget;
        const localFallback = image.dataset.localFallback;
        const remoteFallback = image.dataset.remoteFallback;
        if (!image.dataset.triedLocal && localFallback) {
          image.dataset.triedLocal = 'true';
          image.src = localFallback;
        } else if (!image.dataset.triedRemote && remoteFallback) {
          image.dataset.triedRemote = 'true';
          image.src = remoteFallback;
        }
      }}
      alt={plant.en}
      loading="lazy"
    />
  );
}

function Sun({ value }) {
  return <span className="sun-pill"><span className="sun-glyph">☀</span>{value}</span>;
}

function Stat({ icon, label, zh, value, accent }) {
  return (
    <div className="stat" style={{ '--accent': accent }}>
      <span className="stat-icon">{icon}</span>
      <strong>{value}</strong>
      <span className="stat-label">{label}<small>{zh}</small></span>
    </div>
  );
}

function PlantCard({ plant, index, onOpen }) {
  const family = normalizeFamily(plant.family);
  return (
    <article className="plant-card" style={{ '--accent': plant.color, '--delay': `${index * 45}ms` }}>
      <div className="plant-art">
        <img className="plant-bg" src={getWorldBackground(plant.obtain_world_code)} alt="" aria-hidden="true" loading="lazy" />
        <Image plant={plant} className="plant-sprite" />
        {family && <img className="family-badge" src={getFamilyIcon(family)} alt={plant.family_zh || family} title={plant.family_zh || family} loading="lazy" />}
        <Sun value={plant.sun} />
        <div className="plant-label">
          <b>{plant.en}</b>
          <span>{plant.zh}</span>
        </div>
      </div>
      <div className="card-body">
        <div className="card-unlock"><span>◆</span>{plant.unlock}</div>
        <div className="stats">
          <Stat icon="◷" label="Recharge" zh="冷却" value={`${plant.recharge} · ${plant.recharge_zh}`} accent={plant.color} />
          <Stat icon="♥" label="Toughness" zh="生命" value={plant.toughness} accent={plant.color} />
          <Stat icon="ϟ" label="Damage" zh="攻击" value={plant.damage} accent={plant.color} />
        </div>
        <div className="range"><span>➜</span><b>Range</b> {plant.range}<em>{plant.range_zh}</em></div>
        <div className="say"><b>{plant.sentence}</b><span>{plant.sentence_zh}</span></div>
        <div className="words">{plant.words.map(([en, zh]) => <span key={en}><b>{en}</b><small>{zh}</small></span>)}</div>
        <button type="button" className="card-expand" onClick={() => onOpen(plant)}>
          Details <span>· 详情</span>
        </button>
      </div>
    </article>
  );
}

function PlantDetailModal({ plant, onClose }) {
  useEffect(() => {
    if (!plant) return;
    const onKey = (event) => event.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [plant, onClose]);

  if (!plant) return null;
  const family = normalizeFamily(plant.family);
  const hasFood = plant.plant_food && plant.plant_food !== '—';
  const extra = Object.entries(plant).filter(
    ([key, value]) => !DETAIL_HANDLED_KEYS.has(key) && value != null && value !== '' && value !== '—'
  );

  return (
    <div className="detail-modal-overlay" onClick={onClose} role="presentation">
      <div
        className="detail-modal"
        style={{ '--accent': plant.color }}
        role="dialog"
        aria-modal="true"
        aria-label={plant.en}
        onClick={(event) => event.stopPropagation()}
      >
        <button type="button" className="detail-modal-close" onClick={onClose} aria-label="Close">×</button>
        <div className="detail-head">
          <Image plant={plant} />
          <div className="detail-title"><b>{plant.en}</b><span>{plant.zh}</span></div>
          {family && <img className="family-badge" src={getFamilyIcon(family)} alt={plant.family_zh || family} title={plant.family_zh || family} loading="lazy" />}
        </div>
        <div className="detail-unlock">
          <div><span>◆</span>{plant.unlock}</div>
          <div>{plant.unlock_zh}</div>
        </div>
        <div className="official-copy">
          <p><b>About<small>简介</small></b><span>{plant.description}</span><em>{plant.description_zh}</em></p>
          {hasFood && (
            <p>
              <b>Plant Food<small>叶绿素</small></b>
              <span>{plant.plant_food}</span>
              {plant.plant_food_zh !== '—' && <em>{plant.plant_food_zh}</em>}
            </p>
          )}
        </div>
        {extra.length > 0 && (
          <div className="detail-more">
            {extra.map(([key, value]) => (
              <div key={key}><b>{humanizeKey(key)}</b><span>{stringifyField(value)}</span></div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Intro({ total, world, showGuide, featuredPlants }) {
  const rows = [['☀', 'Sun cost', '阳光', 'What you pay to plant it.'], ['◷', 'Recharge', '冷却', 'How long until you can plant another.'], ['♥', 'Toughness', '生命', 'How many bites it can take.'], ['ϟ', 'Damage', '攻击', 'How hard it hits a zombie.'], ['➜', 'Range', '范围', 'Where it can reach.']];
  return <section className={`page intro-page ${showGuide ? '' : 'intro-page--hero-only'}`}>
    <div className="intro-hero">
      <div className="intro-copy">
        <div className="eyebrow">A bilingual field guide · 双语植物手册</div>
        <h1>Plants vs. Zombies <i>2</i></h1>
        <h2>My Plant Book: <span>{world}</span></h2>
        <p className="cover-zh">我的植物图鉴 · {world === DEFAULT_WORLD ? '古埃及' : world}</p>
        <div className="cover-note">Learn English with your favourite plants! <span>和你最喜欢的植物一起学英语！</span></div>
      </div>
      <div className="cover-plants">{featuredPlants.slice(0, 6).map((plant) => <Image key={plant.en} plant={plant} />)}</div>
    </div>
    {showGuide && <div className="intro-guide">
      <div className="guide-heading"><div><div className="eyebrow">START HERE · 从这里开始</div><h3>How to read a plant card</h3></div><p>怎么看植物种子卡</p></div>
      <div className="legend-list">{rows.map(([icon, title, zh, desc]) => <div className="legend-row" key={title}><strong>{icon}</strong><div><b>{title}</b><span>{zh}</span></div><p>{desc}</p></div>)}</div>
      <div className="legend-tip">Read the sentence out loud, then find the 3 words inside it! <span>大声读句子，再找出下面的单词！</span></div>
    </div>}
    <div className="cover-footer">DEMO EDITION · {total} plants · ages 5–8</div>
    <Pyramids />
  </section>;
}

function Pyramids() { return <div className="pyramids" aria-hidden="true"><i /><i /><i /><i /></div>; }

const familyOptions = (() => {
  const seen = new Map();
  let hasNone = false;
  plants.forEach((plant) => {
    const code = normalizeFamily(plant.family);
    if (!code) { hasNone = true; return; }
    if (!seen.has(code)) seen.set(code, plant.family_zh || code);
  });
  const options = [...seen.entries()]
    .map(([code, zh]) => ({ code, zh, icon: getFamilyIcon(code) }))
    .sort((a, b) => a.zh.localeCompare(b.zh, 'zh'));
  if (hasNone) options.push({ code: 'none', zh: '无家族', icon: FAMILY_NONE_ICON });
  return options;
})();

function App() {
  const [query, setQuery] = useState('');
  const [world, setWorld] = useState(worlds[0] || DEFAULT_WORLD);
  const [family, setFamily] = useState('');
  const [showGuide, setShowGuide] = useState(true);
  const [detailPlant, setDetailPlant] = useState(null);
  const isAllWorlds = world === ALL_WORLDS;
  const worldPlants = useMemo(() => plants.filter((plant) => isAllWorlds || getWorld(plant) === world), [isAllWorlds, world]);
  const filtered = useMemo(() => plants.filter((plant) => {
    const inWorld = isAllWorlds || getWorld(plant) === world;
    const matchesQuery = `${plant.en} ${plant.zh}`.toLowerCase().includes(query.toLowerCase().trim());
    const plantFamily = normalizeFamily(plant.family);
    const matchesFamily = !family || (family === 'none' ? !plantFamily : plantFamily === family);
    return inWorld && matchesQuery && matchesFamily;
  }), [query, world, family, isAllWorlds]);
  const showIntro = !query && !isAllWorlds;
  const pages = Array.from({ length: Math.ceil(filtered.length / pageSize) }, (_, page) => filtered.slice(page * pageSize, page * pageSize + pageSize));
  return <>
    <div className="toolbar">
      <div className="brand">PVZ2 <span>PLANT BOOK</span></div>
      <label className="world-select"><span>🌍</span><select value={world} onChange={(event) => setWorld(event.target.value)} aria-label="Choose world"><option disabled value="">Choose world</option>{worldOptions.map((item) => <option key={item} value={item}>{item === ALL_WORLDS ? 'All worlds / 全部世界' : item}</option>)}</select></label>
      <label className="search"><span>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search plants / 搜索植物" /></label>
      <div className="toolbar-actions"><button className={showGuide ? 'active' : ''} onClick={() => setShowGuide((value) => !value)}>Guide / 图例</button><a className="print-link" href="/PvZ2_Plants_Ancient_Egypt_A4_Print.html">Print layout ↗</a><button className="print-button" onClick={() => window.print()}>Print A4 ↗</button></div>
    </div>
    <div className="family-bar">
      <fieldset className="family-field">
        <legend>Family <span>家族</span></legend>
        <div className="family-picker">
          <button type="button" className={`family-option family-option--all${family === '' ? ' active' : ''}`} onClick={() => setFamily('')} title="All / 全部">
            <img src={FAMILY_ALL_ICON} alt="All" loading="lazy" />
          </button>
          {familyOptions.map((option) => (
            <button key={option.code} type="button" className={`family-option${family === option.code ? ' active' : ''}`} onClick={() => setFamily(option.code)} title={option.zh}>
              <img src={option.icon} alt={option.zh} loading="lazy" />
            </button>
          ))}
        </div>
      </fieldset>
    </div>
    <main className="book">
      {showIntro && <Intro total={filtered.length} world={world} showGuide={showGuide} featuredPlants={worldPlants} />}
      {pages.length ? pages.map((page, pageIndex) => <section className="page cards-page" key={pageIndex}><div className="page-header"><div>Plants vs. Zombies 2 <span>· {isAllWorlds ? 'All worlds / 全部世界' : world}</span></div><b>{pageIndex + (showIntro ? 2 : 1)} / {pages.length + (showIntro ? 1 : 0)}</b></div><div className="cards-grid">{page.map((plant, index) => <PlantCard key={plant.codename || plant.id || plant.en} plant={plant} index={index} onOpen={setDetailPlant} />)}</div><div className="page-footer">Data & art: Plants vs. Zombies Wiki · 沿虚线裁下即为单词卡</div></section>) : <div className="empty">No plants found · 没有找到植物</div>}
    </main>
    <PlantDetailModal plant={detailPlant} onClose={() => setDetailPlant(null)} />
  </>;
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
