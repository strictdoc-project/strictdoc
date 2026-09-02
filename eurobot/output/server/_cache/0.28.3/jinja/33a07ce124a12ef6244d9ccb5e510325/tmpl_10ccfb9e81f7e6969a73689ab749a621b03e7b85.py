from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/frame_form_edit_project_title.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_form = missing
    pass
    parent_template = environment.get_template('components/modal/form.jinja', 'features/project_index/frame_form_edit_project_title.jinja.html')
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
    yield '\nEdit project title\n'

def block_modal_form__content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_form = resolve('form')
    l_0_new_title = resolve('new_title')
    l_0_project_config = resolve('project_config')
    l_0_error_object = resolve('error_object')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    yield '\n  <form\n    id="'
    yield escape((undefined(name='form') if l_0_form is missing else l_0_form))
    yield '"\n    action="/actions/project_index/save_project_title"\n    method="POST"\n    enctype="application/x-www-form-urlencoded"\n    data-turbo="true"\n  >\n    <sdoc-form-grid>\n      <sdoc-form-row>\n        <sdoc-form-row-aside></sdoc-form-row-aside>\n        <sdoc-form-row-main>'
    l_1_field_class_name = None
    l_1_field_editable = True
    l_1_field_input_name = 'project_title'
    l_1_field_label = 'Project title'
    l_1_field_placeholder = 'Enter Project title here...'
    l_1_field_type = 'singleline'
    l_1_field_required = True
    l_1_field_value = ((undefined(name='new_title') if l_0_new_title is missing else l_0_new_title) if t_1((undefined(name='new_title') if l_0_new_title is missing else l_0_new_title)) else environment.getattr((undefined(name='project_config') if l_0_project_config is missing else l_0_project_config), 'project_title'))
    l_1_testid_postfix = 'project_title'
    l_1_errors = context.call(environment.getattr((undefined(name='error_object') if l_0_error_object is missing else l_0_error_object), 'get_errors'), 'project_title', _block_vars=_block_vars)
    pass
    template = environment.get_template('components/form/field/contenteditable/index.jinja', 'features/project_index/frame_form_edit_project_title.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'errors': l_1_errors, 'field_class_name': l_1_field_class_name, 'field_editable': l_1_field_editable, 'field_input_name': l_1_field_input_name, 'field_label': l_1_field_label, 'field_placeholder': l_1_field_placeholder, 'field_required': l_1_field_required, 'field_type': l_1_field_type, 'field_value': l_1_field_value, 'testid_postfix': l_1_testid_postfix}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_class_name = l_1_field_editable = l_1_field_input_name = l_1_field_label = l_1_field_placeholder = l_1_field_type = l_1_field_required = l_1_field_value = l_1_testid_postfix = l_1_errors = missing
    yield '</sdoc-form-row-main>\n        <sdoc-form-row-aside></sdoc-form-row-aside>\n      </sdoc-form-row>\n    </sdoc-form-grid>\n  </form>\n'

def block_modal_form__footer_submit(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    l_1_name = 'Save'
    pass
    template = environment.get_template('components/button/submit.jinja', 'features/project_index/frame_form_edit_project_title.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'name': l_1_name}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_name = missing

blocks = {'modal__context': block_modal__context, 'modal_form__header': block_modal_form__header, 'modal_form__content': block_modal_form__content, 'modal_form__footer_submit': block_modal_form__footer_submit}
debug_info = '1=13&2=16&3=21&4=30&7=40&9=59&31=72&39=81&41=91'