from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/deep_trace/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'has_any_requirements')):
        pass
        yield '<div\n    class="main"\n    js-pan_with_space="true"\n  >\n    '
        template = environment.get_template('_shared/tags.jinja.html', 'features/deep_trace/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n    <div class="content">'
        for (l_1_section_or_requirement, l_1__) in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_content_iterator')):
            _loop_vars = {}
            pass
            if (context.call(environment.getattr(l_1_section_or_requirement, 'is_document_node'), _loop_vars=_loop_vars) and environment.getattr(l_1_section_or_requirement, 'ng_has_requirements')):
                pass
                yield '\n          <section class="content_section">\n            <div class="content_item" data-role="current">'
                l_2_section = l_1_section_or_requirement
                l_2_node_controls = True
                pass
                template = environment.get_template('components/section/tiny_extends_card.jinja', 'features/deep_trace/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'node_controls': l_2_node_controls, 'section': l_2_section, '_': l_1__, 'section_or_requirement': l_1_section_or_requirement}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_section = l_2_node_controls = missing
                yield '</div>\n          </section>'
            elif (context.call(environment.getattr(l_1_section_or_requirement, 'is_content_node'), _loop_vars=_loop_vars) and (not context.call(environment.getattr(l_1_section_or_requirement, 'is_text_node'), _loop_vars=_loop_vars))):
                pass
                yield '\n          <section class="content_section">\n            <div class="content_item" data-role="parents">'
                l_2_requirement = l_1_section_or_requirement
                l_2_node_controls = True
                l_2_requirement_partial = 'components/node_content/tiny_extends_card.jinja'
                pass
                template = environment.get_template('_shared/requirement_tree_left.jinja.html', 'features/deep_trace/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'node_controls': l_2_node_controls, 'requirement': l_2_requirement, 'requirement_partial': l_2_requirement_partial, '_': l_1__, 'section_or_requirement': l_1_section_or_requirement}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_requirement = l_2_node_controls = l_2_requirement_partial = missing
                yield '</div>\n            <div class="content_item" data-role="current">'
                l_2_requirement = l_1_section_or_requirement
                l_2_node_controls = True
                pass
                template = environment.get_template('components/node_content/tiny_extends_card.jinja', 'features/deep_trace/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'node_controls': l_2_node_controls, 'requirement': l_2_requirement, '_': l_1__, 'section_or_requirement': l_1_section_or_requirement}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_requirement = l_2_node_controls = missing
                yield '</div>\n            <div class="content_item" data-role="children">'
                l_2_requirement = l_1_section_or_requirement
                l_2_node_controls = True
                l_2_requirement_partial = 'components/node_content/tiny_extends_card.jinja'
                pass
                template = environment.get_template('_shared/requirement_tree_right.jinja.html', 'features/deep_trace/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'node_controls': l_2_node_controls, 'requirement': l_2_requirement, 'requirement_partial': l_2_requirement_partial, '_': l_1__, 'section_or_requirement': l_1_section_or_requirement}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_requirement = l_2_node_controls = l_2_requirement_partial = missing
                yield '</div>\n          </section>'
        l_1_section_or_requirement = l_1__ = missing
        yield '</div> \n  </div> '
    else:
        pass
        yield '<sdoc-main-placeholder data-testid="document-main-placeholder">\n    This view is empty because\n    <br/>\n    the document has no requirements.\n  </sdoc-main-placeholder>'

blocks = {}
debug_info = '1=12&6=15&8=22&9=25&13=31&17=39&21=46&26=57&31=69'