from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'icons/ico16_eye__stateful.svg'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<svg\n  class="svg_icon"\n  viewBox="0 0 16 16"\n  fill="none"\n  stroke="currentColor"\n  stroke-width="1.5"\n  stroke-linecap="round"\n  stroke-linejoin="round"\n>\n  <g class="svg_icon__opened">\n    <path d="M 8,4 C 5,4 2,7 2,8 2,9 5,12 8,12 11,12 14,9 14,8 14,7 11,4 8,4 Z" />\n    <path d="M 8,4 V 2"/>\n    <path d="M 13,4 12,5"/>\n    <path d="M 3,4 4,5"/>\n    <circle cy="8" cx="8" r="1" />\n  </g>\n  <g class="svg_icon__closed">\n    <path d="m 2,6 c 0,1 3,4 6,4 3,0 6,-3 6,-4" />\n    <path d="M 8,12 V 10" />\n    <path d="M 13,10 12,9" />\n    <path d="M 3,10 4,9" />\n  </g>\n</svg>'

blocks = {}
debug_info = ''