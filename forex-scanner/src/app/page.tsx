'use client';

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import styles from "./page.module.css";

type Quote = {
  pair: string;
  exchange_rate: number;
  bid_price: number | null;
  ask_price: number | null;
  last_refreshed: string;
  timezone: string;
  from_currency: string;
  to_currency: string;
};

type ApiResponse = {
  data?: Quote[];
  errors?: string[];
  error?: string;
};

const DEFAULT_PAIRS = ["EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF", "AUD/USD"];

export default function Home() {
  const [pairs, setPairs] = useState<string[]>(DEFAULT_PAIRS);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [customPair, setCustomPair] = useState<string>("");

  const queryString = useMemo(() => {
    if (!pairs.length) return "";
    const params = pairs.map((pair) => `pairs=${encodeURIComponent(pair)}`).join("&");
    return params;
  }, [pairs]);

  const fetchQuotes = useCallback(async () => {
    if (!pairs.length) {
      setQuotes([]);
      setErrors([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/api/forex?${queryString}`, {
        cache: "no-store",
      });
      const payload = (await response.json()) as ApiResponse;
      if (!response.ok) {
        const message = typeof payload.error === "string" ? payload.error : "Request failed.";
        setErrors([message]);
        setQuotes([]);
        setLastUpdated(null);
        return;
      }

      setQuotes(payload.data ?? []);
      setErrors(payload.errors ?? []);
      setLastUpdated(new Date().toLocaleString());
    } catch {
      setErrors(["Unable to fetch exchange rates."]);
      setQuotes([]);
      setLastUpdated(null);
    } finally {
      setIsLoading(false);
    }
  }, [pairs.length, queryString]);

  useEffect(() => {
    fetchQuotes();
  }, [fetchQuotes]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = customPair.trim();
    if (!trimmed) return;
    const normalized = trimmed.toUpperCase();
    setPairs((prev) => (prev.includes(normalized) ? prev : [...prev, normalized]));
    setCustomPair("");
  };

  const handleRemove = (pair: string) => {
    setPairs((prev) => prev.filter((item) => item !== pair));
  };

  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <div>
          <h1>Forex Scanner</h1>
          <p>Track real-time exchange rates for your favorite currency pairs using the free Alpha Vantage API.</p>
        </div>
        <button className={styles.refreshButton} onClick={fetchQuotes} disabled={isLoading || !pairs.length}>
          {isLoading ? "Refreshing..." : "Refresh Rates"}
        </button>
      </section>

      <section className={styles.card}>
        <h2>Watched Pairs</h2>
        <form className={styles.pairForm} onSubmit={handleSubmit}>
          <input
            aria-label="Add currency pair"
            placeholder="e.g. CAD/JPY or NZDUSD"
            value={customPair}
            onChange={(event) => setCustomPair(event.target.value)}
            className={styles.textInput}
          />
          <button type="submit" className={styles.addButton}>
            Add Pair
          </button>
        </form>
        {pairs.length === 0 ? (
          <p className={styles.empty}>No pairs selected. Add a pair to begin.</p>
        ) : (
          <ul className={styles.pairList}>
            {pairs.map((pair) => (
              <li key={pair} className={styles.pairItem}>
                <span>{pair}</span>
                <button onClick={() => handleRemove(pair)} className={styles.removeButton} aria-label={`Remove ${pair}`}>
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className={styles.card}>
        <div className={styles.tableHeader}>
          <h2>Live Exchange Rates</h2>
          {lastUpdated && <span className={styles.timestamp}>Last updated: {lastUpdated}</span>}
        </div>
        {errors.length > 0 && (
          <div className={styles.errorPanel}>
            {errors.map((message) => (
              <p key={message}>{message}</p>
            ))}
          </div>
        )}
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead className={styles.tableHead}>
              <tr>
                <th className={styles.tableHeaderCell}>Pair</th>
                <th className={styles.tableHeaderCell}>Exchange Rate</th>
                <th className={styles.tableHeaderCell}>Bid</th>
                <th className={styles.tableHeaderCell}>Ask</th>
                <th className={styles.tableHeaderCell}>Last Refreshed</th>
              </tr>
            </thead>
            <tbody>
              {quotes.length === 0 ? (
                <tr className={styles.tableRow}>
                  <td colSpan={5} className={`${styles.tableCell} ${styles.empty}`}>
                    {isLoading ? "Loading exchange rates..." : "No data available. Try refreshing."}
                  </td>
                </tr>
              ) : (
                quotes.map((quote) => (
                  <tr key={quote.pair} className={styles.tableRow}>
                    <td className={styles.tableCell}>
                      <span className={styles.pairLabel}>{quote.pair}</span>
                      <span className={styles.subtle}>
                        {quote.from_currency} → {quote.to_currency}
                      </span>
                    </td>
                    <td className={styles.tableCell}>{quote.exchange_rate.toFixed(6)}</td>
                    <td className={styles.tableCell}>{quote.bid_price != null ? quote.bid_price.toFixed(6) : "N/A"}</td>
                    <td className={styles.tableCell}>{quote.ask_price != null ? quote.ask_price.toFixed(6) : "N/A"}</td>
                    <td className={styles.tableCell}>
                      <span>{quote.last_refreshed}</span>
                      <span className={styles.subtle}>{quote.timezone}</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
