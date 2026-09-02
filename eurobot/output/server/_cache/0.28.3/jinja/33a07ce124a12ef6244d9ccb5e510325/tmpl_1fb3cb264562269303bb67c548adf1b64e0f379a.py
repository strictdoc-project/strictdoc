from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/diff_content.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_document_tree_iterator = resolve('document_tree_iterator')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    if (not context.call(environment.getattr((undefined(name='document_tree_iterator') if l_0_document_tree_iterator is missing else l_0_document_tree_iterator), 'is_empty_tree'))):
        pass
        yield '<div class="diff_content">'
        for l_1_folder_or_file in context.call(environment.getattr((undefined(name='document_tree_iterator') if l_0_document_tree_iterator is missing else l_0_document_tree_iterator), 'iterator_files_first')):
            l_1_document_tree = resolve('document_tree')
            l_1_document = resolve('document')
            l_1_self_stats = resolve('self_stats')
            l_1_document_md5 = resolve('document_md5')
            l_1_other_stats = resolve('other_stats')
            l_1_document_modified = resolve('document_modified')
            l_1_side = resolve('side')
            l_1_traceability_index = resolve('traceability_index')
            l_1_document_iterator = resolve('document_iterator')
            _loop_vars = {}
            pass
            if context.call(environment.getattr(l_1_folder_or_file, 'is_folder'), _loop_vars=_loop_vars):
                pass
                if (t_1(environment.getattr(l_1_folder_or_file, 'files')) > 0):
                    pass
                    yield '\n          <div\n            class="diff_folder"\n            data-level="'
                    yield escape(environment.getattr(l_1_folder_or_file, 'level'))
                    yield '"\n            data-testid="tree-folder-item"\n          >'
                    template = environment.get_template('icons/_separator.svg', 'features/diff_and_changelog/diff_content.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_1_document, 'document_iterator': l_1_document_iterator, 'document_md5': l_1_document_md5, 'document_modified': l_1_document_modified, 'folder_or_file': l_1_folder_or_file}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    yield escape(environment.getattr(l_1_folder_or_file, 'rel_path'))
                    yield '</div>\n        '
                yield '\n      '
            elif context.call(environment.getattr(l_1_folder_or_file, 'has_extension'), '.sdoc', _loop_vars=_loop_vars):
                pass
                l_1_document = context.call(environment.getattr((undefined(name='document_tree') if l_1_document_tree is missing else l_1_document_tree), 'get_document_by_path'), environment.getattr(l_1_folder_or_file, 'full_path'), _loop_vars=_loop_vars)
                _loop_vars['document'] = l_1_document
                yield '\n        '
                if (not context.call(environment.getattr((undefined(name='document') if l_1_document is missing else l_1_document), 'document_is_included'), _loop_vars=_loop_vars)):
                    pass
                    yield '\n        '
                    l_1_document_md5 = context.call(environment.getattr((undefined(name='self_stats') if l_1_self_stats is missing else l_1_self_stats), 'get_md5_by_node'), (undefined(name='document') if l_1_document is missing else l_1_document), _loop_vars=_loop_vars)
                    _loop_vars['document_md5'] = l_1_document_md5
                    yield '\n        '
                    l_1_document_modified = (not context.call(environment.getattr((undefined(name='other_stats') if l_1_other_stats is missing else l_1_other_stats), 'contains_document_md5'), (undefined(name='document_md5') if l_1_document_md5 is missing else l_1_document_md5), _loop_vars=_loop_vars))
                    _loop_vars['document_modified'] = l_1_document_modified
                    yield '\n\n        <details\n          class="diff_document"\n          '
                    if (undefined(name='document_modified') if l_1_document_modified is missing else l_1_document_modified):
                        pass
                        yield '\n            modified="'
                        yield escape((undefined(name='side') if l_1_side is missing else l_1_side))
                        yield '"\n          '
                    yield '\n        >\n          '
                    if (undefined(name='document_modified') if l_1_document_modified is missing else l_1_document_modified):
                        pass
                        yield '\n            \n          '
                    yield '\n          <summary>\n            '
                    template = environment.get_template('icons/ico16_document.svg', 'features/diff_and_changelog/diff_content.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_1_document, 'document_iterator': l_1_document_iterator, 'document_md5': l_1_document_md5, 'document_modified': l_1_document_modified, 'folder_or_file': l_1_folder_or_file}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    yield '\n            <span class="document_title">'
                    yield escape(environment.getattr((undefined(name='document') if l_1_document is missing else l_1_document), 'title'))
                    yield '</span>\n          </summary>\n\n            '
                    template = environment.get_template('features/diff_and_changelog/fields/document_fields.jinja', 'features/diff_and_changelog/diff_content.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_1_document, 'document_iterator': l_1_document_iterator, 'document_md5': l_1_document_md5, 'document_modified': l_1_document_modified, 'folder_or_file': l_1_folder_or_file}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    l_1_document_iterator = context.call(environment.getattr((undefined(name='traceability_index') if l_1_traceability_index is missing else l_1_traceability_index), 'get_document_iterator'), (undefined(name='document') if l_1_document is missing else l_1_document), _loop_vars=_loop_vars)
                    _loop_vars['document_iterator'] = l_1_document_iterator
                    for (l_2_section_or_requirement, l_2__) in context.call(environment.getattr((undefined(name='document_iterator') if l_1_document_iterator is missing else l_1_document_iterator), 'all_content'), print_fragments=True, _loop_vars=_loop_vars):
                        l_2_requirement = resolve('requirement')
                        _loop_vars = {}
                        pass
                        yield '\n                '
                        if context.call(environment.getattr(l_2_section_or_requirement, 'is_document_node'), _loop_vars=_loop_vars):
                            pass
                            yield '\n                    '
                            l_3_document = l_2_section_or_requirement
                            pass
                            yield '\n                        '
                            template = environment.get_template('features/diff_and_changelog/node/document.jinja', 'features/diff_and_changelog/diff_content.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_3_document, '_': l_2__, 'requirement': l_2_requirement, 'section_or_requirement': l_2_section_or_requirement, 'document_iterator': l_1_document_iterator, 'document_md5': l_1_document_md5, 'document_modified': l_1_document_modified, 'folder_or_file': l_1_folder_or_file}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            yield '\n                    '
                            l_3_document = missing
                            yield '\n                '
                        else:
                            pass
                            l_2_requirement = l_2_section_or_requirement
                            _loop_vars['requirement'] = l_2_requirement
                            yield '\n                    '
                            template = environment.get_template('features/diff_and_changelog/node/requirement.jinja', 'features/diff_and_changelog/diff_content.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'_': l_2__, 'requirement': l_2_requirement, 'section_or_requirement': l_2_section_or_requirement, 'document': l_1_document, 'document_iterator': l_1_document_iterator, 'document_md5': l_1_document_md5, 'document_modified': l_1_document_modified, 'folder_or_file': l_1_folder_or_file}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            yield '\n                '
                    l_2_section_or_requirement = l_2__ = l_2_requirement = missing
                    yield '</details>\n        '
                yield '\n      '
        l_1_folder_or_file = l_1_document_tree = l_1_document = l_1_self_stats = l_1_document_md5 = l_1_other_stats = l_1_document_modified = l_1_side = l_1_traceability_index = l_1_document_iterator = missing
        yield '</div>'
    else:
        pass
        yield '<span data-testid="document-tree-empty-text">🌚 The project has no documents yet.</span>'

blocks = {}
debug_info = '2=18&4=21&5=33&6=35&9=38&11=40&13=49&14=51&15=54&16=57&17=60&21=63&22=66&25=69&29=73&30=80&33=82&35=88&36=90&37=95&39=101&42=112&43=115'