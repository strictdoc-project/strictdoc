from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_coverage/folder.jinja'

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
    yield '\n\n<tr class="project_coverage-folder">\n  <td colspan="99" style="padding-left:'
    yield escape(environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'level'))
    yield '0px">\n    <div class="project_coverage-folder-title">'
    template = environment.get_template('icons/ico16_folder.svg', 'features/source_coverage/folder.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield escape(environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'folder_name'))
    yield '/\n      \n    </div>\n\n  </td>\n</tr>\n\n'
    for l_1_folder_ in environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'subfolder_trees'):
        _loop_vars = {}
        pass
        yield '\n  '
        if context.call(environment.getattr(l_1_folder_, 'has_content'), _loop_vars=_loop_vars):
            pass
            yield '\n  '
            l_2_folder = l_1_folder_
            pass
            yield '\n    '
            template = environment.get_template('features/source_coverage/folder.jinja', 'features/source_coverage/folder.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'folder': l_2_folder, 'folder_': l_1_folder_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n  '
            l_2_folder = missing
            yield '\n  '
        yield '\n'
    l_1_folder_ = missing
    yield '\n\n'
    for l_1_file_ in environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'files'):
        _loop_vars = {}
        pass
        yield '\n  '
        l_2_file = l_1_file_
        pass
        yield '\n    '
        template = environment.get_template('features/source_coverage/file.jinja', 'features/source_coverage/folder.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'file': l_2_file, 'file_': l_1_file_}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  '
        l_2_file = missing
        yield '\n'
    l_1_file_ = missing

blocks = {}
debug_info = '1=18&4=25&6=27&7=33&14=35&15=39&17=45&22=57&24=64'