function toggleMark(cell) {
    cell.classList.toggle('marked');
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
    document.getElementById('newBoardBtn').disabled = true;
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
    document.getElementById('newBoardBtn').disabled = false;
}

function newBoard() {
    showLoading();
    fetch('/new-board')
        .then(response => response.json())
        .then(pages => {
            const cells = document.querySelectorAll('.cell');
            pages.forEach((title, index) => {
                cells[index].textContent = title;
                cells[index].classList.remove('marked');
            });
        })
        .catch(error => {
            console.error('Error fetching new board:', error);
            alert('Failed to load new board. Please try again.');
        })
        .finally(() => {
            hideLoading();
        });
}