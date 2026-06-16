"""
PWA servis view'ları: manifest, service worker ve offline sayfası.
Service worker'ın tüm siteyi kapsaması için kök dizinden servis edilir.
"""
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse


def manifest_view(request):
    content = render_to_string('pwa/manifest.webmanifest')
    return HttpResponse(content, content_type='application/manifest+json')


def service_worker_view(request):
    content = render_to_string('pwa/sw.js')
    response = HttpResponse(content, content_type='application/javascript')
    # SW'nin kök kapsamda çalışmasına izin ver
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


def offline_view(request):
    return render(request, 'pwa/offline.html')
