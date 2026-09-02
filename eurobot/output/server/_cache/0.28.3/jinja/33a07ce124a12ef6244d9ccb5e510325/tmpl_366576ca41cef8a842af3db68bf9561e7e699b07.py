from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/field_display_mode/relations.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_requirement = resolve('requirement')
    l_0_requirement_file_links = resolve('requirement_file_links')
    pass
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'has_parent_requirements'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
        pass
        yield '\n  Parents:\n  <ul class="requirement__link">'
        for l_1_requirement in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_parent_requirements'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
            _loop_vars = {}
            pass
            yield '\n      <li>\n        <a class="requirement__link-parent"\n           href="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_link'), l_1_requirement, _loop_vars=_loop_vars))
            yield '"\n        >'
            if environment.getattr(l_1_requirement, 'reserved_uid'):
                pass
                yield '\n            <span class="requirement__parent-uid">'
                yield escape(environment.getattr(l_1_requirement, 'reserved_uid'))
                yield '</span>'
            yield '\n          '
            yield escape((environment.getattr(l_1_requirement, 'reserved_title') if environment.getattr(l_1_requirement, 'reserved_title') else ''))
            yield '\n        </a>\n      </li>'
        l_1_requirement = missing
        yield '\n  </ul>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'has_children_requirements'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
        pass
        yield '\n  Children:\n  <ul class="requirement__link">'
        for l_1_requirement in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_children_requirements'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
            _loop_vars = {}
            pass
            yield '\n      <li>\n        <a class="requirement__link-child"\n           href="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_link'), l_1_requirement, _loop_vars=_loop_vars))
            yield '"\n        >'
            if environment.getattr(l_1_requirement, 'reserved_uid'):
                pass
                yield '\n            <span class="requirement__child-uid">'
                yield escape(environment.getattr(l_1_requirement, 'reserved_uid'))
                yield '</span>'
            yield '\n          '
            yield escape((environment.getattr(l_1_requirement, 'reserved_title') if environment.getattr(l_1_requirement, 'reserved_title') else ''))
            yield '\n        </a>\n      </li>'
        l_1_requirement = missing
        yield '\n  </ul>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_requirements_to_source_traceability')):
        pass
        l_0_requirement_file_links = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_requirement_file_links'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement))
        context.vars['requirement_file_links'] = l_0_requirement_file_links
        context.exported_vars.add('requirement_file_links')
        if (undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links):
            pass
            yield '\n    Source files:\n    <ul class="requirement__link">'
            for (l_1_link, l_1_markers) in (undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links):
                _loop_vars = {}
                pass
                for l_2_marker in l_1_markers:
                    _loop_vars = {}
                    pass
                    yield '\n          <li>\n            <a class="requirement__link-file"\n               href="'
                    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), 'render_source_file_link'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), l_1_link, _loop_vars=_loop_vars))
                    yield '#'
                    yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid'))
                    yield '#'
                    yield escape(environment.getattr(l_2_marker, 'ng_range_line_begin'))
                    yield '#'
                    yield escape(environment.getattr(l_2_marker, 'ng_range_line_end'))
                    yield '"\n            >\n              '
                    yield escape(l_1_link)
                    yield ', <i>lines: '
                    yield escape(environment.getattr(l_2_marker, 'ng_range_line_begin'))
                    yield '-'
                    yield escape(environment.getattr(l_2_marker, 'ng_range_line_end'))
                    yield '</i>\n            </a>\n          </li>'
                l_2_marker = missing
            l_1_link = l_1_markers = missing
            yield '</ul>'

blocks = {}
debug_info = '2=14&5=17&8=21&10=23&11=26&13=29&19=33&22=36&25=40&27=42&28=45&30=48&36=52&37=54&38=57&41=60&42=63&45=67&47=75'