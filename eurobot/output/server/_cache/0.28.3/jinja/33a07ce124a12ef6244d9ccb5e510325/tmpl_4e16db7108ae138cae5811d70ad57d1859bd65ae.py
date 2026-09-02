from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/button/submit.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_form = resolve('form')
    l_0_submit_name = resolve('submit_name')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    try:
        t_2 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    yield '\n<button\n  '
    if t_2((undefined(name='form') if l_0_form is missing else l_0_form)):
        pass
        yield '\n    form="'
        yield escape((undefined(name='form') if l_0_form is missing else l_0_form))
        yield '"\n  '
    yield '\n  data-turbo="true"\n  class="action_button"\n  type="submit"\n  data-action-type="submit"\n  data-testid="form-submit-action"\n>'
    template = environment.get_template('icons/ico16_submit_animated.svg', 'components/button/submit.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield escape(t_1((undefined(name='submit_name') if l_0_submit_name is missing else l_0_submit_name), 'Save'))
    yield '</button>'

blocks = {}
debug_info = '6=26&7=29&14=32'