from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/html2pdf/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    try:
        t_1 = environment.filters['safe']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'safe' found.")
    try:
        t_2 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    try:
        t_3 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_2(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'custom_html2pdf_template')), None, caller=caller)
    yield '\n\n<div\n  html2pdf-preloader\n  class="main"\n>\n      <div\n        html2pdf4doc\n        class="content"\n      >'
    template = environment.get_template('features/html2pdf/toc.jinja', 'features/html2pdf/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    for (l_1_node, l_1__) in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_content_iterator')):
        l_1_sdoc_entity = resolve('sdoc_entity')
        l_1_section = resolve('section')
        _loop_vars = {}
        pass
        if context.call(environment.getattr(l_1_node, 'is_content_node'), _loop_vars=_loop_vars):
            pass
            l_1_sdoc_entity = l_1_node
            _loop_vars['sdoc_entity'] = l_1_sdoc_entity
            yield '\n            '
            template = environment.get_template('components/node_content/index_extends_readonly.jinja', 'features/html2pdf/main.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'node': l_1_node, 'sdoc_entity': l_1_sdoc_entity, 'section': l_1_section}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n          '
        elif context.call(environment.getattr(l_1_node, 'is_document_node'), _loop_vars=_loop_vars):
            pass
            yield '\n          '
            l_1_section = l_1_node
            _loop_vars['section'] = l_1_section
            yield '\n          '
            l_1_sdoc_entity = l_1_node
            _loop_vars['sdoc_entity'] = l_1_sdoc_entity
            template = environment.get_template('components/section/pdf.jinja', 'features/html2pdf/main.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'node': l_1_node, 'sdoc_entity': l_1_sdoc_entity, 'section': l_1_section}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
    l_1_node = l_1__ = l_1_sdoc_entity = l_1_section = missing
    yield '\n\n      </div>\n</div>\n\n'
    if t_3(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'custom_html2pdf_template')):
        pass
        template = environment.get_template('features/html2pdf/template/frontpage.jinja', 'features/html2pdf/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('features/html2pdf/template/header.jinja', 'features/html2pdf/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('features/html2pdf/template/footer.jinja', 'features/html2pdf/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    else:
        pass
        yield '\n  '
        yield escape(t_1(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'custom_html2pdf_template'), 'render'), view_object=(undefined(name='view_object') if l_0_view_object is missing else l_0_view_object))))
        yield '\n'

blocks = {}
debug_info = '1=30&17=37&26=43&28=48&29=50&33=53&36=60&38=63&40=66&41=68&49=76&50=78&51=84&52=90&54=99'