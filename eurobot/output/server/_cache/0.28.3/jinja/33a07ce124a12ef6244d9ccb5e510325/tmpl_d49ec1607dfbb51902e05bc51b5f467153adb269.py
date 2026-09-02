from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/table/update_node_field/stream_update_title_field.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node = resolve('node')
    l_0_field_value = resolve('field_value')
    l_0_title_presence_changed = resolve('title_presence_changed')
    l_0_content_entries = resolve('content_entries')
    pass
    yield '<turbo-stream action="update" target="cell-'
    yield escape(environment.getattr((undefined(name='node') if l_0_node is missing else l_0_node), 'reserved_mid'))
    yield '-TITLE">\n  <template>'
    if (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value):
        pass
        l_1_sdoc_entity = (undefined(name='node') if l_0_node is missing else l_0_node)
        pass
        template = environment.get_template('components/anchor/index.jinja', 'actions/table/update_node_field/stream_update_title_field.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'sdoc_entity': l_1_sdoc_entity}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_sdoc_entity = missing
        l_1_field_content = (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value)
        pass
        template = environment.get_template('screens/document/table/field_display_mode/title.jinja', 'actions/table/update_node_field/stream_update_title_field.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = missing
    yield '</template>\n</turbo-stream>\n\n'
    template = environment.get_template('actions/document/_shared/stream_updated_toc.jinja.html', 'actions/table/update_node_field/stream_update_title_field.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    if (undefined(name='title_presence_changed') if l_0_title_presence_changed is missing else l_0_title_presence_changed):
        pass
        for (l_1_entry_node, l_1__) in (undefined(name='content_entries') if l_0_content_entries is missing else l_0_content_entries):
            l_1_requirement = resolve('requirement')
            _loop_vars = {}
            pass
            if context.call(environment.getattr(l_1_entry_node, 'is_content_node'), _loop_vars=_loop_vars):
                pass
                l_1_requirement = l_1_entry_node
                _loop_vars['requirement'] = l_1_requirement
                yield '<turbo-stream action="replace" target="cell-'
                yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                yield '-LEVEL">\n        <template>'
                template = environment.get_template('screens/document/table/type_level.jinja', 'actions/table/update_node_field/stream_update_title_field.jinja.html')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'entry_node': l_1_entry_node, 'requirement': l_1_requirement}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '</template>\n      </turbo-stream>'
        l_1_entry_node = l_1__ = l_1_requirement = missing

blocks = {}
debug_info = '1=16&3=18&5=22&8=31&14=39&16=45&17=47&18=51&19=53&20=56&22=58'