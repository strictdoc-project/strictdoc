from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/grammar_form/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_form = missing
    pass
    parent_template = environment.get_template('components/modal/form.jinja', 'components/grammar_form/index.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    l_0_form = 'sdoc_modal_form'
    context.vars['form'] = l_0_form
    context.exported_vars.add('form')
    yield from parent_template.root_render_func(context)

def block_modal__context(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield 'form'

def block_modal_form__header(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\nEdit document grammar\n'

def block_modal_form__content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_form_object = resolve('form_object')
    l_0_form = resolve('form')
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '\n'
    if t_1(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'imported_grammar_file')):
        pass
        yield '\n  <form\n    id="'
        yield escape((undefined(name='form') if l_0_form is missing else l_0_form))
        yield '"  \n    method="POST"\n    data-turbo="true"\n    action="/actions/document/save_grammar"\n    >\n    <input type="hidden" id="document_mid" name="document_mid" value="'
        yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
        yield '"/>\n\n    <sdoc-form-grid>\n      <div style="display: contents;" id="document__editable_grammar_elements">'
        for l_1_field_ in environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'fields'):
            _loop_vars = {}
            pass
            yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'render_row_with_grammar_element'), l_1_field_, _loop_vars=_loop_vars))
        l_1_field_ = missing
        yield '</div>\n    </sdoc-form-grid>\n\n    <sdoc-form-footer>\n      <a\n        class="action_button"\n        href="/actions/document/add_grammar_element?document_mid='
        yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
        yield '"\n        data-turbo="true"\n        data-action-type="add_field"\n        data-testid="form-action-add-grammar-element"\n        \n        onclick="setTimeout(()=> {this.scrollIntoView()}, 100)"\n      >'
        template = environment.get_template('icons/ico16_add.svg', 'components/grammar_form/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield ' Add grammar element</a>\n    </sdoc-form-footer>\n\n  </form>\n'
    else:
        pass
        yield '\n\n  <sdoc-main-placeholder data-testid="grammar-from-file-editing-blocker-placeholder">\n    <div style="max-width: 300px;">\n      This document uses a&nbsp;grammar which is&nbsp;imported from a&nbsp;separate grammar file:\n      <code>'
        yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'imported_grammar_file'))
        yield '</code>.\n      <br/><br/>\n      Editing imported grammar files is&nbsp;not implemented yet.\n    </div>\n  </sdoc-main-placeholder>\n\n'
    yield '\n'

blocks = {'modal__context': block_modal__context, 'modal_form__header': block_modal_form__header, 'modal_form__content': block_modal_form__content}
debug_info = '1=13&2=16&3=21&4=31&8=41&9=58&11=61&16=63&20=65&21=68&29=71&35=73&44=83'