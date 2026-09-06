import { StrictMode, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import plants from '../plants_egypt.json';
import './styles.css';

const pageSize = 4;
const DEFAULT_WORLD = 'Ancient Egypt';

function getWorld(plant) {
  if (plant.world) return plant.world;
  if (/Ancient Egypt|Player's House|Start of the game/i.test(plant.unlock || '')) return DEFAULT_WORLD;
  return 'Other worlds';
}

const WORLD_ORDER = ['Ancient Egypt', 'Pirate Seas', 'Wild West', 'Frostbite Caves', 'Lost City', 'Far Future', 'Dark Ages', 'Jurassic Marsh', 'Big Wave Beach', 'Modern Day', 'Premium & special', 'Mint family', 'Other worlds'];
// Keep the catalog data-driven while preserving the in-game world order.
const worlds = WORLD_ORDER.filter((world) => plants.some((plant) => getWorld(plant) === world));

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
      <span className="stat-label">{label}<small>{zh}</small></span>
      <strong>{value}</strong>
    </div>
  );
}

function PlantCard({ plant, index }) {
  return (
            <article className="plant-card" style={{ '--accent': plant.color, '--delay': `${index * 45}ms` }}>
      <header className="card-ribbon">
        <div><b>{plant.en}</b><span>{plant.zh}</span></div>
        <Sun value={plant.sun} />
      </header>
      <div className="card-body">
        <div className="plant-art"><Image plant={plant} /></div>
        <div className="card-copy">
          <div className="card-meta">{plant.family}<span>{plant.unlock}</span></div>
          <div className="stats">
            <Stat icon="◷" label="Recharge" zh="冷却" value={`${plant.recharge} · ${plant.recharge_zh}`} accent={plant.color} />
            <Stat icon="♥" label="Toughness" zh="生命" value={plant.toughness} accent={plant.color} />
            <Stat icon="ϟ" label="Damage" zh="攻击" value={plant.damage} accent={plant.color} />
          </div>
          <div className="range"><span>➜</span><b>Range</b> {plant.range}<em>{plant.range_zh}</em></div>
          <div className="say"><b>{plant.sentence}</b><span>{plant.sentence_zh}</span></div>
          <div className="words">{plant.words.map(([en, zh]) => <span key={en}><b>{en}</b><small>{zh}</small></span>)}</div>
        </div>
      </div>
    </article>
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

function App() {
  const [query, setQuery] = useState('');
  const [world, setWorld] = useState(worlds[0] || DEFAULT_WORLD);
  const [showGuide, setShowGuide] = useState(true);
  const worldPlants = useMemo(() => plants.filter((plant) => getWorld(plant) === world), [world]);
  const filtered = useMemo(() => plants.filter((plant) => {
    const inWorld = getWorld(plant) === world;
    const matchesQuery = `${plant.en} ${plant.zh}`.toLowerCase().includes(query.toLowerCase().trim());
    return inWorld && matchesQuery;
  }), [query, world]);
  const pages = Array.from({ length: Math.ceil(filtered.length / pageSize) }, (_, page) => filtered.slice(page * pageSize, page * pageSize + pageSize));
  return <>
    <div className="toolbar">
      <div className="brand">PVZ2 <span>PLANT BOOK</span></div>
      <label className="world-select"><span>🌍</span><select value={world} onChange={(event) => setWorld(event.target.value)} aria-label="Choose world"><option disabled value="">Choose world</option>{worlds.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
      <label className="search"><span>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search plants / 搜索植物" /></label>
      <div className="toolbar-actions"><button className={showGuide ? 'active' : ''} onClick={() => setShowGuide((value) => !value)}>Guide / 图例</button><a className="print-link" href="/PvZ2_Plants_Ancient_Egypt_A4_Print.html">Print layout ↗</a><button className="print-button" onClick={() => window.print()}>Print A4 ↗</button></div>
    </div>
    <main className="book">
      {!query && <Intro total={filtered.length} world={world} showGuide={showGuide} featuredPlants={worldPlants} />}
      {pages.length ? pages.map((page, pageIndex) => <section className="page cards-page" key={pageIndex}><div className="page-header"><div>Plants vs. Zombies 2 <span>· {world}</span></div><b>{pageIndex + (query ? 1 : 2)} / {pages.length + (query ? 0 : 1)}</b></div><div className="cards-grid">{page.map((plant, index) => <PlantCard key={plant.codename || plant.id || plant.en} plant={plant} index={index} />)}</div><div className="page-footer">Data & art: Plants vs. Zombies Wiki · 沿虚线裁下即为单词卡</div></section>) : <div className="empty">No plants found · 没有找到植物</div>}
    </main>
  </>;
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
