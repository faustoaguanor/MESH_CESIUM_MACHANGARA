#!/usr/bin/env python3
"""Preparación del tileset fotogramétrico de Machángara para el visor.

Sobre el tileset exportado por Cesium ion (b3dm + glTF con Draco, WebP y
KHR_materials_unlit), ``huella`` calcula el contorno de la malla con textura
válida (descarta los faldones blancos de los bordes, que no tienen cobertura
fotográfica) y una muestra de vértices junto al borde para ajustar la altura
contra el terreno.
Escribe ``data/footprint.json``, que el visor usa para recortar la malla por
fuera y el terreno de Cesium por dentro.

``altura`` comprueba el datum vertical de la malla comparando su suelo con el DEM
SRTM de AWS Terrain Tiles (Terrarium, alturas sobre el nivel del mar EGM96).

Las teselas no se modifican. Se evaluó activar mipmaps (LINEAR_MIPMAP_LINEAR)
y se descartó: Cesium reescala las texturas NPOT a potencia de 2, la imagen
pierde nitidez y aparecen costuras del atlas; con HLOD cada nivel ya trae la
resolución de textura adecuada a la distancia.

Requisitos: ``pip install numpy shapely DracoPy pillow``

Uso::

    python tools/preparar_malla.py huella
    python tools/preparar_malla.py altura
"""

import argparse
import io
import json
import math
import struct
import urllib.request
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

GLB_MAGIC = b"glTF"


# ---------------------------------------------------------------------------
# Lectura de b3dm
# ---------------------------------------------------------------------------
def leer_b3dm(ruta):
    """Devuelve (cabecera_b3dm, gltf_json, bin_chunk)."""
    b = ruta.read_bytes()
    _, _, _, ftj, ftb, btj, btb = struct.unpack("<4sIIIIII", b[:28])
    inicio_glb = 28 + ftj + ftb + btj + btb
    glb = b[inicio_glb:]
    if glb[:4] != GLB_MAGIC:
        raise ValueError(f"{ruta}: no contiene GLB")
    json_len = struct.unpack("<I", glb[12:16])[0]
    gltf = json.loads(glb[20 : 20 + json_len])
    off = 20 + json_len
    bin_len = struct.unpack("<I", glb[off : off + 4])[0]
    binario = glb[off + 8 : off + 8 + bin_len]
    return b[:inicio_glb], gltf, binario


def vista(gltf, binario, indice):
    bv = gltf["bufferViews"][indice]
    o = bv.get("byteOffset", 0)
    return binario[o : o + bv["byteLength"]]


# ---------------------------------------------------------------------------
# Huella
# ---------------------------------------------------------------------------
def cmd_huella(args):
    import DracoPy
    import numpy as np
    from PIL import Image
    from shapely import contains_xy
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient
    from shapely.ops import unary_union

    tileset = json.loads((DATA / "tileset.json").read_text())
    # Ion "movable": el primer hijo lleva la traslación que centra la malla en el origen.
    t = tileset["root"]["children"][0]["transform"]
    ox, oy, oz = -t[12], -t[13], -t[14]

    textura_ok, textura_blanca, verts = [], [], []
    pesos = np.array([[1 / 3] * 3, [0.6, 0.2, 0.2], [0.2, 0.6, 0.2], [0.2, 0.2, 0.6]])

    for ruta in sorted((DATA / "1").glob("*.b3dm")):
        _, gltf, binario = leer_b3dm(ruta)
        prim = gltf["meshes"][0]["primitives"][0]
        draco = prim["extensions"]["KHR_draco_mesh_compression"]
        malla = DracoPy.decode(vista(gltf, binario, draco["bufferView"]))
        P = np.asarray(malla.points)
        F = np.asarray(malla.faces).reshape(-1, 3)
        T = np.asarray(malla.tex_coord)
        img = gltf["images"][0]
        im = np.asarray(
            Image.open(io.BytesIO(vista(gltf, binario, img["bufferView"]))).convert("RGB")
        )
        h, w, _ = im.shape

        # Color mínimo en 4 puntos de cada triángulo: blanco puro = sin textura.
        minimos = []
        for pw in pesos:
            uv = (T[F] * pw[None, :, None]).sum(1)
            x = np.clip((uv[:, 0] * w).astype(int), 0, w - 1)
            y = np.clip((uv[:, 1] * h).astype(int), 0, h - 1)
            minimos.append(im[y, x].min(axis=1))
        blanco = np.min(minimos, axis=0) > args.umbral_blanco

        # glTF Y-up -> tesela Z-up: (x, y, z) -> (x, -z, y)
        xy = np.c_[P[:, 0], -P[:, 2]]
        for tri, es_blanco in zip(F, blanco):
            poli = Polygon(xy[tri])
            if poli.area > 1e-6:
                (textura_blanca if es_blanco else textura_ok).append(poli.buffer(0.05))
        verts.append(P)

    total = unary_union(textura_ok + textura_blanca)
    exterior = Polygon(max(getattr(total, "geoms", [total]), key=lambda g: g.area).exterior)
    blancas = unary_union(textura_blanca)
    borde = exterior.exterior.buffer(1.5)
    # Solo se descartan las zonas blancas conectadas al borde (los tejados blancos se quedan).
    faldones = [g for g in getattr(blancas, "geoms", [blancas]) if g.intersects(borde) and g.area > 20]

    valido = exterior.difference(unary_union(faldones).buffer(1.0)) if faldones else exterior
    valido = valido.buffer(-4).buffer(4)  # apertura morfológica: elimina picos
    valido = max(getattr(valido, "geoms", [valido]), key=lambda g: g.area)
    valido = orient(Polygon(valido.exterior).simplify(0.5), 1.0)

    P = np.vstack(verts)
    franja = valido.buffer(-3).difference(valido.buffer(-15))
    idx = np.where(contains_xy(franja, P[:, 0], -P[:, 2]))[0]
    idx = np.random.default_rng(0).choice(idx, min(300, len(idx)), replace=False)

    salida = {
        "descripcion": (
            "Coordenadas en metros ENU locales respecto al origen del tileset (modelMatrix). "
            "'contorno': area de la malla con textura valida (sin los faldones blancos sin "
            "cobertura fotografica); se usa para recortar la malla por fuera y el terreno por "
            "dentro. 'puntosControl': [E,N,U] de vertices de la malla a 3-15 m del contorno, "
            "para ajustar la altura contra el terreno. Generado con tools/preparar_malla.py."
        ),
        "contorno": [[round(x - ox, 2), round(y - oy, 2)] for x, y in list(valido.exterior.coords)[:-1]],
        "puntosControl": [
            [round(float(P[i, 0] - ox), 2), round(float(-P[i, 2] - oy), 2), round(float(P[i, 1] - oz), 2)]
            for i in idx
        ],
    }
    (DATA / "footprint.json").write_text(json.dumps(salida, separators=(",", ":")))
    print(
        f"huella: {len(salida['contorno'])} vértices, {valido.area / 1e4:.2f} ha válidas "
        f"de {exterior.area / 1e4:.2f} ha, {len(faldones)} faldones descartados"
    )


# ---------------------------------------------------------------------------
# Datum vertical
# ---------------------------------------------------------------------------
TERRARIUM = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"


def cmd_altura(args):
    import DracoPy
    import numpy as np
    from PIL import Image

    tileset = json.loads((DATA / "tileset.json").read_text())
    t = tileset["root"]["children"][0]["transform"]
    ox, oy, oz = -t[12], -t[13], -t[14]

    # Vértices de un nivel de detalle intermedio, en ENU local con la altura original.
    pts = []
    for ruta in sorted((DATA / str(args.nivel)).glob("*.b3dm")):
        _, gltf, binario = leer_b3dm(ruta)
        draco = gltf["meshes"][0]["primitives"][0]["extensions"]["KHR_draco_mesh_compression"]
        P = np.asarray(DracoPy.decode(vista(gltf, binario, draco["bufferView"])).points)
        pts.append(np.c_[P[:, 0] - ox, -P[:, 2] - oy, P[:, 1]])
    P = np.vstack(pts)

    lon0, lat0 = args.lon, args.lat
    a, e2 = 6378137.0, 6.69437999014e-3
    phi = math.radians(lat0)
    rm = a * (1 - e2) / (1 - e2 * math.sin(phi) ** 2) ** 1.5
    rn = a / math.sqrt(1 - e2 * math.sin(phi) ** 2)

    z, teselas = 15, {}

    def dem(lon, lat):
        n = 2**z
        X = (lon + 180) / 360 * n * 256 - 0.5
        Y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n * 256 - 0.5
        x0, y0 = int(math.floor(X)), int(math.floor(Y))
        fx, fy = X - x0, Y - y0

        def px(x, y):
            clave = (x // 256, y // 256)
            if clave not in teselas:
                url = TERRARIUM.format(z=z, x=clave[0], y=clave[1])
                im = np.asarray(Image.open(io.BytesIO(urllib.request.urlopen(url).read())).convert("RGB"))
                im = im.astype(float)
                teselas[clave] = im[:, :, 0] * 256 + im[:, :, 1] + im[:, :, 2] / 256 - 32768
            return teselas[clave][y % 256, x % 256]

        return (
            px(x0, y0) * (1 - fx) * (1 - fy) + px(x0 + 1, y0) * fx * (1 - fy)
            + px(x0, y0 + 1) * (1 - fx) * fy + px(x0 + 1, y0 + 1) * fx * fy
        )

    # Suelo de la malla por celda (percentil 5, evita tejados y árboles) frente al DEM.
    c = args.celda
    ix, iy = np.floor(P[:, 0] / c).astype(int), np.floor(P[:, 1] / c).astype(int)
    dif = []
    for cx, cy in set(zip(ix, iy)):
        m = (ix == cx) & (iy == cy)
        if m.sum() < 50:
            continue
        suelo = np.percentile(P[m, 2], 5)
        e, n_ = (cx + 0.5) * c, (cy + 0.5) * c
        lon = lon0 + math.degrees(e / (rn * math.cos(phi)))
        lat = lat0 + math.degrees(n_ / rm)
        dif.append(dem(lon, lat) - suelo)
    dif = np.array(dif)
    med = float(np.median(dif))
    mad = float(np.median(np.abs(dif - med)))
    print(f"{len(dif)} celdas de {c:.0f} m; DEM (nivel del mar) - suelo de la malla:")
    print(f"  si la malla es ortométrica: {med:+.2f} m (MAD {mad:.2f})")
    print(f"  si la malla es elipsoidal (N = {args.n:.2f} m): {med + args.n:+.2f} m")
    print("La hipótesis con el valor más cercano a 0 es la correcta.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("huella", help="genera data/footprint.json")
    h.add_argument("--umbral-blanco", type=int, default=235, help="valor RGB mínimo considerado 'sin textura'")
    h.set_defaults(func=cmd_huella)
    v = sub.add_parser("altura", help="compara la malla con el DEM SRTM para verificar el datum vertical")
    v.add_argument("--lon", type=float, default=-78.5437)
    v.add_argument("--lat", type=float, default=-0.2653)
    v.add_argument("--n", type=float, default=25.58, help="ondulación del geoide EGM96 (m)")
    v.add_argument("--nivel", type=int, default=3, help="nivel de detalle de las teselas")
    v.add_argument("--celda", type=float, default=30.0, help="tamaño de celda (m), ~resolución del DEM")
    v.set_defaults(func=cmd_altura)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
