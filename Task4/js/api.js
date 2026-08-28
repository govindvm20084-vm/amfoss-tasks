const API_BASE = 'https://api.coingecko.com/api/v3';
const API_HEADERS = { accept: 'application/json' };
const apiCache = new Map();

async function fetchApi(path, options = {}) {
  const cacheKey = path;
  if (!options.skipCache && apiCache.has(cacheKey)) return apiCache.get(cacheKey);
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { headers: API_HEADERS });
  } catch {
    throw new Error('Unable to reach market data right now. Please check your connection and try again.');
  }
  if (response.status === 429) throw new Error('The market is busy right now. Please try again in a moment.');
  if (!response.ok) throw new Error(`Market data unavailable (${response.status}).`);
  const data = await response.json();
  if (!options.skipCache) apiCache.set(cacheKey, data);
  return data;
}

async function getMarketData() { return fetchApi('/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=24h'); }
async function getGlobalData() { return fetchApi('/global'); }
async function getTrending() { return fetchApi('/search/trending'); }
async function searchCoins(query) { return fetchApi(`/search?query=${encodeURIComponent(query)}`, { skipCache: true }); }
async function getCoin(id) { return fetchApi(`/coins/${encodeURIComponent(id)}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false`); }
async function getCoinChart(id, days) { return fetchApi(`/coins/${encodeURIComponent(id)}/market_chart?vs_currency=usd&days=${days}&interval=${days === '1' ? 'hourly' : 'daily'}`, { skipCache: true }); }

function formatCurrency(value, compact = false) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '--';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: compact ? 'compact' : 'standard', maximumFractionDigits: value < 1 ? 6 : 2 }).format(value);
}
function formatCompact(value) { return formatCurrency(value, true); }
function formatPercent(value) { return `${Number(value) >= 0 ? '+' : ''}${Number(value || 0).toFixed(2)}%`; }
function formatNumber(value) { return new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 2 }).format(value || 0); }
function getFavorites() { try { return JSON.parse(localStorage.getItem('bullBearFavorites') || '[]'); } catch { return []; } }
function setFavorites(favorites) { localStorage.setItem('bullBearFavorites', JSON.stringify(favorites)); updateFavoriteCount(); }
function isFavorite(id) { return getFavorites().some(coin => coin.id === id); }
function toggleFavorite(coin) { const favorites = getFavorites(); const index = favorites.findIndex(item => item.id === coin.id); if (index >= 0) { favorites.splice(index, 1); } else { favorites.push({ id: coin.id, name: coin.name, symbol: coin.symbol, image: coin.image, current_price: coin.current_price, price_change_percentage_24h: coin.price_change_percentage_24h }); } setFavorites(favorites); return index < 0; }
function updateFavoriteCount() { document.querySelectorAll('.favorites-count').forEach(element => { element.textContent = getFavorites().length; }); }
function applyTheme() { const theme = localStorage.getItem('bullBearTheme') || 'light'; document.documentElement.dataset.theme = theme; document.querySelectorAll('.theme-toggle').forEach(button => { button.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'); }); }
function setupTheme() { applyTheme(); document.querySelectorAll('.theme-toggle').forEach(button => button.addEventListener('click', () => { const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; localStorage.setItem('bullBearTheme', next); applyTheme(); document.dispatchEvent(new CustomEvent('themechange')); })); }
function showToast(message) { const toast = document.getElementById('toast'); if (!toast) return; toast.textContent = message; toast.classList.add('show'); window.clearTimeout(window.toastTimer); window.toastTimer = window.setTimeout(() => toast.classList.remove('show'), 2600); }
function setupSearch() { const input = document.getElementById('global-search'); const results = document.getElementById('search-results'); if (!input || !results) return; let timer; input.addEventListener('input', () => { clearTimeout(timer); const query = input.value.trim(); if (query.length < 2) { results.hidden = true; return; } results.hidden = false; results.innerHTML = '<div class="search-empty">Searching the market...</div>'; timer = setTimeout(async () => { try { const data = await searchCoins(query); const coins = (data.coins || []).slice(0, 6); results.innerHTML = coins.length ? coins.map(coin => `<a class="search-result" role="option" href="coin.html?id=${encodeURIComponent(coin.id)}"><img src="${coin.thumb || ''}" alt=""><span>${coin.name}<small>${coin.symbol || ''}</small></span></a>`).join('') : '<div class="search-empty">No results found</div>'; } catch (error) { results.innerHTML = `<div class="search-empty">${error.message}</div>`; } }, 350); }); document.addEventListener('click', event => { if (!event.target.closest('.search-wrap')) results.hidden = true; }); input.addEventListener('keydown', event => { if (event.key === 'Escape') { input.value = ''; results.hidden = true; input.blur(); } }); }
function setupGlobalUI() { setupTheme(); setupSearch(); updateFavoriteCount(); document.querySelectorAll('.menu-toggle').forEach(button => button.addEventListener('click', () => { const isOpen = button.getAttribute('aria-expanded') === 'true'; button.setAttribute('aria-expanded', String(!isOpen)); })); }
document.addEventListener('DOMContentLoaded', setupGlobalUI);
