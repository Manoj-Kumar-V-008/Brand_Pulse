import hashlib
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

from app.analytics.competitors import resolve_brand_competitors

DB_PATH = Path(__file__).resolve().parent.parent / "brandpulse.db"

DEFAULT_BRAND_CATEGORIES: Dict[str, str] = {
    "Apple": "Consumer Tech & Smartphones",
    "Samsung": "Consumer Tech & Smartphones",
    "OnePlus": "Consumer Tech & Smartphones",
    "Google": "Big Tech & AI",
    "Tesla": "Electric Vehicles & Automotive",
    "BYD": "Electric Vehicles & Automotive",
    "Rivian": "Electric Vehicles & Automotive",
    "Tata Motors": "Electric Vehicles & Automotive",
    "Zomato": "Food Delivery & Quick Commerce",
    "Swiggy": "Food Delivery & Quick Commerce",
    "Zepto": "Quick Commerce & Delivery",
    "Nike": "Sportswear & Footwear",
    "Adidas": "Sportswear & Footwear",
    "Puma": "Sportswear & Footwear",
    "New Balance": "Sportswear & Footwear",
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mentions (
            id TEXT PRIMARY KEY,
            brand TEXT NOT NULL,
            brand_key TEXT NOT NULL,
            source TEXT NOT NULL,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            url TEXT NOT NULL,
            published_at TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            is_seeded INTEGER DEFAULT 0
        )
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_mentions_brand_key
        ON mentions(brand_key, published_at DESC)
        """
    )
    conn.commit()
    conn.close()
    seed_default_brands_if_missing()


def _make_id(brand: str, source: str, title: str, text: str) -> str:
    raw = f"{brand.lower()}|{source.lower()}|{title[:80]}|{text[:120]}"
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _build_seed_records() -> List[Tuple]:
    now = datetime.now(timezone.utc)
    seeded_corpus: Dict[str, List[Tuple[str, str, str, str, int]]] = {
        "Apple": [
            ("Google News", "TechCrunch", "Apple M4 MacBook battery life tops independent laptop benchmarks", "Independent lab tests confirm Apple's M4 MacBook delivers 21 hours of active battery life with zero thermal throttling, impressing developers and creators.", 0),
            ("Bluesky", "@dev_arjun.bsky.social", "Switched to iPhone 16 Pro camera", "Honestly blown away by the camera stabilization and crisp video quality on the new iPhone. Seamless ecosystem handoff with my Mac! 🔥", 0),
            ("Hacker News", "hn_silicon", "Apple Silicon unified memory remains unmatched for local LLMs", "Running quantized 8B models smoothly on Apple Silicon with low power draw is a massive win for AI developers.", 1),
            ("Bluesky", "@priya_ux.bsky.social", "Apple repair pricing is ridiculous", "Cracked the back glass and Apple quoted an absurd repair price without AppleCare. Great hardware, terrible pricing policy.", 1),
            ("Google News", "Reuters", "Apple faces fresh EU antitrust scrutiny over App Store fees", "European regulators warn Apple over developer fee structures and third-party marketplace restrictions, raising regulatory PR concerns.", 2),
            ("Bluesky", "@kiran_tech.bsky.social", "iOS update fixed my battery drain", "After the latest iOS patch my phone stays cool all day and animations feel super smooth again. Glad they pushed a fast fix.", 2),
            ("Hacker News", "ml_builder", "Safari WebGL quirks still frustrate frontend engineers", "Apple's hardware is top notch, though Safari still lags behind Chrome on several WebGPU and WebGL developer APIs.", 3),
            ("Google News", "The Verge", "Apple Intelligence rollout draws mixed reactions from early adopters", "Users praise notification summaries and privacy-first architecture, while critics say Siri upgrades still feel incomplete.", 3),
            ("Bluesky", "@meera_designs.bsky.social", "AirPods Pro hearing health feature is genuinely awesome", "Used the AirPods Pro hearing test and adaptive audio on a noisy Bengaluru flight—crystal clear sound and comfort.", 4),
            ("Google News", "Bloomberg", "Apple expands India manufacturing footprint with record exports", "Apple's India supply chain crossed a major export milestone this quarter as local retail stores see steady footfall.", 4),
            ("Bluesky", "@rahul_codes.bsky.social", "Apple customer support resolved my warranty replacement fast", "Walked into the Apple Store with a faulty USB-C port and walked out with a hassle-free replacement in 30 minutes. Top service!", 5),
            ("Hacker News", "sys_ops", "Storage upgrade tiers on MacBooks feel overpriced", "Charging $200 for an extra 256GB SSD in 2026 is hard to defend even when the build quality is excellent.", 5),
            ("Google News", "CNBC", "Apple announces quarterly revenue beat led by Services", "Strong growth in Apple Services and steady iPhone demand pushed quarterly earnings above analyst consensus.", 6),
            ("Bluesky", "@ananya_v.bsky.social", "Neutral take on the new iPad refresh", "The new iPad is a solid incremental update. Nothing revolutionary if you already own last year's model, just reliable.", 6),
        ],
        "Samsung": [
            ("Google News", "GSMArena", "Samsung Galaxy S25 Ultra anti-reflective display praised in lab tests", "Reviewers highlight Samsung's anti-glare OLED panel and seven years of Android security updates as industry leading.", 0),
            ("Bluesky", "@vikram_m.bsky.social", "Galaxy AI live translate saved me on a business trip", "Used Samsung's real-time call translation and note summary all week—super useful and surprisingly accurate! 👏", 0),
            ("Bluesky", "@neha_g.bsky.social", "Green line display issue after software update is unacceptable", "Updated my 2-year-old Galaxy phone and a bright green vertical line appeared. Service center asked for a huge screen replacement fee!", 1),
            ("Hacker News", "chip_watch", "Samsung Foundry yields under pressure compared to TSMC", "Industry reports cite thermal efficiency gaps on flagship Exynos chips, prompting debate among hardware enthusiasts.", 1),
            ("Google News", "The Verge", "Samsung Galaxy Ring and Watch ecosystem deepens health tracking", "Seamless sleep apnea alerts and long battery life earn positive feedback from fitness-focused buyers.", 2),
            ("Bluesky", "@aditya_p.bsky.social", "Samsung One UI customization is pure joy", "Good Lock modules and DeX desktop mode make my Samsung phone feel like a mini workstation. Love the flexibility.", 2),
            ("Bluesky", "@pooja_home.bsky.social", "Samsung washing machine warranty claim delayed twice", "Customer support kept rescheduling the technician visit for 10 days. Great appliances until you actually need after-sales support.", 3),
            ("Google News", "Economic Times", "Samsung launches new mid-range 5G lineup across India", "Competitive pricing and local festive offers aim to strengthen Samsung's mid-tier smartphone market share.", 3),
            ("Hacker News", "ssd_guru", "Samsung 990 Pro NVMe SSD runs fast and cool after firmware patch", "After updating firmware via Magician, read/write consistency and endurance metrics are rock solid.", 4),
            ("Bluesky", "@sam_mobile.bsky.social", "Too much preinstalled bloatware on budget Galaxy phones", "Setup wizard pushed five sponsored apps I never asked for. Please clean up the out-of-box software experience.", 4),
            ("Google News", "CNET", "Samsung OLED TVs win top ratings for gaming latency and brightness", "Low input lag and vibrant HDR contrast put Samsung's latest OLED series near the top of 2026 buying guides.", 5),
            ("Bluesky", "@karthik_b.bsky.social", "Neutral thoughts on Galaxy Buds 3", "Audio quality is crisp and ANC is decent, though the stem design feels a bit derivative of competitors.", 5),
            ("Google News", "Reuters", "Samsung memory chip profits rebound on surging AI server HBM demand", "Strong orders for high-bandwidth memory lifted semiconductor earnings despite softer consumer electronics growth.", 6),
            ("Bluesky", "@divya_cam.bsky.social", "Zoom camera on the Ultra is unreal at concerts", "Captured crisp 10x stage photos from the back row without blur. Worth every rupee for photography lovers!", 6),
        ],
        "OnePlus": [
            ("Google News", "GSMArena", "OnePlus 13 silicon-carbon battery breaks 2-day endurance records", "Lab tests confirm OnePlus delivers fast 100W charging and cool thermal performance under heavy gaming loads.", 0),
            ("Bluesky", "@rohan_android.bsky.social", "OxygenOS animations feel buttery smooth again", "Switched back to OnePlus this year and the UI speed, alert slider, and fast charger in the box are unbeatable! 🔥", 1),
            ("Bluesky", "@sid_mobile.bsky.social", "OnePlus lifetime green-line screen warranty builds real trust", "Glad OnePlus stepped up with free display replacement policies across Indian service centers.", 2),
            ("Google News", "Economic Times", "OnePlus expands offline retail partnerships across Tier-2 Indian cities", "New flagship experience stores aim to rebuild brand affinity against Samsung and Apple.", 3),
            ("Bluesky", "@anita_cam.bsky.social", "Low-light video still trails flagship rivals slightly", "Photos look sharp in daylight, though night video stabilization feels average compared to pricier competitors.", 4),
            ("Hacker News", "mobile_dev", "OnePlus bootloader unlock policy remains developer friendly", "Custom ROM enthusiasts continue praising OnePlus hardware value for testing Android builds.", 5),
            ("Bluesky", "@tarun_k.bsky.social", "Standard mid-range experience on OnePlus Nord", "Solid everyday phone with good battery life, though a couple of preloaded apps needed uninstalling.", 6),
        ],
        "Google": [
            ("Google News", "The Verge", "Google Pixel 10 Tensor chip boosts on-device AI speed significantly", "Reviewers highlight crisp computational photography and clean Android software updates.", 0),
            ("Bluesky", "@dev_meera.bsky.social", "Gemini coding workflows and Google Cloud tools saved hours this sprint", "Super clean integrations and fast inference latency across our student project.", 1),
            ("Google News", "Reuters", "Google faces ongoing antitrust remedies hearings over search distribution", "Regulators continue evaluating marketplace competition rules across browser and mobile ecosystems.", 2),
            ("Bluesky", "@arjun_pix.bsky.social", "Pixel call screening and spam protection is genuinely awesome", "Zero robocalls getting through this month—easily my favorite everyday smartphone feature.", 3),
            ("Bluesky", "@neel_tech.bsky.social", "Pixel service center turnaround in India took two weeks", "Great camera hardware, but spare part wait times at authorized repair centers need improvement.", 4),
            ("Hacker News", "cloud_arch", "Google Cloud Run cold starts and pricing remain competitive for startups", "Deploying containerized FastAPI microservices stays fast and predictable.", 5),
            ("Bluesky", "@kiran_web.bsky.social", "Routine Chrome and Workspace updates this week", "Performance feels steady across desktop and mobile with standard security patches.", 6),
        ],
        "Tesla": [
            ("Google News", "Reuters", "Tesla recalls over 200,000 vehicles for software camera glitch", "Safety regulators confirmed Tesla is issuing an over-the-air recall patch after rearview camera lag affected visibility.", 0),
            ("Bluesky", "@ev_rohan.bsky.social", "Tesla Supercharger network is still unbeatable on road trips", "Drove 650 km over the weekend and every Supercharger worked seamlessly on plug-in. Zero range anxiety!", 0),
            ("Bluesky", "@sarah_drives.bsky.social", "Service center wait times are getting frustrating", "Had a minor suspension rattle and the earliest Tesla service appointment was 3 weeks away. Customer support needs major scaling.", 1),
            ("Hacker News", "autonomy_dev", "Tesla FSD v13 shows impressive urban smoothness, still needs supervision", "Disengagements dropped sharply on city intersections, though sudden phantom braking in heavy rain remains a safety concern.", 1),
            ("Google News", "Bloomberg", "Tesla Cybertruck panel alignment and delivery delays spark customer complaints", "Early reservation holders report uneven trim gaps and sudden delivery rescheduling, fueling negative social chatter.", 2),
            ("Bluesky", "@nikhil_ev.bsky.social", "Model 3 Highland cabin quietness is a huge upgrade", "Test drove the refreshed Model 3—the acoustic glass, ventilated seats, and responsive UI feel genuinely premium.", 2),
            ("Google News", "Financial Times", "Tesla faces intensifying EV price war and shrinking margins", "Aggressive discounts from rival EV makers put pressure on Tesla's automotive gross margins this quarter.", 3),
            ("Bluesky", "@chris_auto.bsky.social", "Insurance cost and repair wait after fender bender was painful", "Love driving my Model Y, but waiting 5 weeks for a replacement bumper and high repair bill really hurt the ownership experience.", 3),
            ("Hacker News", "energy_grid", "Tesla Megapack energy storage division hits record deployment", "While car headlines dominate PR, Tesla's utility-scale Megapack business is growing rapidly with strong reliability.", 4),
            ("Bluesky", "@maya_green.bsky.social", "Controversial executive tweets hurting brand perception", "Several friends cancelled their EV shortlist purely due to ongoing PR controversy surrounding leadership.", 4),
            ("Google News", "Electrek", "Tesla rolls out Autopilot safety update and winter battery preconditioning", "The latest software update improves cold-weather charging speed by 14% across Model 3 and Model Y fleets.", 5),
            ("Bluesky", "@dan_commute.bsky.social", "Standard commute update on Model Y", "One year with the Model Y: low charging cost, decent software, average interior plastics. Overall balanced daily car.", 5),
            ("Google News", "CNBC", "Analysts debate Tesla robotaxi timeline amid regulatory hurdles", "Investors remain divided on whether autonomous fleet approvals can meet Tesla's ambitious launch schedule.", 6),
            ("Bluesky", "@leo_tech.bsky.social", "Phantom wiper activation still annoys me", "Auto-wipers turned on during a sunny afternoon again. Please fix basic sensor reliability before flashy features!", 6),
        ],
        "BYD": [
            ("Google News", "Reuters", "BYD global EV deliveries surge on strong Blade Battery safety ratings", "Reviewers highlight BYD's affordable pricing and vertical battery manufacturing efficiency.", 0),
            ("Bluesky", "@ev_sanjay.bsky.social", "Test drove the BYD Seal in Bengaluru—cabin quality is genuinely impressive", "Smooth acceleration, comfortable suspension, and solid real-world range for Indian highways! 🚀", 1),
            ("Google News", "Bloomberg", "BYD faces European and US tariff hurdles amid rapid international expansion", "Trade duties are testing BYD's export pricing strategy across Western markets.", 2),
            ("Bluesky", "@auto_claire.bsky.social", "Infotainment software UX feels slightly cluttered compared to rivals", "Hardware and range are awesome, though the rotating touchscreen menus could use cleaner design polish.", 3),
            ("Google News", "Financial Times", "BYD launches ultra-fast charging platform targeting 5-minute range top-ups", "Battery innovation strengthens BYD's competitive lead in mainstream electric sedans.", 4),
            ("Bluesky", "@mark_ev.bsky.social", "Dealer service network still growing outside major metros", "Parts availability took a week longer than expected, otherwise smooth ownership.", 5),
            ("Google News", "CNBC", "BYD expands dealership footprint across Asia-Pacific and Latin America", "Steady monthly sales reinforce BYD's position as a top global EV volume leader.", 6),
        ],
        "Rivian": [
            ("Google News", "The Verge", "Rivian R2 pre-orders remain strong as buyers look for adventure EVs", "Enthusiasts praise thoughtful interior design, rugged capability, and clean software UX.", 0),
            ("Bluesky", "@trail_ev.bsky.social", "Rivian R1S handled a weekend mountain trip effortlessly", "Quiet cabin, awesome storage space, and smooth OTA software updates! 🔥", 1),
            ("Google News", "Reuters", "Rivian works to trim manufacturing costs and narrow quarterly losses", "Investors closely watch factory ramp efficiency and gross margin targets.", 2),
            ("Bluesky", "@alex_r1t.bsky.social", "Service center backlog made a minor trim fix take 3 weeks", "Love driving the truck, but Rivian really needs more service locations.", 3),
            ("Hacker News", "auto_sw", "Rivian's zonal electrical architecture cuts wiring weight significantly", "Clean software-defined vehicle engineering praised by automotive systems engineers.", 4),
            ("Bluesky", "@nina_ev.bsky.social", "Decent highway range on the dual-motor Rivian", "Charging curve is predictable and driver assistance works steadily on interstates.", 5),
        ],
        "Tata Motors": [
            ("Google News", "Economic Times", "Tata Motors EV lineup leads India market share with 5-star safety ratings", "Strong Bharat NCAP scores on Nexon EV and Punch EV boost family buyer confidence.", 0),
            ("Bluesky", "@karthik_ev.bsky.social", "Tata Punch EV city commute cost is unbelievably low", "Smooth drive through Bengaluru traffic with awesome regenerative braking and great value!", 1),
            ("Bluesky", "@vijay_drives.bsky.social", "Tata service center quality still feels inconsistent", "Love the build safety of my car, but waiting twice for a minor software glitch fix was frustrating.", 2),
            ("Google News", "Mint", "Tata Motors expands public EV fast-charging partnerships across highways", "New charging corridors aim to reduce range anxiety for intercity Indian travelers.", 3),
            ("Bluesky", "@deepa_auto.bsky.social", "Infotainment screen occasionally lags on cold startup", "Hardware feels tough and comfortable, just hoping the next OTA update smooths out UI responsiveness.", 4),
            ("Google News", "Reuters", "Tata Motors reports steady commercial and passenger vehicle dispatches", "Balanced quarterly volumes supported by festive SUV demand.", 5),
        ],
        "Zomato": [
            ("Google News", "Mint", "Zomato expands 15-minute quick food delivery across major Indian metros", "Customers praise rapid delivery speeds in Bengaluru and Mumbai, while analysts monitor unit economics.", 0),
            ("Bluesky", "@rohit_blr.bsky.social", "Zomato platform fee keeps creeping up every month", "Order total was ₹240, then packaging, GST, rain surge, and platform fee pushed it to ₹355. Pricing feels deceptive now!", 0),
            ("Bluesky", "@sneha_foodie.bsky.social", "Cold spilled biryani and AI chatbot refused a proper refund", "My order arrived 50 minutes late and leaking everywhere. Zomato customer support bot just gave a ₹30 coupon instead of a refund. Terrible experience!", 1),
            ("Google News", "Economic Times", "Zomato Blinkit quick-commerce arm posts strong quarterly growth", "Blinkit dark stores continue to gain urban market share, boosting Zomato's consolidated revenue outlook.", 1),
            ("Bluesky", "@varun_eats.bsky.social", "Zomato Gold free delivery saved me a lot this semester", "Ordering group dinners with Zomato Gold has been super reliable and the live map tracking is spot on.", 2),
            ("Google News", "Inc42", "Restaurant partners raise concerns over Zomato commission and ad spend", "Several independent cafes report rising visibility costs on the Zomato app, sparking industry debate.", 2),
            ("Bluesky", "@tanya_k.bsky.social", "Delivery partner was polite and arrived ahead of time in heavy rain", "Big shoutout to the Zomato rider who delivered hot food safely despite Bengaluru traffic—tipped extra!", 3),
            ("Hacker News", "ind_startup", "Zomato's live order telemetry and logistics routing is impressive engineering", "Handling peak IPL dinner surges with sub-second ETA updates shows mature backend scalability.", 3),
            ("Bluesky", "@aman_dev.bsky.social", "Wrong item delivered and impossible to reach a human agent", "Spent 20 minutes looping inside the automated support chat. Please bring back real customer support for missing items!", 4),
            ("Google News", "Business Standard", "Zomato launches healthier meal filters and transparent calorie tags", "Health-conscious users welcome verified nutrition labels across partner kitchens.", 4),
            ("Bluesky", "@ishita_m.bsky.social", "District app dining discounts worked smoothly", "Paid our restaurant bill via Zomato dining and got an instant 20% discount with zero friction.", 5),
            ("Bluesky", "@deepak_n.bsky.social", "Average experience ordering lunch today", "Food arrived on time and tasted fine, though menu prices are noticeably higher than dine-in rates.", 5),
            ("Google News", "Reuters", "Zomato shares rally on profitability milestone and quick-commerce scale", "Investors reacted positively to expanding margins across dining-out and instant grocery verticals.", 6),
            ("Bluesky", "@kavi_s.bsky.social", "Love Zomato's witty notifications, hate hidden surge fees", "Marketing is hilarious, UX is sleek, just wish checkout pricing stayed transparent.", 6),
        ],
        "Swiggy": [
            ("Google News", "Economic Times", "Swiggy Instamart adds 10-minute electronics and pharmacy essentials", "Shoppers appreciate fast late-night delivery of chargers, medicines, and groceries across Tier-1 cities.", 0),
            ("Bluesky", "@harsha_blr.bsky.social", "Swiggy Bolt delivered hot dosas in 11 minutes flat!", "Ordered breakfast before college and it reached piping hot in 11 minutes. Insanely smooth experience! 🚀", 0),
            ("Bluesky", "@nisha_r.bsky.social", "Swiggy One renewal hiked fees while shrinking free delivery radius", "Feels frustrating paying for membership when most nearby restaurants now trigger distance surcharges.", 1),
            ("Google News", "Mint", "Swiggy expands Bolt quick-food service to 400+ Indian towns", "Expansion beyond metro hubs aims to capture high-frequency snack and beverage orders.", 1),
            ("Bluesky", "@aravind_v.bsky.social", "Instamart sent stale veggies and refund took three chats", "Convenience is great, but fresh produce quality checks at dark stores really need improvement.", 2),
            ("Hacker News", "ops_eng", "Swiggy's demand forecasting ML models cut dark-store stockouts", "Interesting engineering blog on how Swiggy uses spatiotemporal forecasting for hyperlocal inventory.", 2),
            ("Bluesky", "@kavya_food.bsky.social", "Swiggy Dineout offers made our team outing super affordable", "Booked a table for 8 and saved ₹1,400 seamlessly through Swiggy Dineout. Super clean UI.", 3),
            ("Google News", "Business Today", "Gig worker unions protest Swiggy payout structure during monsoon peak", "Delivery partners cite rising fuel costs and tight delivery timers, drawing social media scrutiny.", 3),
            ("Bluesky", "@siddharth_k.bsky.social", "Support agent refunded missing dessert within 2 minutes", "Pleasantly surprised—uploaded a photo of the bill and Swiggy credited the refund immediately.", 4),
            ("Bluesky", "@megha_t.bsky.social", "App feels a bit cluttered with too many banners", "Just wanted to reorder my usual meal, had to dismiss three promo popups first. UX could be cleaner.", 4),
            ("Google News", "Inc42", "Swiggy narrows quarterly losses as Instamart average order value rises", "Larger grocery baskets and ad monetization helped improve operational efficiency.", 5),
            ("Bluesky", "@pranav_j.bsky.social", "Standard late-night snack order on Swiggy", "Arrived in 35 minutes, packaging was intact, fees were slightly steep. Nothing unusual.", 5),
            ("Google News", "Reuters", "Swiggy partners with regional restaurant chains for exclusive combos", "New value meals target budget-conscious college students and young professionals.", 6),
            ("Bluesky", "@rhea_d.bsky.social", "Instamart saved my house party at 11 PM", "Got ice, snacks, and plates delivered in 9 minutes. Easily my most used app in Bengaluru.", 6),
        ],
        "Zepto": [
            ("Google News", "Inc42", "Zepto Cafe scales 10-minute coffee and snacks across Indian metros", "High repeat order frequency boosts Zepto's quick-commerce momentum.", 0),
            ("Bluesky", "@aditi_blr.bsky.social", "Zepto delivered fresh groceries and iced coffee in 8 minutes flat!", "Super clean app and reliable live rider tracking during morning rush! 🚀", 1),
            ("Bluesky", "@manoj_shop.bsky.social", "Handling fee and rain surge on Zepto feel confusing at checkout", "Free cash banner looked great until extra checkout surcharges wiped out the discount.", 2),
            ("Google News", "Mint", "Zepto intensifies dark-store competition with Blinkit and Swiggy Instamart", "Analysts track customer retention and basket size economics across quick-commerce rivals.", 3),
            ("Bluesky", "@rahul_qc.bsky.social", "Instant refund for crushed bread loaf worked smoothly", "Uploaded a quick photo and Zepto credited my wallet in under a minute.", 4),
            ("Bluesky", "@pooja_k.bsky.social", "Standard grocery restock via Zepto today", "Arrived in 12 minutes, items matched the list, pricing slightly above local supermarket.", 5),
        ],
        "Nike": [
            ("Google News", "CNBC", "Nike Pegasus 41 running shoes receive rave reviews for cushioning", "Marathon runners praise the responsive ReactX foam and durable outsole grip during long training blocks.", 0),
            ("Bluesky", "@run_akash.bsky.social", "Clocked a new 10K PB in my Nike Vaporflys!", "Unbelievable energy return and featherlight fit. Nike still owns race-day running tech! 🏃‍♂️🔥", 0),
            ("Bluesky", "@sneaker_raj.bsky.social", "SNKRS app crashed again during limited drop—bots took everything", "Woke up early for the drop, app froze at payment, and pairs were on resale sites within 2 minutes. Fix your bot protection!", 1),
            ("Google News", "Bloomberg", "Nike faces stiff competition from Adidas and New Balance in running", "Analysts note shifting consumer preference toward rival athletic brands as Nike resets its product pipeline.", 1),
            ("Bluesky", "@elena_fit.bsky.social", "Sole started peeling after just 3 months of gym wear", "Paid ₹12,000 for Nike trainers and the glue gave up way too early. Quality control has noticeably slipped.", 2),
            ("Google News", "Reuters", "Nike unveils recycled knit sustainability collection ahead of marathon season", "New apparel line cuts manufacturing carbon footprint by 30% while keeping breathable comfort.", 2),
            ("Bluesky", "@omar_kicks.bsky.social", "Nike customer service honored my defective shoe return smoothly", "Filed a warranty claim online and received full store credit within 4 days. Solid post-purchase support.", 3),
            ("Bluesky", "@zoya_style.bsky.social", "Classic Air Force 1 never misses", "Clean, comfortable, pairs with literally every outfit. Timeless design.", 3),
            ("Google News", "Financial Times", "Nike overhauls wholesale retail partnerships to win back store shelf space", "Leadership emphasizes renewed innovation and stronger partnerships with multi-brand athletic retailers.", 4),
            ("Bluesky", "@dev_hoops.bsky.social", "Basketball shoe traction is great, pricing is getting wild", "Great ankle lock and court feel, though ₹16,000+ for regular colorways feels steep for students.", 4),
            ("Hacker News", "design_ops", "Nike's 3D custom shoe configurator runs remarkably fast in browser", "Nike By You demonstrates clean WebGL asset streaming without lag on mobile devices.", 5),
            ("Bluesky", "@nina_run.bsky.social", "Decent everyday hoodie from Nike", "Fabric is soft and fits true to size. Standard athletic wear, nothing groundbreaking.", 5),
            ("Google News", "Wall Street Journal", "Nike invests heavily in athlete-led storytelling campaigns", "Brand marketing refocuses on grassroots running clubs and global sporting events to rebuild hype.", 6),
            ("Bluesky", "@taran_s.bsky.social", "Shipping delay on custom Nike By You order", "Order has been stuck in customs clearance for 10 days with vague tracking updates.", 6),
        ],
        "Adidas": [
            ("Google News", "Reuters", "Adidas sales surge as Samba, Gazelle and Adizero running shoes dominate demand", "Strong lifestyle sneaker momentum and marathon podium wins lift Adidas revenue forecasts.", 0),
            ("Bluesky", "@marathon_neha.bsky.social", "Adidas Adios Pro 4 cushioning feels unreal at tempo pace!", "Super light, grippy Continental outsole, and zero heel slip during my half-marathon! 🔥", 1),
            ("Bluesky", "@kicks_varun.bsky.social", "Adidas Ultraboost durability still beats most daily trainers", "Logged 600 km in these shoes and the midsole bounce still feels fresh and supportive.", 2),
            ("Google News", "Bloomberg", "Adidas expands India retail footprint with cricket and running collections", "Team India jersey drops and local running clubs strengthen brand loyalty across metros.", 3),
            ("Bluesky", "@rohit_sneaks.bsky.social", "Adidas Confirmed app checkout glitched during hyped release", "Payment failed twice and size sold out—frustrating drop experience.", 4),
            ("Bluesky", "@maya_fit.bsky.social", "Returned a tight pair to Adidas online and refund took 9 days", "Great shoe quality, though return pickup and refund speed could be faster.", 5),
            ("Google News", "CNBC", "Adidas raises full-year margin guidance on disciplined inventory control", "Analysts praise balanced wholesale partnerships and steady full-price sell-through.", 6),
        ],
        "Puma": [
            ("Google News", "Economic Times", "Puma strengthens India sportswear leadership with Nitro running lineup", "Affordable performance trainers and IPL athlete campaigns drive strong youth adoption.", 0),
            ("Bluesky", "@runner_sid.bsky.social", "Puma Velocity Nitro 3 is easily the best value running shoe right now!", "Incredible grip on wet Bengaluru roads and half the price of flagship rivals! 👏", 1),
            ("Bluesky", "@tanya_style.bsky.social", "Puma Palermo sneakers look super clean and comfortable", "Great colorway options and soft insole right out of the box.", 2),
            ("Google News", "Reuters", "Puma navigates softer wholesale demand in Europe while investing in running tech", "Brand refocuses marketing spend on performance footwear and motorsport collaborations.", 3),
            ("Bluesky", "@akash_gear.bsky.social", "Puma online order exchange took over a week", "Shoes fit slightly narrow and customer support took two follow-ups to schedule pickup.", 4),
            ("Bluesky", "@liam_gym.bsky.social", "Solid everyday training tee from Puma", "Breathable fabric, standard fit, reasonable pricing during seasonal sales.", 5),
        ],
        "New Balance": [
            ("Google News", "Bloomberg", "New Balance posts double-digit growth driven by 1080v14 and retro lifestyle hits", "Consumers praise all-day arch comfort and consistent sizing across running and casual lines.", 0),
            ("Bluesky", "@walk_priya.bsky.social", "New Balance 990v6 is the most comfortable sneaker I have ever owned!", "Walked 18,000 steps all day with zero foot fatigue—worth every rupee! 🔥", 1),
            ("Bluesky", "@sneaker_sam.bsky.social", "Premium Made in USA New Balance pricing feels steep", "Build quality is top tier, though ₹22,000+ makes it hard to justify for daily wear.", 2),
            ("Google News", "CNBC", "New Balance expands performance running footprint against Nike and Adidas", "Strong specialty run-store partnerships sustain high organic word-of-mouth advocacy.", 3),
            ("Bluesky", "@dev_fit.bsky.social", "Limited stock availability for wide-fit models in India", "Great shoes when in stock, wish local stores carried more sizes.", 4),
        ],
    }

    rows = []
    fetched_iso = now.isoformat()
    for brand, items in seeded_corpus.items():
        bkey = brand.strip().lower()
        for idx, (source, author, title, text, days_ago) in enumerate(items):
            pub = (now - timedelta(days=days_ago, hours=(idx * 3) % 20)).isoformat()
            mid = _make_id(brand, source, title, text)
            url = f"https://news.google.com/search?q={brand.replace(' ', '+')}"
            if source == "Bluesky":
                url = f"https://bsky.app/search?q={brand.replace(' ', '+')}"
            elif source == "Hacker News":
                url = f"https://hn.algolia.com/?q={brand.replace(' ', '+')}"
            rows.append((mid, brand, bkey, source, author, title, text, url, pub, fetched_iso, 1))
    return rows


def seed_default_brands_if_missing() -> None:
    """Ensures all default brands & true industry competitors are seeded even on existing DBs."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT brand_key FROM mentions WHERE is_seeded = 1")
    existing_keys = {r["brand_key"] for r in cur.fetchall()}

    rows = _build_seed_records()
    missing_rows = [r for r in rows if r[2] not in existing_keys]
    if missing_rows:
        cur.executemany(
            """
            INSERT OR IGNORE INTO mentions
            (id, brand, brand_key, source, author, title, text, url, published_at, fetched_at, is_seeded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            missing_rows,
        )
        conn.commit()
    conn.close()


def save_mentions(brand: str, mentions: List[Dict], is_seeded: int = 0) -> int:
    if not mentions:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    bkey = brand.strip().lower()
    now_iso = datetime.now(timezone.utc).isoformat()
    inserted = 0
    for m in mentions:
        mid = m.get("id") or _make_id(brand, m.get("source", "Web"), m.get("title", ""), m.get("text", ""))
        cur.execute(
            """
            INSERT OR REPLACE INTO mentions
            (id, brand, brand_key, source, author, title, text, url, published_at, fetched_at, is_seeded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mid,
                brand.strip(),
                bkey,
                m.get("source", "Web"),
                m.get("author", "Community"),
                m.get("title", "")[:240],
                m.get("text", "")[:1200],
                m.get("url", ""),
                m.get("published_at", now_iso),
                now_iso,
                is_seeded,
            ),
        )
        inserted += 1
    conn.commit()
    conn.close()
    return inserted


def get_cached_mentions(brand: str, limit: int = 80) -> List[Dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, brand, source, author, title, text, url, published_at, fetched_at, is_seeded
        FROM mentions
        WHERE brand_key = ?
        ORDER BY published_at DESC
        LIMIT ?
        """,
        (brand.strip().lower(), limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def list_known_brands() -> List[Dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT brand, brand_key, COUNT(*) as cached_mentions, MAX(fetched_at) as last_updated,
               MAX(is_seeded) as has_seed
        FROM mentions
        GROUP BY brand_key
        ORDER BY has_seed DESC, cached_mentions DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    results = []
    for r in rows:
        display_name = r["brand"]
        category = DEFAULT_BRAND_CATEGORIES.get(display_name, "Custom Tracked Brand")
        results.append(
            {
                "brand": display_name,
                "category": category,
                "is_default": display_name in DEFAULT_BRAND_CATEGORIES,
                "cached_mentions": r["cached_mentions"],
                "last_updated": r["last_updated"] or datetime.now(timezone.utc).isoformat(),
            }
        )
    return results


def get_default_competitors(brand: str) -> List[str]:
    _, comps = resolve_brand_competitors(brand)
    return comps
