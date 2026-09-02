from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_submit_url = resolve('submit_url')
    l_0_cancel_url = resolve('cancel_url')
    l_0_frame_id = resolve('frame_id')
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
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='submit_url') if l_0_submit_url is missing else l_0_submit_url)), 'submit_url must be defined.', caller=caller)
    yield '\n'
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='cancel_url') if l_0_cancel_url is missing else l_0_cancel_url)), 'cancel_url must be defined.', caller=caller)
    yield '\n'
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='frame_id') if l_0_frame_id is missing else l_0_frame_id)), 'frame_id must be defined.', caller=caller)
    yield '\n\n<turbo-frame id="'
    yield escape((undefined(name='frame_id') if l_0_frame_id is missing else l_0_frame_id))
    yield '">\n\n<sdoc-form>\n\n<form\n  action="'
    yield escape((undefined(name='submit_url') if l_0_submit_url is missing else l_0_submit_url))
    yield '"\n  method="POST"\n  data-turbo="true"\n  data-js-tabs\n  data-js-scroll-into-view\n>\n\n  <sdoc-form-grid>\n\n    '
    yield from context.blocks['form_content'][0](context)
    yield '\n\n  </sdoc-form-grid>\n\n  <sdoc-form-footer>\n    '
    template = environment.get_template('components/button/submit.jinja', 'components/form/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_cancel_href = (undefined(name='cancel_url') if l_0_cancel_url is missing else l_0_cancel_url)
    pass
    template = environment.get_template('components/button/cancel.jinja', 'components/form/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'cancel_href': l_1_cancel_href}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_cancel_href = missing
    yield '</sdoc-form-footer>\n</form>\n\n</sdoc-form>\n</turbo-frame>'

def block_form_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n      '
    def macro():
        t_5 = []
        pass
        return concat(t_5)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, 0, 'Must not reach here!', caller=caller, _block_vars=_block_vars)
    yield '\n    '

blocks = {'form_content': block_form_content}
debug_info = '1=20&2=27&3=34&5=41&10=43&19=45&26=47&29=55&19=64&20=73'