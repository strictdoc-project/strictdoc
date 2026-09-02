from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/trace/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'has_any_nodes')):
        pass
        yield '<div class="main">\n    '
        template = environment.get_template('_shared/tags.jinja.html', 'features/trace/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n      <div class="content">'
        for (l_1_node, l_1__) in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_content_iterator')):
            l_1_section = resolve('section')
            l_1_text_node = resolve('text_node')
            l_1_requirement = resolve('requirement')
            _loop_vars = {}
            pass
            if context.call(environment.getattr(l_1_node, 'is_document_node'), _loop_vars=_loop_vars):
                pass
                yield '\n            <section class="content_section">\n              <div class="content_item" data-role="parents"></div>\n              <div class="content_item" data-role="current">'
                l_1_section = l_1_node
                _loop_vars['section'] = l_1_section
                yield '\n                '
                template = environment.get_template('components/section/card_extends_card.jinja', 'features/trace/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'node': l_1_node, 'requirement': l_1_requirement, 'section': l_1_section, 'text_node': l_1_text_node}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n              </div>\n              <div class="content_item" data-role="children"></div>\n            </section>'
            elif context.call(environment.getattr(l_1_node, 'is_content_node'), _loop_vars=_loop_vars):
                pass
                if context.call(environment.getattr(l_1_node, 'is_text_node'), _loop_vars=_loop_vars):
                    pass
                    yield '\n              <section class="content_section">\n                <div class="content_item" data-role="parents"></div>\n                <div class="content_item" data-role="current">'
                    l_1_text_node = l_1_node
                    _loop_vars['text_node'] = l_1_text_node
                    yield '\n                  '
                    template = environment.get_template('components/text_node/card_extends_card.jinja', 'features/trace/main.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'node': l_1_node, 'requirement': l_1_requirement, 'section': l_1_section, 'text_node': l_1_text_node}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    yield '\n                </div>\n                <div class="content_item" data-role="children"></div>\n              </section>\n            '
                else:
                    pass
                    yield '\n              <section class="content_section">\n                <div class="content_item" data-role="parents">'
                    l_2_requirement = l_1_node
                    l_2_requirement_partial = 'components/node_content/card_extends_card.jinja'
                    pass
                    template = environment.get_template('_shared/requirement_tree_left.jinja.html', 'features/trace/main.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'requirement': l_2_requirement, 'requirement_partial': l_2_requirement_partial, '_': l_1__, 'node': l_1_node, 'section': l_1_section, 'text_node': l_1_text_node}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    l_2_requirement = l_2_requirement_partial = missing
                    yield '</div>\n                <div class="content_item" data-role="current">'
                    l_1_requirement = l_1_node
                    _loop_vars['requirement'] = l_1_requirement
                    yield '\n                  '
                    template = environment.get_template('components/node_content/card_extends_card.jinja', 'features/trace/main.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'node': l_1_node, 'requirement': l_1_requirement, 'section': l_1_section, 'text_node': l_1_text_node}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    yield '\n                </div>\n                <div class="content_item" data-role="children">'
                    l_2_requirement = l_1_node
                    l_2_requirement_partial = 'components/node_content/card_extends_card.jinja'
                    pass
                    template = environment.get_template('_shared/requirement_tree_right.jinja.html', 'features/trace/main.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'requirement': l_2_requirement, 'requirement_partial': l_2_requirement_partial, '_': l_1__, 'node': l_1_node, 'section': l_1_section, 'text_node': l_1_text_node}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    l_2_requirement = l_2_requirement_partial = missing
                    yield '</div>\n              </section>\n            '
        l_1_node = l_1__ = l_1_section = l_1_text_node = l_1_requirement = missing
        yield '\n      </div>\n  </div>\n  '
    else:
        pass
        yield '<sdoc-main-placeholder data-testid="document-main-placeholder">\n    This view is empty because\n    <br/>\n    the document has no content.\n  </sdoc-main-placeholder>'

blocks = {}
debug_info = '1=12&3=15&5=22&6=28&10=31&11=34&15=41&16=43&20=46&21=49&29=62&33=70&34=73&38=83'