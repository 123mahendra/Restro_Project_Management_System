
const userMenu = document.querySelector('.user-dropdown');
userMenu.addEventListener('click', () => {
    const dropdown = userMenu.querySelector('.dropdown-content');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
});

document.addEventListener('click', (e) => {
    const dropdown = document.querySelector('.dropdown-content');
    if (!userMenu.contains(e.target)) {
        dropdown.style.display = 'none';
    }
});