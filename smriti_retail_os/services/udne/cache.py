from smriti_retail_os.services.udne.template_compiler import CompiledTemplate

_COMPILED_TEMPLATE_CACHE = {}

def get_compiled_template(rule_id: str, version: int, template_str: str) -> CompiledTemplate:
    """
    Fetches the compiled template from cache, or compiles and caches it.
    The version-based cache key prevents stale compiled templates.
    """
    cache_key = f"{rule_id}:{version}"
    if cache_key not in _COMPILED_TEMPLATE_CACHE:
        _COMPILED_TEMPLATE_CACHE[cache_key] = CompiledTemplate(template_str)
    return _COMPILED_TEMPLATE_CACHE[cache_key]

def clear_compiled_template_cache():
    """Manually invalidates the compiled template cache."""
    _COMPILED_TEMPLATE_CACHE.clear()
