/**
 * Logic for Quick Create Modal
 * Requires Bootstrap 5 and Tom Select
 */

let quickCreateModal = null;
let currentTargetSelectId = null;

window.openQuickCreate = function(url, title, targetSelectId) {
    if (!quickCreateModal) {
        const modalEl = document.getElementById('quickCreateModal');
        if (modalEl) {
            // Ensure bootstrap is available
            if (typeof bootstrap !== 'undefined') {
                quickCreateModal = new bootstrap.Modal(modalEl);
            } else {
                console.error("Bootstrap is not loaded");
                return;
            }
        } else {
            console.error("Quick Create Modal element not found!");
            return;
        }
    }

    currentTargetSelectId = targetSelectId;
    const modalTitle = document.getElementById('quickCreateTitle');
    const modalBody = document.getElementById('quickCreateBody');

    if (modalTitle) modalTitle.textContent = title;

    if (modalBody) {
        modalBody.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';

        quickCreateModal.show();

        fetch(url)
            .then(response => response.text())
            .then(html => {
                modalBody.innerHTML = html;
                // Re-bind form submission
                const form = modalBody.querySelector('form');
                if (form) {
                    form.addEventListener('submit', handleQuickCreateSubmit);
                }
            })
            .catch(err => {
                modalBody.innerHTML = '<div class="alert alert-danger">Error cargando el formulario.</div>';
                console.error(err);
            });
    }
};

function handleQuickCreateSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            if (quickCreateModal) quickCreateModal.hide();

            // Add to Tom Select
            if (currentTargetSelectId) {
                const selectEl = document.getElementById(currentTargetSelectId);
                if (selectEl && selectEl.tomselect) {
                    selectEl.tomselect.addOption({value: data.id, text: data.text});
                    selectEl.tomselect.addItem(data.id);
                }
            }
        } else {
            // Replace form with validation errors
            const modalBody = document.getElementById('quickCreateBody');
            if (modalBody) {
                modalBody.innerHTML = data.html;
                const newForm = modalBody.querySelector('form');
                if (newForm) {
                    newForm.addEventListener('submit', handleQuickCreateSubmit);
                }
            }
        }
    })
    .catch(err => {
        console.error('Error submitting form:', err);
        alert('Error al guardar.');
    });
}
