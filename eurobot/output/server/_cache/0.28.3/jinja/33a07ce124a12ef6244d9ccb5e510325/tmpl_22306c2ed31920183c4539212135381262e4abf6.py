from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'icons/ico16_folder_collapse.svg'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<svg\n  class="svg_icon icon_collapse_expand"\n  viewBox="0 0 16 16"\n  fill="none"\n  stroke="currentColor"\n  stroke-width="1.5"\n  stroke-linecap="round"\n  stroke-linejoin="round"\n>\n  <polyline class="collapsed" points="13 7 8 12 3 7"></polyline>\n  <line class="expanded" x1="4" y1="8" x2="12" y2="8"></line>\n</svg>'

blocks = {}
debug_info = ''