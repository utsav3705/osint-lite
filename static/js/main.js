/**
 * OSINT-Pro — Main JavaScript
 * Form validation, loading states, dark mode, case management,
 * court upload drag-and-drop, and micro-animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    initFormValidation();
    initRiskAnimation();
    initScrollAnimations();
    initDarkMode();
    initCaseSearch();
    initCourtUpload();
    initDeleteHandlers();
    initWorkspaceTabs();
});


// ── Form validation & loading state ──────────────────────────

function initFormValidation() {
    const form = document.getElementById('investigation-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        const inputs = form.querySelectorAll('.custom-input');
        let hasValue = false;

        inputs.forEach((input) => {
            if (input.value.trim()) {
                hasValue = true;
            }
        });

        if (!hasValue) {
            e.preventDefault();
            showToast('Please fill in at least one field to start an investigation.', 'warning');
            return;
        }

        // Show loading state
        const btn = document.getElementById('btn-investigate');
        if (btn) {
            const btnText = btn.querySelector('.btn-text');
            const btnLoading = btn.querySelector('.btn-loading');
            if (btnText && btnLoading) {
                btnText.classList.add('d-none');
                btnLoading.classList.remove('d-none');
            }
            btn.disabled = true;
        }
    });

    // Court upload form loading
    const courtForm = document.getElementById('court-upload-form');
    if (courtForm) {
        courtForm.addEventListener('submit', () => {
            const btn = document.getElementById('btn-analyze');
            if (btn) {
                const btnText = btn.querySelector('.btn-text');
                const btnLoading = btn.querySelector('.btn-loading');
                if (btnText && btnLoading) {
                    btnText.classList.add('d-none');
                    btnLoading.classList.remove('d-none');
                }
                btn.disabled = true;
            }
        });
    }
}


// ── Risk score animation ─────────────────────────────────────

function initRiskAnimation() {
    const scoreEl = document.getElementById('risk-score-number');
    const progressBar = document.getElementById('risk-progress-bar');
    if (!scoreEl) return;

    const target = parseInt(scoreEl.textContent, 10);
    scoreEl.textContent = '0';

    setTimeout(() => {
        animateCounter(scoreEl, 0, target, 1200);

        if (progressBar) {
            progressBar.style.width = '0%';
            requestAnimationFrame(() => {
                progressBar.style.width = target + '%';
            });
        }
    }, 400);
}


function animateCounter(element, start, end, duration) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (end - start) * eased);

        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}


// ── Scroll animations ────────────────────────────────────────

function initScrollAnimations() {
    if (!('IntersectionObserver' in window)) return;

    const cards = document.querySelectorAll('.report-card, .feature-card, .stat-card');
    if (!cards.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach((card) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(card);
    });
}


// ── Dark Mode Toggle ─────────────────────────────────────────

function initDarkMode() {
    const toggle = document.getElementById('dark-mode-toggle');
    if (!toggle) return;

    const icon = toggle.querySelector('i');
    const savedMode = localStorage.getItem('osint-pro-mode') || 'dark';

    if (savedMode === 'light') {
        document.documentElement.setAttribute('data-bs-theme', 'light');
        if (icon) {
            icon.classList.remove('bi-moon-stars-fill');
            icon.classList.add('bi-sun-fill');
        }
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
    }

    toggle.addEventListener('click', (e) => {
        e.preventDefault();
        
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('osint-pro-mode', newTheme);

        if (icon) {
            if (newTheme === 'light') {
                icon.classList.remove('bi-moon-stars-fill');
                icon.classList.add('bi-sun-fill');
            } else {
                icon.classList.remove('bi-sun-fill');
                icon.classList.add('bi-moon-stars-fill');
            }
        }
    });
}


// ── Case Search & Filter ─────────────────────────────────────

function initCaseSearch() {
    const searchInput = document.getElementById('case-search');
    const filterSelect = document.getElementById('risk-filter');
    const table = document.getElementById('cases-table');

    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');

    function filterRows() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const riskFilter = filterSelect ? filterSelect.value : '';
        let visibleCount = 0;

        rows.forEach(row => {
            const name = row.dataset.name || '';
            const company = row.dataset.company || '';
            const risk = row.dataset.risk || '';

            const matchesSearch = !searchTerm ||
                name.includes(searchTerm) ||
                company.includes(searchTerm);

            const matchesRisk = !riskFilter || risk === riskFilter;

            if (matchesSearch && matchesRisk) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Update count badge
        const countBadge = document.getElementById('case-count');
        if (countBadge) {
            countBadge.textContent = visibleCount;
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterRows);
    }
    if (filterSelect) {
        filterSelect.addEventListener('change', filterRows);
    }
}


// ── Court Document Upload ────────────────────────────────────

function initCourtUpload() {
    const zone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('court-pdf-input');
    const fileDisplay = document.getElementById('file-name-display');
    const fileName = document.getElementById('selected-file-name');

    if (!zone || !fileInput) return;

    // Drag-and-drop visual feedback
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('drag-over');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');

        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            showSelectedFile(e.dataTransfer.files[0].name);
        }
    });

    // Click-to-select feedback
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            showSelectedFile(fileInput.files[0].name);
        }
    });

    function showSelectedFile(name) {
        if (fileDisplay && fileName) {
            fileName.textContent = name;
            fileDisplay.classList.remove('d-none');
        }
    }
}


// ── Delete Confirmation ──────────────────────────────────────

function initDeleteHandlers() {
    const deleteButtons = document.querySelectorAll('.btn-delete-case');
    const deleteForm = document.getElementById('delete-form');
    const deleteModal = document.getElementById('deleteModal');

    if (!deleteForm || !deleteModal) return;

    deleteButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const caseId = btn.dataset.caseId;
            if (caseId) {
                deleteForm.action = `/cases/${caseId}/delete`;
                const modal = new bootstrap.Modal(deleteModal);
                modal.show();
            }
        });
    });
}


// ── Toast Helper ─────────────────────────────────────────────

function showToast(message, type) {
    const container = document.querySelector('.container.mt-3') || document.querySelector('main');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        <i class="bi bi-exclamation-triangle-fill me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.prepend(alert);

    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

// ── Workspace Tab Events ─────────────────────────────────────
function initWorkspaceTabs() {
    const tabEls = document.querySelectorAll('button[data-bs-toggle="pill"]');
    tabEls.forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', function (event) {
            if (event.target.id === 'tab-network-tab') {
                if (typeof Plotly !== 'undefined') {
                    const plotEl = document.querySelector('.js-plotly-plot');
                    if (plotEl) {
                        Plotly.Plots.resize(plotEl);
                    }
                } else {
                    window.dispatchEvent(new Event('resize'));
                }
            }
        });
    });
}
