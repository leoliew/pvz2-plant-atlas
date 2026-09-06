// Code -> filename table, copied verbatim from pvzg_site's
// src/components/almanac-v2/world-backgrounds.ts (handles the two
// irregular names: ice -> iceage, water -> beach_watered).
export const WORLD_BACKGROUND_FILES = {
  beach: 'beach', boost: 'boost', cowboy: 'cowboy', dark: 'dark', dino: 'dino',
  egypt: 'egypt', eighties: 'eighties', epic: 'epic', frontyard: 'frontyard',
  future: 'future', ice: 'iceage', kongfu: 'kongfu', lod: 'lod', lostcity: 'lostcity',
  market: 'market', mint: 'mint', modern: 'modern', pirate: 'pirate', sky: 'sky',
  water: 'beach_watered',
};

export function resolveWorldBackgroundFile(code) {
  return WORLD_BACKGROUND_FILES[code] || 'default';
}
