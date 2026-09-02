from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/button/diff.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_form = resolve('form')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    yield '\n'
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'), None, caller=caller)
    yield '\n<button\n  '
    if t_1((undefined(name='form') if l_0_form is missing else l_0_form)):
        pass
        yield '\n    form="'
        yield escape((undefined(name='form') if l_0_form is missing else l_0_form))
        yield '"\n  '
    yield '\n  data-turbo="true"\n  title="See the diff"\n  class="action_icon"\n  type="submit"\n  data-action-type="submit"\n  data-testid="form-submit-action"\n>'
    template = environment.get_template('icons/ico16_diff.svg', 'components/button/diff.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</button>\n'

blocks = {}
debug_info = '5=20&7=27&8=30&16=33'