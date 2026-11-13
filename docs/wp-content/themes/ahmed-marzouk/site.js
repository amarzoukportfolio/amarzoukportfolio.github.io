const filterButtons = document.querySelectorAll('[data-filter]');
filterButtons.forEach(button => button.addEventListener('click', () => {
  const selected = button.dataset.filter;
  let count = 0;
  filterButtons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  document.querySelectorAll('[data-tags]').forEach(card => {
    const show = selected === 'all' || card.dataset.tags.split('|').includes(selected);
    card.hidden = !show;
    if (show) count++;
  });
  const status = document.querySelector('.filter-status');
  if (status) status.textContent = `${count} ${count === 1 ? 'project' : 'projects'} shown`;
}));

document.querySelectorAll('[data-gif]').forEach(button => {
  button.addEventListener('click', () => {
    const playing = button.getAttribute('aria-pressed') === 'true';
    const img = button.closest('.project-animation').querySelector('img');
    img.src = playing ? button.dataset.poster : button.dataset.gif;
    button.setAttribute('aria-pressed', String(!playing));
    button.textContent = playing ? 'Play GIF' : 'Pause GIF';
  });
});
