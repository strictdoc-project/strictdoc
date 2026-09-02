from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/issue/banner.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_issues_number = missing
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    l_0_issues_number = 2
    context.vars['issues_number'] = l_0_issues_number
    context.exported_vars.add('issues_number')
    yield '\n\n<div class="document_issues-banner">\n  <details class="document_issues-banner_details">\n    <summary class="document_issues-banner_summary">\n      <div class="document_issues-banner_title">Document has\n        '
    if ((t_1((undefined(name='issues_number') if l_0_issues_number is missing else l_0_issues_number)) and ((undefined(name='issues_number') if l_0_issues_number is missing else l_0_issues_number) != '0')) and ((undefined(name='issues_number') if l_0_issues_number is missing else l_0_issues_number) != 0)):
        pass
        yield '\n        '
        yield escape((undefined(name='issues_number') if l_0_issues_number is missing else l_0_issues_number))
        yield '\n        '
    yield '\n      issues\n      </div>\n    </summary>\n    <div class="document_issues-banner_content">\n      <ul class="simple">\n        <li>\n          <a href="#field_issue_ID">Some issue</a>\n        </li>\n        <li>\n          <a href="#field_issue_ID">Other issue</a>\n        </li>\n      </ul>\n    </div>\n  </details>\n  \n  <a href="#" class="document_issues-toggler"><b>Hide</b> issues in the document ▾</a>\n</div>'

blocks = {}
debug_info = '1=18&7=22&8=25'