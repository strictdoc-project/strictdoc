from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/sync/button.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_uid = resolve('uid')
    l_0_side = resolve('side')
    pass
    yield '<button\n  uid="'
    yield escape((undefined(name='uid') if l_0_uid is missing else l_0_uid))
    yield '"\n  side="'
    yield escape((undefined(name='side') if l_0_side is missing else l_0_side))
    yield '"\n  style="margin-left: auto;"\n  class="action_icon diff_scroll_positioned"\n  data-testid="diff-"\n><a-a style="position:absolute;top:-40px;"></a-a>'
    template = environment.get_template('icons/ico16_sync.svg', 'features/diff_and_changelog/sync/button.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</button>'

blocks = {}
debug_info = '2=14&3=16&9=18'