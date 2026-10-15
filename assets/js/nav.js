// Header: solid after scrolling, active-section highlight, and the mobile menu.
(() => {
  const root = document.documentElement;
  const header = document.querySelector('[data-header]');
  const toggle = document.querySelector('[data-nav-toggle]');
  const links = [...document.querySelectorAll('.nav__link')];

  const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 24);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const linkFor = new Map(links.map((link) => [link.getAttribute('href').slice(1), link]));
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      links.forEach((link) => { link.classList.remove('is-active'); link.removeAttribute('aria-current'); });
      const active = linkFor.get(entry.target.id);
      if (active) { active.classList.add('is-active'); active.setAttribute('aria-current', 'location'); }
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  linkFor.forEach((_, id) => { const section = document.getElementById(id); if (section) observer.observe(section); });

  const setOpen = (open) => {
    root.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    toggle.querySelector('use').setAttribute('href', `assets/brand/icons.svg#${open ? 'x' : 'menu'}`);
  };
  toggle.addEventListener('click', () => setOpen(!root.classList.contains('nav-open')));
  links.forEach((link) => link.addEventListener('click', () => setOpen(false)));
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') setOpen(false); });
  window.matchMedia('(min-width: 901px)').addEventListener('change', (event) => { if (event.matches) setOpen(false); });
})();
