"""
Türkçe doğal dil sorgularını araç arama filtrelerine çeviren parser.
Harici API kullanmaz — tamamen kural tabanlı (regex + kelime listeleri).
"""
from __future__ import annotations
import re


# ── Bilinen markalar ──────────────────────────────────────────────────────────
KNOWN_MAKES = [
    'BMW', 'Mercedes', 'Audi', 'Volkswagen', 'VW', 'Toyota', 'Honda', 'Ford',
    'Renault', 'Peugeot', 'Citroën', 'Citroen', 'Fiat', 'Opel', 'Hyundai',
    'Kia', 'Nissan', 'Mazda', 'Volvo', 'Porsche', 'Ferrari', 'Lamborghini',
    'Jeep', 'Land Rover', 'Range Rover', 'Tesla', 'Skoda', 'Seat', 'Dacia',
    'Alfa Romeo', 'Maserati', 'Subaru', 'Suzuki', 'Mitsubishi', 'Lexus',
    'Infiniti', 'Jaguar', 'Chevrolet', 'Cadillac', 'Chrysler', 'Dodge',
    'Mini', 'Smart', 'Bentley', 'Rolls Royce', 'Aston Martin',
]

# ── Yakıt türü eşleştirmeleri ─────────────────────────────────────────────────
FUEL_MAP = {
    r'dizel|diesel': 'diesel',
    r'benzin|gasoline|petrol': 'gasoline',
    r'elektrik|elektrikli|electric|ev\b': 'electric',
    r'hibrit|hybrid': 'hybrid',
    r'\blpg\b': 'lpg',
}

# ── Vites türü ────────────────────────────────────────────────────────────────
TRANSMISSION_MAP = {
    r'otomatik|automatic|otomobil': 'automatic',
    r'manuel|manual|düz vites': 'manual',
}

# ── Kasa tipi ─────────────────────────────────────────────────────────────────
BODY_MAP = {
    r'\bsedan\b': 'sedan',
    r'\bhatchback\b|\bhb\b': 'hatchback',
    r'\bsuv\b|\b4x4\b|\bjeep\b': 'suv',
    r'\bcoupe\b|\bkupe\b': 'coupe',
    r'\bkabrio\b|\bconvertible\b|\bcabriolet\b': 'convertible',
    r'\bstation\b|\bwagon\b|\bkombi\b': 'wagon',
    r'\bvan\b|\bminivan\b': 'van',
    r'\bpickup\b|\bpick.?up\b': 'pickup',
}

# ── Türkçe sayı kelimeleri ────────────────────────────────────────────────────
NUMBER_WORDS = {
    'bir': 1, 'iki': 2, 'üç': 3, 'dört': 4, 'beş': 5,
    'altı': 6, 'yedi': 7, 'sekiz': 8, 'dokuz': 9, 'on': 10,
    'yirmi': 20, 'otuz': 30, 'kırk': 40, 'elli': 50,
    'altmış': 60, 'yetmiş': 70, 'seksen': 80, 'doksan': 90,
    'yüz': 100, 'bin': 1000, 'milyon': 1_000_000,
}


def _normalize(text: str) -> str:
    text = text.lower()
    text = text.replace('ı', 'i').replace('ğ', 'g').replace('ş', 's')
    text = text.replace('ç', 'c').replace('ü', 'u').replace('ö', 'o')
    text = re.sub(r'[.,](?=\d)', '', text)   # 300.000 → 300000
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _extract_price(text: str) -> tuple[int | None, int | None]:
    """
    Fiyat aralığı çıkarır.
    Örnekler:
      "300 bin altında"      → (None, 300000)
      "200-400 bin arası"    → (200000, 400000)
      "500.000 tl üzeri"     → (500000, None)
      "1 milyon altı"        → (None, 1000000)
    """
    n = _normalize(text)

    def to_number(s: str) -> int | None:
        s = s.strip()
        if re.match(r'^\d+$', s):
            val = int(s)
            if val < 10000:            # "300" → 300.000
                val *= 1000
            return val
        # kelime sayıları: "iki yüz bin" vb.
        total = 0
        current = 0
        for word in s.split():
            if word in NUMBER_WORDS:
                n_val = NUMBER_WORDS[word]
                if n_val >= 1000:
                    current = (current or 1) * n_val
                    total += current
                    current = 0
                elif n_val == 100:
                    current = (current or 1) * 100
                else:
                    current += n_val
        total += current
        return total if total else None

    min_price = max_price = None

    # "X - Y bin/milyon arası"
    m = re.search(
        r'(\d[\d\s]*)\s*[-–ile]\s*(\d[\d\s]*)\s*(bin|milyon)?\s*(arasi|arasinda|between)?',
        n
    )
    if m:
        mult = 1_000_000 if m.group(3) == 'milyon' else (1000 if m.group(3) == 'bin' else 1)
        lo = to_number(m.group(1).strip())
        hi = to_number(m.group(2).strip())
        if lo and hi:
            if lo < 10000:
                lo *= mult
            if hi < 10000:
                hi *= mult
            min_price, max_price = lo, hi
            return min_price, max_price

    # "X bin/milyon altında/aşağısında/den az"
    m = re.search(
        r'(\d[\d\s]*|(?:(?:bir|iki|uc|dort|bes|alti|yedi|sekiz|dokuz|on|yirmi|otuz|kirk|elli|altmis|yetmis|seksen|doksan|yuz|bin|milyon)\s*)+)'
        r'\s*(bin|milyon)?\s*(altinda|asagisinda|den az|dan az|alt[iı]|max|en fazla)',
        n
    )
    if m:
        mult = 1_000_000 if m.group(2) == 'milyon' else (1000 if m.group(2) == 'bin' else 1)
        val = to_number(m.group(1).strip())
        if val:
            if val < 10000:
                val *= mult
            max_price = val

    # "X bin/milyon üzeri/yukarısı/den fazla"
    m = re.search(
        r'(\d[\d\s]*|(?:(?:bir|iki|uc|dort|bes|alti|yedi|sekiz|dokuz|on|yirmi|otuz|kirk|elli|altmis|yetmis|seksen|doksan|yuz|bin|milyon)\s*)+)'
        r'\s*(bin|milyon)?\s*(uzeri|yukarisinda|den fazla|dan fazla|ustu|min|en az)',
        n
    )
    if m:
        mult = 1_000_000 if m.group(2) == 'milyon' else (1000 if m.group(2) == 'bin' else 1)
        val = to_number(m.group(1).strip())
        if val:
            if val < 10000:
                val *= mult
            min_price = val

    return min_price, max_price


def _extract_year(text: str) -> tuple[int | None, int | None]:
    n = _normalize(text)
    year_min = year_max = None

    # "2020 model" / "2020 yili"
    m = re.search(r'(20\d\d|19\d\d)\s*(?:model|yili?)?', n)
    if m:
        y = int(m.group(1))
        year_min = year_max = y

    # "2018-2022 arası"
    m = re.search(r'(20\d\d|19\d\d)\s*[-–]\s*(20\d\d|19\d\d)', n)
    if m:
        year_min = int(m.group(1))
        year_max = int(m.group(2))

    # "2020 sonrasi / uzeri"
    m = re.search(r'(20\d\d|19\d\d)\s*(?:sonrasi|uzeri|ve uzeri)', n)
    if m:
        year_min = int(m.group(1))
        year_max = None

    # "2020 oncesi"
    m = re.search(r'(20\d\d|19\d\d)\s*(?:oncesi|alti)', n)
    if m:
        year_min = None
        year_max = int(m.group(1))

    return year_min, year_max


def _extract_make_model(text: str) -> tuple[str | None, str | None]:
    """Marka ve model çıkarır."""
    found_make = None
    found_model = None
    t_lower = text.lower()

    for make in sorted(KNOWN_MAKES, key=len, reverse=True):
        if make.lower() in t_lower:
            found_make = make
            # Marka sonrasındaki kelime model olabilir
            pattern = re.compile(re.escape(make.lower()) + r'\s+([a-z0-9]+(?:\s+[a-z0-9]+)?)', re.I)
            m = pattern.search(t_lower)
            if m:
                candidate = m.group(1).strip()
                # Gereksiz kelimeleri filtrele
                stopwords = {'var', 'mi', 'mu', 'mu', 'araba', 'otomobil', 'arac', 'model',
                             'satilk', 'kiralik', 'ilan', 'araç', 'satilik'}
                if candidate.split()[0] not in stopwords:
                    found_model = candidate.split()[0].upper()
            break

    return found_make, found_model


def _extract_listing_type(text: str) -> str | None:
    n = _normalize(text)
    if re.search(r'kirali[kğ]|kiralama|rent|kira', n):
        return 'rental'
    if re.search(r'satili[kğ]|satlik|satilik|sale|satis', n):
        return 'sale'
    return None


def _extract_city(text: str) -> str | None:
    cities = [
        'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya',
        'Gaziantep', 'Mersin', 'Kayseri', 'Eskişehir', 'Diyarbakır', 'Samsun',
        'Denizli', 'Trabzon', 'Kocaeli', 'Gebze', 'Manisa', 'Tekirdağ',
    ]
    t = _normalize(text)
    for city in cities:
        if _normalize(city) in t:
            return city
    return None


def parse_query(text: str) -> dict:
    """
    Kullanıcı metnini arama filtrelerine çevirir.
    Döndürülen dict doğrudan listings.selectors.search_listings(filters=...) e geçirilebilir.
    """
    filters: dict = {}

    make, model = _extract_make_model(text)
    if make:
        filters['make'] = make
    if model:
        filters['model'] = model

    price_min, price_max = _extract_price(text)
    if price_min is not None:
        filters['price_min'] = price_min
    if price_max is not None:
        filters['price_max'] = price_max

    year_min, year_max = _extract_year(text)
    if year_min:
        filters['year_min'] = year_min
    if year_max:
        filters['year_max'] = year_max

    listing_type = _extract_listing_type(text)
    if listing_type:
        filters['listing_type'] = listing_type

    city = _extract_city(text)
    if city:
        filters['city'] = city

    n = _normalize(text)
    for pattern, fuel in FUEL_MAP.items():
        if re.search(pattern, n):
            filters['fuel_type'] = fuel
            break

    for pattern, trans in TRANSMISSION_MAP.items():
        if re.search(pattern, n):
            filters['transmission'] = trans
            break

    for pattern, body in BODY_MAP.items():
        if re.search(pattern, n):
            filters['body_type'] = body
            break

    return filters


def build_human_summary(filters: dict) -> str:
    """Filtreleri okunabilir Türkçe özetle."""
    parts = []
    if filters.get('listing_type') == 'sale':
        parts.append('satılık')
    elif filters.get('listing_type') == 'rental':
        parts.append('kiralık')
    if filters.get('make'):
        s = filters['make']
        if filters.get('model'):
            s += ' ' + filters['model']
        parts.append(s)
    if filters.get('body_type'):
        parts.append(filters['body_type'])
    if filters.get('fuel_type'):
        fuel_labels = {'diesel': 'dizel', 'gasoline': 'benzinli', 'electric': 'elektrikli',
                       'hybrid': 'hibrit', 'lpg': 'LPG\'li'}
        parts.append(fuel_labels.get(filters['fuel_type'], filters['fuel_type']))
    if filters.get('transmission'):
        parts.append('otomatik' if filters['transmission'] == 'automatic' else 'manuel')
    if filters.get('year_min') and filters.get('year_max'):
        if filters['year_min'] == filters['year_max']:
            parts.append(f"{filters['year_min']} model")
        else:
            parts.append(f"{filters['year_min']}-{filters['year_max']} model")
    elif filters.get('year_min'):
        parts.append(f"{filters['year_min']} sonrası")
    elif filters.get('year_max'):
        parts.append(f"{filters['year_max']} öncesi")
    price_parts = []
    if filters.get('price_min'):
        price_parts.append(f"{filters['price_min']:,} TL üzeri".replace(',', '.'))
    if filters.get('price_max'):
        price_parts.append(f"{filters['price_max']:,} TL altı".replace(',', '.'))
    if price_parts:
        parts.append(', '.join(price_parts))
    if filters.get('city'):
        parts.append(filters['city'] + "'da")
    return ', '.join(parts) if parts else 'tüm araçlar'
