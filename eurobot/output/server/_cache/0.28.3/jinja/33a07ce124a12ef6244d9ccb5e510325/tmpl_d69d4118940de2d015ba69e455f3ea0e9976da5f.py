from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/anchor/anchor_clipboard_button.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_anchor_button_text = resolve('anchor_button_text')
    pass
    yield '\n<div\n  class="anchor_button"\n  title="Click to copy"\n  data-testid="section-anchor-button"\n  data-copy-clipboard-target="button"\n  data-anchor-id="'
    yield escape((undefined(name='anchor_button_text') if l_0_anchor_button_text is missing else l_0_anchor_button_text))
    yield '"\n>\n  <span\n    class="anchor_base_icon"\n    style="display: contents; line-height: 0.1;"\n    data-copy-clipboard-target="copyIcon"\n  >\n    <span class="svg_icon_not_hover_visible">'
    template = environment.get_template('icons/ico16_anchor.svg', 'components/anchor/anchor_clipboard_button.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</span>\n    <span class="svg_icon_hover_visible">'
    template = environment.get_template('icons/ico16_copy.svg', 'components/anchor/anchor_clipboard_button.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</span>\n  </span>\n  <span\n    class="anchor_check_icon"\n    style="display: none; line-height: 0.1;"\n    data-copy-clipboard-target="doneIcon"\n  >\n    '
    template = environment.get_template('icons/ico16_done.svg', 'components/anchor/anchor_clipboard_button.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </span>\n  <div class="copy_to_clipboard-cover" data-copy-clipboard-target="cover"></div>\n  <span class="anchor_button_text">'
    yield escape((undefined(name='anchor_button_text') if l_0_anchor_button_text is missing else l_0_anchor_button_text))
    yield '</span>\n</div>'

blocks = {}
debug_info = '21=13&28=15&29=22&36=29&39=36'