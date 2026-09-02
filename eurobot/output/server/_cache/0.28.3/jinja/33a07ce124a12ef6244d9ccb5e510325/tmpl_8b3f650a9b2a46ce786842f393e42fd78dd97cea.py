from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/modal/_usage_example.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_form = missing
    pass
    parent_template = environment.get_template('components/modal/form.jinja', 'components/modal/_usage_example.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    l_0_form = 'sdoc_modal_form_id'
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

def block_modal_form__header(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\nImport ReqIF document\n'

def block_modal_form__content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_form = resolve('form')
    l_0_error_object = resolve('error_object')
    pass
    yield '\n  <form\n    id="'
    yield escape((undefined(name='form') if l_0_form is missing else l_0_form))
    yield '"\n\n    action="/actions/project_index/import_document_reqif"\n    method="POST"\n    enctype="multipart/form-data"\n    data-turbo="true"\n  >\n    <sdoc-form-grid>'
    l_1_field_class_name = ''
    l_1_field_input_name = 'reqif_file'
    l_1_field_label = 'Select a file'
    l_1_errors = context.call(environment.getattr((undefined(name='error_object') if l_0_error_object is missing else l_0_error_object), 'get_errors'), 'reqif_file', _block_vars=_block_vars)
    pass
    template = environment.get_template('components/form/field/file/index.jinja', 'components/modal/_usage_example.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_input_name = l_1_field_label = l_1_errors = missing
    yield '</sdoc-form-grid>\n  </form>\n'

def block_modal_form__footer_extra(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_modal_form__footer_submit(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n  '
    l_1_name = 'Import ReqIF'
    pass
    template = environment.get_template('components/button/submit.jinja', 'components/modal/_usage_example.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'name': l_1_name}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_name = missing

def block_modal_form__footer_cancel(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_super = context.super('modal_form__footer_cancel', block_modal_form__footer_cancel)
    _block_vars = {}
    pass
    yield '\n  \n  '
    yield escape(context.call(l_0_super, _block_vars=_block_vars))
    yield '\n'

blocks = {'modal__context': block_modal__context, 'modal_form__header': block_modal_form__header, 'modal_form__content': block_modal_form__content, 'modal_form__footer_extra': block_modal_form__footer_extra, 'modal_form__footer_submit': block_modal_form__footer_submit, 'modal_form__footer_cancel': block_modal_form__footer_cancel}
debug_info = '1=13&17=16&18=21&19=30&22=40&24=51&38=58&44=67&45=76&48=87&51=95&53=105'