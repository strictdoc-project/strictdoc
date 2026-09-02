from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/html2pdf/template/footer.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<style html2pdf-footer-style>\nhtml2pdf-footer {\n  padding-bottom: 0;\n}\n.html2pdf-footer {\n  display: flex;\n  justify-content: space-between;\n  column-gap: 16px;\n  font-size: small;\n  line-height: 1;\n  color: rgba(0,0,0,0.5);\n  border-top: 1px solid rgba(0,0,0,0.25);\n  padding-top: 8px;\n}\n.html2pdf-footer-left {\n  text-align: left;\n}\n.html2pdf-footer-right {\n  text-align: right;\n}\n.html2pdf-header-page_placeholder {\n  width: 54px; /* max for pattern 888/888 */\n  flex-shrink: 0;\n  text-indent: -10000px;\n}\n</style>\n<template html2pdf4doc-footer><div html2pdf4doc-page-number>\n    <span html2pdf4doc-page-number-current></span>/<span html2pdf4doc-page-number-total></span>\n  </div>\n  <div class="html2pdf-footer">\n    <div class="html2pdf-footer-left">'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'date_today')))
    yield '</div>\n    <div class="html2pdf-footer-right"></div>\n    <div class="html2pdf-header-page_placeholder"></div>\n  </div>\n</template>'

blocks = {}
debug_info = '36=13'