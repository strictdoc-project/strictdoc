from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/button/delete.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_delete_href = resolve('delete_href')
    l_0_delete_name = resolve('delete_name')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    pass
    yield '<a\n  href="'
    yield escape((undefined(name='delete_href') if l_0_delete_href is missing else l_0_delete_href))
    yield '"\n  class="action_button"\n  data-turbo="true"\n  data-turbo-method="delete"\n  data-action-type="delete"\n  data-testid="form-delete-action"\n>'
    yield escape(t_1((undefined(name='delete_name') if l_0_delete_name is missing else l_0_delete_name), 'Delete'))
    yield '</a>'

blocks = {}
debug_info = '2=20&8=22'