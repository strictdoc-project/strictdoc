from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/diff_controls.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<div class="diff_controls" left>\n  <a id="diff_left_open" class="action_button compact">\n    <span>＋</span>\n    <span class="action_button_compact__arising">open all modified</span>\n  </a>\n  <a id="diff_left_close" class="action_button compact">\n    <span>－</span>\n    <span class="action_button_compact__arising">close all</span>\n  </a>\n</div>\n<div class="diff_controls" right>\n  <a id="diff_right_open" class="action_button compact">\n    <span>＋</span>\n    <span class="action_button_compact__arising">open all modified</span>\n  </a>\n  <a id="diff_right_close" class="action_button compact">\n    <span>－</span>\n    <span class="action_button_compact__arising">close all</span>\n  </a>\n</div>'

blocks = {}
debug_info = ''