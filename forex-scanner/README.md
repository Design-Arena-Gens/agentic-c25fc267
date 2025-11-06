## Forex Scanner

A simple Forex scanner web application that fetches live exchange rates for multiple currency pairs using the free [Alpha Vantage](https://www.alphavantage.co/) API. The UI is built with Next.js and can be deployed directly to Vercel. A reusable Python module and CLI helper are included for local scripting or automation.

## Prerequisites

- Node.js 18+
- npm 9+
- Python 3.10+ (for local CLI usage)
- An Alpha Vantage API key

## Environment Variables

Create a `.env.local` file in the project root (copy `.env.example`) and set the API key:

```bash
cp .env.example .env.local
echo "ALPHA_VANTAGE_API_KEY=your_key_here" >> .env.local
```

The same environment variable is required when deploying (for example, `vercel env add ALPHA_VANTAGE_API_KEY`).

## Development

Install dependencies and run the dev server:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser. You can add or remove currency pairs on the page and fetch the latest quotes with the refresh button.

## CLI Usage

A standalone Python script is provided for quick terminal access:

```bash
export ALPHA_VANTAGE_API_KEY=your_key_here
python scripts/forex_scanner.py EUR/USD GBPJPY AUDNZD
```

The script reuses the same fetching logic as the web app and prints the latest exchange rate, bid, ask, and timestamp for each pair.

## Testing & Linting

```bash
npm run lint
```

## Deployment

Deploy with Vercel once you have configured the environment variable:

```bash
vercel deploy --prod --yes --token $VERCEL_TOKEN --name agentic-c25fc267
```

After deployment, confirm availability with:

```bash
curl https://agentic-c25fc267.vercel.app
```
