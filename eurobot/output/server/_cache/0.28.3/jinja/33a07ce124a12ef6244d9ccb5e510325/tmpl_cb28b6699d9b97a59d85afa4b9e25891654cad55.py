from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/frame_changelog_result.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<turbo-frame id="diff_result">\n'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'results'):
        pass
        yield '\n  <div class="changelog preloaded">'
        l_1_tab = 'changelog'
        pass
        template = environment.get_template('features/diff_and_changelog/changelog_content.jinja', 'features/diff_and_changelog/frame_changelog_result.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'tab': l_1_tab}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_tab = missing
        yield '</div>\n'
    yield '\n</turbo-frame>'

blocks = {}
debug_info = '2=13&6=18'