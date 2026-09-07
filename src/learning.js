export const WORD_COLORS = ['#c2410c', '#047857', '#1d4ed8'];

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function highlightSentence(sentence, words) {
  const marks = [];
  (words || []).forEach(([en], index) => {
    if (!en) return;
    const matcher = new RegExp(`\\b${escapeRegExp(en)}\\b`, 'ig');
    let match = matcher.exec(sentence);
    while (match) {
      marks.push({
        start: match.index,
        end: match.index + match[0].length,
        index,
        text: match[0],
      });
      if (match[0].length === 0) break;
      match = matcher.exec(sentence);
    }
  });
  marks.sort((a, b) => a.start - b.start || (b.end - b.start) - (a.end - a.start));
  const kept = [];
  let cursor = 0;
  marks.forEach((mark) => {
    if (mark.start >= cursor) {
      kept.push(mark);
      cursor = mark.end;
    }
  });
  const parts = [];
  let offset = 0;
  kept.forEach((mark) => {
    if (mark.start > offset) parts.push({ text: sentence.slice(offset, mark.start) });
    parts.push({ text: mark.text, colorIndex: mark.index });
    offset = mark.end;
  });
  if (offset < sentence.length) parts.push({ text: sentence.slice(offset) });
  return parts;
}
