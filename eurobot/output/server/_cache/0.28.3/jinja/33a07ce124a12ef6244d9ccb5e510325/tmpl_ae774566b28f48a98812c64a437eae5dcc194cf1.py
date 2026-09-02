from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/changelog_content.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0__documents_modified = resolve('_documents_modified')
    l_0_documents_modified = l_0_documents_included_modified = missing
    try:
        t_1 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '<div class="changelog_content">\n  <div class="sdoc-table_key_value">\n    '
    l_1_key_value_pair = {'Section': 'Compared revisions'}
    pass
    yield '\n      '
    template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    l_1_key_value_pair = missing
    yield '\n\n    '
    l_1_key_value_pair = {'Key': 'Left', 'Value': environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'left_revision')}
    pass
    yield '\n      '
    template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    l_1_key_value_pair = missing
    yield '\n\n    '
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'left_revision_tags'):
        pass
        yield '\n      '
        l_1_key_value_pair = {'Key': 'Left tags', 'Value': t_1(context.eval_ctx, environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'left_revision_tags'), ', ')}
        pass
        yield '\n        '
        template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n      '
        l_1_key_value_pair = missing
        yield '\n    '
    yield '\n\n    '
    l_1_key_value_pair = {'Key': 'Right', 'Value': environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'right_revision')}
    pass
    yield '\n      '
    template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    l_1_key_value_pair = missing
    yield '\n\n    '
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'right_revision_tags'):
        pass
        yield '\n      '
        l_1_key_value_pair = {'Key': 'Right tags', 'Value': t_1(context.eval_ctx, environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'right_revision_tags'), ', ')}
        pass
        yield '\n        '
        template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n      '
        l_1_key_value_pair = missing
        yield '\n    '
    yield '\n\n    '
    l_1_key_value_pair = {'Section': 'Summary of the changes'}
    pass
    yield '\n      '
    template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    l_1_key_value_pair = missing
    yield '\n\n    '
    l_1_key_value_pair = {'Key': 'Nodes modified', 'Value': context.call(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'change_stats'), 'get_total_changes'))}
    pass
    yield '\n      '
    template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    l_1_key_value_pair = missing
    yield '\n\n    '
    l_0_documents_modified = context.call(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'change_stats'), 'get_changes_documents_modified'))
    context.vars['documents_modified'] = l_0_documents_modified
    context.exported_vars.add('documents_modified')
    yield '\n    '
    if ((undefined(name='documents_modified') if l_0_documents_modified is missing else l_0_documents_modified) > 0):
        pass
        yield '\n        '
        l_0__documents_modified = (undefined(name='documents_modified') if l_0_documents_modified is missing else l_0_documents_modified)
        context.vars['_documents_modified'] = l_0__documents_modified
        yield '\n    '
    else:
        pass
        yield '\n        '
        l_0__documents_modified = 'No documents were modified.'
        context.vars['_documents_modified'] = l_0__documents_modified
        yield '\n    '
    yield '\n    '
    l_1_key_value_pair = {'Key': 'Documents modified', 'Value': (undefined(name='_documents_modified') if l_0__documents_modified is missing else l_0__documents_modified)}
    pass
    yield '\n      '
    template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    l_1_key_value_pair = missing
    yield '\n\n    '
    l_0_documents_included_modified = context.call(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'change_stats'), 'get_changes_included_documents_modified'))
    context.vars['documents_included_modified'] = l_0_documents_included_modified
    context.exported_vars.add('documents_included_modified')
    yield '\n    '
    if ((undefined(name='documents_included_modified') if l_0_documents_included_modified is missing else l_0_documents_included_modified) > 0):
        pass
        yield '\n        '
        l_1_key_value_pair = {'Key': 'DOCUMENT (included) nodes', 'Value': (undefined(name='documents_included_modified') if l_0_documents_included_modified is missing else l_0_documents_included_modified)}
        pass
        yield '\n          '
        template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_1_key_value_pair, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n        '
        l_1_key_value_pair = missing
        yield '\n    '
    yield '\n\n    '
    for l_1_node_type_ in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_node_types')):
        l_1__requirements_modified = resolve('_requirements_modified')
        l_1_requirements_modified = missing
        _loop_vars = {}
        pass
        yield '\n      '
        l_1_requirements_modified = context.call(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'change_stats'), 'get_changes_requirements_changed'), l_1_node_type_, _loop_vars=_loop_vars)
        _loop_vars['requirements_modified'] = l_1_requirements_modified
        yield '\n      '
        if (not t_2((undefined(name='requirements_modified') if l_1_requirements_modified is missing else l_1_requirements_modified))):
            pass
            yield '\n        '
            l_1__requirements_modified = markup_join(((undefined(name='requirements_modified') if l_1_requirements_modified is missing else l_1_requirements_modified), ' (', context.call(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'change_stats'), 'get_changes_requirements_stats_string'), l_1_node_type_, _loop_vars=_loop_vars), ')', ))
            _loop_vars['_requirements_modified'] = l_1__requirements_modified
            yield '\n      '
        else:
            pass
            yield '\n        '
            l_1__requirements_modified = 'No nodes were modified.'
            _loop_vars['_requirements_modified'] = l_1__requirements_modified
            yield '\n      '
        yield '\n\n      '
        l_2_key_value_pair = {'Key': markup_join((l_1_node_type_, ' nodes', )), 'Value': (undefined(name='_requirements_modified') if l_1__requirements_modified is missing else l_1__requirements_modified)}
        pass
        yield '\n        '
        template = environment.get_template('components/table_key_value/index.jinja', 'features/diff_and_changelog/changelog_content.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_2_key_value_pair, '_requirements_modified': l_1__requirements_modified, 'node_type_': l_1_node_type_, 'requirements_modified': l_1_requirements_modified, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n      '
        l_2_key_value_pair = missing
        yield '\n    '
    l_1_node_type_ = l_1_requirements_modified = l_1__requirements_modified = missing
    yield '\n  </div>\n\n  <div class="changelog_changes">\n    '
    l_1_loop = missing
    for l_1_change, l_1_loop in LoopContext(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'change_stats'), 'changes'), undefined):
        l_1__change_type = missing
        _loop_vars = {}
        pass
        yield '\n    <div class="changelog_change">\n      <div class="changelog_change_meta">\n        <span class="changelog_change_num"># '
        yield escape(environment.getattr(l_1_loop, 'index'))
        yield '</span>\n        '
        l_1__change_type = context.call(environment.getattr(environment.getattr(environment.getattr(l_1_change, 'change_type'), 'value'), 'split'), ' ', _loop_vars=_loop_vars)
        _loop_vars['_change_type'] = l_1__change_type
        yield '\n        \n        <span class="changelog_change_type '
        yield escape(environment.getitem((undefined(name='_change_type') if l_1__change_type is missing else l_1__change_type), 1))
        yield '">'
        yield escape(environment.getattr(environment.getattr(l_1_change, 'change_type'), 'value'))
        yield '</span>\n      </div>\n      <div class="changelog_change_node">\n        '
        if ((environment.getattr(l_1_change, 'change_type') == 'Node added') or (environment.getattr(l_1_change, 'change_type') == 'Section added')):
            pass
            yield '\n          <div class="changelog_node_null">'
            yield escape(environment.getattr(environment.getattr(l_1_change, 'change_type'), 'value'))
            yield '</div>\n        '
        elif ((environment.getattr(l_1_change, 'change_type') == 'Node removed') or (environment.getattr(l_1_change, 'change_type') == 'Node modified')):
            pass
            yield '\n          '
            l_2_requirement_change = missing
            l_2_requirement = environment.getattr(l_1_change, 'lhs_requirement')
            l_2_side = 'left'
            l_2_self_stats = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'lhs_stats')
            l_2_other_stats = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'rhs_stats')
            l_2_traceability_index = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'traceability_index_lhs')
            pass
            yield '\n            '
            l_2_requirement_change = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_stats'), 'find_change'), l_2_requirement)
            yield '\n            '
            template = environment.get_template('features/diff_and_changelog/fields/requirement_fields.jinja', 'features/diff_and_changelog/changelog_content.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'other_stats': l_2_other_stats, 'requirement': l_2_requirement, 'requirement_change': l_2_requirement_change, 'self_stats': l_2_self_stats, 'side': l_2_side, 'traceability_index': l_2_traceability_index, '_change_type': l_1__change_type, 'change': l_1_change, 'loop': l_1_loop, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n          '
            l_2_requirement = l_2_side = l_2_self_stats = l_2_other_stats = l_2_traceability_index = l_2_requirement_change = missing
            yield '\n        '
        elif (environment.getattr(l_1_change, 'change_type') == 'Document modified'):
            pass
            yield '\n          '
            if (not t_2(environment.getattr(l_1_change, 'lhs_document'))):
                pass
                yield '\n            '
                l_2_document = environment.getattr(l_1_change, 'lhs_document')
                l_2_side = 'left'
                l_2_self_stats = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'lhs_stats')
                l_2_other_stats = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'rhs_stats')
                l_2_traceability_index = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'traceability_index_lhs')
                pass
                yield '\n              '
                template = environment.get_template('features/diff_and_changelog/fields/document_fields.jinja', 'features/diff_and_changelog/changelog_content.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_2_document, 'other_stats': l_2_other_stats, 'self_stats': l_2_self_stats, 'side': l_2_side, 'traceability_index': l_2_traceability_index, '_change_type': l_1__change_type, 'change': l_1_change, 'loop': l_1_loop, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n            '
                l_2_document = l_2_side = l_2_self_stats = l_2_other_stats = l_2_traceability_index = missing
                yield '\n          '
            else:
                pass
                yield '\n            <div class="changelog_node_null"></div>\n          '
            yield '\n        '
        else:
            pass
            yield '\n          '
            def macro():
                t_3 = []
                pass
                return concat(t_3)
            caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
            yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, 0, 'Must not reach here.', caller=caller, _loop_vars=_loop_vars)
            yield '\n        '
        yield '\n      </div>\n      <div class="changelog_change_node">\n        '
        if ((environment.getattr(l_1_change, 'change_type') == 'Node removed') or (environment.getattr(l_1_change, 'change_type') == 'Section removed')):
            pass
            yield '\n          <div class="changelog_node_null">'
            yield escape(environment.getattr(environment.getattr(l_1_change, 'change_type'), 'value'))
            yield '</div>\n        '
        elif ((environment.getattr(l_1_change, 'change_type') == 'Node added') or (environment.getattr(l_1_change, 'change_type') == 'Node modified')):
            pass
            yield '\n          '
            l_2_requirement_change = missing
            l_2_requirement = environment.getattr(l_1_change, 'rhs_requirement')
            l_2_side = 'right'
            l_2_self_stats = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'rhs_stats')
            l_2_other_stats = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'lhs_stats')
            l_2_traceability_index = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'traceability_index_rhs')
            pass
            yield '\n            '
            l_2_requirement_change = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_stats'), 'find_change'), l_2_requirement)
            yield '\n            '
            template = environment.get_template('features/diff_and_changelog/fields/requirement_fields.jinja', 'features/diff_and_changelog/changelog_content.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'other_stats': l_2_other_stats, 'requirement': l_2_requirement, 'requirement_change': l_2_requirement_change, 'self_stats': l_2_self_stats, 'side': l_2_side, 'traceability_index': l_2_traceability_index, '_change_type': l_1__change_type, 'change': l_1_change, 'loop': l_1_loop, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n          '
            l_2_requirement = l_2_side = l_2_self_stats = l_2_other_stats = l_2_traceability_index = l_2_requirement_change = missing
            yield '\n        '
        elif (environment.getattr(l_1_change, 'change_type') == 'Document modified'):
            pass
            yield '\n          '
            if (not t_2(environment.getattr(l_1_change, 'rhs_document'))):
                pass
                yield '\n            '
                l_2_document = environment.getattr(l_1_change, 'rhs_document')
                l_2_side = 'right'
                l_2_self_stats = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'rhs_stats')
                l_2_other_stats = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'lhs_stats')
                l_2_traceability_index = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_container'), 'traceability_index_rhs')
                pass
                yield '\n              '
                template = environment.get_template('features/diff_and_changelog/fields/document_fields.jinja', 'features/diff_and_changelog/changelog_content.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_2_document, 'other_stats': l_2_other_stats, 'self_stats': l_2_self_stats, 'side': l_2_side, 'traceability_index': l_2_traceability_index, '_change_type': l_1__change_type, 'change': l_1_change, 'loop': l_1_loop, '_documents_modified': l_0__documents_modified, 'documents_included_modified': l_0_documents_included_modified, 'documents_modified': l_0_documents_modified}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n            '
                l_2_document = l_2_side = l_2_self_stats = l_2_other_stats = l_2_traceability_index = missing
                yield '\n          '
            else:
                pass
                yield '\n            <div class="changelog_node_null"></div>\n          '
            yield '\n        '
        else:
            pass
            yield '\n          '
            def macro():
                t_4 = []
                pass
                return concat(t_4)
            caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
            yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, 0, 'Must not reach here.', caller=caller, _loop_vars=_loop_vars)
            yield '\n        '
        yield '\n      </div>\n    </div>\n    '
    l_1_loop = l_1_change = l_1__change_type = missing
    yield '\n  </div>\n</div>'

blocks = {}
debug_info = '6=30&15=42&18=51&25=57&35=70&38=79&45=85&52=98&61=110&64=119&65=123&66=126&68=132&76=139&79=148&80=152&87=158&91=168&92=174&93=177&94=180&96=186&105=193&111=205&114=210&115=212&117=215&120=219&121=222&122=224&124=235&125=237&127=246&128=249&130=259&136=275&140=283&141=286&142=288&144=299&145=301&147=310&148=313&150=323&156=339'