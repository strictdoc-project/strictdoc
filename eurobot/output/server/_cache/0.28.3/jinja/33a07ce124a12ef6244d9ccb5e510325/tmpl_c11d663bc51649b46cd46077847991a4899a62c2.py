from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/files/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_requirement_file_links = resolve('requirement_file_links')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_requirements_to_source_traceability')):
        pass
        l_0_requirement_file_links = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_requirement_file_links'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity))
        context.vars['requirement_file_links'] = l_0_requirement_file_links
        context.exported_vars.add('requirement_file_links')
        if ((not t_2((undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links))) and (t_1((undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links)) > 0)):
            pass
            yield '\n      <sdoc-node-field-label>RELATIONS (File):</sdoc-node-field-label>\n      <sdoc-node-field data-field-label="file relations">\n        <ul class="requirement__link">'
            for (l_1_link, l_1_markers) in (undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links):
                _loop_vars = {}
                pass
                for l_2_marker in l_1_markers:
                    l_2_description = missing
                    _loop_vars = {}
                    pass
                    yield '\n              <li>\n                <a data-turbo="false" class="requirement__link-file" href="'
                    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), 'render_source_file_link'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), l_1_link, _loop_vars=_loop_vars))
                    yield '#'
                    yield escape(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_uid'))
                    yield '#'
                    yield escape(environment.getattr(l_2_marker, 'ng_range_line_begin'))
                    yield '#'
                    yield escape(environment.getattr(l_2_marker, 'ng_range_line_end'))
                    yield '">\n                  '
                    yield escape(l_1_link)
                    yield ', <i>lines: '
                    yield escape(environment.getattr(l_2_marker, 'ng_range_line_begin'))
                    yield '-'
                    yield escape(environment.getattr(l_2_marker, 'ng_range_line_end'))
                    yield '</i>'
                    l_2_description = context.call(environment.getattr(l_2_marker, 'get_description'), _loop_vars=_loop_vars)
                    _loop_vars['description'] = l_2_description
                    if (undefined(name='description') if l_2_description is missing else l_2_description):
                        pass
                        yield ', '
                        yield escape((undefined(name='description') if l_2_description is missing else l_2_description))
                    if (not t_2(environment.getattr(l_2_marker, 'role'))):
                        pass
                        yield '\n                      <span class="requirement__type-tag">('
                        yield escape(environment.getattr(l_2_marker, 'role'))
                        yield ')</span>\n                  '
                    yield '\n                </a>\n              </li>'
                l_2_marker = l_2_description = missing
            l_1_link = l_1_markers = missing
            yield '</ul>\n      </sdoc-node-field>'

blocks = {}
debug_info = '2=26&3=28&4=31&8=34&9=37&11=42&12=50&13=56&14=58&15=61&17=62&18=65'