from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_file_view/node_title_for_banner_header.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_node = resolve('node')
    l_0_is_forward_from_requirements_to_code = resolve('is_forward_from_requirements_to_code')
    l_0_role = resolve('role')
    l_0_badge_text = missing
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '\n'
    l_0_badge_text = environment.getattr((undefined(name='node') if l_0_node is missing else l_0_node), 'node_type')
    context.vars['badge_text'] = l_0_badge_text
    context.exported_vars.add('badge_text')
    yield '\n\n'
    if (undefined(name='is_forward_from_requirements_to_code') if l_0_is_forward_from_requirements_to_code is missing else l_0_is_forward_from_requirements_to_code):
        pass
        yield '<span class="source__range-title-icon" title="Relation from document node to source file">'
        template = environment.get_template('icons/ico16_source_pointer_in.svg', 'features/source_file_view/node_title_for_banner_header.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_0_badge_text}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</span>'
    else:
        pass
        yield '<span class="source__range-title-icon" title="Relation from source file to document node">'
        template = environment.get_template('icons/ico16_source_pointer_out.svg', 'features/source_file_view/node_title_for_banner_header.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_0_badge_text}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</span>'
    yield '\n  "'
    yield escape(context.call(environment.getattr((undefined(name='node') if l_0_node is missing else l_0_node), 'get_display_title')))
    yield '" ('
    yield escape(environment.getattr((undefined(name='node') if l_0_node is missing else l_0_node), 'node_type'))
    if (not t_1((undefined(name='role') if l_0_role is missing else l_0_role))):
        pass
        yield ', '
        yield escape((undefined(name='role') if l_0_role is missing else l_0_role))
    yield ')\n'

blocks = {}
debug_info = '5=22&7=26&8=29&10=39&12=47&13=50&14=53'