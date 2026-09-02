from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/html2pdf/template/header.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<style html2pdf-header-style>\nhtml2pdf-header {\n  padding-top: 0;\n}\n.html2pdf-header {\n  display: flex;\n  justify-content: space-between;\n  align-items: flex-end;\n  column-gap: 32px;\n  font-size: small;\n  line-height: 1;\n  color: rgba(0,0,0,0.5);\n  border-bottom: 1px solid rgba(0,0,0,0.25);\n  padding-bottom: 8px;\n}\n.html2pdf-header-left {\n  text-align: left;\n  flex-shrink: 0;\n}\n.html2pdf-header-right {\n  text-align: right;\n  font-weight: bold;\n}\n</style>\n<template html2pdf4doc-header><div class="html2pdf-header">\n    <div class="html2pdf-header-left">'
    yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'project_title'))
    yield '</div>\n    <div class="html2pdf-header-right">'
    yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'title'))
    yield '</div>\n  </div>\n</template>'

blocks = {}
debug_info = '33=13&34=15'