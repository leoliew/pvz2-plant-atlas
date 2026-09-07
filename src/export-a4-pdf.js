import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

const A4_WIDTH_MM = 210;
const A4_HEIGHT_MM = 297;

function wait(ms = 0) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function fitA4(canvasWidth, canvasHeight) {
  const canvasRatio = canvasWidth / canvasHeight;
  const pageRatio = A4_WIDTH_MM / A4_HEIGHT_MM;
  if (Math.abs(canvasRatio - pageRatio) < 0.002) {
    return { x: 0, y: 0, width: A4_WIDTH_MM, height: A4_HEIGHT_MM };
  }
  if (canvasRatio > pageRatio) {
    const height = A4_WIDTH_MM / canvasRatio;
    return { x: 0, y: (A4_HEIGHT_MM - height) / 2, width: A4_WIDTH_MM, height };
  }
  const width = A4_HEIGHT_MM * canvasRatio;
  return { x: (A4_WIDTH_MM - width) / 2, y: 0, width, height: A4_HEIGHT_MM };
}

function sizeReplacedImages(root) {
  const view = root.ownerDocument.defaultView;
  if (!view) return;
  root.querySelectorAll('img.art, img.fam, img.family-badge').forEach((img) => {
    const naturalWidth = img.naturalWidth;
    const naturalHeight = img.naturalHeight;
    if (!naturalWidth || !naturalHeight) return;
    const computed = view.getComputedStyle(img);
    const boxWidth = img.clientWidth || Number.parseFloat(computed.width);
    const boxHeight = img.clientHeight || Number.parseFloat(computed.height);
    if (!boxWidth || !boxHeight) return;
    const scale = Math.min(boxWidth / naturalWidth, boxHeight / naturalHeight);
    img.style.width = `${naturalWidth * scale}px`;
    img.style.height = `${naturalHeight * scale}px`;
    img.style.maxWidth = 'none';
    img.style.maxHeight = 'none';
    img.style.padding = '0';
    img.style.objectFit = 'fill';
  });
}

function clampPage(value, pageCount) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return 1;
  return Math.min(Math.max(1, parsed), pageCount);
}

export function setPageRangeInputs({ fromInput, toInput, totalLabel, pageCount }) {
  fromInput.min = '1';
  toInput.min = '1';
  fromInput.max = String(pageCount);
  toInput.max = String(pageCount);
  fromInput.value = '1';
  toInput.value = String(pageCount);
  totalLabel.textContent = `of ${pageCount} pages · 共 ${pageCount} 页`;
}

function readRange(fromInput, toInput, pageCount) {
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

export function bindA4PdfExport({
  button,
  statusEl,
  fromInput,
  toInput,
  filename,
  pageSelector = '.page',
}) {
  const setStatus = (text) => {
    statusEl.hidden = !text;
    statusEl.textContent = text;
  };

  button.addEventListener('click', async () => {
    const allPages = [...document.querySelectorAll(pageSelector)];
    if (!allPages.length) return;
    const { from, to } = readRange(fromInput, toInput, allPages.length);
    const pages = allPages.slice(from - 1, to);
    const rangeLabel = from === 1 && to === allPages.length ? '' : `_p${from}-${to}`;

    button.disabled = true;
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
          backgroundColor: getComputedStyle(page).backgroundColor || '#ffffff',
          logging: false,
          imageTimeout: 20000,
          onclone: (clonedDoc, clonedPage) => sizeReplacedImages(clonedPage || clonedDoc.body),
        });
        const imageData = canvas.toDataURL('image/jpeg', 0.88);
        if (index > 0) pdf.addPage('a4', 'p');
        const { x, y, width, height } = fitA4(canvas.width, canvas.height);
        pdf.addImage(imageData, 'JPEG', x, y, width, height, undefined, 'FAST');
        canvas.width = 0;
        canvas.height = 0;
      }

      pdf.save(`${filename}${rangeLabel}.pdf`);
      setStatus(`Saved p${from}–${to} · 已保存`);
    } catch (error) {
      console.error(error);
      setStatus('Export failed · 导出失败');
    } finally {
      button.disabled = false;
      fromInput.disabled = false;
      toInput.disabled = false;
    }
  });
}
