from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_statistics/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '<div class="main">\n\n<div class="sdoc-table_key_value">\n\n'
    for l_1_metric_or_section_ in environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'metrics'):
        _loop_vars = {}
        pass
        yield '\n  '
        if (environment.getattr(environment.getattr(l_1_metric_or_section_, '__class__'), '__name__') == 'MetricSection'):
            pass
            yield '\n    '
            l_2_key_value_pair = {'Section': environment.getattr(l_1_metric_or_section_, 'name')}
            pass
            yield '\n      '
            template = environment.get_template('components/table_key_value/index.jinja', 'features/project_statistics/main.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_2_key_value_pair, 'metric_or_section_': l_1_metric_or_section_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n    '
            l_2_key_value_pair = missing
            yield '\n\n    '
            for l_2_metric_ in environment.getattr(l_1_metric_or_section_, 'metrics'):
                _loop_vars = {}
                pass
                yield '\n      '
                l_3_key_value_pair = {'Key': environment.getattr(l_2_metric_, 'name'), 'Value': environment.getattr(l_2_metric_, 'value'), 'Link': (context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), environment.getattr(l_2_metric_, 'link'), _loop_vars=_loop_vars) if (not t_1(environment.getattr(l_2_metric_, 'link'))) else None)}
                pass
                yield '\n        '
                template = environment.get_template('components/table_key_value/index.jinja', 'features/project_statistics/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_3_key_value_pair, 'metric_': l_2_metric_, 'metric_or_section_': l_1_metric_or_section_}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n      '
                l_3_key_value_pair = missing
                yield '\n    '
            l_2_metric_ = missing
            yield '\n  '
        else:
            pass
            yield '\n    '
            l_2_key_value_pair = {'Key': environment.getattr(l_1_metric_or_section_, 'name'), 'Value': environment.getattr(l_1_metric_or_section_, 'value')}
            pass
            yield '\n      '
            template = environment.get_template('components/table_key_value/index.jinja', 'features/project_statistics/main.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'key_value_pair': l_2_key_value_pair, 'metric_or_section_': l_1_metric_or_section_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n    '
            l_2_key_value_pair = missing
            yield '\n  '
        yield '\n'
    l_1_metric_or_section_ = missing
    yield '\n\n</div>\n\n</div>'

blocks = {}
debug_info = '5=19&6=23&12=29&15=38&23=45&33=62'