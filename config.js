// Configuración del Visor Mesh Machángara.
// Este archivo se carga antes del visor (index.html). Edite aquí el token y el origen.
"use strict";

const CONFIG = {
  // Token de Cesium ion (terreno e imágenes). En una web estática el token llega al
  // navegador; se recomienda limitar en https://ion.cesium.com/tokens sus "Allowed URLs"
  // a los dominios del visor. Si falla, el visor sigue con OpenStreetMap y sin relieve.
  ionToken:
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI4YmRiN2Y3My1hMmYxLTQ4ZTktYWU2Yy02NWUyNWIyYTU5MzQiLCJpZCI6NzUyODcsImlhdCI6MTY3Njc0Mjk1N30.VVfP2xRmcNDp-Yy_qsDRhGvdDORhDlAcINz-WDawy_U",
  tilesetUrl: "data/tileset.json",
  footprintUrl: "data/footprint.json",
  // Origen local del tileset (Ion "movable", sin georreferencia propia).
  origen: {
    lon: -78.5437,
    lat: -0.2653,
    // Cota ortométrica (sobre el nivel del mar) del origen local de la malla: es la
    // traslación Z que Cesium ion aplicó al tileset (tileset.json, root.children[0].transform).
    alturaOrtometrica: 2872.497,
    // Ondulación del geoide EGM96 en (lon, lat): N = h - H. Cesium trabaja con alturas
    // elipsoidales WGS84 (h), así que h = H + N. Calculada con egm96-universal.
    ondulacionGeoide: 25.58,
  },
};
