from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/body.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_content_entries = resolve('content_entries')
    l_0_is_server = missing
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    l_0_is_server = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server')
    context.vars['is_server'] = l_0_is_server
    context.exported_vars.add('is_server')
    yield '<tbody id="table-content-body" data-testid="table-content-body">'
    if (not (undefined(name='content_entries') if l_0_content_entries is missing else l_0_content_entries)):
        pass
        yield '\n  <tr class="content-view__empty-row-TR" data-testid="table-empty-placeholder">\n    <td class="content-view__empty-row-TD" colspan="100%">\n      <sdoc-main-placeholder data-testid="empty-table-placeholder">\n        This table is empty because the document has no content.\n      </sdoc-main-placeholder>\n    </td>\n  </tr>'
    if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
        pass
        l_1_prev_node = None
        l_1_next_node = (environment.getitem(environment.getitem((undefined(name='content_entries') if l_0_content_entries is missing else l_0_content_entries), 0), 0) if (undefined(name='content_entries') if l_0_content_entries is missing else l_0_content_entries) else None)
        pass
        template = environment.get_template('screens/document/table/row_add_new_node.jinja', 'screens/document/table/body.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'next_node': l_1_next_node, 'prev_node': l_1_prev_node, 'is_server': l_0_is_server}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_prev_node = l_1_next_node = missing
    l_1_loop = missing
    for (l_1_node, l_1__), l_1_loop in LoopContext((undefined(name='content_entries') if l_0_content_entries is missing else l_0_content_entries), undefined):
        l_1_requirement = resolve('requirement')
        l_1_namespace = resolve('namespace')
        l_1_ns = resolve('ns')
        l_1_section = resolve('section')
        l_1_ns_span = resolve('ns_span')
        l_1_ns_sec = resolve('ns_sec')
        _loop_vars = {}
        pass
        yield '\n\n  \n  \n  '
        if context.call(environment.getattr(l_1_node, 'is_content_node'), _loop_vars=_loop_vars):
            pass
            l_1_requirement = l_1_node
            _loop_vars['requirement'] = l_1_requirement
            yield '\n    <tr data-row-type="'
            yield escape(environment.getattr(l_1_node, 'node_type'))
            yield '" data-node-mid="'
            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
            yield '">'
            template = environment.get_template('screens/document/table/type_cell.jinja', 'screens/document/table/body.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            template = environment.get_template('screens/document/table/type_level.jinja', 'screens/document/table/body.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_1_ns = context.call((undefined(name='namespace') if l_1_namespace is missing else l_1_namespace), past_reserved=False, _loop_vars=_loop_vars)
            _loop_vars['ns'] = l_1_ns
            for l_2_column in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'enumerate_table_columns'), _loop_vars=_loop_vars):
                l_2_field_title = resolve('field_title')
                l_2_field_value = resolve('field_value')
                l_2_cell_edit_mode = resolve('cell_edit_mode')
                l_2_td_class = resolve('td_class')
                _loop_vars = {}
                pass
                if (l_2_column == 'RELATIONS'):
                    pass
                    if not isinstance(l_1_ns, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_1_ns['past_reserved'] = True
                    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_table_cell_editable'), environment.getattr(l_1_node, 'node_type'), 'RELATIONS', _loop_vars=_loop_vars):
                        pass
                        yield '\n          <td class="content-view-td content-view-td-meta content-view-td-related"\n              data-field-name="RELATIONS"'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '\n              data-node-mid="'
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '"\n              data-field-type="relations"\n              js-table_view_edit-field="relations"\n              data-url="/actions/table/get_node_relations_inline?node_mid='
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '"'
                        yield '\n          >'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '<div class="editable-cell-indicator"></div>'
                        yield '\n            <div id="cell-'
                        yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                        yield '-RELATIONS" wrapper-field-type="contenteditable">'
                        template = environment.get_template('screens/document/table/field_display_mode/relations.jinja', 'screens/document/table/body.jinja')
                        gen = template.root_render_func(template.new_context(context.get_all(), True, {'cell_edit_mode': l_2_cell_edit_mode, 'column': l_2_column, 'field_title': l_2_field_title, 'field_value': l_2_field_value, 'td_class': l_2_td_class, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                        try:
                            for event in gen:
                                yield event
                        finally: gen.close()
                        yield '\n            </div>\n          </td>'
                    else:
                        pass
                        yield '\n          <td class="content-view-td content-view-td-meta content-view-td-related content-view-td--dimmed"\n              data-field-name="RELATIONS">\n            <div class="content-view-td--dimmed_tips"></div>\n          </td>'
                elif (l_2_column == 'TITLE'):
                    pass
                    if not isinstance(l_1_ns, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_1_ns['past_reserved'] = True
                    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_table_cell_editable'), environment.getattr(l_1_node, 'node_type'), 'TITLE', _loop_vars=_loop_vars):
                        pass
                        yield '\n          <td class="content-view-td content-view-td-title"\n              data-field-name="TITLE"'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '\n              data-node-mid="'
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '"\n              data-field-type="contenteditable"\n              js-table_view_edit-field="contenteditable"\n              data-url="/actions/table/get_node_contenteditable_inline?node_mid='
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '&amp;field_name=TITLE"'
                        yield '\n          >'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '<div class="editable-cell-indicator"></div>'
                        yield '\n            <div id="cell-'
                        yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                        yield '-TITLE" wrapper-field-type="contenteditable">'
                        if environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_title'):
                            pass
                            l_3_sdoc_entity = (undefined(name='requirement') if l_1_requirement is missing else l_1_requirement)
                            pass
                            template = environment.get_template('components/anchor/index.jinja', 'screens/document/table/body.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'sdoc_entity': l_3_sdoc_entity, 'cell_edit_mode': l_2_cell_edit_mode, 'column': l_2_column, 'field_title': l_2_field_title, 'field_value': l_2_field_value, 'td_class': l_2_td_class, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            l_3_sdoc_entity = missing
                            l_3_field_content = environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_title')
                            pass
                            template = environment.get_template('screens/document/table/field_display_mode/title.jinja', 'screens/document/table/body.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_3_field_content, 'cell_edit_mode': l_2_cell_edit_mode, 'column': l_2_column, 'field_title': l_2_field_title, 'field_value': l_2_field_value, 'td_class': l_2_td_class, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            l_3_field_content = missing
                        yield '</div>\n          </td>'
                    else:
                        pass
                        yield '\n          <td class="content-view-td content-view-td-title content-view-td--dimmed"\n              data-field-name="TITLE">\n            <div class="content-view-td--dimmed_tips"></div>\n          </td>'
                elif (l_2_column == 'STATEMENT'):
                    pass
                    if not isinstance(l_1_ns, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_1_ns['past_reserved'] = True
                    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_table_cell_editable'), environment.getattr(l_1_node, 'node_type'), 'STATEMENT', _loop_vars=_loop_vars):
                        pass
                        yield '\n          <td class="content-view-td content-view-td-content"\n              data-field-name="STATEMENT"'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '\n              data-node-mid="'
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '"\n              data-field-type="contenteditable"\n              js-table_view_edit-field="contenteditable"\n              data-url="/actions/table/get_node_contenteditable_inline?node_mid='
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '&amp;field_name=STATEMENT"'
                        yield '\n          >'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '<div class="editable-cell-indicator"></div>'
                        yield '\n            <div id="cell-'
                        yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                        yield '-STATEMENT" wrapper-field-type="contenteditable">'
                        if context.call(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'has_reserved_statement'), _loop_vars=_loop_vars):
                            pass
                            l_3_field_content = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_statement'), (undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), _loop_vars=_loop_vars)
                            pass
                            template = environment.get_template('screens/document/table/field_display_mode/statement.jinja', 'screens/document/table/body.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_3_field_content, 'cell_edit_mode': l_2_cell_edit_mode, 'column': l_2_column, 'field_title': l_2_field_title, 'field_value': l_2_field_value, 'td_class': l_2_td_class, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            l_3_field_content = missing
                        yield '</div>\n          </td>'
                    else:
                        pass
                        yield '\n          <td class="content-view-td content-view-td-content content-view-td--dimmed"\n              data-field-name="STATEMENT">\n            <div class="content-view-td--dimmed_tips"></div>\n          </td>'
                elif (l_2_column == 'RATIONALE'):
                    pass
                    if not isinstance(l_1_ns, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_1_ns['past_reserved'] = True
                    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_table_cell_editable'), environment.getattr(l_1_node, 'node_type'), 'RATIONALE', _loop_vars=_loop_vars):
                        pass
                        yield '\n          <td class="content-view-td content-view-td-content"\n              data-field-name="RATIONALE"'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '\n              data-node-mid="'
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '"\n              data-field-type="contenteditable"\n              js-table_view_edit-field="contenteditable"\n              data-url="/actions/table/get_node_contenteditable_inline?node_mid='
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '&amp;field_name=RATIONALE"'
                        yield '\n          >'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '<div class="editable-cell-indicator"></div>'
                        yield '\n            <div id="cell-'
                        yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                        yield '-RATIONALE" wrapper-field-type="contenteditable">'
                        if environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'rationale'):
                            pass
                            l_3_field_content = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_rationale'), (undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), _loop_vars=_loop_vars)
                            pass
                            template = environment.get_template('screens/document/table/field_display_mode/rationale.jinja', 'screens/document/table/body.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_3_field_content, 'cell_edit_mode': l_2_cell_edit_mode, 'column': l_2_column, 'field_title': l_2_field_title, 'field_value': l_2_field_value, 'td_class': l_2_td_class, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            l_3_field_content = missing
                        yield '</div>\n          </td>'
                    else:
                        pass
                        yield '\n          <td class="content-view-td content-view-td-content content-view-td--dimmed"\n              data-field-name="RATIONALE">\n            <div class="content-view-td--dimmed_tips"></div>\n          </td>'
                elif (l_2_column == 'COMMENT'):
                    pass
                    if not isinstance(l_1_ns, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_1_ns['past_reserved'] = True
                    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_table_cell_editable'), environment.getattr(l_1_node, 'node_type'), 'COMMENT', _loop_vars=_loop_vars):
                        pass
                        yield '\n          <td class="content-view-td content-view-td-content"\n              data-field-name="COMMENT"'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '\n              data-node-mid="'
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '"\n              data-field-type="comments"\n              js-table_view_edit-field="comments"\n              data-url="/actions/table/get_node_comments_inline?node_mid='
                            yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                            yield '"'
                        yield '\n          >'
                        if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                            pass
                            yield '<div class="editable-cell-indicator"></div>'
                        yield '\n            <div id="cell-'
                        yield escape(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'reserved_mid'))
                        yield '-COMMENT" wrapper-field-type="comments">'
                        for l_3_comment_field_ in context.call(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'get_comment_fields'), _loop_vars=_loop_vars):
                            _loop_vars = {}
                            pass
                            l_4_field_content = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_field'), l_3_comment_field_, _loop_vars=_loop_vars)
                            pass
                            template = environment.get_template('screens/document/table/field_display_mode/comment.jinja', 'screens/document/table/body.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_4_field_content, 'comment_field_': l_3_comment_field_, 'cell_edit_mode': l_2_cell_edit_mode, 'column': l_2_column, 'field_title': l_2_field_title, 'field_value': l_2_field_value, 'td_class': l_2_td_class, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            l_4_field_content = missing
                        l_3_comment_field_ = missing
                        yield '</div>\n          </td>'
                    else:
                        pass
                        yield '\n          <td class="content-view-td content-view-td-content content-view-td--dimmed"\n              data-field-name="COMMENT">\n            <div class="content-view-td--dimmed_tips"></div>\n          </td>'
                else:
                    pass
                    l_2_field_title = l_2_column
                    _loop_vars['field_title'] = l_2_field_title
                    l_2_field_value = context.call(environment.getattr((undefined(name='requirement') if l_1_requirement is missing else l_1_requirement), 'get_meta_field_value_by_title'), (undefined(name='field_title') if l_2_field_title is missing else l_2_field_title), _loop_vars=_loop_vars)
                    _loop_vars['field_value'] = l_2_field_value
                    l_2_cell_edit_mode = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_table_cell_edit_mode'), environment.getattr(l_1_node, 'node_type'), (undefined(name='field_title') if l_2_field_title is missing else l_2_field_title), _loop_vars=_loop_vars)
                    _loop_vars['cell_edit_mode'] = l_2_cell_edit_mode
                    if environment.getattr((undefined(name='ns') if l_1_ns is missing else l_1_ns), 'past_reserved'):
                        pass
                        l_2_td_class = 'content-view-td'
                        _loop_vars['td_class'] = l_2_td_class
                    else:
                        pass
                        l_2_td_class = 'content-view-td content-view-td-meta'
                        _loop_vars['td_class'] = l_2_td_class
                    template = environment.get_template('screens/document/table/td_by_edit_mode.jinja', 'screens/document/table/body.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'cell_edit_mode': l_2_cell_edit_mode, 'column': l_2_column, 'field_title': l_2_field_title, 'field_value': l_2_field_value, 'td_class': l_2_td_class, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
            l_2_column = l_2_field_title = l_2_field_value = l_2_cell_edit_mode = l_2_td_class = missing
            yield '\n\n    </tr>'
            if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                pass
                l_2_prev_node = l_1_node
                l_2_next_node = (environment.getitem(environment.getattr(l_1_loop, 'nextitem'), 0) if t_1(environment.getattr(l_1_loop, 'nextitem')) else None)
                pass
                template = environment.get_template('screens/document/table/row_add_new_node.jinja', 'screens/document/table/body.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'next_node': l_2_next_node, 'prev_node': l_2_prev_node, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_prev_node = l_2_next_node = missing
            yield '\n\n  \n  \n  '
        elif context.call(environment.getattr(l_1_node, 'is_document_node'), _loop_vars=_loop_vars):
            pass
            l_1_section = l_1_node
            _loop_vars['section'] = l_1_section
            l_1_ns_span = context.call((undefined(name='namespace') if l_1_namespace is missing else l_1_namespace), count=0, counting=False, _loop_vars=_loop_vars)
            _loop_vars['ns_span'] = l_1_ns_span
            for l_2_column in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'enumerate_table_columns'), _loop_vars=_loop_vars):
                _loop_vars = {}
                pass
                if (l_2_column == 'TITLE'):
                    pass
                    if not isinstance(l_1_ns_span, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_1_ns_span['counting'] = True
                if environment.getattr((undefined(name='ns_span') if l_1_ns_span is missing else l_1_ns_span), 'counting'):
                    pass
                    if not isinstance(l_1_ns_span, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_1_ns_span['count'] = (environment.getattr((undefined(name='ns_span') if l_1_ns_span is missing else l_1_ns_span), 'count') + 1)
            l_2_column = missing
            yield '\n\n    <tr data-row-type="SECTION" data-node-mid="'
            yield escape(environment.getattr((undefined(name='section') if l_1_section is missing else l_1_section), 'reserved_mid'))
            yield '">'
            l_2_node = (undefined(name='section') if l_1_section is missing else l_1_section)
            pass
            template = environment.get_template('screens/document/table/type_cell.jinja', 'screens/document/table/body.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'node': l_2_node, '_': l_1__, 'loop': l_1_loop, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_node = missing
            yield '<td class="content-view-td content-view-td-meta">'
            yield escape(environment.getattr(environment.getattr((undefined(name='section') if l_1_section is missing else l_1_section), 'context'), 'title_number_string'))
            yield '</td>'
            l_1_ns_sec = context.call((undefined(name='namespace') if l_1_namespace is missing else l_1_namespace), past_title=False, _loop_vars=_loop_vars)
            _loop_vars['ns_sec'] = l_1_ns_sec
            for l_2_column in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'enumerate_table_columns'), _loop_vars=_loop_vars):
                _loop_vars = {}
                pass
                if environment.getattr((undefined(name='ns_sec') if l_1_ns_sec is missing else l_1_ns_sec), 'past_title'):
                    pass
                elif (l_2_column == 'TITLE'):
                    pass
                    if not isinstance(l_1_ns_sec, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_1_ns_sec['past_title'] = True
                    yield '\n          <td class="content-view-td content-view-td-title" colspan="'
                    yield escape((environment.getattr((undefined(name='ns_span') if l_1_ns_span is missing else l_1_ns_span), 'count') if (environment.getattr((undefined(name='ns_span') if l_1_ns_span is missing else l_1_ns_span), 'count') > 0) else 1))
                    yield '">'
                    if environment.getattr((undefined(name='section') if l_1_section is missing else l_1_section), 'title'):
                        pass
                        l_3_sdoc_entity = (undefined(name='section') if l_1_section is missing else l_1_section)
                        pass
                        template = environment.get_template('components/anchor/index.jinja', 'screens/document/table/body.jinja')
                        gen = template.root_render_func(template.new_context(context.get_all(), True, {'sdoc_entity': l_3_sdoc_entity, 'column': l_2_column, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                        try:
                            for event in gen:
                                yield event
                        finally: gen.close()
                        l_3_sdoc_entity = missing
                        yield '\n              <sdoc-node-title>'
                        l_3_field_content = environment.getattr((undefined(name='section') if l_1_section is missing else l_1_section), 'title')
                        pass
                        template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'screens/document/table/body.jinja')
                        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_3_field_content, 'column': l_2_column, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                        try:
                            for event in gen:
                                yield event
                        finally: gen.close()
                        l_3_field_content = missing
                        yield '</sdoc-node-title>'
                    yield '</td>'
                else:
                    pass
                    yield '\n          <td class="content-view-td content-view-td-meta"></td>'
            l_2_column = missing
            yield '\n\n    </tr>'
            if (undefined(name='is_server') if l_0_is_server is missing else l_0_is_server):
                pass
                l_2_prev_node = l_1_node
                l_2_next_node = (environment.getitem(environment.getattr(l_1_loop, 'nextitem'), 0) if t_1(environment.getattr(l_1_loop, 'nextitem')) else None)
                pass
                template = environment.get_template('screens/document/table/row_add_new_node.jinja', 'screens/document/table/body.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'next_node': l_2_next_node, 'prev_node': l_2_prev_node, '_': l_1__, 'loop': l_1_loop, 'node': l_1_node, 'ns': l_1_ns, 'ns_sec': l_1_ns_sec, 'ns_span': l_1_ns_span, 'requirement': l_1_requirement, 'section': l_1_section, 'is_server': l_0_is_server}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_prev_node = l_2_next_node = missing
    l_1_loop = l_1_node = l_1__ = l_1_requirement = l_1_namespace = l_1_ns = l_1_section = l_1_ns_span = l_1_ns_sec = missing
    yield '\n</tbody>'

blocks = {}
debug_info = '1=20&4=24&14=27&19=32&23=40&28=50&29=52&30=55&32=59&33=65&35=71&36=73&38=80&39=84&40=85&43=88&44=91&47=93&50=96&51=100&52=102&62=112&63=116&64=117&67=120&68=123&71=125&74=128&75=132&76=134&78=138&81=147&93=158&94=162&95=163&98=166&99=169&102=171&105=174&106=178&107=180&109=184&121=195&122=199&123=200&126=203&127=206&130=208&133=211&134=215&135=217&137=221&149=232&150=236&151=237&154=240&155=243&158=245&161=248&162=252&163=254&165=259&178=273&179=275&180=277&181=279&182=281&184=285&186=287&193=295&198=300&205=308&206=310&207=312&208=314&209=317&210=321&212=322&213=326&217=329&219=333&221=341&223=343&224=345&225=348&226=350&227=354&228=356&229=358&231=362&235=372&247=386&252=391'