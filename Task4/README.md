# The Bull & The Bear

A responsive cryptocurrency tracker built with HTML, CSS, and vanilla JavaScript. It uses live CoinGecko market data, interactive Chart.js history charts, local favorites, and persistent light/dark themes.

## Features

- Live cryptocurrency prices, market cap, volume, and 24-hour changes
- Debounced cryptocurrency search by name or symbol
- Interactive price charts with 24H, 7D, 30D, 90D, 1Y, and MAX ranges
- Wishlist/favorites saved in `localStorage`
- Persistent light/dark mode
- Responsive dashboard, details, and favorites pages

## Technologies

HTML5, CSS3, vanilla JavaScript, CoinGecko API, Chart.js, and localStorage.

## API

The app uses the free CoinGecko API:

- `/global` for market-wide capitalization, volume, and change
- `/coins/markets` for the dashboard asset table
- `/search` for debounced search results
- `/coins/{id}` for detailed coin data and market statistics
- `/coins/{id}/market_chart` for historical chart points

The API is called from `js/api.js`. Responses are cached during a page session where appropriate, and HTTP 429 responses show a friendly rate-limit message.

## How to Run

This is a static site. Open `index.html` directly in a browser, or serve the folder locally for the best browser behavior:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

The free CoinGecko API can rate-limit frequent requests. Wait briefly and reload if that happens.

## How to Test

1. Search for Bitcoin, Ethereum, or Solana and open a result.
2. Add a coin from the dashboard or details page, refresh, and verify it remains in Favorites.
3. Remove a favorite and verify the empty state appears when the list is clear.
4. Toggle the theme, refresh, and verify the preference persists.
5. Open a coin and click every chart range button.
6. Resize the browser to mobile width and verify cards, navigation, search, and the chart remain usable.

## Deployment

To deploy with GitHub Pages:

1. Create a GitHub repository and push this folder to its default branch.
2. Open **Settings > Pages** in the repository.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select the default branch and the `/ (root)` folder, then save.
5. GitHub will provide the public Pages URL after deployment finishes.
