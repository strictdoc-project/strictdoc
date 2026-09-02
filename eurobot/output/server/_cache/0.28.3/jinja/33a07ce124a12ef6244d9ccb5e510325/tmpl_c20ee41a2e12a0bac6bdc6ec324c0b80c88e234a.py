from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_view_object = resolve('view_object')
    l_0_node_type = l_0_is_included = l_0_node_type_string = l_0_is_editable = l_0_copy_to_clipboard = missing
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '\n\n\n\n'
    l_0_node_type = context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_type_string'))
    context.vars['node_type'] = l_0_node_type
    context.exported_vars.add('node_type')
    yield '\n'
    l_0_is_included = context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'document_is_included'))
    context.vars['is_included'] = l_0_is_included
    context.exported_vars.add('is_included')
    yield '\n'
    l_0_node_type_string = context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_node_type_string'))
    context.vars['node_type_string'] = l_0_node_type_string
    context.exported_vars.add('node_type_string')
    yield '\n'
    l_0_is_editable = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'can_edit_node'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity))
    context.vars['is_editable'] = l_0_is_editable
    context.exported_vars.add('is_editable')
    yield '\n\n<turbo-frame id="article-'
    yield escape(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_mid'))
    yield '">\n\n  <sdoc-node\n    data-editable_node="on"\n    show-anchors\n    node-role="'
    yield escape((undefined(name='node_type') if l_0_node_type is missing else l_0_node_type))
    yield '"\n    '
    if context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'is_content_node')):
        pass
        yield '\n      node-view="'
        yield escape(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_requirement_style_mode')))
        yield '"'
    if (not t_1((undefined(name='node_type_string') if l_0_node_type_string is missing else l_0_node_type_string))):
        pass
        yield '\n      show-node-type-name="'
        yield escape((undefined(name='node_type_string') if l_0_node_type_string is missing else l_0_node_type_string))
        if (not (undefined(name='is_editable') if l_0_is_editable is missing else l_0_is_editable)):
            pass
            yield ' (READ-ONLY)'
        yield '"'
    yield '\n    data-included-document="'
    yield escape((undefined(name='is_included') if l_0_is_included is missing else l_0_is_included))
    yield '"\n    data-testid="node-'
    yield escape((undefined(name='node_type') if l_0_node_type is missing else l_0_node_type))
    yield '"\n  >\n\n    '
    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'should_display_stable_link'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)):
        pass
        yield '\n      '
        l_1_path = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_stable_link'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity))
        pass
        yield '\n        '
        template = environment.get_template('components/node/copy_stable_link_button.jinja', 'components/node/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'path': l_1_path, 'copy_to_clipboard': l_0_copy_to_clipboard, 'is_editable': l_0_is_editable, 'is_included': l_0_is_included, 'node_type': l_0_node_type, 'node_type_string': l_0_node_type_string}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n      '
        l_1_path = missing
    yield '\n    '
    template = environment.get_template('components/anchor/index.jinja', 'components/node/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'copy_to_clipboard': l_0_copy_to_clipboard, 'is_editable': l_0_is_editable, 'is_included': l_0_is_included, 'node_type': l_0_node_type, 'node_type_string': l_0_node_type_string}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n\n    '
    l_0_copy_to_clipboard = True
    context.vars['copy_to_clipboard'] = l_0_copy_to_clipboard
    context.exported_vars.add('copy_to_clipboard')
    yield '\n    '
    yield from context.blocks['sdoc_entity'][0](context)
    yield '\n\n    \n    '
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '\n    '
        template = environment.get_template('components/node/node_controls/index.jinja', 'components/node/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'copy_to_clipboard': l_0_copy_to_clipboard, 'is_editable': l_0_is_editable, 'is_included': l_0_is_included, 'node_type': l_0_node_type, 'node_type_string': l_0_node_type_string}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n    '
    yield '\n\n  </sdoc-node>\n</turbo-frame>'

def block_sdoc_entity(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n      \n      '
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, 0, 'Must not reach here!', caller=caller, _block_vars=_block_vars)
    yield '\n    '

blocks = {'sdoc_entity': block_sdoc_entity}
debug_info = '15=21&16=25&17=29&18=33&20=37&25=39&26=41&27=44&29=46&30=49&32=55&33=57&36=59&38=65&43=74&50=81&53=85&59=87&60=90&53=99&55=108'