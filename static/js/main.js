/**
 * EVENTPULSE - Modern Event Discovery & Management Platform
 * Frontend Interactions & Dynamic Components
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Bootstrap Tooltips & Popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. Demo Login Quick-Fill Helper
    window.fillDemoLogin = function(username, password) {
        const userInput = document.getElementById('id_username') || document.querySelector('input[name="username"]');
        const passInput = document.getElementById('id_password') || document.querySelector('input[name="password"]');
        if (userInput && passInput) {
            userInput.value = username;
            passInput.value = password;
            // Highlight inputs briefly
            userInput.classList.add('border-primary');
            passInput.classList.add('border-primary');
            setTimeout(() => {
                userInput.classList.remove('border-primary');
                passInput.classList.remove('border-primary');
            }, 600);
        }
    };

    // 3. Dynamic QR Code Generator (Renders clean SVG QR matrix)
    window.renderQRCode = function(elementId, text) {
        const container = document.getElementById(elementId);
        if (!container) return;

        // Deterministic hash to generate reproducible realistic QR matrix
        let hash = 0;
        for (let i = 0; i < text.length; i++) {
            hash = ((hash << 5) - hash) + text.charCodeAt(i);
            hash |= 0;
        }

        const size = 25; // 25x25 QR grid
        const cellSize = 5;
        const svgSize = size * cellSize;

        let rects = '';
        
        // Function to check if a cell is part of the 3 corner position markers
        function isCornerMarker(r, c) {
            // Top-left
            if (r < 7 && c < 7) return true;
            // Top-right
            if (r < 7 && c >= size - 7) return true;
            // Bottom-left
            if (r >= size - 7 && c < 7) return true;
            return false;
        }

        // Draw standard position squares
        function drawFinder(startR, startC) {
            let out = '';
            // Outer 7x7
            out += `<rect x="${startC * cellSize}" y="${startR * cellSize}" width="${7 * cellSize}" height="${7 * cellSize}" fill="#0f172a" rx="2" />`;
            out += `<rect x="${(startC + 1) * cellSize}" y="${(startR + 1) * cellSize}" width="${5 * cellSize}" height="${5 * cellSize}" fill="#ffffff" />`;
            out += `<rect x="${(startC + 2) * cellSize}" y="${(startR + 2) * cellSize}" width="${3 * cellSize}" height="${3 * cellSize}" fill="#7c3aed" rx="1" />`;
            return out;
        }

        let svg = `<svg viewBox="0 0 ${svgSize} ${svgSize}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">`;
        svg += `<rect width="${svgSize}" height="${svgSize}" fill="#ffffff" rx="8" />`;

        svg += drawFinder(0, 0);
        svg += drawFinder(0, size - 7);
        svg += drawFinder(size - 7, 0);

        // Pseudorandom grid seeded by the text hash
        let seed = Math.abs(hash);
        for (let r = 0; r < size; r++) {
            for (let c = 0; c < size; c++) {
                if (isCornerMarker(r, c)) continue;
                // Seed update
                seed = (seed * 9301 + 49297) % 233280;
                const rnd = seed / 233280;
                if (rnd > 0.52) {
                    rects += `<rect x="${c * cellSize}" y="${r * cellSize}" width="${cellSize - 0.5}" height="${cellSize - 0.5}" fill="#1e1b4b" rx="1"/>`;
                }
            }
        }

        svg += rects;
        svg += `</svg>`;
        container.innerHTML = svg;
    };

    // Auto render QR code if element exists
    const qrTarget = document.getElementById('ticket-qrcode-canvas');
    if (qrTarget) {
        const token = qrTarget.getAttribute('data-token') || 'EVENT-PASS-DEMO';
        renderQRCode('ticket-qrcode-canvas', token);
    }

    // 4. Barcode Generator
    const barcodeTarget = document.getElementById('ticket-barcode');
    if (barcodeTarget) {
        const code = barcodeTarget.getAttribute('data-code') || 'EVT-98240-2026';
        let bars = '';
        for (let i = 0; i < 38; i++) {
            const width = (i % 3 === 0) ? 3 : (i % 2 === 0 ? 1 : 2);
            bars += `<span style="display:inline-block;height:40px;width:${width}px;background:#0f172a;margin-right:2px;"></span>`;
        }
        barcodeTarget.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;">${bars}</div><div class="text-center font-monospace mt-1 text-muted small">${code}</div>`;
    }

    // 5. Live Ticket Selection & Pricing Calculator
    const ticketSelect = document.getElementById('ticket_tier_select');
    const ticketQtyInput = document.getElementById('ticket_quantity');
    const subtotalDisplay = document.getElementById('checkout_subtotal');
    const totalDisplay = document.getElementById('checkout_total');
    const feeDisplay = document.getElementById('checkout_fee');

    function updateTicketCalculation() {
        if (!ticketSelect || !ticketQtyInput) return;

        const selectedOption = ticketSelect.options[ticketSelect.selectedIndex];
        if (!selectedOption) return;

        const price = parseFloat(selectedOption.getAttribute('data-price') || '0');
        let qty = parseInt(ticketQtyInput.value || '1', 10);
        if (qty < 1) qty = 1;

        const subtotal = price * qty;
        const fee = price > 0 ? (subtotal * 0.03) : 0; // 3% simulated fee
        const total = subtotal + fee;

        if (subtotalDisplay) subtotalDisplay.innerText = '$' + subtotal.toFixed(2);
        if (feeDisplay) feeDisplay.innerText = '$' + fee.toFixed(2);
        if (totalDisplay) totalDisplay.innerText = '$' + total.toFixed(2);
    }

    if (ticketSelect) {
        ticketSelect.addEventListener('change', updateTicketCalculation);
    }
    if (ticketQtyInput) {
        ticketQtyInput.addEventListener('input', updateTicketCalculation);
    }

    // Quantity buttons (+ / -)
    const btnQtyDec = document.getElementById('btn_qty_dec');
    const btnQtyInc = document.getElementById('btn_qty_inc');
    if (btnQtyDec && ticketQtyInput) {
        btnQtyDec.addEventListener('click', function () {
            let current = parseInt(ticketQtyInput.value || '1', 10);
            if (current > 1) {
                ticketQtyInput.value = current - 1;
                updateTicketCalculation();
            }
        });
    }
    if (btnQtyInc && ticketQtyInput) {
        btnQtyInc.addEventListener('click', function () {
            let current = parseInt(ticketQtyInput.value || '1', 10);
            const max = parseInt(ticketQtyInput.getAttribute('max') || '10', 10);
            if (current < max) {
                ticketQtyInput.value = current + 1;
                updateTicketCalculation();
            }
        });
    }

    // Initial calculation on load
    updateTicketCalculation();

    // 6. Bookmark / Save Event Toggle
    window.toggleBookmark = function(eventId, buttonEl) {
        const csrfToken = getCookie('csrftoken');
        fetch(`/events/${eventId}/bookmark/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.status === 401 || response.status === 403) {
                window.location.href = '/login/?next=' + window.location.pathname;
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                const icon = buttonEl.querySelector('i');
                if (data.saved) {
                    buttonEl.classList.add('saved');
                    if (icon) {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                    }
                    showToast('Event Saved', 'Added to your saved events list.', 'success');
                } else {
                    buttonEl.classList.remove('saved');
                    if (icon) {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                    }
                    showToast('Event Removed', 'Removed from saved events.', 'info');
                }
            }
        })
        .catch(err => {
            console.error('Bookmark error:', err);
        });
    };

    // Helper: get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 7. Toast Notification Helper
    window.showToast = function(title, message, type = 'info') {
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        const bgClass = type === 'success' ? 'bg-success' : (type === 'error' ? 'bg-danger' : 'bg-primary');
        const iconClass = type === 'success' ? 'bi-check-circle-fill' : (type === 'error' ? 'bi-exclamation-triangle-fill' : 'bi-info-circle-fill');

        const toastEl = document.createElement('div');
        toastEl.className = 'toast align-items-center text-white border-0 ' + bgClass;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2">
                    <i class="bi ${iconClass} fs-5"></i>
                    <div>
                        <strong>${title}</strong>
                        <div class="small">${message}</div>
                    </div>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toastEl);
        const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
        bsToast.show();
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    };

    // 8. Copy to Clipboard Utility
    window.copyToClipboard = function(text, successMessage = 'Copied to clipboard!') {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Success', successMessage, 'success');
        }).catch(() => {
            // Fallback
            const el = document.createElement('textarea');
            el.value = text;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            showToast('Success', successMessage, 'success');
        });
    };
});
