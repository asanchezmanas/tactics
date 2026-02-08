# Sistema de Blog (Tactics)

El blog de Tactics ha sido migrado de prototipos estáticos a un sistema dinámico integrado en el ecosistema de la plataforma.

## Arquitectura

- **Motor de Plantillas**: Jinja2 (extendiendo `base.html`).
- **Framework Experimental**: Tailwind CSS (Prose).
- **Backend**: FastAPI (Rutas dedicadas).

## Archivos Clave

- `templates/public/blog.html`: Listado principal de artículos.
- `templates/public/blog_post.html`: Plantilla para artículos individuales.
- `api/main.py`: Contiene las rutas `/blog` y `/blog/{slug}`.

## Cómo Añadir un Artículo

Actualmente, los artículos se gestionan mediante el diccionario `slug_titles` en `api/main.py` y se renderizan estáticamente en las plantillas. 

Para añadir un post:
1. Crear el contenido visual en `templates/public/blog_post.html` (o parametrizar el contenido).
2. Registrar el nuevo slug en `api/main.py` dentro de la función `serve_blog_post`.

## Diseño

El blog utiliza la **"Ciencia de la Sutileza"** como principio de diseño:
- **Barra de Progreso**: Implementada con Alpine.js para indicar la lectura.
- **Tipografía Prose**: Configurada para máxima legibilidad en modo claro y oscuro.
- **Branding**: Alineado con los tokens de Indigo-600 y Slate-900.

---
*Nota: Este sistema sustituye a los archivos legacy `blog_post_d.html` y `posts_d.html`.*
