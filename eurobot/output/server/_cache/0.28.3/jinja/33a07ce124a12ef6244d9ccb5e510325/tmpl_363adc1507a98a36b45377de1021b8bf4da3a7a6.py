from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/field/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_copy_to_clipboard = resolve('copy_to_clipboard')
    l_0_field_content = resolve('field_content')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    if t_1((undefined(name='copy_to_clipboard') if l_0_copy_to_clipboard is missing else l_0_copy_to_clipboard)):
        pass
        yield '<sdoc-field>\n  <sdoc-field-content>\n    <sdoc-autogen>'
        yield escape((undefined(name='field_content') if l_0_field_content is missing else l_0_field_content))
        yield '</sdoc-autogen>\n  </sdoc-field-content>\n  <sdoc-field-service>\n\n    <div class="copy_to_clipboard">\n      <div class="copy_to_clipboard-cover" data-copy-clipboard-target="cover">\n        <div title="Click to copy" class="copy_to_clipboard-button action_button" data-copy-clipboard-target="button">\n          <span style="display: contents;" data-copy-clipboard-target="copyIcon">\n            '
        template = environment.get_template('icons/ico16_copy.svg', 'components/field/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n          </span>\n          <span style="display: none;" data-copy-clipboard-target="doneIcon">\n            '
        template = environment.get_template('icons/ico16_done.svg', 'components/field/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n          </span>\n        </div>\n      </div>\n    </div>\n\n  </sdoc-field-service>\n</sdoc-field>'
    else:
        pass
        yield '<sdoc-autogen>'
        yield escape((undefined(name='field_content') if l_0_field_content is missing else l_0_field_content))
        yield '</sdoc-autogen>'

blocks = {}
debug_info = '24=19&27=22&35=24&38=31&47=41'