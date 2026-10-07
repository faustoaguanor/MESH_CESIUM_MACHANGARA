# MESH_CESIUM_MACHANGARA - Visualizador 3D de Mallas en Cesium

Un visualizador web interactivo de mallas 3D para el sector de Machangara, desarrollado con CesiumJS para representación geoespacial avanzada en navegadores web.

## Descripción

Este proyecto implementa un visualizador 3D web para mallas de datos geoespaciales del sector Machangara utilizando CesiumJS, la biblioteca líder para visualización 3D de datos geoespaciales en navegadores. La aplicación permite la exploración interactiva de modelos 3D optimizados sobre terreno real con integración completa de coordenadas geográficas.

## Características principales

- **Malla fotogramétrica en 3D Tiles** (HLOD de 6 niveles, 637 teselas b3dm con geometría Draco y texturas WebP, material *unlit*), servida de forma progresiva según la distancia.
- **Terreno recortado bajo la malla**: Cesium World Terrain (~30 m de resolución en Ecuador) ya no atraviesa la malla en el cauce del Machángara ni en los taludes.
- **Bordes limpios**: se ocultan los faldones blancos sin cobertura fotográfica del perímetro (≈1,7 ha), recortando la malla con su contorno válido.
- **Ajuste vertical**: control deslizante de la altura del origen y botón *Ajustar al terreno*, que compara 300 vértices del borde de la malla con el terreno (mediana y MAD).
- **Coordenadas y medición**: clic para obtener latitud/longitud/altura elipsoidal; medición de distancia 3D, horizontal y desnivel.
- **Rendimiento**: `requestRenderMode` (solo redibuja cuando algo cambia), SSE dinámico y foveado, MSAA 4×, sin sombras ni iluminación para un material *unlit*, selector de calidad (SSE 4–32).
- **Interfaz responsiva** en español, panel plegable en móviles.

## Tecnologías utilizadas

- **[CesiumJS 1.146](https://cesium.com/platform/cesiumjs/)** desde jsDelivr (API asíncrona `Cesium3DTileset.fromUrl`, `Terrain.fromWorldTerrain`, `ClippingPolygonCollection`).
- **[3D Tiles](https://github.com/CesiumGS/3d-tiles)** 1.0 (b3dm) con glTF 2.0: `KHR_draco_mesh_compression`, `EXT_texture_webp`, `KHR_materials_unlit`.
- **[Cesium ion](https://cesium.com/platform/cesium-ion/)**: terreno global e imágenes base.
- **Python** (numpy, shapely, DracoPy, Pillow) para preparar la huella de la malla.

## Estructura del proyecto

```
MESH_CESIUM_MACHANGARA/
├── index.html              # Visor (HTML + CSS + JS, sin compilación)
├── config.js               # Token de Cesium ion y origen de la malla
├── data/
│   ├── tileset.json        # Árbol de teselas (Cesium ion, "movable": sin georreferencia propia)
│   ├── footprint.json      # Contorno válido y puntos de control (generado)
│   └── 0/ … 5/             # Teselas .b3dm por nivel de detalle
└── tools/
    └── preparar_malla.py   # Genera data/footprint.json a partir de las teselas
```

## Instalación y uso

Requisitos: un servidor web estático y un navegador con WebGL 2 (los recortes por polígono lo requieren).

```bash
git clone https://github.com/faustoaguanor/MESH_CESIUM_MACHANGARA.git
cd MESH_CESIUM_MACHANGARA
python -m http.server 8000   # o: npx http-server
```

Abra `http://localhost:8000`. No funciona abriendo `index.html` directamente (`file://`), porque el navegador bloquea la carga de las teselas.

### Token de Cesium ion

El token y el origen de la malla están en **`config.js`** (`CONFIG.ionToken`, `CONFIG.origen`), que `index.html` carga antes del visor. Para cambiar de token basta con editar ese archivo.

En un visor web estático el token siempre llega al navegador, así que no se puede ocultar. Para que nadie lo use fuera de tu visor, puede limitarse sin cambiarlo: en <https://ion.cesium.com/tokens>, edite el token y en **Allowed URLs** añada los dominios del visor (p. ej. `https://faustoaguanor.github.io` y `http://localhost:8000`).

Si el token falla, el visor no se rompe: muestra OpenStreetMap sin relieve y lo indica en la barra de estado.

## Georreferenciación y alturas

El tileset se exportó desde Cesium ion como *movable* (`georeferenced: false`): sus coordenadas son métricas locales. El visor lo coloca con una matriz Este-Norte-Arriba según `config.js`:

```javascript
origen: {
  lon: -78.5437,
  lat: -0.2653,
  altura: 2872.497, // altura ELIPSOIDAL WGS84 del origen local de la malla
}
```

- Cesium trabaja con **alturas elipsoidales WGS84**. `altura` es la traslación Z que Cesium ion aplicó al tileset (`tileset.json` → `root.children[0].transform`), es decir, la altura original de la malla.
- **La malla ya está en alturas elipsoidales** (las del GNSS del dron), así que no se suma la ondulación del geoide. Comprobación contra el DEM SRTM (alturas sobre el nivel del mar), comparando el suelo de la malla en 278 celdas de 30 m:

  | Hipótesis | DEM − suelo de la malla |
  |---|---|
  | Malla ortométrica (sobre el nivel del mar) | −24,86 m |
  | Malla elipsoidal (N EGM96 = 25,58 m) | **+0,72 m** |

  Versiones anteriores usaban 2900 m y luego 2898,08 m (sumando el geoide), lo que dejaba la malla unos 25–27 m por encima del terreno.
- Para repetir la verificación: `python tools/preparar_malla.py altura`.
- Con ~600 m de extensión, la convergencia de cuadrícula UTM 17S (≈0,01°) y el factor de escala (≈1,0005) son despreciables.
- El control de altura y *Ajustar al terreno* del visor sirven para revisar el encaje visual; el terreno global (~30 m) es una guía, no una verdad de campo.

## Preparación de datos

`data/footprint.json` se regenera si cambian las teselas:

```bash
pip install numpy shapely DracoPy pillow
python tools/preparar_malla.py huella
```

El script decodifica las teselas del nivel 1, marca los triángulos cuya textura es blanco puro y descarta solo las zonas blancas conectadas al borde (los tejados blancos se conservan). Después aplica una apertura morfológica de 4 m y simplifica el contorno a 0,5 m.

Las teselas no se modifican: ya vienen optimizadas por Cesium ion (Draco + WebP, 26 MB en total). Se evaluó activar mipmaps en las texturas y se descartó, porque restaba nitidez y producía costuras del atlas.

Para cargar una malla nueva: súbala a Cesium ion (OBJ, FBX, glTF, etc.) como *3D Tiles*, descargue el tileset en `data/`, ajuste `CONFIG.origen` y regenere la huella.

## Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.

```
MIT License

Copyright (c) 2025 faustoaguanor

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y los archivos de documentación asociados (el "Software"), para
utilizar el Software sin restricción, incluyendo sin limitación los derechos
de uso, copia, modificación, fusión, publicación, distribución, sublicencia y/o
venta de copias del Software, y para permitir a las personas a las que se les
proporcione el Software hacer lo mismo, sujeto a las siguientes condiciones:

El aviso de copyright anterior y este aviso de permiso se incluirán en todas
las copias o partes sustanciales del Software.

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O
IMPLÍCITA, INCLUYENDO PERO NO LIMITADO A GARANTÍAS DE COMERCIALIZACIÓN,
IDONEIDAD PARA UN PROPÓSITO PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO LOS
AUTORES O TITULARES DEL COPYRIGHT SERÁN RESPONSABLES DE NINGUNA RECLAMACIÓN,
DAÑOS U OTRAS RESPONSABILIDADES, YA SEA EN UNA ACCIÓN DE CONTRATO, AGRAVIO O
CUALQUIER OTRO MOTIVO, QUE SURJA DE O EN CONEXIÓN CON EL SOFTWARE O EL USO U
OTRO TIPO DE ACCIONES EN EL SOFTWARE.
```

## Créditos

### Desarrollo y Mantenimiento
- **Desarrollador principal**: faustoaguanor

### Plataforma Cesium
- **CesiumJS**: CesiumGS, Analítica Graphics Inc. (AGI)
- **3D Tiles Working Group**: Khronos Group, OGC Community
- **Cesium Ion**: Cesium Team

### Estándares y Formatos
- **glTF**: Khronos Group - Formato estándar 3D para la web
- **WebGL**: Khronos Group - API de gráficos 3D para navegadores
- **OGC Standards**: Open Geospatial Consortium - Estándares geoespaciales

### Tecnologías Relacionadas
- **Proj4js**: Transformaciones de sistemas de coordenadas
- **OpenStreetMap**: Datos cartográficos de base
- **Bing Maps**: Imágenes satelitales y aéreas

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Abre un issue para discutir cambios significativos
2. Sigue las convenciones de código existentes
3. Incluye documentación actualizada
4. Prueba los cambios en diferentes navegadores

## Soporte técnico

Para problemas o preguntas:

1. Consulta la [documentación oficial de Cesium](https://cesium.com/learn/)
2. Revisa los [issues del repositorio](https://github.com/faustoaguanor/MESH_CESIUM_MACHANGARA/issues)
3. Para problemas con datos 3D, consulta la [especificación 3D Tiles](https://github.com/CesiumGS/3d-tiles)

## Casos de uso y aplicaciones

Este proyecto está diseñado para:

- **Planificación urbana**: Visualización de desarrollo en Machangara
- **Análisis ambiental**: Evaluación de impacto en cuencas hidrográficas
- **Infraestructura**: Planificación de obras civiles y servicios
- **Educación**: Herramienta de enseñanza de SIG 3D
- **Participación ciudadana**: Visualización accesible de proyectos urbanos

---

*Proyecto desarrollado para la visualización 3D geoespacial del sector Machangara, integrando tecnologías modernas de representación territorial.*
