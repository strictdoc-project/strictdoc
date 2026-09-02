from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/frame_form_new_document.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_form = missing
    pass
    parent_template = environment.get_template('components/modal/form.jinja', 'features/project_index/frame_form_new_document.jinja.html')
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

def block_modal_form__header(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\nAdd new document\n'

def block_modal_form__content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_form = resolve('form')
    l_0_document_title = resolve('document_title')
    l_0_error_object = resolve('error_object')
    l_0_document_path = resolve('document_path')
    l_0_include_doc_paths = resolve('include_doc_paths')
    l_0_editable_document_extensions = resolve('editable_document_extensions')
    pass
    yield '\n  <form\n    id="'
    yield escape((undefined(name='form') if l_0_form is missing else l_0_form))
    yield '"  \n    action="/actions/project_index/create_document"\n    method="POST"\n    data-turbo="true"\n  >\n    <sdoc-form-grid>\n      <sdoc-form-row>\n        <sdoc-form-row-aside></sdoc-form-row-aside>\n        <sdoc-form-row-main>'
    l_1_field_class_name = None
    l_1_field_editable = True
    l_1_field_input_name = 'document_title'
    l_1_field_label = 'document title'
    l_1_field_placeholder = 'Enter document title here...'
    l_1_field_type = 'singleline'
    l_1_field_value = (undefined(name='document_title') if l_0_document_title is missing else l_0_document_title)
    l_1_testid_postfix = 'document_title'
    l_1_errors = context.call(environment.getattr((undefined(name='error_object') if l_0_error_object is missing else l_0_error_object), 'get_errors'), 'document_title', _block_vars=_block_vars)
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'features/project_index/frame_form_new_document.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_testid_postfix = l_1_errors = missing
    yield '</sdoc-form-row-main>\n        <sdoc-form-row-aside></sdoc-form-row-aside>\n      </sdoc-form-row>\n\n      <sdoc-form-row>\n        <sdoc-form-row-aside></sdoc-form-row-aside>\n        <sdoc-form-row-main>'
    l_1_field_class_name = 'std-input-document_path'
    l_1_field_editable = True
    l_1_field_input_name = 'document_path'
    l_1_field_label = 'document path and filename'
    l_1_field_placeholder = 'Enter document path and filename here...'
    l_1_field_type = 'singleline'
    l_1_field_value = (undefined(name='document_path') if l_0_document_path is missing else l_0_document_path)
    l_1_testid_postfix = 'document_path'
    l_1_errors = context.call(environment.getattr((undefined(name='error_object') if l_0_error_object is missing else l_0_error_object), 'get_errors'), 'document_path', _block_vars=_block_vars)
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'features/project_index/frame_form_new_document.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_value = l_1_testid_postfix = l_1_errors = missing
    if (undefined(name='include_doc_paths') if l_0_include_doc_paths is missing else l_0_include_doc_paths):
        pass
        yield '<sdoc-form-hint>\n            ☞ Path must start with one of:\n            '
        l_1_loop = missing
        for l_1_path, l_1_loop in LoopContext((undefined(name='include_doc_paths') if l_0_include_doc_paths is missing else l_0_include_doc_paths), undefined):
            _loop_vars = {}
            pass
            yield '<code>'
            yield escape(l_1_path)
            yield '</code>'
            if (not environment.getattr(l_1_loop, 'last')):
                pass
                yield ', '
        l_1_loop = l_1_path = missing
        yield '</sdoc-form-hint>'
    if (undefined(name='editable_document_extensions') if l_0_editable_document_extensions is missing else l_0_editable_document_extensions):
        pass
        yield '<sdoc-form-hint>\n            ☞ File name must end with one of:\n            '
        l_1_loop = missing
        for l_1_extension, l_1_loop in LoopContext((undefined(name='editable_document_extensions') if l_0_editable_document_extensions is missing else l_0_editable_document_extensions), undefined):
            _loop_vars = {}
            pass
            yield '<code>'
            yield escape(l_1_extension)
            yield '</code>'
            if (not environment.getattr(l_1_loop, 'last')):
                pass
                yield ', '
        l_1_loop = l_1_extension = missing
        yield '</sdoc-form-hint>'
    yield '</sdoc-form-row-main>\n        <sdoc-form-row-aside></sdoc-form-row-aside>\n      </sdoc-form-row>\n    </sdoc-form-grid>\n  </form>\n'

blocks = {'modal__context': block_modal__context, 'modal_form__header': block_modal_form__header, 'modal_form__content': block_modal_form__content}
debug_info = '1=13&2=16&3=21&4=30&7=40&9=55&29=67&49=85&51=92&54=96&55=100&59=107&62=111&63=115'