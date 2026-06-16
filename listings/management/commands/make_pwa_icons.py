"""
PWA için uygulama ikonlarını üretir (BabaCars altın 'BC' amblemi).
Kullanım:  python manage.py make_pwa_icons
"""
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont


class Command(BaseCommand):
    help = 'PWA uygulama ikonlarını static/icons/ altına üretir.'

    def handle(self, *args, **options):
        out_dir = Path(settings.BASE_DIR) / 'static' / 'icons'
        out_dir.mkdir(parents=True, exist_ok=True)

        INK = (17, 17, 17)
        GOLD = (201, 168, 76)

        def draw_icon(size, maskable=False):
            img = Image.new('RGB', (size, size), INK)
            d = ImageDraw.Draw(img)
            # Maskable ikonlarda kenar boşluğu (safe zone) bırak
            pad = int(size * 0.18) if maskable else int(size * 0.08)
            # Altın yuvarlak köşeli kare
            d.rounded_rectangle(
                [pad, pad, size - pad, size - pad],
                radius=int(size * 0.16), fill=GOLD,
            )
            # 'BC' metni
            try:
                font = ImageFont.truetype('arialbd.ttf', int(size * 0.42))
            except Exception:
                try:
                    font = ImageFont.truetype('arial.ttf', int(size * 0.42))
                except Exception:
                    font = ImageFont.load_default()
            text = 'BC'
            bbox = d.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            d.text(
                ((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]),
                text, fill=INK, font=font,
            )
            return img

        targets = [
            ('icon-192.png', 192, False),
            ('icon-512.png', 512, False),
            ('icon-maskable-512.png', 512, True),
            ('apple-touch-icon.png', 180, False),
        ]
        for name, size, maskable in targets:
            draw_icon(size, maskable).save(out_dir / name)
            self.stdout.write(f'  ✓ {name}')

        self.stdout.write(self.style.SUCCESS('PWA ikonları üretildi.'))
