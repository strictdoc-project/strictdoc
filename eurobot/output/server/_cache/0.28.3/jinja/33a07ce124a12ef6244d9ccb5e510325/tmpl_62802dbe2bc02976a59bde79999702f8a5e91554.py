from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/project_map_folder.jinja'

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
    for l_1_folder_ in environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'subfolder_trees'):
        _loop_vars = {}
        pass
        if environment.getattr(l_1_folder_, 'has_sdoc_content'):
            pass
            l_2_folder = l_1_folder_
            pass
            template = environment.get_template('features/project_index/project_map_folder.jinja', 'features/project_index/project_map_folder.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'folder': l_2_folder, 'folder_': l_1_folder_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_folder = missing
    l_1_folder_ = missing
    for l_1_file_ in environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'files'):
        _loop_vars = {}
        pass
        if context.call(environment.getattr(l_1_file_, 'has_extension'), '.sdoc', _loop_vars=_loop_vars):
            pass
            l_2_file = l_1_file_
            pass
            template = environment.get_template('features/project_index/project_map_file.jinja', 'features/project_index/project_map_folder.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'file': l_2_file, 'file_': l_1_file_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_file = missing
    l_1_file_ = missing

blocks = {}
debug_info = '1=18&2=24&3=27&5=31&9=39&10=42&12=46'