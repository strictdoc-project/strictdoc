from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/project_tree_folder.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_folder = resolve('folder')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='folder') if l_0_folder is missing else l_0_folder)), None, caller=caller)
    yield '\n\n<details open class="project_tree-folder">\n  <summary>\n    <div class="project_tree-folder-title">'
    template = environment.get_template('icons/ico16_folder.svg', 'features/project_index/project_tree_folder.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield escape(environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'folder_name'))
    yield '/'
    template = environment.get_template('icons/ico16_folder_collapse.svg', 'features/project_index/project_tree_folder.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</div>\n  </summary>\n\n  <div class="project_tree-folder-content">\n    '
    for l_1_folder_ in environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'subfolder_trees'):
        l_1_view_object = resolve('view_object')
        _loop_vars = {}
        pass
        yield '\n      '
        if context.call(environment.getattr((undefined(name='view_object') if l_1_view_object is missing else l_1_view_object), 'should_display_folder'), l_1_folder_, _loop_vars=_loop_vars):
            pass
            yield '\n        '
            l_2_folder = l_1_folder_
            pass
            yield '\n          '
            template = environment.get_template('features/project_index/project_tree_folder.jinja', 'features/project_index/project_tree_folder.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'folder': l_2_folder, 'folder_': l_1_folder_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n        '
            l_2_folder = missing
            yield '\n      '
        yield '\n    '
    l_1_folder_ = l_1_view_object = missing
    yield '\n\n    '
    for l_1_file_ in environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'files'):
        l_1_view_object = resolve('view_object')
        _loop_vars = {}
        pass
        yield '\n      '
        if context.call(environment.getattr((undefined(name='view_object') if l_1_view_object is missing else l_1_view_object), 'should_display_file'), l_1_file_, _loop_vars=_loop_vars):
            pass
            yield '\n        '
            l_2_file = l_1_file_
            pass
            yield '\n          '
            template = environment.get_template('features/project_index/project_tree_file.jinja', 'features/project_index/project_tree_folder.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'file': l_2_file, 'file_': l_1_file_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n        '
            l_2_file = missing
            yield '\n      '
        yield '\n    '
    l_1_file_ = l_1_view_object = missing
    yield '\n  </div>\n</details>'

blocks = {}
debug_info = '1=18&6=25&7=31&8=33&13=40&14=45&16=51&21=63&22=68&24=74'