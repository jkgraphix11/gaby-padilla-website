#!/usr/bin/env python3
"""Generate responsive WebP copies; keep original photographs for the lightbox.

Run from any directory with Python + Pillow: python scripts/optimize_images.py
"""
from pathlib import Path
from PIL import Image, ImageOps
from io import BytesIO
import json

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / 'assets/images'


def variants(name, widths, *, lossless=False, quality=84):
    source = IMAGES / name
    with Image.open(source) as opened:
        photo = ImageOps.exif_transpose(opened)
        results = []
        for width in sorted(set(min(width, photo.width) for width in widths)):
            height = round(photo.height * width / photo.width)
            target = IMAGES / f'{source.stem}-responsive-{width}.webp'
            resized = photo.resize((width, height), Image.Resampling.LANCZOS)
            encoded = BytesIO()
            resized.save(encoded, 'WEBP', quality=quality, lossless=lossless, method=6)
            with Image.open(BytesIO(encoded.getvalue())) as check:
                check.load()
                assert check.size == (width, height)
            target.write_bytes(encoded.getvalue())
            results.append({'path': str(target.relative_to(ROOT)), 'width': width,
                            'height': height, 'bytes': target.stat().st_size})
        return results


def main():
    # Read only the original src names, so reruns cannot recompress derivatives.
    home_photos = [
        'gaby-padilla-hero-actualizado.webp',
        'gaby-padilla-maquillaje-evento-entre-vinedos.webp',
        'quinceanera-maquillaje-corona-vestido-rojo-actualizado.webp',
        'maquillaje-social-labios-rosados-clienta.webp',
        'maquillaje-labios-rojos-cabello-lacio.webp',
        'maquillaje-social-soft-glam-ondas-editado.webp',
        'maquillaje-social-labios-rosa-vestido-verde-editado.webp',
        'maquillaje-rosa-recogido-eventos.webp',
        'maquillaje-neutro-labios-brillo.webp',
        'gaby-padilla-maquillaje-detras-del-look.webp',
        'gaby-padilla-aplicacion-maquillaje-profesional.webp',
        'preparacion-novia-velo-blanco-negro-editado.webp',
        'peinado-recogido-textura-eventos.webp',
        'maquillaje-mirada-definida-coleta.webp',
        'maquillaje-dorado-labios-frambuesa.webp',
        'maquillaje-malva-ondas-suaves.webp',
        'gaby-padilla-maquillista-aplicando-maquillaje-tijuana.webp',
        'quinceanera-vestido-rosa-atardecer-mar.webp',
    ]
    manifest = {name: variants(name, [480, 768]) for name in home_photos}
    manifest['gaby-padilla-logo.png'] = variants('gaby-padilla-logo.png', [240, 480, 720], lossless=True)
    manifest['gaby-padilla-estudio-transparente.png'] = variants('gaby-padilla-estudio-transparente.png', [640, 960, 1672])
    manifest['quinceanera-maquillaje-rosa-vestido-lila-1400.webp'] = variants('quinceanera-maquillaje-rosa-vestido-lila-1400.webp', [480, 768, 1110], quality=72)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
