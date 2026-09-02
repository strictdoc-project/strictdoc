from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/html2pdf/toc.jinja'

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
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_has_any_toc_nodes')):
        pass
        yield '<div class="pdf-toc" data-testid="pdf-toc-list">\n    <div class="pdf-toc-row">\n    <span class="pdf-toc-cell"></span>\n    <span class="pdf-toc-cell" style="text-align: center;font-weight: bold;">Table of contents</span>\n    <span class="pdf-toc-cell"></span>\n    </div>'
        for (l_1_item, l_1_node_context_) in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_iterator'), 'table_of_contents')):
            _loop_vars = {}
            pass
            yield '<div class="pdf-toc-row" data-nodeid="'
            yield escape(environment.getattr(l_1_item, 'reserved_mid'))
            yield '">\n\n          <span class="pdf-toc-cell">\n            '
            yield escape((environment.getattr(environment.getattr(l_1_item, 'context'), 'title_number_string') if environment.getattr(environment.getattr(l_1_item, 'context'), 'title_number_string') else (Markup('&nbsp;') * ((context.call(environment.getattr(l_1_node_context_, 'get_level'), _loop_vars=_loop_vars) * 2) - 1))))
            yield '\n          </span>\n          <span dotted class="pdf-toc-cell">\n            <a href="#'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), l_1_item, _loop_vars=_loop_vars))
            yield '" data-turbo="false">'
            if (not t_2(environment.getattr(l_1_item, 'reserved_title'))):
                pass
                yield escape(environment.getattr(l_1_item, 'reserved_title'))
            yield '</a>\n          </span>\n          <span class="pdf-toc-cell"><html2pdf-toc-page-number data-id="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), l_1_item, _loop_vars=_loop_vars))
            yield '"></html2pdf-toc-page-number></span>\n\n      </div>'
        l_1_item = l_1_node_context_ = missing
        yield '\n</div>\n'

blocks = {}
debug_info = '1=24&8=27&10=31&13=33&16=35&17=37&18=39&22=41'