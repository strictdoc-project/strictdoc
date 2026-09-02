from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/nav_tabs.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<nav class="sdoc-tabs">\n  <div class="sdoc-tab-list">\n    <a class="sdoc-tab"\n      '
    if (environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'tab') == 'diff'):
        pass
        yield 'active'
    yield '\n      '
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '\n      href="/diff?tab=diff&left_revision='
        yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'left_revision_urlencoded'))
        yield '&right_revision='
        yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'right_revision_urlencoded'))
        yield '"\n      '
    else:
        pass
        yield '\n      href="diff.html"\n      '
    yield '\n    >Diff</a>\n    <a class="sdoc-tab"\n      '
    if (environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'tab') == 'changelog'):
        pass
        yield 'active'
    yield '\n      '
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '\n      href="/diff?tab=changelog&left_revision='
        yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'left_revision_urlencoded'))
        yield '&right_revision='
        yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'right_revision_urlencoded'))
        yield '"\n      '
    else:
        pass
        yield '\n      href="changelog.html"\n      '
    yield '\n      data-testid="diff-screen-tab-changelog"\n    >Changelog</a>\n  </div>\n</nav>'

blocks = {}
debug_info = '4=13&5=17&6=20&12=28&13=32&14=35'