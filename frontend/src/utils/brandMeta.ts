export interface BrandVisualMeta {
  slug: string;
  domain: string;
  accent: string;
  secondary: string;
}

const KNOWN_BRAND_VISUALS: Record<string, BrandVisualMeta> = {
  apple: { slug: "apple", domain: "apple.com", accent: "#e2e8f0", secondary: "#38bdf8" },
  samsung: { slug: "samsung", domain: "samsung.com", accent: "#3b82f6", secondary: "#6366f1" },
  oneplus: { slug: "oneplus", domain: "oneplus.com", accent: "#ef4444", secondary: "#f43f5e" },
  nothing: { slug: "nothing", domain: "nothing.tech", accent: "#f8fafc", secondary: "#94a3b8" },
  xiaomi: { slug: "xiaomi", domain: "mi.com", accent: "#f97316", secondary: "#fb923c" },
  sony: { slug: "sony", domain: "sony.com", accent: "#60a5fa", secondary: "#818cf8" },
  lg: { slug: "lg", domain: "lg.com", accent: "#ec4899", secondary: "#f43f5e" },
  dell: { slug: "dell", domain: "dell.com", accent: "#0284c7", secondary: "#38bdf8" },
  hp: { slug: "hp", domain: "hp.com", accent: "#0ea5e9", secondary: "#22d3ee" },
  lenovo: { slug: "lenovo", domain: "lenovo.com", accent: "#ef4444", secondary: "#f97316" },
  asus: { slug: "asus", domain: "asus.com", accent: "#38bdf8", secondary: "#6366f1" },
  google: { slug: "google", domain: "google.com", accent: "#4285f4", secondary: "#34a853" },
  microsoft: { slug: "microsoft", domain: "microsoft.com", accent: "#00a4ef", secondary: "#7fba00" },
  openai: { slug: "openai", domain: "openai.com", accent: "#10b981", secondary: "#14b8a6" },
  anthropic: { slug: "anthropic", domain: "anthropic.com", accent: "#f59e0b", secondary: "#fb923c" },
  perplexity: { slug: "perplexity", domain: "perplexity.ai", accent: "#22d3ee", secondary: "#06b6d4" },
  meta: { slug: "meta", domain: "meta.com", accent: "#3b82f6", secondary: "#06b6d4" },
  nvidia: { slug: "nvidia", domain: "nvidia.com", accent: "#84cc16", secondary: "#22c55e" },
  amd: { slug: "amd", domain: "amd.com", accent: "#ef4444", secondary: "#f97316" },
  intel: { slug: "intel", domain: "intel.com", accent: "#0ea5e9", secondary: "#3b82f6" },
  tesla: { slug: "tesla", domain: "tesla.com", accent: "#ef4444", secondary: "#f87171" },
  byd: { slug: "byd", domain: "byd.com", accent: "#f43f5e", secondary: "#fb7185" },
  rivian: { slug: "rivian", domain: "rivian.com", accent: "#f59e0b", secondary: "#10b981" },
  "tata motors": { slug: "tata", domain: "tatamotors.com", accent: "#3b82f6", secondary: "#38bdf8" },
  tata: { slug: "tata", domain: "tatamotors.com", accent: "#3b82f6", secondary: "#38bdf8" },
  mahindra: { slug: "mahindra", domain: "mahindra.com", accent: "#ef4444", secondary: "#f97316" },
  hyundai: { slug: "hyundai", domain: "hyundai.com", accent: "#60a5fa", secondary: "#3b82f6" },
  toyota: { slug: "toyota", domain: "toyota.com", accent: "#ef4444", secondary: "#f43f5e" },
  bmw: { slug: "bmw", domain: "bmw.com", accent: "#38bdf8", secondary: "#3b82f6" },
  "mercedes-benz": { slug: "mercedes", domain: "mercedes-benz.com", accent: "#e2e8f0", secondary: "#94a3b8" },
  "ola electric": { slug: "ola", domain: "olaelectric.com", accent: "#22c55e", secondary: "#84cc16" },
  "ather energy": { slug: "ather", domain: "atherenergy.com", accent: "#10b981", secondary: "#22d3ee" },
  zomato: { slug: "zomato", domain: "zomato.com", accent: "#f43f5e", secondary: "#ef4444" },
  swiggy: { slug: "swiggy", domain: "swiggy.com", accent: "#f97316", secondary: "#fb923c" },
  zepto: { slug: "zepto", domain: "zeptonow.com", accent: "#a855f7", secondary: "#ec4899" },
  blinkit: { slug: "blinkit", domain: "blinkit.com", accent: "#eab308", secondary: "#22c55e" },
  nike: { slug: "nike", domain: "nike.com", accent: "#f8fafc", secondary: "#38bdf8" },
  adidas: { slug: "adidas", domain: "adidas.com", accent: "#38bdf8", secondary: "#818cf8" },
  puma: { slug: "puma", domain: "puma.com", accent: "#ef4444", secondary: "#f59e0b" },
  "new balance": { slug: "newbalance", domain: "newbalance.com", accent: "#f43f5e", secondary: "#e2e8f0" },
  reebok: { slug: "reebok", domain: "reebok.com", accent: "#ef4444", secondary: "#38bdf8" },
  zara: { slug: "zara", domain: "zara.com", accent: "#f8fafc", secondary: "#cbd5e1" },
  amazon: { slug: "amazon", domain: "amazon.com", accent: "#f59e0b", secondary: "#fbbf24" },
  flipkart: { slug: "flipkart", domain: "flipkart.com", accent: "#3b82f6", secondary: "#facc15" },
  myntra: { slug: "myntra", domain: "myntra.com", accent: "#ec4899", secondary: "#f97316" },
  nykaa: { slug: "nykaa", domain: "nykaa.com", accent: "#f43f5e", secondary: "#ec4899" },
  phonepe: { slug: "phonepe", domain: "phonepe.com", accent: "#8b5cf6", secondary: "#a855f7" },
  paytm: { slug: "paytm", domain: "paytm.com", accent: "#0ea5e9", secondary: "#38bdf8" },
  razorpay: { slug: "razorpay", domain: "razorpay.com", accent: "#3b82f6", secondary: "#22d3ee" },
  stripe: { slug: "stripe", domain: "stripe.com", accent: "#6366f1", secondary: "#818cf8" },
  jio: { slug: "jio", domain: "jio.com", accent: "#2563eb", secondary: "#38bdf8" },
  airtel: { slug: "airtel", domain: "airtel.in", accent: "#ef4444", secondary: "#f43f5e" },
  netflix: { slug: "netflix", domain: "netflix.com", accent: "#ef4444", secondary: "#dc2626" },
  spotify: { slug: "spotify", domain: "spotify.com", accent: "#22c55e", secondary: "#10b981" },
  starbucks: { slug: "starbucks", domain: "starbucks.com", accent: "#10b981", secondary: "#34d399" },
  "coca-cola": { slug: "cocacola", domain: "coca-colacompany.com", accent: "#ef4444", secondary: "#f43f5e" },
  pepsi: { slug: "pepsi", domain: "pepsi.com", accent: "#2563eb", secondary: "#ef4444" },
  "mcdonald's": { slug: "mcdonalds", domain: "mcdonalds.com", accent: "#facc15", secondary: "#ef4444" },
};

export function resolveBrandVisualMeta(brand: string, explicitDomain?: string): BrandVisualMeta {
  const key = brand.trim().toLowerCase();
  if (KNOWN_BRAND_VISUALS[key]) {
    return KNOWN_BRAND_VISUALS[key];
  }
  const cleanSlug = key.replace(/[^a-z0-9]/g, "") || "brand";
  return {
    slug: cleanSlug,
    domain: explicitDomain || `${cleanSlug}.com`,
    accent: "#06b6d4",
    secondary: "#6366f1",
  };
}
