# MESH_CESIUM_MACHANGARA - Visualizador 3D de Mallas en Cesium

Un visualizador web interactivo de mallas 3D para el sector de Machangara, desarrollado con CesiumJS para representación geoespacial avanzada en navegadores web.

## Descripción

Este proyecto implementa un visualizador 3D web para mallas de datos geoespaciales del sector Machangara utilizando CesiumJS, la biblioteca líder para visualización 3D de datos geoespaciales en navegadores. La aplicación permite la exploración interactiva de modelos 3D optimizados sobre terreno real con integración completa de coordenadas geográficas.

## Características principales

- **Visualización 3D geoespacial**: Integración nativa con sistemas de coordenadas terrestres
- **Carga de mallas 3D optimizadas**: Formato 3D Tiles para visualización eficiente
- **Terreno real de Cesium**: Superposición sobre datos de elevación globales
- **Navegación fluida**: Controles intuitivos para exploración 3D
- **Sincronización temporal**: Potencial para visualización de datos temporales
- **Interfaz responsiva**: Diseño adaptativo para diferentes dispositivos
- **Integración con Cesium Ion**: Acceso a datasets globales y servicios en la nube

## Tecnologías utilizadas

### Visualización 3D Geoespacial
- **[CesiumJS](https://cesium.com/platform/cesiumjs/)**: Biblioteca principal para visualización 3D de datos geoespaciales
- **[3D Tiles](https://github.com/CesiumGS/3d-tiles)**: Formato abierto para transmisión masiva de datos 3D heterogéneos
- **[Cesium Ion](https://cesium.com/platform/cesium-ion/)**: Plataforma en la nube para datasets geoespaciales

### Formato de Datos
- **glTF/GLB**: Formato estándar para modelos 3D en la web
- **3D Tiles**: Formato optimizado para streaming de datos 3D masivos
- **Cesium Terrain**: Datos de elevación global optimizados

### Desarrollo Web
- **HTML5/CSS3**: Estándares web modernos
- **JavaScript ES6+**: Programación del lado del cliente
- **WebGL**: Aceleración por hardware para gráficos 3D

## Estructura del proyecto

```
MESH_CESIUM_MACHANGARA/
├── index.html                  # Aplicación web principal
├── logo.png                    # Logo del proyecto
├── data/                       # Datos 3D y configuración
│   └── tileset.json            # Archivo de configuración de 3D Tiles
└── [archivos de malla 3D]      # Archivos .b3dm, .i3dm, .pnts, etc.
```

## Instalación y uso

### Requisitos previos
- Servidor web estático (Apache, Nginx, o servidor de desarrollo como `http-server`)
- Navegador web moderno con soporte WebGL 2.0 (Chrome 70+, Firefox 63+, Edge 79+)
- Conexión a internet para cargar CesiumJS desde CDN y datos de terreno

### Instalación local
1. Clona el repositorio:
   ```bash
   git clone https://github.com/faustoaguanor/MESH_CESIUM_MACHANGARA.git
   cd MESH_CESIUM_MACHANGARA
   ```

2. Inicia un servidor web local:
   ```bash
   # Con Python 3
   python -m http.server 8000
   
   # O con Node.js http-server
   npx http-server
   ```

3. Abre tu navegador en `http://localhost:8000`

### Configuración de Cesium Ion
El proyecto utiliza Cesium Ion para datos de terreno. Para usar tu propio token:

1. Regístrate en [Cesium Ion](https://cesium.com/ion/)
2. Genera un token de acceso
3. Reemplaza el token en `index.html`:
   ```javascript
   Cesium.Ion.defaultAccessToken = "TU_TOKEN_AQUI";
   ```

## Funcionalidades

### Navegación 3D
- **Movimiento libre**: Click izquierdo + arrastrar para rotar
- **Panorámica**: Click derecho + arrastrar para desplazar
- **Zoom**: Rueda del ratón o gestos táctiles
- **Vuelo a ubicaciones**: Navegación automatizada a puntos de interés

### Visualización de Datos
- **Mallas 3D optimizadas**: Streaming progresivo de datos con 3D Tiles
- **Terreno real**: Datos de elevación global de Cesium World Terrain
- **Sombreado realista**: Iluminación basada en posición solar
- **Selección de objetos**: Interacción con elementos individuales del modelo

### Herramientas de Análisis
- **Medición de distancias**: Herramientas lineales y de área
- **Perfiles de elevación**: Cortes transversales del terreno
- **Información de posición**: Coordenadas geográficas en tiempo real
- **Captura de vistas**: Exportación de imágenes y vistas 3D

## Preparación de datos 3D

### Conversión a 3D Tiles
Para usar datos propios, necesitas convertirlos al formato 3D Tiles:

```bash
# Usando Cesium Ion CLI (recomendado)
npm install -g cesium-ion-cli
cesium-ion upload tu_modelo.glb --type 3dtiles

# O usando herramientas de conversión offline
# Consulta la documentación de CesiumGS/3d-tiles-tools
```

### Formatos soportados
- **Entrada**: OBJ, FBX, CityGML, IFC, SketchUp, glTF/GLB
- **Salida**: 3D Tiles (.b3dm, .i3dm, .pnts, .cmpt)

## Configuración avanzada

### Personalización de la vista inicial
Modifica las coordenadas en `index.html`:
```javascript
Cesium.Cartesian3.fromDegrees(-78.5437, -0.2653, 2900)
```

### Estilos visuales
Ajusta la apariencia de los modelos 3D:
```javascript
tileset.style = new Cesium.Cesium3DTileStyle({
    color: "color('red')",
    show: "${Height} > 100"
});
```

### Optimización de rendimiento
- **Nivel de detalle (LOD)**: Configuración automática basada en distancia
- **Frustum culling**: Eliminación de elementos fuera de vista
- **Occlusion culling**: Optimización para objetos ocultos

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
