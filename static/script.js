// ============ DARK MODE TOGGLE ============
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    
    const btn = document.querySelector('.btn-dark-mode');
    if (btn) btn.textContent = isDark ? '☀️' : '🌙';
}

// Load dark mode preference
document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        const btn = document.querySelector('.btn-dark-mode');
        if (btn) btn.textContent = '☀️';
    }
    
    showSearchHistory();
});

// ============ AUTHENTICATION ============
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('user');
        localStorage.removeItem('login_time');
        window.location.href = '/';
    }
}

// ============ SEARCH HISTORY ============
function saveSearchHistory(product) {
    if (!product || product.trim() === '') return;
    
    let history = JSON.parse(localStorage.getItem('search_history') || '[]');
    history = history.filter(item => item.toLowerCase() !== product.toLowerCase());
    history.unshift(product);
    
    if (history.length > 5) {
        history = history.slice(0, 5);
    }
    
    localStorage.setItem('search_history', JSON.stringify(history));
}

function showSearchHistory() {
    const container = document.getElementById('search-history-container');
    if (!container) return;
    
    let history = JSON.parse(localStorage.getItem('search_history') || '[]');
    
    if (history.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<div class="search-history">';
    html += '<h4>🕐 Recent Searches:</h4>';
    
    history.forEach(item => {
        html += `<button onclick="searchFromHistory('${item}')">${item}</button>`;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function searchFromHistory(product) {
    const input = document.getElementById('product-search');
    if (input) {
        input.value = product;
        input.closest('form').submit();
    }
}

// ============ WISHLIST FUNCTIONS ============
function addToWishlist(title, price, store, cardIndex) {
    let wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    
    const item = {
        title: title,
        price: price,
        store: store,
        date: new Date().toISOString()
    };
    
    const exists = wishlist.some(w => w.title === title && w.store === store);
    
    if (!exists) {
        wishlist.push(item);
        localStorage.setItem('wishlist', JSON.stringify(wishlist));
        
        // Highlight the button
        const btn = document.querySelector(`#product-${cardIndex} .btn-wishlist`);
        if (btn) {
            btn.classList.add('wishlisted');
            btn.style.backgroundColor = '#ff6b6b';
            btn.style.borderColor = '#ff6b6b';
            btn.style.color = 'white';
        }
        
        showNotification(`❤️ Added "${title.substring(0, 30)}..." to wishlist!`);
    } else {
        // Remove from wishlist
        wishlist = wishlist.filter(w => !(w.title === title && w.store === store));
        localStorage.setItem('wishlist', JSON.stringify(wishlist));
        
        const btn = document.querySelector(`#product-${cardIndex} .btn-wishlist`);
        if (btn) {
            btn.classList.remove('wishlisted');
            btn.style.backgroundColor = '#f0f0f0';
            btn.style.borderColor = '#ddd';
            btn.style.color = 'inherit';
        }
        
        showNotification(`❌ Removed from wishlist!`);
    }
}

// ============ MULTI-PLATFORM SHARE FUNCTIONALITY ============
function shareProduct(title, price, store) {
    const text = `🔥 Check this out on Price Compare!\n\n📱 ${title}\n💰 Price: ₹${price}\n🏪 Store: ${store}\n\nCompare prices now! 💰`;
    const url = window.location.href;
    
    // Show share modal with multiple options
    showShareModal(title, price, store, text, url);
}

// ============ NOTIFICATION ============
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 1rem 2rem;
        border-radius: 5px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============ PRICE CHART ============
function toggleChart(chartId) {
    const chartDiv = document.getElementById('chart-container-' + chartId);
    if (chartDiv.style.display === 'none' || !chartDiv.style.display) {
        chartDiv.style.display = 'block';
        drawChart(chartId);
    } else {
        chartDiv.style.display = 'none';
    }
}

function drawChart(chartId) {
    const chartContainer = document.getElementById('chart-container-' + chartId);
    if (chartContainer.children.length === 0) {
        // Get product price
        const productCard = document.querySelector(`[id*="product-${chartId}"]`);
        const priceElement = productCard.querySelector('.price');
        const currentPrice = parseFloat(priceElement.textContent.replace(/[^\d.]/g, ''));
        
        // Generate realistic data
        const dates = [];
        const prices = [];
        
        const basePrice = currentPrice * 1.15;
        
        for (let i = 0; i < 30; i++) {
            // Trend: price decreasing
            const trend = i * (basePrice * 0.0066);
            
            // Weekly pattern
            const dayOfWeek = i % 7;
            const weeklyVar = (dayOfWeek === 5 || dayOfWeek === 6) ? -0.02 : 0.01;
            
            // Daily randomness
            const dailyRandom = (Math.random() - 0.5) * 0.06;
            
            let price = basePrice - trend + (basePrice * weeklyVar) + (basePrice * dailyRandom);
            price = Math.max(price, currentPrice * 0.85);
            
            const date = new Date();
            date.setDate(date.getDate() - (30 - i));
            dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            prices.push(Math.round(price));
        }
        
        dates.push('Today');
        prices.push(Math.round(currentPrice));
        
        const traces = [{
            x: dates,
            y: prices,
            mode: 'lines+markers',
            type: 'scatter',
            name: 'Price',
            line: {color: '#ff6b35', width: 3},
            marker: {size: 6},
            fill: 'tozeroy',
            fillcolor: 'rgba(255, 107, 53, 0.15)'
        }];

        const layout = {
            title: '30-Day Price History (₹)',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Price in Rupees (₹)' },
            plot_bgcolor: '#f9f9f9',
            paper_bgcolor: '#fff',
            font: {color: '#333', size: 11},
            margin: {l: 70, r: 40, t: 50, b: 60},
            hovermode: 'x unified'
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot(chartContainer, traces, layout, {responsive: true, displayModeBar: false});
        }
    }
}

function showShareModal(title, price, store, text, url) {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'share-modal';
    modal.innerHTML = `
        <div class="share-modal-content">
            <h3>📱 Share This Product</h3>
            <p>${title}</p>
            <p class="share-price">₹${price}</p>
            
            <div class="share-options">
                <button class="share-btn whatsapp-share" onclick="shareToWhatsApp('${title}', '${price}', '${store}')">
                    💬 WhatsApp
                </button>
                <button class="share-btn email-share" onclick="shareToEmail('${title}', '${price}', '${store}')">
                    📧 Email
                </button>
                <button class="share-btn twitter-share" onclick="shareToTwitter('${title}', '${price}')">
                    𝕏 Twitter
                </button>
                <button class="share-btn facebook-share" onclick="shareToFacebook()">
                    f Facebook
                </button>
                <button class="share-btn copy-share" onclick="copyToClipboard('${title}', '${price}', '${store}')">
                    📋 Copy Link
                </button>
            </div>
            
            <button class="close-modal" onclick="this.closest('.share-modal').remove()">✕ Close</button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function shareToWhatsApp(title, price, store) {
    const text = `🔥 Check out this product!\n\n📱 ${title}\n💰 Price: ₹${price}\n🏪 Store: ${store}\n\n🔗 Compare prices: ${window.location.href}`;
    const whatsappURL = `https://wa.me/?text=${encodeURIComponent(text)}`;
    window.open(whatsappURL, '_blank');
    closeShareModal();
}

function shareToEmail(title, price, store) {
    const subject = `Check out: ${title} - ₹${price}`;
    const body = `Hi!\n\nI found this product on Price Compare:\n\nProduct: ${title}\nPrice: ₹${price}\nStore: ${store}\n\nLink: ${window.location.href}\n\nBest regards`;
    const emailURL = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.open(emailURL);
    closeShareModal();
}

function shareToTwitter(title, price) {
    const text = `Found this amazing product on Price Compare! 🛍️\n\n${title}\nPrice: ₹${price}\n\n#PriceCompare #Shopping #Deals`;
    const twitterURL = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${window.location.href}`;
    window.open(twitterURL, '_blank');
    closeShareModal();
}

function shareToFacebook() {
    const facebookURL = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`;
    window.open(facebookURL, '_blank');
    closeShareModal();
}

function copyToClipboard(title, price, store) {
    const text = `Check out ${title} for ₹${price} on Price Compare!\n${window.location.href}`;
    navigator.clipboard.writeText(text).then(() => {
        showNotification('✅ Link copied to clipboard!');
        closeShareModal();
    }).catch(() => {
        showNotification('❌ Failed to copy');
    });
}

function closeShareModal() {
    const modal = document.querySelector('.share-modal');
    if (modal) modal.remove();
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.querySelector('.share-modal');
    if (modal && event.target === modal) {
        modal.remove();
    }
});

// ============ ANIMATIONS ============
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
