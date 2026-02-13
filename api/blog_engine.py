import markdown
from pathlib import Path
from typing import Dict, Any

def get_blog_post_data(slug: str, locale: str = "es") -> Dict[str, Any]:
    """
    Standalone logic to map a slug to a Markdown file and render it.
    Supports multi-language routing (ES/EN).
    """
    special_mappings = {
        "radar-rentabilidad": "radar_rentabilidad_instantaneo.md",
        "que-es-el-ltv": "que_es_customer_lifetime_value.md",
        "ciencia-de-la-sutileza": "que_es_customer_lifetime_value.md",
        "ia-transparente": "ia_transparente.md",
        "atribucion-causal": "atribucion_causal.md",
        "cinetica-gasto": "cinetica_gasto.md",
        # English mappings
        "profit-radar": "radar_rentabilidad_instantaneo.md",
        "what-is-ltv": "que_es_customer_lifetime_value.md"
    }
    
    filename = special_mappings.get(slug, slug.replace("-", "_") + ".md")
    
    # Try locale-specific paths first
    lang_dir = locale if locale in ["en", "es"] else "es"
    
    possible_paths = [
        Path(f"docs/blog/{lang_dir}") / filename,
        Path("docs/blog") / filename if lang_dir == "es" else None,
        Path("docs") / filename,
    ]
    
    # Filter out None paths
    possible_paths = [p for p in possible_paths if p]
    
    filepath = None
    for p in possible_paths:
        if p.exists():
            filepath = p
            break
            
    if not filepath:
        # Final attempt: glob search by prefix in the locale directory
        search_dir = Path(f"docs/blog/{lang_dir}")
        if not search_dir.exists():
            search_dir = Path("docs/blog")
            
        matches = list(search_dir.glob(f"{slug.replace('-', '_')}*.md"))
        if matches:
            filepath = matches[0]
        else:
            error_msg = "Article not found" if lang_dir == "en" else "Artículo no encontrado"
            return {"success": False, "error": error_msg, "status_code": 404}
            
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
        title = "Art├¡culo de Tactics"
        for line in lines:
            if line.startswith("# "):
                title = line.replace("# ", "").strip()
                break
        
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables', 'nl2br'])
        
        return {
            "success": True,
            "title": title,
            "html": html_content
        }
    except Exception as e:
        return {"success": False, "error": str(e), "status_code": 500}
