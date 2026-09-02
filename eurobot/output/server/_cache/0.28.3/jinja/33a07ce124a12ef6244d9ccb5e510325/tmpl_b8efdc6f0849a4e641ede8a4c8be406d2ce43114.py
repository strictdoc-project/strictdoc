from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/project_map.jinja.js'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '// map of the project for the stable_uri forwarder\nwindow.StrictDoc = window.StrictDoc || {};\nwindow.StrictDoc.project = window.StrictDoc.project || {};\nwindow.StrictDoc.project.map = {'
    for l_1_root_tree_ in environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_tree_iterator'), 'document_tree'), 'file_tree'):
        _loop_vars = {}
        pass
        if context.call(environment.getattr(environment.getattr(l_1_root_tree_, 'root_folder_or_file'), 'is_folder'), _loop_vars=_loop_vars):
            pass
            if environment.getattr(environment.getattr(l_1_root_tree_, 'root_folder_or_file'), 'has_sdoc_content'):
                pass
                l_2_folder = environment.getattr(l_1_root_tree_, 'root_folder_or_file')
                pass
                template = environment.get_template('features/project_index/project_map_folder.jinja', 'features/project_index/project_map.jinja.js')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'folder': l_2_folder, 'root_tree_': l_1_root_tree_}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_folder = missing
        else:
            pass
            l_2_file = environment.getattr(l_1_root_tree_, 'root_folder_or_file')
            pass
            template = environment.get_template('features/project_index/project_map_file.jinja', 'features/project_index/project_map.jinja.js')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'file': l_2_file, 'root_tree_': l_1_root_tree_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_file = missing
    l_1_root_tree_ = missing
    yield '\n};'

blocks = {}
debug_info = '5=13&6=16&7=18&9=22&14=33'