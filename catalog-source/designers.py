"""Дизайнерам и архитекторам (steelline.store/diz): на старом сайте вся информация — слайды-картинки презентации EXCLUSIVE.
Текст со слайдов перенесён в разметку страницы вручную (prototype-catalog/build.py), а здесь из слайдов вырезаются только фото —
двери, интерьеры и образцы отделки — без надписей. Координаты — в системе слайда шириной 1400 px.
Запуск: venv-python catalog-source/designers.py папка/со/слайдами (s01.png … s21.png)"""
import os, sys
from PIL import Image, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prototype-catalog', 'img', 'diz')

CROPS = {
    # слайд: [(имя, (x0, y0, x1, y1), макс. сторона)]
    's05': [('awards', (768, 0, 1400, 785), 1000)],
    's10': [('size-1', (92, 215, 385, 680), 700), ('size-2', (442, 243, 770, 680), 700), ('size-3', (840, 195, 1120, 680), 700)],
    's11': [('false-1', (96, 218, 314, 647), 600), ('false-2', (385, 268, 623, 647), 600), ('false-room', (725, 0, 1400, 700), 1100)],
    's13': [('color-1', (95, 182, 428, 652), 700), ('color-2', (482, 175, 716, 652), 600), ('color-3', (765, 160, 1015, 652), 600), ('color-4', (1066, 148, 1322, 652), 600)],
    's14': [('brilliant', (757, 47, 1077, 678), 700), ('brilliant-ruby', (100, 410, 358, 588), 500), ('brilliant-violet', (420, 410, 680, 588), 500)],
    's15': [('pearl', (706, 54, 1030, 684), 700), ('pearl-macro', (98, 262, 660, 684), 900)],
    's16': [('chameleon', (621, 54, 946, 684), 700), ('chameleon-macro', (980, 0, 1400, 785), 800),
            ('ch-1', (100, 252, 276, 370), 300), ('ch-2', (328, 252, 500, 370), 300), ('ch-3', (100, 407, 276, 525), 300),
            ('ch-4', (328, 407, 500, 525), 300), ('ch-5', (100, 565, 276, 683), 300), ('ch-6', (328, 565, 503, 683), 300)],
    's17': [('metallic', (586, 57, 880, 684), 700), ('metallic-macro', (96, 314, 538, 684), 900)],
    's18': [('wood-house', (716, 0, 1400, 785), 1100)],
    's19': [('bjork', (652, 54, 984, 684), 700)],
    's20': [('concord', (664, 52, 986, 690), 700)],
    's21': [('oak', (664, 55, 962, 690), 700)],
}
# образцы панелей из дерева: сетка 2×5 справа на слайдах 19–21 (подписи у плиток — вертикальные, их переносим текстом)
TILES = [(1068, 1213), (1256, 1400)]
ROWS = [(2, 147), (161, 306), (321, 466), (481, 626), (641, 785)]
for slide, prefix in (('s19', 'bj'), ('s20', 'cc'), ('s21', 'oak')):
    k = 0
    for y0, y1 in ROWS:
        for x0, x1 in TILES:
            k += 1
            CROPS[slide].append(('%s-%d' % (prefix, k), (x0, y0, x1, y1), 300))


# эти фото заменены обработанными от заказчика — из слайдов не перезаписываем
KEEP = {'size-1', 'size-2', 'size-3', 'false-1', 'false-2', 'false-room'}
# образцы отделки и фото дверей с покрытиями: в слайдах они мелкие (плитка ~210 px) — увеличиваем в 2 раза
# (Lanczos) и повышаем резкость, чтобы на экранах с высокой плотностью пикселей фактура не была мыльной
SHARPEN = ('bj-', 'cc-', 'oak-', 'ch-', 'brilliant', 'pearl', 'chameleon', 'metallic', 'bjork', 'concord', 'oak')


def enhance(c, side):
    w, h = c.size
    k = min(2.0, side / max(w, h))
    if k > 1:
        c = c.resize((round(w * k), round(h * k)), Image.LANCZOS)
    c = c.filter(ImageFilter.UnsharpMask(radius=1.6, percent=90, threshold=2))
    return c.filter(ImageFilter.UnsharpMask(radius=0.6, percent=60, threshold=1))


def main(src):
    os.makedirs(OUT, exist_ok=True)
    for slide, items in CROPS.items():
        im = Image.open(os.path.join(src, slide + '.png')).convert('RGB')
        k = im.size[0] / 1400
        for name, box, side in items:
            if name in KEEP:
                continue
            c = im.crop(tuple(int(v * k) for v in box))
            if name.startswith(SHARPEN):
                c = enhance(c, max(side, 420) if name.startswith(('bj-', 'cc-', 'oak-', 'ch-')) else side)
            c.thumbnail((max(side, 420), max(side, 420)) if name.startswith(('bj-', 'cc-', 'oak-', 'ch-')) else (side, side), Image.LANCZOS)
            c.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=90, method=6)
    print(len(os.listdir(OUT)), 'файлов в', OUT)


main(sys.argv[1])
