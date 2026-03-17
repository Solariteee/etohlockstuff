if (!localStorage.getItem('doNotShow')) {
    const overlay = document.createElement('div');
    overlay.id = 'warning-overlay';
    overlay.innerHTML = `
        <div id="warning-box">
            <h1 id="warning-title">Sensitive Content</h1>
            <p id="warning-body">This site contains evidence of misconduct including potentially inappropriate language, imagery, and other sensitive material.</p>
            <div id="warning-actions">
                <button id="warning-proceed">I understand, proceed</button>
                <button id="warning-leave">Do not show again</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById('warning-proceed').addEventListener('click', () => {
        sessionStorage.setItem('warned', '1');
        overlay.remove();
    });

    document.getElementById('warning-leave').addEventListener('click', () => {
        localStorage.setItem('doNotShow', '1');
        overlay.remove();
    });
}