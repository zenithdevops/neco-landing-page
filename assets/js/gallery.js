// Film-strip gallery: arrow buttons, mouse drag-to-scroll (touch scrolls natively), and a
// <dialog> lightbox. Esc closing comes free with showModal().
(() => {
  const film = document.querySelector('[data-film]');
  const dialog = document.querySelector('[data-lightbox]');
  if (!film || !dialog) return;
  const track = film.querySelector('.film__track');
  const prev = film.querySelector('[data-film-prev]');
  const next = film.querySelector('[data-film-next]');
  const dialogImg = dialog.querySelector('img');
  const dialogCaption = dialog.querySelector('figcaption');

  const step = () => track.clientWidth * 0.8;
  prev.addEventListener('click', () => track.scrollBy({ left: -step(), behavior: 'smooth' }));
  next.addEventListener('click', () => track.scrollBy({ left: step(), behavior: 'smooth' }));

  const updateButtons = () => {
    prev.disabled = track.scrollLeft <= 1;
    next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 1;
  };
  track.addEventListener('scroll', updateButtons, { passive: true });
  window.addEventListener('resize', updateButtons);
  window.addEventListener('load', updateButtons);
  track.querySelectorAll('img').forEach((img) => img.addEventListener('load', updateButtons));
  updateButtons();

  let down = false;
  let dragged = false;
  let startX = 0;
  let startScroll = 0;
  track.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'mouse') return;
    down = true; dragged = false; startX = event.clientX; startScroll = track.scrollLeft;
  });
  window.addEventListener('pointermove', (event) => {
    if (!down) return;
    const dx = event.clientX - startX;
    if (!dragged && Math.abs(dx) > 5) { dragged = true; track.classList.add('is-dragging'); }
    if (dragged) track.scrollLeft = startScroll - dx;
  });
  window.addEventListener('pointerup', () => { down = false; track.classList.remove('is-dragging'); });

  track.addEventListener('click', (event) => {
    const opener = event.target.closest('.film__open');
    if (!opener) return;
    if (dragged) { dragged = false; return; }
    const img = opener.querySelector('img');
    dialogImg.src = opener.dataset.full || img.currentSrc || img.src;
    dialogImg.alt = img.alt;
    dialogCaption.textContent = opener.closest('figure').querySelector('figcaption')?.textContent || '';
    dialog.showModal();
  });
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog || event.target.closest('[data-lightbox-close]')) dialog.close();
  });
})();
