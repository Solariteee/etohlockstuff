const cards = document.querySelectorAll('.card');
let level = 'all';

document.getElementById('search').addEventListener('input', filter);
document.querySelectorAll('.f-btn[data-level]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.f-btn[data-level]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        level = btn.dataset.level;
        filter();
    });
});

function filter() {
    const q = document.getElementById('search').value.toLowerCase();
    let n = 0;
    cards.forEach(c => {
        const ok = (level === 'all' || c.dataset.level === level) && (!q || c.dataset.name.includes(q) || c.dataset.desc.includes(q) || c.dataset.ids.includes(q));
        c.style.display = ok ? '' : 'none';
        if (ok) n++;
    });
    document.getElementById('empty').style.display = n === 0 ? 'block' : 'none';
}

const viewToggle = document.getElementById('view-toggle');
viewToggle.addEventListener('click', () => {
    const grid = document.getElementById('grid');
    const isList = grid.classList.toggle('list-view');
    viewToggle.textContent = isList ? 'Grid' : 'List';
});