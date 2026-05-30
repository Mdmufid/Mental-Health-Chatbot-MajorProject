const modal = document.getElementById('deleteModal');
const openBtn = document.getElementById('openDeleteModal');
const cancelBtn = document.getElementById('cancelDelete');

openBtn.addEventListener('click', () => {
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
});

cancelBtn.addEventListener('click', () => {
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
});

// Close modal if user clicks outside the box
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
    }
});