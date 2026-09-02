from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/field/file/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_field_required = resolve('field_required')
    l_0_data_controller = resolve('data_controller')
    l_0_errors = resolve('errors')
    l_0_field_input_name = resolve('field_input_name')
    l_0_field_label = resolve('field_label')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    try:
        t_2 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_3 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    yield '\n\n'
    if (not t_3((undefined(name='field_required') if l_0_field_required is missing else l_0_field_required))):
        pass
        l_0_field_required = False
        context.vars['field_required'] = l_0_field_required
        context.exported_vars.add('field_required')
    yield '<sdoc-form-row\n  '
    if t_3((undefined(name='data_controller') if l_0_data_controller is missing else l_0_data_controller)):
        pass
        yield 'data-controller="'
        yield escape((undefined(name='data_controller') if l_0_data_controller is missing else l_0_data_controller))
        yield '"'
    yield '>\n  <sdoc-form-row-main>'
    if (t_2((undefined(name='errors') if l_0_errors is missing else l_0_errors)) > 0):
        pass
        for l_1_error in (undefined(name='errors') if l_0_errors is missing else l_0_errors):
            _loop_vars = {}
            pass
            yield '<sdoc-form-error>\n        '
            yield escape(l_1_error)
            yield '\n      </sdoc-form-error>'
        l_1_error = missing
    yield '<sdoc-form-field '
    if (undefined(name='field_required') if l_0_field_required is missing else l_0_field_required):
        pass
        yield 'required'
    yield '>\n        <label for="'
    yield escape((undefined(name='field_input_name') if l_0_field_input_name is missing else l_0_field_input_name))
    yield '">\n          '
    yield escape(t_1((undefined(name='field_label') if l_0_field_label is missing else l_0_field_label), 'Choose a file', True))
    if (undefined(name='field_required') if l_0_field_required is missing else l_0_field_required):
        pass
        yield ' *'
    yield '\n        </label>\n        <input\n          '
    if (undefined(name='field_required') if l_0_field_required is missing else l_0_field_required):
        pass
        yield 'required'
    yield '\n          type="file"\n          name="'
    yield escape((undefined(name='field_input_name') if l_0_field_input_name is missing else l_0_field_input_name))
    yield '"\n          id="'
    yield escape((undefined(name='field_input_name') if l_0_field_input_name is missing else l_0_field_input_name))
    yield '"\n          data-testid="form-'
    yield escape((undefined(name='field_input_name') if l_0_field_input_name is missing else l_0_field_input_name))
    yield '-field"\n        />\n    </sdoc-form-field>\n\n  </sdoc-form-row-main>\n</sdoc-form-row>'

blocks = {}
debug_info = '12=35&13=37&17=41&18=44&23=47&24=49&26=53&31=57&32=61&33=63&36=68&38=72&39=74&40=76'