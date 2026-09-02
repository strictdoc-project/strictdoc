from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, (environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'tab') in ('diff', 'changelog')), None, caller=caller)
    yield '\n\n<div class="main">\n\n  <div class="main_sticky_header">\n    '
    template = environment.get_template('features/diff_and_changelog/form.jinja', 'features/diff_and_changelog/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    template = environment.get_template('features/diff_and_changelog/nav_tabs.jinja', 'features/diff_and_changelog/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </div>\n\n  '
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '\n    '
        if ((((t_2(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'error_message')) and (not t_2(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'left_revision')))) and (not t_2(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'right_revision')))) and (t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'left_revision')) > 0)) and (t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'right_revision')) > 0)):
            pass
            yield '\n      <turbo-frame id="diff_result" src="/diff_result?tab='
            yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'tab'))
            yield '&left_revision='
            yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'left_revision_urlencoded'))
            yield '&right_revision='
            yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'right_revision_urlencoded'))
            yield '">\n      '
            template = environment.get_template('features/diff_and_changelog/skeleton.jinja', 'features/diff_and_changelog/main.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n      </turbo-frame>\n    '
        else:
            pass
            yield '\n      '
            template = environment.get_template('features/diff_and_changelog/legend.jinja', 'features/diff_and_changelog/main.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n    '
        yield '\n  '
    else:
        pass
        yield '\n    '
        template = environment.get_or_select_template(markup_join(('features/diff_and_changelog/frame_', environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'tab'), '_result.jinja', )), 'features/diff_and_changelog/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  '
    yield '\n\n</div>'

blocks = {}
debug_info = '1=24&6=31&7=38&10=45&11=48&12=51&13=57&16=67&19=78'