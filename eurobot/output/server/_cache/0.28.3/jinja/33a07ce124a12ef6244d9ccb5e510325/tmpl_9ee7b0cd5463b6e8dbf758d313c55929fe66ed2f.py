from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/project_tree.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    if (not context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_empty_tree'))):
        pass
        yield '<div class="project_tree" js-collapsible_tree>\n    '
        for l_1_root_tree_ in environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_tree_iterator'), 'document_tree'), 'file_tree'):
            _loop_vars = {}
            pass
            yield '\n\n      '
            if context.call(environment.getattr(environment.getattr(l_1_root_tree_, 'root_folder_or_file'), 'is_folder'), _loop_vars=_loop_vars):
                pass
                yield '\n        '
                if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'should_display_folder'), environment.getattr(l_1_root_tree_, 'root_folder_or_file'), _loop_vars=_loop_vars):
                    pass
                    yield '\n          '
                    l_2_folder = environment.getattr(l_1_root_tree_, 'root_folder_or_file')
                    pass
                    yield '\n            '
                    template = environment.get_template('features/project_index/project_tree_folder.jinja', 'features/project_index/project_tree.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'folder': l_2_folder, 'root_tree_': l_1_root_tree_}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    yield '\n          '
                    l_2_folder = missing
                    yield '\n        '
                yield '\n      '
            else:
                pass
                yield '\n        '
                if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'should_display_file'), environment.getattr(l_1_root_tree_, 'root_folder_or_file'), _loop_vars=_loop_vars):
                    pass
                    yield '\n          '
                    l_2_file = environment.getattr(l_1_root_tree_, 'root_folder_or_file')
                    pass
                    yield '\n            '
                    template = environment.get_template('features/project_index/project_tree_file.jinja', 'features/project_index/project_tree.jinja')
                    gen = template.root_render_func(template.new_context(context.get_all(), True, {'file': l_2_file, 'root_tree_': l_1_root_tree_}))
                    try:
                        for event in gen:
                            yield event
                    finally: gen.close()
                    yield '\n          '
                    l_2_file = missing
                    yield '\n        '
                yield '\n      '
            yield '\n\n    '
        l_1_root_tree_ = missing
        yield '\n  </div>'
    else:
        pass
        yield '<span data-testid="document-tree-empty-text">The document tree has no documents yet.</span>'

blocks = {}
debug_info = '1=12&3=15&5=19&6=22&8=28&12=41&14=47'