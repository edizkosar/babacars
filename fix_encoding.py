"""Fix remaining mojibake."""
filepath = r'c:\Users\Arda_Yazıcı\OneDrive\Masaüstü\babacars\templates\base.html'
with open(filepath, 'r', encoding='utf-8') as f:
    t = f.read()

# Fix ş (U+00C5 U+0178)
t = t.replace('\u00c5\u0178', '\u015f')
# Fix Ş (U+00C5 U+017E)  
t = t.replace('\u00c5\u017e', '\u015e')

with open(filepath, 'w', encoding='utf-8', newline='') as f:
    f.write(t)

checks = ['Karşılaştır', 'Çıkış', 'Giriş', 'İlanlar', 'Satılık']
for c in checks:
    status = 'OK' if c in t else 'MISSING'
    print(c + ': ' + status)
