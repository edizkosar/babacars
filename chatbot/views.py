import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from chatbot.parser import parse_query, build_human_summary
from listings.selectors import search_listings


@ratelimit(key='ip', rate='30/m', method='POST', block=True)
@require_http_methods(["POST"])
def chat_view(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Geçersiz istek.'}, status=400)

    if not message:
        return JsonResponse({'error': 'Mesaj boş olamaz.'}, status=400)

    if len(message) > 300:
        return JsonResponse({'error': 'Mesaj çok uzun.'}, status=400)

    # Selamlama / yardım sorguları
    greetings = ['merhaba', 'selam', 'hey', 'hi', 'hello', 'naber', 'nasılsın']
    msg_lower = message.lower()
    if any(g in msg_lower for g in greetings):
        return JsonResponse({
            'reply': (
                "Merhaba! Ben BabaCars asistanıyım 🚗\n\n"
                "Araç aramanıza yardımcı olabilirim. Örneğin:\n"
                "• \"300 bin altında BMW var mı?\"\n"
                "• \"Kiralık otomatik SUV\"\n"
                "• \"2020 sonrası dizel Mercedes\"\n"
                "• \"İstanbul'da 500 bin TL altında satılık araç\""
            ),
            'listings': [],
            'filters': {},
        })

    help_keywords = ['yardım', 'help', 'nasıl', 'ne yapabilirsin', 'neler yapabilirsin']
    if any(k in msg_lower for k in help_keywords):
        return JsonResponse({
            'reply': (
                "Şunları sorabilirsiniz:\n\n"
                "🔍 **Marka/Model:** \"BMW 3 serisi var mı?\"\n"
                "💰 **Fiyat:** \"200-400 bin arası araç\"\n"
                "📅 **Yıl:** \"2021 sonrası araçlar\"\n"
                "⛽ **Yakıt:** \"Elektrikli araç\"\n"
                "🏙️ **Şehir:** \"Ankara'da satılık\"\n"
                "🚗 **Kasa:** \"Sedan veya SUV\""
            ),
            'listings': [],
            'filters': {},
        })

    # Sorguyu parse et
    filters = parse_query(message)

    if not filters:
        return JsonResponse({
            'reply': (
                "Aramanızı anlayamadım. Daha açık bir şekilde sorabilir misiniz?\n\n"
                "Örnek: \"300 bin TL altında satılık BMW\""
            ),
            'listings': [],
            'filters': {},
        })

    # Veritabanı araması
    qs = search_listings(filters=filters)
    total = qs.count()
    results = qs[:5]

    summary = build_human_summary(filters)

    if total == 0:
        reply = f"**{summary}** için sonuç bulunamadı. Filtreleri genişletmeyi deneyin."
    elif total == 1:
        reply = f"**{summary}** için **1 ilan** bulundu:"
    else:
        shown = min(total, 5)
        reply = f"**{summary}** için **{total} ilan** bulundu. İlk {shown} tanesi:"

    listings_data = []
    for listing in results:
        vehicle = getattr(listing, 'vehicle', None)
        cover = listing.photos.filter(is_cover=True).first() or listing.photos.first()
        listings_data.append({
            'id': listing.id,
            'title': listing.title,
            'price': f"{listing.price:,.0f} {listing.currency}".replace(',', '.'),
            'city': listing.city,
            'url': f'/{listing.slug}/',
            'make': vehicle.make if vehicle else '',
            'model': vehicle.model if vehicle else '',
            'year': vehicle.year if vehicle else '',
            'listing_type': listing.listing_type,
            'cover_url': cover.image.url if cover else None,
        })

    return JsonResponse({
        'reply': reply,
        'listings': listings_data,
        'filters': filters,
        'total': total,
    })
