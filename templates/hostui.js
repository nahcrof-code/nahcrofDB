function createToast(text) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
	toastContainer = document.createElement('div');
	toastContainer.id = 'toast-container';
	toastContainer.style.cssText = `
	    position: fixed;
	    bottom: 20px;
	    left: 20px;
	    z-index: 10000;
	    display: flex;
	    flex-direction: column-reverse;
	    gap: 10px;
	    pointer-events: none;
	`;
	document.body.appendChild(toastContainer);
    }

    // Create the toast element
    const toast = document.createElement('div');
    toast.style.cssText = `
	background: rgba(255, 255, 255, 0.1);
	backdrop-filter: blur(10px);
	border: 1px solid var(--border);
	color: #e5e5e5;
	padding: 12px 16px;
	border-radius: 12px;
	font-size: 14px;
	font-weight: 500;
	max-width: 300px;
	word-wrap: break-word;
	transform: translateX(-100%);
	transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	opacity: 0;
	pointer-events: auto;
    `;

    toast.textContent = text;
    toastContainer.appendChild(toast);

    setTimeout(() => {
	toast.style.transform = 'translateX(0)';
	toast.style.opacity = '1';
    }, 10);

    setTimeout(() => {
	toast.style.transform = 'translateX(-100%)';
	toast.style.opacity = '0';
	setTimeout(() => {
	    if (toast.parentNode) {
		toast.parentNode.removeChild(toast);
	    }
	}, 300);
    }, 4000);

    toast.addEventListener('click', () => {
	toast.style.transform = 'translateX(-100%)';
	toast.style.opacity = '0';
	setTimeout(() => {
	    if (toast.parentNode) {
		toast.parentNode.removeChild(toast);
	    }
	}, 300);
    });
}
