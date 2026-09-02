from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_coverage/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_root_tree_ = missing
    pass
    yield '\n\n<div class="main">\n  '
    l_0_root_tree_ = environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'document_tree'), 'source_tree'), 'file_tree')
    context.vars['root_tree_'] = l_0_root_tree_
    context.exported_vars.add('root_tree_')
    yield '\n\n  '
    if context.call(environment.getattr(environment.getattr((undefined(name='root_tree_') if l_0_root_tree_ is missing else l_0_root_tree_), 'root_folder_or_file'), 'has_content')):
        pass
        yield '\n\n    <table class="project_coverage" js-project_coverage>\n      '
        template = environment.get_template('features/source_coverage/thead.jinja', 'features/source_coverage/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'root_tree_': l_0_root_tree_}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n      <tbody>\n        '
        if context.call(environment.getattr(environment.getattr((undefined(name='root_tree_') if l_0_root_tree_ is missing else l_0_root_tree_), 'root_folder_or_file'), 'is_folder')):
            pass
            yield '\n          '
            if context.call(environment.getattr(environment.getattr((undefined(name='root_tree_') if l_0_root_tree_ is missing else l_0_root_tree_), 'root_folder_or_file'), 'has_content')):
                pass
                yield '\n            '
                l_1_folder = environment.getattr((undefined(name='root_tree_') if l_0_root_tree_ is missing else l_0_root_tree_), 'root_folder_or_file')
                pass
                yield '\n              '
                template = environment.get_template('features/source_coverage/folder.jinja', 'features/source_coverage/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'folder': l_1_folder, 'root_tree_': l_0_root_tree_}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n            '
                l_1_folder = missing
                yield '\n          '
            yield '\n        '
        else:
            pass
            yield '\n          '
            l_1_file = environment.getattr((undefined(name='root_tree_') if l_0_root_tree_ is missing else l_0_root_tree_), 'root_folder_or_file')
            pass
            yield '\n            '
            template = environment.get_template('features/source_coverage/file.jinja', 'features/source_coverage/main.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'file': l_1_file, 'root_tree_': l_0_root_tree_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n          '
            l_1_file = missing
            yield '\n        '
        yield '\n      </tbody>\n    </table>'
    else:
        pass
        yield '<span data-testid="document-tree-empty-text">The document tree has no documents yet.</span>'
    yield '</div>\n'

blocks = {}
debug_info = '17=14&19=18&22=21&24=28&25=31&27=37&32=53'