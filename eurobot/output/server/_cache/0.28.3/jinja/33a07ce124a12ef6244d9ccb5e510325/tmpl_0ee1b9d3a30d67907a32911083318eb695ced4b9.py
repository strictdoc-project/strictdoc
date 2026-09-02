from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/issue/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_issue = resolve('issue')
    pass
    yield '<div id="field_issue_ID" class="field_issue">\n  <div class="field_issue-ribbon">\n    '
    yield escape((undefined(name='issue') if l_0_issue is missing else l_0_issue))
    yield '\n  </div>\n</div>'

blocks = {}
debug_info = '3=13'