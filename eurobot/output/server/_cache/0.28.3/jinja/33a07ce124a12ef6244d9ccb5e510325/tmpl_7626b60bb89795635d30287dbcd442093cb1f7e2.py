from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/traceability_matrix/file.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_requirement = resolve('requirement')
    l_0_requirement_file_links = missing
    pass
    l_0_requirement_file_links = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_requirement_file_links'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement))
    context.vars['requirement_file_links'] = l_0_requirement_file_links
    context.exported_vars.add('requirement_file_links')
    if (undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links):
        pass
        for (l_1_link, l_1_markers) in (undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links):
            _loop_vars = {}
            pass
            for l_2_marker in l_1_markers:
                _loop_vars = {}
                pass
                yield '\n        <div class="traceability_matrix__file" with_relation="file">\n          <a data-turbo="false" class="" href="'
                yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), 'render_source_file_link_from_root'), l_1_link, _loop_vars=_loop_vars))
                yield '#'
                yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid'))
                yield '#'
                yield escape(environment.getattr(l_2_marker, 'ng_range_line_begin'))
                yield '#'
                yield escape(environment.getattr(l_2_marker, 'ng_range_line_end'))
                yield '">\n            <b>[ '
                yield escape(environment.getattr(l_2_marker, 'ng_range_line_begin'))
                yield '-'
                yield escape(environment.getattr(l_2_marker, 'ng_range_line_end'))
                yield ' ]</b> '
                yield escape(l_1_link)
                yield '\n          </a>\n        </div>'
            l_2_marker = missing
        l_1_link = l_1_markers = missing

blocks = {}
debug_info = '6=14&7=17&9=19&10=22&12=26&13=34'