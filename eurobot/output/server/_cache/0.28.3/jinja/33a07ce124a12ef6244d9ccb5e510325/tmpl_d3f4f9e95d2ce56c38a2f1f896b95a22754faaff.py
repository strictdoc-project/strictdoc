from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'markup/anchor.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_link_renderer = resolve('link_renderer')
    l_0_anchor = resolve('anchor')
    l_0_traceability_index = resolve('traceability_index')
    l_0_local_anchor = l_0_incoming_links = l_0_anchor_has_back_links = missing
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    l_0_local_anchor = context.call(environment.getattr((undefined(name='link_renderer') if l_0_link_renderer is missing else l_0_link_renderer), 'render_local_anchor'), (undefined(name='anchor') if l_0_anchor is missing else l_0_anchor))
    context.vars['local_anchor'] = l_0_local_anchor
    context.exported_vars.add('local_anchor')
    l_0_incoming_links = context.call(environment.getattr((undefined(name='traceability_index') if l_0_traceability_index is missing else l_0_traceability_index), 'get_incoming_links'), (undefined(name='anchor') if l_0_anchor is missing else l_0_anchor))
    context.vars['incoming_links'] = l_0_incoming_links
    context.exported_vars.add('incoming_links')
    l_0_anchor_has_back_links = ((not t_2((undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links))) and (t_1((undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links)) > 0))
    context.vars['anchor_has_back_links'] = l_0_anchor_has_back_links
    context.exported_vars.add('anchor_has_back_links')
    yield '\n<sdoc-anchor id="'
    yield escape((undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor))
    yield '" data-uid="'
    yield escape((undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor))
    yield '" data-anchor="'
    yield escape((undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor))
    yield '" class="anchor_in_rst">\n  <div class="anchor_block" data-testid="anchor_hover_button">\n    '
    l_1_anchor_button_text = (undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor)
    pass
    yield '\n    '
    template = environment.get_template('components/anchor/anchor_clipboard_button.jinja', 'markup/anchor.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'anchor_button_text': l_1_anchor_button_text, 'anchor_has_back_links': l_0_anchor_has_back_links, 'incoming_links': l_0_incoming_links, 'local_anchor': l_0_local_anchor}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    l_1_anchor_button_text = missing
    yield '\n    '
    if (undefined(name='anchor_has_back_links') if l_0_anchor_has_back_links is missing else l_0_anchor_has_back_links):
        pass
        yield '\n    <div class="anchor_back_links">\n      Incoming link'
        if (t_1((undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links)) > 1):
            pass
            yield 's'
        yield ' from:\n      '
        for l_1_incoming_link in (undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links):
            l_1_document_type = resolve('document_type')
            l_1_incoming_link_parent_node = l_1_incoming_link_href = missing
            _loop_vars = {}
            pass
            yield '\n        '
            l_1_incoming_link_parent_node = context.call(environment.getattr(l_1_incoming_link, 'parent_node'), _loop_vars=_loop_vars)
            _loop_vars['incoming_link_parent_node'] = l_1_incoming_link_parent_node
            yield '\n        '
            l_1_incoming_link_href = context.call(environment.getattr((undefined(name='link_renderer') if l_0_link_renderer is missing else l_0_link_renderer), 'render_node_link'), context.call(environment.getattr(l_1_incoming_link, 'parent_node'), _loop_vars=_loop_vars), context.call(environment.getattr((undefined(name='anchor') if l_0_anchor is missing else l_0_anchor), 'get_parent_or_including_document'), _loop_vars=_loop_vars), (undefined(name='document_type') if l_1_document_type is missing else l_1_document_type), _loop_vars=_loop_vars)
            _loop_vars['incoming_link_href'] = l_1_incoming_link_href
            yield '\n        <a href="'
            yield escape((undefined(name='incoming_link_href') if l_1_incoming_link_href is missing else l_1_incoming_link_href))
            yield '">\n          '
            yield escape(context.call(environment.getattr((undefined(name='incoming_link_parent_node') if l_1_incoming_link_parent_node is missing else l_1_incoming_link_parent_node), 'get_display_title'), _loop_vars=_loop_vars))
            yield '\n        </a>\n      '
        l_1_incoming_link = l_1_incoming_link_parent_node = l_1_document_type = l_1_incoming_link_href = missing
        yield '\n    </div>\n    <div class="anchor_back_links_number" data-testid="anchor_links_number">'
        yield escape(t_1((undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links)))
        yield '</div>\n    '
    yield '\n  </div>\n</sdoc-anchor>\n\n'

blocks = {}
debug_info = '6=27&7=30&8=33&9=37&12=46&14=55&16=58&17=62&18=68&19=71&20=74&21=76&25=80'