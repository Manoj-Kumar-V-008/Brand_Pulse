import re
from typing import Dict, List, Tuple

# Curated Industry + Competitor + Visual Metadata Registry (60+ Global & Indian Brands)
BRAND_REGISTRY: Dict[str, Dict] = {
    # Smartphones & Consumer Tech
    "apple": {"display": "Apple", "industry": "Consumer Tech & Smartphones", "competitors": ["Samsung", "Google", "OnePlus"], "domain": "apple.com", "accent": "#e2e8f0"},
    "samsung": {"display": "Samsung", "industry": "Consumer Tech & Smartphones", "competitors": ["Apple", "OnePlus", "Xiaomi"], "domain": "samsung.com", "accent": "#3b82f6"},
    "oneplus": {"display": "OnePlus", "industry": "Consumer Tech & Smartphones", "competitors": ["Samsung", "Apple", "Nothing"], "domain": "oneplus.com", "accent": "#ef4444"},
    "nothing": {"display": "Nothing", "industry": "Consumer Tech & Smartphones", "competitors": ["OnePlus", "Apple", "Samsung"], "domain": "nothing.tech", "accent": "#f8fafc"},
    "xiaomi": {"display": "Xiaomi", "industry": "Consumer Tech & Smartphones", "competitors": ["Samsung", "OnePlus", "Realme"], "domain": "mi.com", "accent": "#f97316"},
    "realme": {"display": "Realme", "industry": "Consumer Tech & Smartphones", "competitors": ["Xiaomi", "Samsung", "OnePlus"], "domain": "realme.com", "accent": "#eab308"},
    "sony": {"display": "Sony", "industry": "Consumer Electronics", "competitors": ["Samsung", "LG", "Nintendo"], "domain": "sony.com", "accent": "#60a5fa"},
    "lg": {"display": "LG", "industry": "Consumer Electronics", "competitors": ["Samsung", "Sony", "Whirlpool"], "domain": "lg.com", "accent": "#ec4899"},
    "dell": {"display": "Dell", "industry": "PC & Computing", "competitors": ["HP", "Lenovo", "Apple"], "domain": "dell.com", "accent": "#0284c7"},
    "hp": {"display": "HP", "industry": "PC & Computing", "competitors": ["Dell", "Lenovo", "Asus"], "domain": "hp.com", "accent": "#0ea5e9"},
    "lenovo": {"display": "Lenovo", "industry": "PC & Computing", "competitors": ["Dell", "HP", "Asus"], "domain": "lenovo.com", "accent": "#ef4444"},
    "asus": {"display": "Asus", "industry": "PC & Computing", "competitors": ["Lenovo", "Dell", "HP"], "domain": "asus.com", "accent": "#38bdf8"},

    # AI, Cloud & Big Tech
    "google": {"display": "Google", "industry": "Big Tech & AI", "competitors": ["Microsoft", "OpenAI", "Apple"], "domain": "google.com", "accent": "#4285f4"},
    "microsoft": {"display": "Microsoft", "industry": "Big Tech & AI", "competitors": ["Google", "Apple", "Amazon"], "domain": "microsoft.com", "accent": "#00a4ef"},
    "openai": {"display": "OpenAI", "industry": "Generative AI", "competitors": ["Anthropic", "Google", "Perplexity"], "domain": "openai.com", "accent": "#10b981"},
    "anthropic": {"display": "Anthropic", "industry": "Generative AI", "competitors": ["OpenAI", "Google", "Mistral"], "domain": "anthropic.com", "accent": "#f59e0b"},
    "perplexity": {"display": "Perplexity", "industry": "Generative AI", "competitors": ["OpenAI", "Google", "Anthropic"], "domain": "perplexity.ai", "accent": "#22d3ee"},
    "meta": {"display": "Meta", "industry": "Social Media & AI", "competitors": ["Google", "TikTok", "Snap"], "domain": "meta.com", "accent": "#3b82f6"},
    "nvidia": {"display": "Nvidia", "industry": "Semiconductors & AI Hardware", "competitors": ["AMD", "Intel", "Qualcomm"], "domain": "nvidia.com", "accent": "#84cc16"},
    "amd": {"display": "AMD", "industry": "Semiconductors & AI Hardware", "competitors": ["Nvidia", "Intel", "Qualcomm"], "domain": "amd.com", "accent": "#ef4444"},
    "intel": {"display": "Intel", "industry": "Semiconductors & AI Hardware", "competitors": ["AMD", "Nvidia", "Qualcomm"], "domain": "intel.com", "accent": "#0ea5e9"},

    # Automotive & Electric Vehicles
    "tesla": {"display": "Tesla", "industry": "Electric Vehicles & Automotive", "competitors": ["BYD", "Rivian", "Tata Motors"], "domain": "tesla.com", "accent": "#ef4444"},
    "byd": {"display": "BYD", "industry": "Electric Vehicles & Automotive", "competitors": ["Tesla", "Tata Motors", "Hyundai"], "domain": "byd.com", "accent": "#f43f5e"},
    "rivian": {"display": "Rivian", "industry": "Electric Vehicles & Automotive", "competitors": ["Tesla", "BYD", "Ford"], "domain": "rivian.com", "accent": "#f59e0b"},
    "tata motors": {"display": "Tata Motors", "industry": "Electric Vehicles & Automotive", "competitors": ["Mahindra", "Maruti Suzuki", "Hyundai"], "domain": "tatamotors.com", "accent": "#3b82f6"},
    "mahindra": {"display": "Mahindra", "industry": "Electric Vehicles & Automotive", "competitors": ["Tata Motors", "Maruti Suzuki", "Hyundai"], "domain": "mahindra.com", "accent": "#ef4444"},
    "maruti suzuki": {"display": "Maruti Suzuki", "industry": "Automotive", "competitors": ["Hyundai", "Tata Motors", "Mahindra"], "domain": "marutisuzuki.com", "accent": "#2563eb"},
    "hyundai": {"display": "Hyundai", "industry": "Automotive", "competitors": ["Tata Motors", "Maruti Suzuki", "Kia"], "domain": "hyundai.com", "accent": "#60a5fa"},
    "toyota": {"display": "Toyota", "industry": "Automotive", "competitors": ["Honda", "Hyundai", "Tesla"], "domain": "toyota.com", "accent": "#ef4444"},
    "bmw": {"display": "BMW", "industry": "Luxury Automotive", "competitors": ["Mercedes-Benz", "Audi", "Porsche"], "domain": "bmw.com", "accent": "#38bdf8"},
    "mercedes-benz": {"display": "Mercedes-Benz", "industry": "Luxury Automotive", "competitors": ["BMW", "Audi", "Porsche"], "domain": "mercedes-benz.com", "accent": "#cbd5e1"},
    "ola electric": {"display": "Ola Electric", "industry": "Electric Two-Wheelers", "competitors": ["Ather Energy", "TVS Motor", "Bajaj Auto"], "domain": "olaelectric.com", "accent": "#22c55e"},
    "ather energy": {"display": "Ather Energy", "industry": "Electric Two-Wheelers", "competitors": ["Ola Electric", "TVS Motor", "Bajaj Auto"], "domain": "atherenergy.com", "accent": "#10b981"},

    # Food Delivery & Quick Commerce
    "zomato": {"display": "Zomato", "industry": "Food Delivery & Quick Commerce", "competitors": ["Swiggy", "Zepto"], "domain": "zomato.com", "accent": "#f43f5e"},
    "swiggy": {"display": "Swiggy", "industry": "Food Delivery & Quick Commerce", "competitors": ["Zomato", "Zepto"], "domain": "swiggy.com", "accent": "#f97316"},
    "zepto": {"display": "Zepto", "industry": "Quick Commerce & Delivery", "competitors": ["Blinkit", "Swiggy", "Zomato"], "domain": "zeptonow.com", "accent": "#a855f7"},
    "blinkit": {"display": "Blinkit", "industry": "Quick Commerce & Delivery", "competitors": ["Zepto", "Swiggy", "BigBasket"], "domain": "blinkit.com", "accent": "#eab308"},
    "uber eats": {"display": "Uber Eats", "industry": "Food Delivery", "competitors": ["DoorDash", "Grubhub", "Zomato"], "domain": "ubereats.com", "accent": "#10b981"},
    "doordash": {"display": "DoorDash", "industry": "Food Delivery", "competitors": ["Uber Eats", "Grubhub"], "domain": "doordash.com", "accent": "#ef4444"},

    # Sportswear & Apparel
    "nike": {"display": "Nike", "industry": "Sportswear & Footwear", "competitors": ["Adidas", "Puma", "New Balance"], "domain": "nike.com", "accent": "#f8fafc"},
    "adidas": {"display": "Adidas", "industry": "Sportswear & Footwear", "competitors": ["Nike", "Puma", "New Balance"], "domain": "adidas.com", "accent": "#38bdf8"},
    "puma": {"display": "Puma", "industry": "Sportswear & Footwear", "competitors": ["Nike", "Adidas", "Reebok"], "domain": "puma.com", "accent": "#ef4444"},
    "new balance": {"display": "New Balance", "industry": "Sportswear & Footwear", "competitors": ["Nike", "Adidas", "Asics"], "domain": "newbalance.com", "accent": "#f43f5e"},
    "reebok": {"display": "Reebok", "industry": "Sportswear & Footwear", "competitors": ["Nike", "Adidas", "Puma"], "domain": "reebok.com", "accent": "#ef4444"},
    "zara": {"display": "Zara", "industry": "Fashion & Apparel", "competitors": ["H&M", "Uniqlo", "Mango"], "domain": "zara.com", "accent": "#e2e8f0"},
    "h&m": {"display": "H&M", "industry": "Fashion & Apparel", "competitors": ["Zara", "Uniqlo", "Myntra"], "domain": "hm.com", "accent": "#ef4444"},

    # E-Commerce & Retail
    "amazon": {"display": "Amazon", "industry": "E-Commerce & Cloud", "competitors": ["Flipkart", "Walmart", "Shopify"], "domain": "amazon.com", "accent": "#f59e0b"},
    "flipkart": {"display": "Flipkart", "industry": "E-Commerce & Retail", "competitors": ["Amazon", "Myntra", "Meesho"], "domain": "flipkart.com", "accent": "#3b82f6"},
    "myntra": {"display": "Myntra", "industry": "Fashion E-Commerce", "competitors": ["Ajio", "Nykaa", "Flipkart"], "domain": "myntra.com", "accent": "#ec4899"},
    "nykaa": {"display": "Nykaa", "industry": "Beauty & Lifestyle Retail", "competitors": ["Sephora", "Myntra", "Purplle"], "domain": "nykaa.com", "accent": "#f43f5e"},

    # Fintech & Payments
    "phonepe": {"display": "PhonePe", "industry": "Fintech & UPI Payments", "competitors": ["Paytm", "Google Pay", "CRED"], "domain": "phonepe.com", "accent": "#8b5cf6"},
    "paytm": {"display": "Paytm", "industry": "Fintech & UPI Payments", "competitors": ["PhonePe", "Google Pay", "Razorpay"], "domain": "paytm.com", "accent": "#0ea5e9"},
    "razorpay": {"display": "Razorpay", "industry": "Fintech & Payment Infrastructure", "competitors": ["Stripe", "Paytm", "Cashfree"], "domain": "razorpay.com", "accent": "#3b82f6"},
    "stripe": {"display": "Stripe", "industry": "Fintech & Payment Infrastructure", "competitors": ["Razorpay", "PayPal", "Adyen"], "domain": "stripe.com", "accent": "#6366f1"},

    # Telecom, Airlines, Streaming & QSR
    "jio": {"display": "Jio", "industry": "Telecom & Digital Services", "competitors": ["Airtel", "Vi"], "domain": "jio.com", "accent": "#2563eb"},
    "airtel": {"display": "Airtel", "industry": "Telecom & Digital Services", "competitors": ["Jio", "Vi"], "domain": "airtel.in", "accent": "#ef4444"},
    "indigo": {"display": "IndiGo", "industry": "Aviation & Airlines", "competitors": ["Air India", "Akasa Air"], "domain": "goindigo.in", "accent": "#3b82f6"},
    "air india": {"display": "Air India", "industry": "Aviation & Airlines", "competitors": ["IndiGo", "Emirates"], "domain": "airindia.com", "accent": "#ef4444"},
    "netflix": {"display": "Netflix", "industry": "Streaming & Entertainment", "competitors": ["Disney+", "Prime Video", "Spotify"], "domain": "netflix.com", "accent": "#ef4444"},
    "spotify": {"display": "Spotify", "industry": "Audio Streaming", "competitors": ["Apple Music", "YouTube Music"], "domain": "spotify.com", "accent": "#22c55e"},
    "starbucks": {"display": "Starbucks", "industry": "Coffee & QSR", "competitors": ["Costa Coffee", "Blue Tokai", "Dunkin"], "domain": "starbucks.com", "accent": "#10b981"},
    "coca-cola": {"display": "Coca-Cola", "industry": "Beverages & FMCG", "competitors": ["Pepsi", "Red Bull"], "domain": "coca-colacompany.com", "accent": "#ef4444"},
    "pepsi": {"display": "Pepsi", "industry": "Beverages & FMCG", "competitors": ["Coca-Cola", "Red Bull"], "domain": "pepsi.com", "accent": "#2563eb"},
    "mcdonald's": {"display": "McDonald's", "industry": "Quick Service Restaurants", "competitors": ["Burger King", "KFC", "Domino's"], "domain": "mcdonalds.com", "accent": "#facc15"},
}

# Semantic keyword detectors for unknown custom brands so they NEVER get unrelated competitors
_SECTOR_SIGNALS: List[Tuple[str, List[str], List[str]]] = [
    ("Electric Vehicles & Automotive", ["car", "ev", "vehicle", "suv", "motor", "scooter", "bike", "charging", "driving", "mileage", "engine", "autopilot"], ["Tesla", "BYD", "Tata Motors"]),
    ("Sportswear & Footwear", ["shoe", "shoes", "sneaker", "running", "marathon", "apparel", "jersey", "hoodie", "sportswear", "athletic", "sole", "footwear"], ["Nike", "Adidas", "Puma"]),
    ("Food Delivery & Quick Commerce", ["food", "delivery", "biryani", "restaurant", "grocery", "groceries", "order", "rider", "instamart", "blinkit", "meal", "cafe"], ["Zomato", "Swiggy", "Zepto"]),
    ("Generative AI & Software", ["llm", "gpt", "model", "ai", "agent", "chatbot", "api", "cloud", "developer", "code", "saas", "prompt"], ["OpenAI", "Google", "Anthropic"]),
    ("Fintech & Payments", ["upi", "payment", "bank", "wallet", "credit", "card", "checkout", "fintech", "loan", "merchant", "transaction"], ["PhonePe", "Paytm", "Razorpay"]),
    ("E-Commerce & Retail", ["shopping", "ecommerce", "seller", "marketplace", "cart", "parcel", "discount", "fashion", "beauty", "retail"], ["Amazon", "Flipkart", "Myntra"]),
    ("Streaming & Media", ["stream", "movie", "series", "music", "podcast", "subscription", "episode", "playlist", "ott"], ["Netflix", "Spotify", "Disney+"]),
    ("Consumer Tech & Smartphones", ["phone", "smartphone", "laptop", "camera", "display", "oled", "chip", "processor", "earbuds", "smartwatch", "ios", "android"], ["Apple", "Samsung", "OnePlus"]),
]


def get_brand_meta(brand: str) -> Dict:
    key = brand.strip().lower()
    if key in BRAND_REGISTRY:
        return BRAND_REGISTRY[key]
    # Partial alias match (e.g. "Nothing Phone" -> "nothing", "Tata" -> "tata motors")
    for reg_key, info in BRAND_REGISTRY.items():
        if reg_key in key or key in reg_key:
            return {**info, "display": brand.strip()}
    slug = re.sub(r"[^a-z0-9]", "", key) or "brand"
    return {
        "display": brand.strip(),
        "industry": "General Consumer Brand",
        "competitors": [],
        "domain": f"{slug}.com",
        "accent": "#06b6d4",
    }


def resolve_brand_competitors(brand: str, mentions: List[Dict] | None = None) -> Tuple[str, List[str]]:
    """
    Resolves accurate, same-industry competitors for Share of Voice (SoV):
      1. Exact or alias lookup in the 60+ brand industry registry.
      2. If unknown brand, infers the industry from the fetched mentions corpus.
      3. Guarantees the target brand itself is never duplicated in its competitor list.
    """
    key = brand.strip().lower()
    if key in BRAND_REGISTRY:
        entry = BRAND_REGISTRY[key]
        comps = [c for c in entry["competitors"] if c.lower() != key]
        return entry["industry"], comps[:3]

    # Alias match (e.g. "iPhone" -> Apple, "Nike Running" -> Nike)
    alias_map = {
        "iphone": "apple",
        "macbook": "apple",
        "galaxy": "samsung",
        "blinkit": "blinkit",
        "instamart": "swiggy",
        "chatgpt": "openai",
        "claude": "anthropic",
        "gemini": "google",
        "youtube": "google",
        "aws": "amazon",
        "playstation": "sony",
        "xbox": "microsoft",
        "tata": "tata motors",
        "ola": "ola electric",
        "ather": "ather energy",
    }
    for alias, target in alias_map.items():
        if alias in key and target in BRAND_REGISTRY:
            entry = BRAND_REGISTRY[target]
            comps = [c for c in entry["competitors"] if c.lower() != key]
            return entry["industry"], comps[:3]

    for reg_key, entry in BRAND_REGISTRY.items():
        if len(reg_key) >= 4 and reg_key in key:
            comps = [c for c in entry["competitors"] if c.lower() != key]
            return entry["industry"], comps[:3]

    # Infer industry dynamically from mentions text
    if mentions:
        corpus = " ".join(
            f"{m.get('title', '')} {m.get('clean_text', m.get('text', ''))}"
            for m in mentions[:30]
        ).lower()
        best_sector = None
        best_hits = 0
        best_peers: List[str] = []
        for sector_name, signals, peers in _SECTOR_SIGNALS:
            hits = sum(corpus.count(sig) for sig in signals)
            if hits > best_hits:
                best_hits = hits
                best_sector = sector_name
                best_peers = peers
        if best_sector and best_hits >= 2:
            comps = [p for p in best_peers if p.lower() != key]
            return best_sector, comps[:3]

    # Clean fallback: Consumer Tech peers if completely unclassifiable
    return "General Market Benchmark", [c for c in ["Apple", "Google", "Amazon"] if c.lower() != key][:2]
