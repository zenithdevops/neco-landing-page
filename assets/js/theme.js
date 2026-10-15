// Dark/light toggle. The inline <head> snippet applies a saved choice before paint; this file
// only runs the button. No colour is touched here: data-theme flips color-scheme in tokens.css.
(() => {
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');
  if (!button) return;
  const icon = button.querySelector('use');
  const prefersLight = window.matchMedia('(prefers-color-scheme: light)');
  const current = () => root.dataset.theme || (prefersLight.matches ? 'light' : 'dark');

  const render = () => {
    const next = current() === 'dark' ? 'light' : 'dark';
    button.setAttribute('aria-label', `Switch to ${next} theme`);
    icon.setAttribute('href', `assets/brand/icons.svg#${next === 'light' ? 'sun' : 'moon'}`);
  };

  button.addEventListener('click', () => {
    const next = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('neco-theme', next); } catch (e) { /* storage blocked: lasts this visit */ }
    render();
  });
  prefersLight.addEventListener('change', render);
  render();
})();
