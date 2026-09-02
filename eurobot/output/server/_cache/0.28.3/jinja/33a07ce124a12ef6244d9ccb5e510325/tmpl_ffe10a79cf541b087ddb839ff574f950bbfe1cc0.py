from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/_shared/project_tree.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    try:
        t_1 = environment.filters['e']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'e' found.")
    pass
    if (not context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_empty_tree'))):
        pass
        yield '<div\n    class="tree"\n    js-project_tree_preserve_scroll="tree"\n    data-project-title="'
        yield escape(t_1(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'project_title')))
        yield '"\n    data-testid="aside-project-tree"\n  >\n    '
        for l_1_folder_or_file in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'iterator_files_first')):
            l_1_document_ = resolve('document_')
            _loop_vars = {}
            pass
            if context.call(environment.getattr(l_1_folder_or_file, 'is_folder'), _loop_vars=_loop_vars):
                pass
                yield '\n        '
                if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'should_display_folder'), l_1_folder_or_file, _loop_vars=_loop_vars):
                    pass
                    yield '\n          <div\n            class="tree_folder"\n            data-level="'
                    yield escape(environment.getattr(l_1_folder_or_file, 'level'))
                    yield '"\n            data-testid="tree-folder-item"\n          >\n          <span class="tree_folder_path">/'
                    yield escape(environment.getattr(l_1_folder_or_file, 'rel_path'))
                    yield '</span>\n          </div>\n        '
                yield '\n      '
            elif context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'should_display_file'), l_1_folder_or_file, _loop_vars=_loop_vars):
                pass
                l_1_document_ = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_document_by_path'), environment.getattr(l_1_folder_or_file, 'full_path'), _loop_vars=_loop_vars)
                _loop_vars['document_'] = l_1_document_
                yield '\n        '
                if (not context.call(environment.getattr((undefined(name='document_') if l_1_document_ is missing else l_1_document_), 'document_is_included'), _loop_vars=_loop_vars)):
                    pass
                    yield '\n        <a\n          href="'
                    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_current_view_document_link'), (undefined(name='document_') if l_1_document_ is missing else l_1_document_), _loop_vars=_loop_vars))
                    yield '"\n          class="tree_item"\n          '
                    if (environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document') == (undefined(name='document_') if l_1_document_ is missing else l_1_document_)):
                        pass
                        yield '\n          active="true"\n          '
                    yield '\n          data-folder="'
                    yield escape(environment.getattr(l_1_folder_or_file, 'mount_folder'))
                    yield '"\n          data-testid="tree-document-link"\n        >\n          '
                    template = environment.get_template('icons/ico16_document.svg', 'screens/document/_shared/project_tree.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'document_': l_1_document_, 'folder_or_file': l_1_folder_or_file}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    yield '\n          <div\n            class="document_title"\n            title="'
                    yield escape(environment.getattr((undefined(name='document_') if l_1_document_ is missing else l_1_document_), 'title'))
                    yield '"\n            data-file_name="'
                    yield escape(environment.getattr(l_1_folder_or_file, 'file_name'))
                    yield '"\n          >'
                    yield escape(environment.getattr((undefined(name='document_') if l_1_document_ is missing else l_1_document_), 'title'))
                    yield '</div>\n        </a>\n        '
                    l_2_document = (undefined(name='document_') if l_1_document_ is missing else l_1_document_)
                    pass
                    yield '\n        '
                    template = environment.get_template('screens/document/_shared/project_tree_child_documents.jinja', 'screens/document/_shared/project_tree.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_2_document, 'document_': l_1_document_, 'folder_or_file': l_1_folder_or_file}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    yield '\n        '
                    l_2_document = missing
                    yield '\n        '
                yield '\n      '
        l_1_folder_or_file = l_1_document_ = missing
        yield '</div>'
    else:
        pass
        yield '<span></span>\n  <span data-testid="document-tree-empty-text">🐛 The project has no documents yet.</span>'

blocks = {}
debug_info = '1=18&5=21&8=23&9=27&10=30&13=33&18=35&21=38&22=40&23=43&25=46&27=48&30=52&33=54&36=61&37=63&38=65&41=70'