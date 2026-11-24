import React, { useState } from "react";
import { Database, Globe, RefreshCw, Search, Sparkles } from "lucide-react";
import { BrandSummary } from "../types";
import { BrandLogo } from "./BrandLogo";

interface BrandSearchBarProps {
  currentBrand: string;
  knownBrands: BrandSummary[];
  liveMode: boolean;
  loading: boolean;
  onToggleLive: () => void;
  onSearchBrand: (brand: string) => void;
}

const FEATURED_BRANDS = ["Apple", "Samsung", "Tesla", "Zomato", "Swiggy", "Nike", "Adidas", "Tata Motors"];

export const BrandSearchBar: React.FC<BrandSearchBarProps> = ({
  currentBrand,
  knownBrands,
  liveMode,
  loading,
  onToggleLive,
  onSearchBrand,
}) => {
  const [inputVal, setInputVal] = useState(currentBrand);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = inputVal.trim();
    if (trimmed) onSearchBrand(trimmed);
  };

  // Show curated featured brands + any newly searched custom brand
  const customNames = knownBrands
    .filter((b) => !b.is_default)
    .map((b) => b.brand)
    .slice(0, 3);
  const quickChips = Array.from(new Set([...FEATURED_BRANDS, ...customNames]));

  return (
    <section className="glass-panel rounded-2xl p-4 sm:p-5">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3 lg:flex-row lg:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-cyan-400" />
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Search ANY brand (Apple, Nike, Tesla, Zomato, OpenAI, Nvidia, Nothing, Mahindra)..."
            className="w-full rounded-xl border border-slate-700/80 bg-obsidian-950/90 py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/25"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={onToggleLive}
            className={`flex items-center gap-1.5 rounded-xl border px-3.5 py-2.5 text-xs font-semibold transition ${
              liveMode
                ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20"
                : "border-amber-500/40 bg-amber-500/10 text-amber-300 hover:bg-amber-500/20"
            }`}
          >
            {liveMode ? <Globe className="h-4 w-4" /> : <Database className="h-4 w-4" />}
            {liveMode ? "Live Web + Cache" : "Instant Cache Only"}
          </button>

          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/25 transition hover:brightness-110 disabled:opacity-60"
          >
            {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            {loading ? "Analyzing..." : "Analyze Brand"}
          </button>
        </div>
      </form>

      {/* Quick-Select Brand Chips with Actual Brand Logos */}
      <div className="mt-3.5 flex flex-wrap items-center gap-2">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Quick Brands:
        </span>
        {quickChips.map((brand) => {
          const selected = brand.toLowerCase() === currentBrand.toLowerCase();
          return (
            <button
              key={brand}
              type="button"
              onClick={() => {
                setInputVal(brand);
                onSearchBrand(brand);
              }}
              className={`flex items-center gap-2 rounded-full border py-1 pl-1.5 pr-3 text-xs font-semibold transition ${
                selected
                  ? "border-cyan-400 bg-cyan-500/20 text-cyan-100 shadow-md shadow-cyan-500/15"
                  : "border-slate-700/80 bg-obsidian-900/75 text-slate-300 hover:border-slate-500 hover:text-white"
              }`}
            >
              <BrandLogo brand={brand} size="xs" />
              <span>{brand}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
};
