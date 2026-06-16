# template_redesign.md

## Reference
See PROJECT_OVERVIEW.md for stack (Tailwind CSS + GSAP).
See AI_CONSTRAINTS.md for frontend rules.
See bug_fixes.md — apply bug fixes BEFORE this redesign.

## Purpose
Complete redesign of all HTML templates.
Design inspiration: Nike.com — minimal, bold typography, luxury feel, few elements but powerful.
Color: Beige/cream backgrounds + luxury gold accents.
No clutter. Every element earns its place.

---

## Design Philosophy
```
- Less is more. Remove everything unnecessary.
- Big, bold typography does the heavy lifting.
- Gold accent (#C9A84C) is used sparingly — only for prices, CTAs, and key highlights.
- Lots of whitespace. Let content breathe.
- No emoji in headers, titles, or UI elements. Professional only.
- No amateur icons — use clean SVG icons only (inline SVG or Heroicons style).
- Footer is minimal — no duplicate nav links. Nav links stay in navbar only.
```

---

## Design System

### Color Palette
```
Background:   #FAF7F2 (warm beige)
Surface:      #FFFFFF (white cards)
Surface2:     #F5EFE6 (slightly darker beige for sections)
Primary:      #111111 (near black — headings, body)
Accent Gold:  #C9A84C (luxury gold)
Accent Dark:  #A8872E (gold hover)
Blue:         #1D4ED8 (action blue — secondary CTAs)
Success:      #059669
Error:        #DC2626
Text:         #111111
Text Muted:   #6B7280
Border:       #E5DDD0 (warm border)
```

### Typography — Nike inspired
```
Headings: font-black, tracking-tighter, very large sizes
Hero H1: text-6xl sm:text-7xl lg:text-8xl, font-black, tracking-tighter
Section H2: text-4xl sm:text-5xl, font-black, tracking-tight
Card title: text-lg, font-bold
Body: text-base, font-normal, leading-relaxed, text-[#374151]
Price: font-black, text-[#C9A84C], text-2xl+
Labels: text-xs, font-semibold, uppercase, tracking-widest, text-[#6B7280]
```

### Component Classes (in base.html <style>)
```css
*, *::before, *::after { box-sizing: border-box; }
body { background: #FAF7F2; color: #111111; font-family: 'Inter', sans-serif; }

/* Cards */
.card { background: #FFFFFF; border: 1px solid #E5DDD0; border-radius: 12px; }
.card-hover { transition: transform 0.25s ease, box-shadow 0.25s ease; }
.card-hover:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,0.1); }

/* Buttons — Nike style: bold, no-nonsense */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.75rem 2rem; border-radius: 4px; font-weight: 700; font-size: 0.875rem; letter-spacing: 0.05em; text-transform: uppercase; transition: all 0.2s ease; cursor: pointer; border: none; text-decoration: none; }
.btn-primary { background: #111111; color: #FAF7F2; }
.btn-primary:hover { background: #000000; transform: translateY(-1px); }
.btn-gold { background: #C9A84C; color: #111111; }
.btn-gold:hover { background: #A8872E; transform: translateY(-1px); }
.btn-outline { background: transparent; color: #111111; border: 2px solid #111111; }
.btn-outline:hover { background: #111111; color: #FAF7F2; }
.btn-outline-gold { background: transparent; color: #C9A84C; border: 2px solid #C9A84C; }
.btn-outline-gold:hover { background: #C9A84C; color: #111111; }
.btn-danger { background: #DC2626; color: white; }
.btn-danger:hover { background: #B91C1C; }
.btn-sm { padding: 0.5rem 1.25rem; font-size: 0.75rem; }
.btn-lg { padding: 1rem 2.5rem; font-size: 1rem; }

/* Inputs */
.form-input { width: 100%; background: #FFFFFF; border: 1.5px solid #E5DDD0; border-radius: 4px; padding: 0.875rem 1rem; color: #111111; font-size: 0.875rem; transition: border-color 0.2s; outline: none; }
.form-input:focus { border-color: #C9A84C; }
.form-input::placeholder { color: #9CA3AF; }
.form-select { width: 100%; background: #FFFFFF; border: 1.5px solid #E5DDD0; border-radius: 4px; padding: 0.875rem 1rem; color: #111111; font-size: 0.875rem; outline: none; cursor: pointer; appearance: none; }
.form-select:focus { border-color: #C9A84C; }
.form-label { display: block; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #6B7280; margin-bottom: 0.5rem; }

/* Badges */
.badge { display: inline-flex; align-items: center; padding: 0.2rem 0.625rem; border-radius: 2px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
.badge-gold { background: #C9A84C; color: #111111; }
.badge-blue { background: #1D4ED8; color: white; }
.badge-green { background: #059669; color: white; }
.badge-red { background: #DC2626; color: white; }
.badge-gray { background: #6B7280; color: white; }
.badge-outline-gold { background: transparent; color: #C9A84C; border: 1.5px solid #C9A84C; }

/* Gold accent line */
.gold-line { width: 48px; height: 3px; background: #C9A84C; border-radius: 0; margin: 1rem 0; }

/* Section headings */
.section-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #C9A84C; margin-bottom: 0.75rem; }
.section-title { font-size: 2.5rem; font-weight: 900; color: #111111; letter-spacing: -0.04em; line-height: 1.1; }
.section-subtitle { font-size: 1rem; color: #6B7280; margin-top: 0.75rem; line-height: 1.6; }

/* Price */
.price-tag { font-size: 1.875rem; font-weight: 900; color: #C9A84C; letter-spacing: -0.03em; }

/* Hero */
.hero-dark { background: #111111; color: #FAF7F2; }

/* Divider */
.divider { border: none; border-top: 1px solid #E5DDD0; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #FAF7F2; }
::-webkit-scrollbar-thumb { background: #C9A84C; border-radius: 0; }

/* Dark mode */
[data-theme="dark"] body { background: #0F1117; color: #F1F5F9; }
[data-theme="dark"] .card { background: #1A1F2E; border-color: rgba(255,255,255,0.08); }
[data-theme="dark"] .form-input { background: #1A1F2E; border-color: rgba(255,255,255,0.1); color: #F1F5F9; }
[data-theme="dark"] .form-select { background: #1A1F2E; border-color: rgba(255,255,255,0.1); color: #F1F5F9; }
[data-theme="dark"] header { background: rgba(15,17,23,0.97) !important; border-color: rgba(255,255,255,0.06) !important; }
[data-theme="dark"] .section-title { color: #F1F5F9; }
[data-theme="dark"] .section-subtitle { color: #94A3B8; }
[data-theme="dark"] footer { background: #060912 !important; }
[data-theme="dark"] .divider { border-color: rgba(255,255,255,0.08); }
[data-theme="dark"] .btn-primary { background: #F1F5F9; color: #111111; }
[data-theme="dark"] .btn-outline { border-color: #F1F5F9; color: #F1F5F9; }
[data-theme="dark"] .btn-outline:hover { background: #F1F5F9; color: #111111; }

/* Toast */
#toast-container { position:fixed; top:1.5rem; right:1.5rem; z-index:9999; display:flex; flex-direction:column; gap:.5rem; }
.toast { display:flex; align-items:center; gap:.75rem; padding:.875rem 1.25rem; border-radius:4px; font-size:.875rem; font-weight:600; color:#fff; min-width:280px; max-width:380px; box-shadow:0 8px 24px rgba(0,0,0,0.15); animation:slideRight .3s ease-out; }
.toast-success { background: #059669; }
.toast-error { background: #DC2626; }
.toast-info { background: #1D4ED8; }
```

### Tailwind Config
```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        beige: { DEFAULT:'#FAF7F2', dark:'#F5EFE6' },
        gold: { DEFAULT:'#C9A84C', dark:'#A8872E', light:'#E8C97A' },
        ink: { DEFAULT:'#111111', light:'#374151' },
        warm: { border:'#E5DDD0' },
      },
      fontFamily: { sans: ['Inter','ui-sans-serif','system-ui'] },
      letterSpacing: { tighter: '-0.04em', tight: '-0.02em' },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-right': 'slideRight 0.3s ease-out',
      },
      keyframes: {
        fadeIn: { '0%': {opacity:'0'}, '100%': {opacity:'1'} },
        slideUp: { '0%': {opacity:'0',transform:'translateY(24px)'}, '100%': {opacity:'1',transform:'translateY(0)'} },
        slideRight: { '0%': {opacity:'0',transform:'translateX(-16px)'}, '100%': {opacity:'1',transform:'translateX(0)'} },
      }
    }
  }
}
```

---

## base.html

### Navbar — clean, minimal, professional
```
- Background: white, 1px bottom border #E5DDD0
- Height: 64px
- Logo: "BabaCars" — "Baba" in #111111 + "Cars" in #C9A84C, font-black, no emoji
- Center links: İlanlar | Satılık | Kiralık | Karşılaştır
  - text-sm, font-medium, #111111
  - Hover: gold underline (2px solid #C9A84C, transition)
- Right: notification bell (SVG) + messages (SVG) + user menu
- Unauthenticated: "Giriş Yap" btn-outline-sm + "Kayıt Ol" btn-gold-sm
- Theme toggle button: sun/moon SVG icon, no label
- Mobile: hamburger menu, full-width slide-down panel
- NO emoji anywhere in navbar
```

### Footer — minimal, no duplicate nav
```
- Background: #111111
- Max-width container, 3 columns:
  Left: Logo (BabaCars in white/gold) + one-line tagline
  Middle: empty or brand statement ("Premium Araç Platformu")
  Right: copyright only
- Top: 1px #C9A84C gold line (full width)
- Text: #9CA3AF
- NO platform/hesap link columns (those are in navbar)
- Height: compact, ~120px
```

### Theme toggle logic (JS in base.html):
```javascript
const savedTheme = localStorage.getItem('babacars-theme') ||
  '{{ request.user.theme_preference|default:"light" }}';
document.documentElement.setAttribute('data-theme', savedTheme);

function toggleTheme() {
  const curr = document.documentElement.getAttribute('data-theme');
  const next = curr === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('babacars-theme', next);
  fetch('/accounts/set-theme/', {
    method: 'POST',
    headers: {'X-CSRFToken': getCSRF(), 'Content-Type': 'application/json'},
    body: JSON.stringify({theme: next})
  }).catch(() => {});
}
```

---

## listings/index.html — Nike-style hero

### Hero Section:
```
- Full viewport height (min-h-screen), hero-dark background (#111111)
- Giant heading: "TÜRKİYE'NİN" (small label, gold) + "EN İYİ" (massive, white) + "ARAÇ PLATFORMU" (massive, white)
- Font: text-6xl md:text-8xl lg:text-9xl, font-black, tracking-tighter
- Subtext: small, muted, max-w-sm
- Search bar: white glass card below heading
  - listing_type select + make input + city input + "ARA" btn-gold
- Bottom: horizontal stats strip — X+ İlan | X+ Kullanıcı | X+ Şehir
  - Separated by thin gold vertical lines
- GSAP: heading words stagger in from bottom
```

### Featured Section (beige bg):
```
- section-label: "NEDEN BABACARS"
- 3 cards side by side: white, square, no rounded corners (Nike style)
  - Large gold number (01, 02, 03)
  - Bold title
  - Short description
  - No icons
```

### Listings Grid (white bg):
```
- section-label: "SON İLANLAR"
- Large section-title
- 4-col grid
- GSAP ScrollTrigger stagger
- Pagination: minimal, gold active number
```

---

## listings/_listing_card.html

### Card — minimal, no clutter:
```
- White card, 1px warm border, no border-radius or 4px max
- Cover photo: aspect-[4/3], object-cover, no rounded top
- Thin gold top border on hover (border-t-2 border-gold)
- Body padding: 1rem
- listing_type badge: top-left on image (gold=sale, blue=rental)
- Heart icon: top-right on image (unfilled → filled gold on favorite)
- Price: price-tag class, gold, large
- Title: font-bold, #111111, 1-line truncate
- Specs row: year · mileage km · fuel — text-xs, muted, dots as separators
- Bottom: city — text-xs, muted
- NO seller info on card (keep it clean)
- Hover: thin gold top border + very subtle shadow
```

---

## listings/detail.html

### Layout: 60/40 split desktop, stacked mobile

### Photo Gallery (left):
```
- Main photo: full-width, aspect-[4/3], no border-radius
- Thumbnail row: 5 small squares below, gold border on active
- "X / Y" counter: bottom-right of main photo, white text on dark overlay
- Fullscreen: button top-right
- GSAP crossfade between photos
```

### Info Panel (right):
```
- listing_type badge + status badge (small, square)
- Title: text-3xl, font-black, #111111
- Price: price-tag (gold, very large)
- Gold line (gold-line class)
- 3 buttons in a row:
  "TEKLİF VER" → btn-gold
  "FAVORİYE EKLE" → btn-outline
  "MESAJ GÖNDER" → btn-outline
- Specs grid: 2 columns, label above value, warm border between rows
  Marka | Model | Yıl | Kilometre | Yakıt | Vites
- "Detaylı Özellikler" — expandable, no animation needed
  Beygir | Tork | Bagaj | Tüketim | Kapı | Koltuk
- Location: city/district, muted
- Description: clean paragraph
- Seller card: minimal — name + "Doğrulanmış" badge + rating + "Profili Gör" link
```

### Offer Modal:
```
- Fixed overlay: rgba(0,0,0,0.6)
- White modal, no border-radius (square), max-w-md
- "TEKLİF GÖNDER" title + current price in gold
- Amount input (large)
- Rental dates if applicable
- Optional message
- "GÖNDER" btn-gold + "İPTAL" btn-outline
- GSAP scale-in from center
```

### Similar Listings:
```
- White bg section
- section-label: "BENZER İLANLAR"
- 4-card horizontal grid using _listing_card.html
```

### Recently Viewed:
```
- Beige bg section
- section-label: "SON BAKTIKLARINIZ"
- Horizontal scrollable row, _listing_card.html
```

---

## listings/search.html

### Layout: left sidebar (fixed width 280px) + right results

### Sidebar:
```
- White card, warm border
- "FİLTRELE" title — font-black uppercase
- Gold line below title
- Each filter section: label + input/select
- "ARA" btn-gold full-width
- "Filtreleri Temizle" — text-xs, gold, underline
```

### Results:
```
- Top bar: "X sonuç" (bold) + sort select (right-aligned)
- Active filter chips: gold bg, black text, × to remove
- 3-col grid (lg), 2 (sm), 1 (xs)
- Minimal pagination: ← 1 2 3 ... →
- Empty state: large text "SONUÇ BULUNAMADI" + suggestion
```

---

## listings/compare.html

### Design — premium comparison table:
```
- Beige background
- section-label: "ARAÇ KARŞILAŞTIRMA" (NO emoji, NO amateur icon)
- Large bold section-title: "Araçları Karşılaştır"
- White comparison card
- Column per vehicle:
  - Photo (aspect 4/3, object-cover)
  - Title bold
  - Price (gold)
  - "Kaldır" — text-xs, red, top-right
- "İlan Ekle +" column: dashed border, centered + icon
- Spec rows: alternating beige/white
  Marka | Model | Yıl | KM | Yakıt | Vites | Beygir | Tork | Bagaj | Tüketim
- Better value: green badge | worse: red badge
- "TEKLİF VER" btn-gold per column footer
```

---

## listings/create.html & edit.html

### Design — 3-step form:
```
- Step indicator: 3 circles, gold filled = active/done, gray = pending
  "İlan Bilgileri" → "Araç Özellikleri" → "Fotoğraflar"
- Each step: white card, clean inputs
- Step 1: listing_type, title, description, price, city, district
- Step 2: Araç özellikleri
  - Make/Model: TextInput (user types — no dropdown, keep simple)
  - Year: NumberInput
  - Mileage: NumberInput
  - Fuel/Transmission/Body: Select dropdowns
  - num_doors: Select (2, 3, 4, 5)
  - num_seats: Select (2, 4, 5, 6, 7, 8, 9)
  - Optional: horsepower, torque, trunk_volume, fuel_consumption
- Step 3: Photo upload
  - Drag & drop zone: dashed gold border, large
  - "En az 8 fotoğraf gereklidir" warning
  - Photo preview grid: 4-col, each with × remove button
  - Counter: "X / 8 minimum"
- "İLERİ" btn-gold + "GERİ" btn-outline navigation
- GSAP: slide transition between steps
```

---

## listings/favorites.html
```
- section-label: "FAVORİLERİM"
- section-title: "Kayıtlı İlanlar"
- 4-col grid
- Empty: large "HENÜz FAVORİ YOK" + btn-gold "İLANLARA GÖZ AT"
```

---

## accounts/login.html & register.html
```
- Left half: hero-dark (#111111)
  - Large "HOŞ GELDİN" or "HESAP OLUŞTUR" heading (white, massive)
  - Gold line
  - Tagline (small, muted)
- Right half: beige bg
  - White card, centered, max-w-sm
  - Form: clean inputs, gold focus
  - Submit: btn-gold full-width
  - Links: gold color
- GSAP: right panel slide from right
```

---

## accounts/profile.html
```
- Beige background
- Top section: dark hero strip
  - Avatar (gold border circle) + full_name + email + role badge
- Content: white card, tabbed
  - Tab 1: "Bilgilerim" — profile form (full_name, email, phone, avatar)
  - Tab 2: "Şifre Değiştir" — old/new/confirm password form
  - Tab 3: "Tercihler" — theme toggle (light/dark), dark mode switch
  - Tab 4: "İlanlarım" — listing cards
  - Tab 5: "Tekliflerim" — offer list
  - Tab 6: "Rezervasyonlarım" — booking list
- Gold underline on active tab
- Stats bar: X İlan | X Favori | X Teklif — gold numbers
```

---

## accounts/seller_profile.html
```
- Dark hero: seller name (large, white) + "Doğrulanmış Satıcı" gold badge + rating
- Gold line
- Stats row: white cards on beige bg
- Listings grid
- Reviews: star breakdown + review cards
- Fixed "MESAJ GÖNDER" btn-gold bottom-right
```

---

## accounts/become_seller.html
```
- Split: left dark panel (benefits) + right beige panel (form)
- Left: 3 benefits with gold checkmark lines
- Right: white card, form, "SATICI OL" btn-gold
```

---

## dashboard/dashboard.html
```
- Beige background
- "DASHBOARD" section-label
- Seller name heading
- 4 stat cards: white, gold number count-up (GSAP), label below
- Listings table: white card
  Columns: İlan | Görüntülenme | Favori | Teklif | Durum | İşlemler
- Clean, minimal rows, warm border separators
```

---

## dashboard/listing_stats.html
```
- "← Geri" link (gold)
- Listing summary: photo + title + price
- 2 charts: Chart.js CDN, gold color scheme
  - Bar: saatlik trafik
  - Line: günlük trafik
- Conversion rate: large gold percentage
- Recent offers: clean table
```

---

## messaging/inbox.html
```
- 2-col: conversation list (beige bg) + right placeholder (white)
- Conversation item: initials circle (gold bg) + name + listing title + time + unread gold dot
- Active: gold left border 3px
- Search: clean input at top
- Empty: "HENÜz MESAJINIZ YOK"
```

---

## messaging/conversation.html
```
- Left: conversation list (narrow)
- Right: full chat
- Header: white, warm border-bottom, other user + listing name
- Sender (you): gold bg bubble, right-aligned, square corners
- Receiver: white card, warm border, left-aligned
- Deleted: italic, muted
- Input: white bar, "GÖNDER" btn-gold
- GSAP: new message fade-in
```

---

## notifications/notifications.html
```
- "BİLDİRİMLER" section-label
- "Tümünü Okundu İşaretle" btn-outline-gold right-aligned
- Notification row: type icon (SVG) + title bold + body muted + time
- Unread: warm left border 3px gold
- Empty state
```

---

## offers/my_offers.html
```
- Tabs: "GÖNDERİLEN" | "ALINAN"
- Gold underline active tab
- Offer card: white, listing thumbnail + title + amount (gold) + status badge + actions
- Chain: indented, gold connecting line
```

---

## offers/listing_offers.html
```
- Listing summary card top
- Offer rows: white card per offer
- Buyer + amount (gold) + status + "KABUL ET" (green) / "REDDET" (red) / "KARŞI TEKLİF" (gold)
- Confirmation: simple modal before accept/reject
```

---

## bookings/my_bookings.html
```
- Booking cards: white, listing thumb + title + dates + price (gold) + status
- Status: thin colored left border
- "İPTAL ET" btn-danger for cancellable
```

---

## bookings/booking_detail.html
```
- Listing photo (large, full-width top)
- Booking card: dates + price breakdown + status
- Price breakdown: daily × days = subtotal → indirim → TOPLAM (gold, large)
- Contact card: seller/renter minimal info
- "İPTAL ET" btn-danger + confirmation modal
```

---

## notifications/verify_email pages
```
- Centered card on beige bg
- Clean message, gold accent
- CTA button
```

---

## New Features

### Similar Listings — listings/selectors.py add:
```python
def get_similar_listings(*, listing, limit: int = 4) -> QuerySet:
    return Listing.objects.filter(
        status='active',
        vehicle__make__iexact=listing.vehicle.make,
    ).exclude(id=listing.id).select_related('vehicle').prefetch_related('photos')[:limit]
```

### Recently Viewed — listings/views.py update listing_detail_view:
```python
# Add after fetching listing:
recently_viewed = request.session.get('recently_viewed', [])
if listing.id not in recently_viewed:
    recently_viewed.insert(0, listing.id)
    recently_viewed = recently_viewed[:6]
    request.session['recently_viewed'] = recently_viewed

similar_listings = selectors.get_similar_listings(listing=listing)
recent_listings = []
for lid in recently_viewed:
    if lid != listing.id:
        try:
            recent_listings.append(selectors.get_listing_by_id(listing_id=lid))
        except Exception:
            pass

# Add to render context:
# 'similar_listings': similar_listings,
# 'recent_listings': recent_listings[:5],
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py runserver
```
Manually verify:
- Beige/cream background on all pages
- Gold accent on prices, active states, primary CTAs
- NO emoji in headers or titles
- Navbar: white bg, gold hover underline, no footer nav duplication
- Footer: minimal, dark, single line
- Cards: white with warm border
- Similar listings appear on detail page
- Recently viewed updates on each visit
- Dark mode toggle works
- Mobile responsive on all pages
- GSAP animations work
Expected: 0 errors, all pages render without 500 errors.
Report any errors before proceeding.

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- bug_fixes.md (apply first)
- listings_models.md
- listings_views.md
- selectors.md

### Task
Redesign all HTML templates with Warm Luxury Minimal theme and add new features.
Apply bug_fixes.md BEFORE starting this redesign.

### Design Rules
1. Beige/cream background (#FAF7F2) on all pages.
2. Gold (#C9A84C) only for prices, primary CTAs, active states. Use sparingly.
3. Near-black (#111111) for all headings and body text.
4. NO emoji in any heading, title, badge, or UI element.
5. NO footer nav links — nav links stay in navbar only.
6. Footer is minimal: logo + tagline + copyright only.
7. Buttons: square corners (border-radius: 4px), uppercase labels, bold.
8. Inputs: square corners (border-radius: 4px), gold focus border.
9. Nike-style hero: massive bold typography, dark bg, gold accents.
10. All component classes defined in base.html <style> block.

### Files to Modify
- templates/base.html
- templates/listings/index.html
- templates/listings/_listing_card.html
- templates/listings/detail.html
- templates/listings/search.html
- templates/listings/compare.html
- templates/listings/create.html
- templates/listings/edit.html
- templates/listings/favorites.html
- templates/accounts/login.html
- templates/accounts/register.html
- templates/accounts/profile.html
- templates/accounts/seller_profile.html
- templates/accounts/become_seller.html
- templates/accounts/verify_email_notice.html
- templates/accounts/verify_email_failed.html
- templates/dashboard/dashboard.html
- templates/dashboard/listing_stats.html
- templates/messaging/inbox.html
- templates/messaging/conversation.html
- templates/notifications/notifications.html
- templates/offers/my_offers.html
- templates/offers/listing_offers.html
- templates/bookings/my_bookings.html
- templates/bookings/booking_detail.html

### Files to Modify (Python)
- listings/selectors.py → add get_similar_listings
- listings/views.py → update listing_detail_view

### Implementation Order
1. base.html (run server and verify before continuing)
2. listings/index.html
3. listings/_listing_card.html
4. listings/detail.html
5. Remaining pages

### Rules
1. ALL templates extend base.html, use {% block content %}.
2. ALL forms keep existing action/method/name/csrf_token.
3. ALL AJAX endpoints unchanged — restyle JS only.
4. Mobile-first responsive on every template.
5. Chart.js CDN only on dashboard pages.
6. Do NOT change URL names or view logic beyond specified additions.
7. Run healthcheck after base.html before continuing.

### Output
One code block per file. Start with base.html. No explanations.
