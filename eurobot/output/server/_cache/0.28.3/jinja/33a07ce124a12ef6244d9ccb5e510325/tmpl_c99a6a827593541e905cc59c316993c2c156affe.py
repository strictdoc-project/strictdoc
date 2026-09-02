from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/anchor/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_sdoc_entity = resolve('sdoc_entity')
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
    l_0_local_anchor = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity))
    context.vars['local_anchor'] = l_0_local_anchor
    context.exported_vars.add('local_anchor')
    l_0_incoming_links = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_incoming_links'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity))
    context.vars['incoming_links'] = l_0_incoming_links
    context.exported_vars.add('incoming_links')
    l_0_anchor_has_back_links = ((not t_2((undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links))) and (t_1((undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links)) > 0))
    context.vars['anchor_has_back_links'] = l_0_anchor_has_back_links
    context.exported_vars.add('anchor_has_back_links')
    yield '<sdoc-anchor\n  id="'
    yield escape((undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor))
    yield '"\n  data-anchor="'
    yield escape((undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor))
    yield '"\n  node-role="'
    yield escape(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_type_string')))
    yield '"\n  '
    if (not t_2(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_uid'))):
        pass
        yield 'data-uid="'
        yield escape(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_uid'))
        yield '"\n  '
    yield '\n  '
    if (undefined(name='anchor_has_back_links') if l_0_anchor_has_back_links is missing else l_0_anchor_has_back_links):
        pass
        yield 'class="anchor_has_back_links"'
    yield '\n>\n  '
    if environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_uid'):
        pass
        yield '\n  <div class="anchor_block" data-testid="anchor_hover_button">\n    '
        l_1_anchor_button_text = (undefined(name='local_anchor') if l_0_local_anchor is missing else l_0_local_anchor)
        pass
        yield '\n      '
        template = environment.get_template('components/anchor/anchor_clipboard_button.jinja', 'components/anchor/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'anchor_button_text': l_1_anchor_button_text, 'anchor_has_back_links': l_0_anchor_has_back_links, 'incoming_links': l_0_incoming_links, 'local_anchor': l_0_local_anchor}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n    '
        l_1_anchor_button_text = missing
        if (undefined(name='anchor_has_back_links') if l_0_anchor_has_back_links is missing else l_0_anchor_has_back_links):
            pass
            yield '<div class="anchor_back_links">\n      Incoming link'
            if (t_1((undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links)) > 1):
                pass
                yield 's'
            yield ' from:\n      '
            for l_1_incoming_link in (undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links):
                l_1_incoming_link_parent_node = l_1_incoming_link_href = missing
                _loop_vars = {}
                pass
                l_1_incoming_link_parent_node = context.call(environment.getattr(l_1_incoming_link, 'parent_node'), _loop_vars=_loop_vars)
                _loop_vars['incoming_link_parent_node'] = l_1_incoming_link_parent_node
                l_1_incoming_link_href = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_link'), context.call(environment.getattr(l_1_incoming_link, 'parent_node'), _loop_vars=_loop_vars), _loop_vars=_loop_vars)
                _loop_vars['incoming_link_href'] = l_1_incoming_link_href
                yield '<a href="'
                yield escape((undefined(name='incoming_link_href') if l_1_incoming_link_href is missing else l_1_incoming_link_href))
                yield '">\n          '
                yield escape(context.call(environment.getattr((undefined(name='incoming_link_parent_node') if l_1_incoming_link_parent_node is missing else l_1_incoming_link_parent_node), 'get_display_title'), _loop_vars=_loop_vars))
                yield '\n        </a>\n      '
            l_1_incoming_link = l_1_incoming_link_parent_node = l_1_incoming_link_href = missing
            yield '</div>\n    <div class="anchor_back_links_number" data-testid="anchor_links_number">'
            yield escape(t_1((undefined(name='incoming_links') if l_0_incoming_links is missing else l_0_incoming_links)))
            yield '</div>'
        yield '</div>'
    yield '</sdoc-anchor>'

blocks = {}
debug_info = '5=26&6=29&7=32&9=36&10=38&11=40&12=42&13=45&15=48&17=52&29=58&31=66&33=69&34=73&35=77&36=79&37=82&38=84&42=88'