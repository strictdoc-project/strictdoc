from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/button/cancel.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_cancel_href = resolve('cancel_href')
    l_0_cancel_name = resolve('cancel_name')
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
    if t_2((undefined(name='cancel_href') if l_0_cancel_href is missing else l_0_cancel_href)):
        pass
        yield '<a\n    href="'
        yield escape((undefined(name='cancel_href') if l_0_cancel_href is missing else l_0_cancel_href))
        yield '"\n    class="action_button"\n    data-turbo="true"\n    data-action-type="cancel"\n    data-testid="form-cancel-action"\n  >'
        yield escape(t_1((undefined(name='cancel_name') if l_0_cancel_name is missing else l_0_cancel_name), 'Cancel'))
        yield '</a>'
    else:
        pass
        yield '<button\n    data-js-modal-cancel-button\n    type="button"\n    class="action_button"\n    data-action-type="cancel"\n    data-testid="form-cancel-action"\n  >'
        yield escape(t_1((undefined(name='cancel_name') if l_0_cancel_name is missing else l_0_cancel_name), 'Cancel'))
        yield '</button>'

blocks = {}
debug_info = '1=25&3=28&8=30&16=35'