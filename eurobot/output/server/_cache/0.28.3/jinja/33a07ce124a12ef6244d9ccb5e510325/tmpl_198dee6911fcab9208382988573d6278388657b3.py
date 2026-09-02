from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/html2pdf/template/frontpage.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<style html2pdf-frontpage-style>\n.html2pdf-frontpage-grid {\n  display: grid;\n  height: 100%;\n}\n.html2pdf-frontpage-grid-middle {\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  text-align: center;\n}\n.html2pdf-frontpage-grid-bottom {\n  display: flex;\n  justify-content: center;\n  align-items: flex-end;\n}\n</style>\n<template html2pdf4doc-frontpage><div class="html2pdf-frontpage-grid">\n  <div class="html2pdf-frontpage-grid-top"></div>\n  <div class="html2pdf-frontpage-grid-middle">\n    '
    template = environment.get_template('components/node_field/document_title/index.jinja', 'features/html2pdf/template/frontpage.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </div>\n  <div class="html2pdf-frontpage-grid-bottom">\n    '
    template = environment.get_template('components/node_field/document_meta/index.jinja', 'features/html2pdf/template/frontpage.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </div>\n  </div>\n</template>'

blocks = {}
debug_info = '23=12&26=19'