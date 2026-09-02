from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'icons/ico16_sort.svg'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<svg\n  class="svg_icon icon_sort"\n  viewBox="0 0 16 16"\n  fill="none"\n  stroke="currentColor"\n  stroke-width="1.5"\n  stroke-linecap="round"\n  stroke-linejoin="round"\n>\n  <g class="sort-none">\n    <polyline points="5 10 8 13 11 10"></polyline>\n    <polyline points="5 6 8 3 11 6"></polyline>\n  </g>\n  <g class="sort-desc">\n    <polyline points="5 10 8 13 11 10"></polyline>\n    <line x1="8" y1="5" x2="8" y2="13"></line>\n  </g>\n  <g class="sort-asc">\n    <line x1="8" y1="11" x2="8" y2="3"></line>\n    <polyline points="5 6 8 3 11 6"></polyline>\n  </g>\n</svg>'

blocks = {}
debug_info = ''