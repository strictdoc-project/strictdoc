from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/grammar_form_element/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_form = missing
    pass
    parent_template = environment.get_template('components/modal/form.jinja', 'components/grammar_form_element/index.jinja')
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
    l_0_form_object = resolve('form_object')
    pass
    yield '\n<turbo-frame>\n  <a\n    href="/actions/document/edit_grammar?document_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '"\n    data-testid="back-link-grammar-element"\n    class="sdoc-modal-header-back-button"\n    data-turbo="true"\n    data-turbo-action="replace"\n  >←</a>Edit grammar element: '
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'element_name'))
    yield '\n</turbo-frame>\n'

def block_modal_form__content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_form = resolve('form')
    l_0_form_object = resolve('form_object')
    l_0_errors_ = missing
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '\n  <form\n    id="'
    yield escape((undefined(name='form') if l_0_form is missing else l_0_form))
    yield '"  \n    method="POST"\n    data-turbo="true"\n    action="/actions/document/save_grammar_element"\n    data-js-tabs\n    >\n    <input type="hidden" id="document_mid" name="document_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '"/>\n    <input type="hidden" id="element_mid" name="element_mid" value="'
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'element_mid'))
    yield '"/>\n\n    \n    <input\n      type="hidden"\n      value="'
    yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_input_field_is_composite_value'), _block_vars=_block_vars))
    yield '"\n      name="'
    yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_input_field_is_composite'), _block_vars=_block_vars))
    yield '"\n    />\n    \n    <input\n      type="hidden"\n      value="'
    yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_input_field_prefix_value'), _block_vars=_block_vars))
    yield '"\n      name="'
    yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_input_field_prefix'), _block_vars=_block_vars))
    yield '"\n    />\n    \n    <input\n      type="hidden"\n      value="'
    yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_input_field_view_style_value'), _block_vars=_block_vars))
    yield '"\n      name="'
    yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_input_field_view_style'), _block_vars=_block_vars))
    yield '"\n    />\n\n    \n    <sdoc-tab-content id="Fields" active>\n      <sdoc-form-descr>\n        <b>StrictDoc conventions:</b>\n        <br/>\n        The requirements fields above the reserved "TITLE" field are dedicated to meta information and will be rendered as single-line. The fields below the reserved "STATEMENT" field are multiline and should be used for fields with more descriptive text.\n      </sdoc-form-descr>\n\n      <sdoc-form-grid>\n        <div style="display: contents;" id="document__editable_grammar_fields">'
    for l_1_field_ in environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'fields'):
        _loop_vars = {}
        pass
        if environment.getattr(l_1_field_, 'reserved'):
            pass
            yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'render_row_with_reserved_field'), l_1_field_, _loop_vars=_loop_vars))
        else:
            pass
            yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'render_row_with_custom_field'), l_1_field_, _loop_vars=_loop_vars))
    l_1_field_ = missing
    yield '</div>\n      </sdoc-form-grid>\n\n      <sdoc-form-footer>\n        <a\n          class="action_button"\n          href="/actions/document/add_grammar_field?document_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '"\n          data-turbo="true"\n          data-action-type="add_field"\n          data-testid="form-action-add-grammar-field"\n          \n          onclick="setTimeout(()=> {this.scrollIntoView()}, 100)"\n        >'
    template = environment.get_template('icons/ico16_add.svg', 'components/grammar_form_element/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors_': l_0_errors_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield ' Add grammar field</a>\n      </sdoc-form-footer>\n\n    </sdoc-tab-content>\n\n    \n    <sdoc-tab-content id="Relations">\n\n      \n\n      <sdoc-form-grid>\n        <div style="display: contents;" id="document__editable_grammar_relations">'
    l_0_errors_ = context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'get_errors'), 'Relations_Row', _block_vars=_block_vars)
    _block_vars['errors_'] = l_0_errors_
    if (t_1((undefined(name='errors_') if l_0_errors_ is missing else l_0_errors_)) > 0):
        pass
        for l_1_error_ in (undefined(name='errors_') if l_0_errors_ is missing else l_0_errors_):
            _loop_vars = {}
            pass
            yield '<sdoc-form-error>\n              '
            yield escape(l_1_error_)
            yield '\n            </sdoc-form-error>'
        l_1_error_ = missing
    for l_1_relation_ in environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'relations'):
        _loop_vars = {}
        pass
        yield escape(context.call(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'render_row_with_relation'), l_1_relation_, _loop_vars=_loop_vars))
    l_1_relation_ = missing
    yield '</div>\n      </sdoc-form-grid>\n\n      <sdoc-form-footer>\n        <a\n          class="action_button"\n          href="/actions/document/add_grammar_relation?document_mid='
    yield escape(environment.getattr((undefined(name='form_object') if l_0_form_object is missing else l_0_form_object), 'document_mid'))
    yield '"\n          data-turbo="true"\n          data-action-type="add_relation"\n          data-testid="form-action-add-grammar-relation"\n          \n          onclick="setTimeout(()=> {this.scrollIntoView()}, 100)"\n        >'
    template = environment.get_template('icons/ico16_add.svg', 'components/grammar_form_element/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors_': l_0_errors_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield ' Add grammar relation</a>\n      </sdoc-form-footer>\n\n    </sdoc-tab-content>\n\n  </form>\n'

blocks = {'modal__context': block_modal__context, 'modal_form__header': block_modal_form__header, 'modal_form__content': block_modal_form__content}
debug_info = '1=13&2=16&3=21&4=31&7=41&12=43&15=46&17=64&23=66&24=68&29=70&30=72&35=74&36=76&41=78&42=80&55=82&56=85&57=87&59=90&68=93&74=95&87=102&88=104&89=106&91=110&96=113&97=116&105=119&111=121'