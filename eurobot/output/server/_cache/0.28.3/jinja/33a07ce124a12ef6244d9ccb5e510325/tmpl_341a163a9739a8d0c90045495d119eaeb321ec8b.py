from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/search/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '<div\n  class="main"\n>\n  <div class="main_sticky_header">'
    template = environment.get_template('components/form/search.jinja', 'features/search/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</div>'
    if (t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'search_results')) > 0):
        pass
        yield '<div class="content">\n    '
        for l_1_node in environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'search_results'):
            _loop_vars = {}
            pass
            yield '\n      '
            if context.call(environment.getattr(l_1_node, 'is_content_node'), _loop_vars=_loop_vars):
                pass
                yield '\n        '
                l_2_requirement = l_1_node
                l_2_document = environment.getattr(l_1_node, 'document')
                l_2_node_controls = True
                pass
                template = environment.get_template('components/node_content/tiny_extends_card.jinja', 'features/search/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_2_document, 'node_controls': l_2_node_controls, 'requirement': l_2_requirement, 'node': l_1_node}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_requirement = l_2_document = l_2_node_controls = missing
                yield '\n      '
            elif context.call(environment.getattr(l_1_node, 'is_document_node'), _loop_vars=_loop_vars):
                pass
                yield '\n        '
                l_2_section = l_1_node
                l_2_document = environment.getattr(l_1_node, 'document')
                l_2_node_controls = True
                pass
                template = environment.get_template('components/section/tiny_extends_card.jinja', 'features/search/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_2_document, 'node_controls': l_2_node_controls, 'section': l_2_section, 'node': l_1_node}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_section = l_2_document = l_2_node_controls = missing
                yield '\n      '
            elif context.call(environment.getattr(l_1_node, 'is_source_file'), _loop_vars=_loop_vars):
                pass
                yield '\n        <sdoc-node node-style="card" node-role="requirement" data-testid="node-source-file">\n          <sdoc-node-field>\n          \n          '
                if (t_1(context.call(environment.getattr(environment.getattr(l_1_node, 'ng_map_reqs_to_markers'), 'keys'), _loop_vars=_loop_vars)) > 0):
                    pass
                    yield '\n          <a href="'
                    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_source_file_link_from_root_2'), environment.getattr(l_1_node, 'source_file'), _loop_vars=_loop_vars))
                    yield '">'
                    yield escape(environment.getattr(environment.getattr(l_1_node, 'source_file'), 'in_doctree_source_file_rel_path'))
                    yield '</a>\n          '
                else:
                    pass
                    yield '\n          '
                    yield escape(environment.getattr(environment.getattr(l_1_node, 'source_file'), 'in_doctree_source_file_rel_path'))
                    yield '\n          '
                yield '\n          </sdoc-node-field>\n          <sdoc-node-field>\n          Lines: '
                yield escape(environment.getattr(environment.getattr(l_1_node, 'file_stats'), 'lines_total'))
                yield '\n          </sdoc-node-field>\n          <sdoc-node-field>\n          Connected requirements: '
                yield escape(t_1(context.call(environment.getattr(environment.getattr(l_1_node, 'ng_map_reqs_to_markers'), 'keys'), _loop_vars=_loop_vars)))
                yield '\n          </sdoc-node-field>\n          <sdoc-node-field>\n          Coverage: '
                yield escape(context.call(environment.getattr(l_1_node, 'get_coverage'), _loop_vars=_loop_vars))
                yield '%\n          </sdoc-node-field>\n        </sdoc-node>\n      '
            yield '\n    '
        l_1_node = missing
        yield '\n    </div>'
    else:
        pass
        template = environment.get_template('features/search/legend.jinja', 'features/search/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    yield '</div> '

blocks = {}
debug_info = '5=19&8=26&10=29&11=33&13=40&15=48&17=55&19=63&26=66&27=69&29=76&33=79&36=81&39=83&46=90'