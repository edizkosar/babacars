"""
Şehir + ilçe adından yaklaşık koordinat çözümleme (offline, API'siz).

Kural:
  - İlçe doluysa ve biliniyorsa → o ilçenin koordinatı
  - İlçe boşsa veya bilinmiyorsa → şehrin merkez ilçesinin koordinatı
  - Şehir bilinmiyorsa → None (haritada gösterilmez)

Koordinatlar harita isteğinde anlık hesaplanır; veritabanına yazılmaz.
Aynı ilçedeki ilanların üst üste binmemesi için ilan id'sine bağlı
DETERMİNİSTİK küçük bir sapma uygulanır (her yüklemede aynı yerde durur).
"""
import random


def _normalize(s: str) -> str:
    s = (s or '').strip()
    s = s.replace('İ', 'i').replace('I', 'i').replace('Ş', 's').replace('Ğ', 'g')
    s = s.replace('Ç', 'c').replace('Ü', 'u').replace('Ö', 'o')
    s = s.lower().replace('̇', '')
    return (s.replace('ı', 'i').replace('ğ', 'g').replace('ş', 's')
             .replace('ç', 'c').replace('ü', 'u').replace('ö', 'o'))


# Şehir → (merkez ilçe adı, enlem, boylam)
CITY_CENTER = {
    'istanbul': ('Fatih', 41.0186, 28.9497),
    'ankara': ('Çankaya', 39.9208, 32.8541),
    'izmir': ('Konak', 38.4192, 27.1287),
    'bursa': ('Osmangazi', 40.1885, 29.0610),
    'antalya': ('Muratpaşa', 36.8845, 30.7056),
    'adana': ('Seyhan', 37.0000, 35.3289),
    'konya': ('Selçuklu', 37.9189, 32.4847),
    'eskisehir': ('Odunpazarı', 39.7639, 30.5256),
    'gaziantep': ('Şahinbey', 37.0594, 37.3825),
    'mersin': ('Akdeniz', 36.8000, 34.6333),
    'kayseri': ('Melikgazi', 38.7333, 35.4833),
    'samsun': ('İlkadım', 41.2867, 36.3300),
    'denizli': ('Pamukkale', 37.7833, 29.0964),
    'trabzon': ('Ortahisar', 41.0050, 39.7225),
    'kocaeli': ('İzmit', 40.7656, 29.9406),
    'manisa': ('Şehzadeler', 38.6191, 27.4289),
    'diyarbakir': ('Sur', 37.9117, 40.2306),
    'tekirdag': ('Süleymanpaşa', 40.9780, 27.5117),
}

# (normalize şehir, normalize ilçe) → (enlem, boylam)
DISTRICT_COORDS = {
    # İstanbul
    ('istanbul', 'fatih'): (41.0186, 28.9497),
    ('istanbul', 'kadikoy'): (40.9833, 29.0333),
    ('istanbul', 'besiktas'): (41.0422, 29.0094),
    ('istanbul', 'sisli'): (41.0602, 28.9877),
    ('istanbul', 'uskudar'): (41.0233, 29.0150),
    ('istanbul', 'bakirkoy'): (40.9819, 28.8772),
    ('istanbul', 'beyoglu'): (41.0370, 28.9770),
    ('istanbul', 'maltepe'): (40.9351, 29.1311),
    ('istanbul', 'pendik'): (40.8775, 29.2333),
    ('istanbul', 'atasehir'): (40.9833, 29.1167),
    ('istanbul', 'beylikduzu'): (41.0028, 28.6394),
    ('istanbul', 'sariyer'): (41.1669, 29.0561),
    ('istanbul', 'umraniye'): (41.0167, 29.1167),
    # Ankara
    ('ankara', 'cankaya'): (39.9208, 32.8541),
    ('ankara', 'kecioren'): (39.9803, 32.8703),
    ('ankara', 'yenimahalle'): (39.9667, 32.8000),
    ('ankara', 'mamak'): (39.9333, 32.9167),
    ('ankara', 'etimesgut'): (39.9450, 32.6800),
    ('ankara', 'sincan'): (39.9667, 32.5833),
    # İzmir
    ('izmir', 'konak'): (38.4192, 27.1287),
    ('izmir', 'bornova'): (38.4700, 27.2178),
    ('izmir', 'karsiyaka'): (38.4600, 27.1200),
    ('izmir', 'buca'): (38.3833, 27.1833),
    ('izmir', 'bayrakli'): (38.4625, 27.1656),
    ('izmir', 'cigli'): (38.4969, 27.0689),
    # Bursa
    ('bursa', 'osmangazi'): (40.1885, 29.0610),
    ('bursa', 'nilufer'): (40.2139, 28.9869),
    ('bursa', 'yildirim'): (40.1950, 29.1110),
    # Antalya
    ('antalya', 'muratpasa'): (36.8845, 30.7056),
    ('antalya', 'kepez'): (36.9200, 30.7000),
    ('antalya', 'konyaalti'): (36.8700, 30.6300),
    # Adana
    ('adana', 'seyhan'): (37.0000, 35.3289),
    ('adana', 'cukurova'): (37.0500, 35.2800),
    ('adana', 'yuregir'): (36.9833, 35.3833),
    # Konya
    ('konya', 'selcuklu'): (37.9189, 32.4847),
    ('konya', 'meram'): (37.8500, 32.4500),
    ('konya', 'karatay'): (37.8833, 32.5167),
    # Eskişehir
    ('eskisehir', 'odunpazari'): (39.7639, 30.5256),
    ('eskisehir', 'tepebasi'): (39.7833, 30.4833),
}


def resolve_coordinates(city: str, district: str = '', seed=None):
    """
    (enlem, boylam) döndürür; şehir bilinmiyorsa None.
    `seed` (örn. ilan id) verilirse deterministik küçük sapma uygulanır.
    """
    c = _normalize(city)
    d = _normalize(district)

    base = None
    if d:
        base = DISTRICT_COORDS.get((c, d))
    if base is None:
        center = CITY_CENTER.get(c)
        if center:
            base = (center[1], center[2])
    if base is None:
        return None

    lat, lng = base
    # Aynı noktadaki ilanların üst üste binmemesi için id'ye bağlı minik sapma
    if seed is not None:
        rng = random.Random(seed)
        lat += rng.uniform(-0.0035, 0.0035)
        lng += rng.uniform(-0.0035, 0.0035)
    return (round(lat, 6), round(lng, 6))


def central_district_name(city: str) -> str:
    center = CITY_CENTER.get(_normalize(city))
    return center[0] if center else ''
