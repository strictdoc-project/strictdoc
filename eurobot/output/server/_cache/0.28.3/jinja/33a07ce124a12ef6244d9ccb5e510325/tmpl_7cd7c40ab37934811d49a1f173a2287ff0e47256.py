from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'icons/ico16_section_collapse.svg'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<svg\n  class="svg_icon"\n  viewBox="0 0 16 16"\n  fill="none"\n  stroke="currentColor"\n  stroke-width="1.5"\n  stroke-linecap="round"\n  stroke-linejoin="round"\n>\n  <path d="M8.25,8 L7.75,8 M2.25,8 L1.75,8 M14.25,8 L13.75,8 M11.25,8 L10.75,8 M5.25,8 L4.75,8"></path>\n  <g class="expanded">\n    <g class="arrow_top">\n      <polyline points="10.5 13.5 8 11 5.5 13.5"></polyline>\n      <line x1="8" y1="11" x2="8" y2="15"></line>\n    </g>\n    <g class="arrow_bottom">\n      <polyline points="10.5 2.5 8 5 5.5 2.5"></polyline>\n      <line x1="8" y1="5" x2="8" y2="1"></line>\n    </g>\n  </g>\n  <g class="collapsed">\n    <g class="arrow_top_coll">\n      <polyline points="10.5 3.5 8 1 5.5 3.5"></polyline>\n      <line x1="8" y1="1" x2="8" y2="5"></line>\n    </g>\n    <g class="arrow_bottom_coll">\n      <polyline points="10.5 12.5 8 15 5.5 12.5"></polyline>\n      <line x1="8" y1="15" x2="8" y2="11"></line>\n    </g>\n  </g>\n</svg>'

blocks = {}
debug_info = ''