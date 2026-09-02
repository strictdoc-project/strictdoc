from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/_shared/viewtype_menu.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_trace_is_empty = l_0_deeptrace_is_empty = missing
    pass
    l_0_trace_is_empty = (not context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'has_any_nodes')))
    context.vars['trace_is_empty'] = l_0_trace_is_empty
    context.exported_vars.add('trace_is_empty')
    l_0_deeptrace_is_empty = (not context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'has_any_requirements')))
    context.vars['deeptrace_is_empty'] = l_0_deeptrace_is_empty
    context.exported_vars.add('deeptrace_is_empty')
    yield '<div class="viewtype">\n  <div\n    id="viewtype_handler"\n    class="viewtype__handler"\n    data-dropdown-handler\n    aria-expanded="false"\n    aria-controls="viewtype_menu"\n  >\n    <span>'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_page_title')))
    yield '</span>\n    '
    template = environment.get_template('icons/ico16_expand.svg', 'screens/document/_shared/viewtype_menu.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'deeptrace_is_empty': l_0_deeptrace_is_empty, 'trace_is_empty': l_0_trace_is_empty}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </div>\n  <menu\n    id="viewtype_menu"\n    class="dropdown_menu"\n    aria-hidden="true"\n    aria-labelledby="viewtype_handler"\n  >\n    <li class="dropdown_menu_header">VIEWS</li>\n    <li>\n      <a\n        data-viewtype_link="document"\n        class="dropdown_menu_item"\n        title="Go to Document view"\n        href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_document_link'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), None, 'DOCUMENT'))
    yield '">\n      Document</a>\n    </li>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_table_screen')):
        pass
        yield '<li>\n      <a\n        data-viewtype_link="table"\n        class="dropdown_menu_item"\n        title="Go to Table view"\n        href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_document_link'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), None, 'TABLE'))
        yield '">\n      Table</a>\n    </li>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_trace_screen')):
        pass
        yield '<li>\n      <a\n        data-viewtype_link="traceability"\n        class="dropdown_menu_item'
        if (undefined(name='trace_is_empty') if l_0_trace_is_empty is missing else l_0_trace_is_empty):
            pass
            yield ' empty'
        yield '"\n        title="'
        if (undefined(name='trace_is_empty') if l_0_trace_is_empty is missing else l_0_trace_is_empty):
            pass
            yield 'This page has no content'
        else:
            pass
            yield 'Go to Traceability view'
        yield '"\n        href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_document_link'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), None, 'TRACE'))
        yield '">\n      Traceability'
        if (undefined(name='trace_is_empty') if l_0_trace_is_empty is missing else l_0_trace_is_empty):
            pass
            yield ' (empty)'
        yield '</a>\n    </li>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_deep_trace_screen')):
        pass
        yield '<li>\n      <a\n        data-viewtype_link="deep_traceability"\n        class="dropdown_menu_item'
        if (undefined(name='deeptrace_is_empty') if l_0_deeptrace_is_empty is missing else l_0_deeptrace_is_empty):
            pass
            yield ' empty'
        yield '"\n        title="'
        if (undefined(name='deeptrace_is_empty') if l_0_deeptrace_is_empty is missing else l_0_deeptrace_is_empty):
            pass
            yield 'This page has no content'
        else:
            pass
            yield 'Go to Deep Traceability view'
        yield '"\n        href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_document_link'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), None, 'DEEPTRACE'))
        yield '">\n      Deep Traceability'
        if (undefined(name='deeptrace_is_empty') if l_0_deeptrace_is_empty is missing else l_0_deeptrace_is_empty):
            pass
            yield ' (empty)'
        yield '</a>\n    </li>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_html2pdf')):
        pass
        yield '<li>\n      <a\n        data-viewtype_link="html2pdf"\n        class="dropdown_menu_item"\n        title="Go to PDF view"\n        href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_document_link'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), None, 'PDF'))
        yield '">\n      PDF</a>\n    </li>'
    yield '</menu>\n</div>'

blocks = {}
debug_info = '10=13&11=16&21=20&22=22&36=29&39=31&45=34&49=36&53=39&54=43&55=50&56=52&59=56&63=59&64=63&65=70&66=72&69=76&75=79'