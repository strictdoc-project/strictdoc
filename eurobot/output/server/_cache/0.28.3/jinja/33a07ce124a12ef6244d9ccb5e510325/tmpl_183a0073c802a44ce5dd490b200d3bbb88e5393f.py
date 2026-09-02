from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_file_view/aside.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_source_file_range_reqs = missing
    pass
    yield '<div class="source-file__aside">\n  <sdoc-tabs class="in_aside_panel">\n    <sdoc-tab data-testid="source-file-tab-Nodes" active="" style="order: 0;">Nodes</sdoc-tab>\n    <sdoc-tab data-testid="source-file-tab-Ranges" style="order: 1;">Ranges</sdoc-tab>\n  </sdoc-tabs>\n\n  <div class="source-file__refer" id="referContainer">\n  <sdoc-tab-content id="Nodes" active>\n    <div class="source-file__toc">'
    l_0_source_file_range_reqs = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_source_file_reqs'), environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'source_file'), 'in_doctree_source_file_rel_path_posix'))
    context.vars['source_file_range_reqs'] = l_0_source_file_range_reqs
    context.exported_vars.add('source_file_range_reqs')
    if (undefined(name='source_file_range_reqs') if l_0_source_file_range_reqs is missing else l_0_source_file_range_reqs):
        pass
        for l_1_requirement in (undefined(name='source_file_range_reqs') if l_0_source_file_range_reqs is missing else l_0_source_file_range_reqs):
            _loop_vars = {}
            pass
            yield '<div class="source-file__toc-node">\n            '
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_aside_requirement'), environment.getattr(l_1_requirement, 'reserved_uid'), _loop_vars=_loop_vars))
            yield '\n          </div>'
        l_1_requirement = missing
    yield '</div>\n  </sdoc-tab-content>\n  <sdoc-tab-content id="Ranges">\n    <div class="source-file__toc">'
    for l_1_line in environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'pygmented_source_file_lines'):
        _loop_vars = {}
        pass
        if ((environment.getattr(environment.getattr(l_1_line, '__class__'), '__name__') == 'SourceMarkerTuple') and (not context.call(environment.getattr(l_1_line, 'is_end'), _loop_vars=_loop_vars))):
            pass
            yield '<div class="source-file__toc-range">\n            <div class="source-file__toc-range-header">'
            l_2_begin = environment.getattr(l_1_line, 'ng_range_line_begin')
            l_2_end = environment.getattr(l_1_line, 'ng_range_line_end')
            l_2_href = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_marker_range_link'), environment.getitem(environment.getattr(l_1_line, 'markers'), 0), _loop_vars=_loop_vars)
            l_2_scope = context.call(environment.getattr(environment.getitem(environment.getattr(l_1_line, 'markers'), 0), 'get_description'), _loop_vars=_loop_vars)
            pass
            template = environment.get_template('features/source_file_view/range_button.jinja', 'features/source_file_view/aside.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'begin': l_2_begin, 'end': l_2_end, 'href': l_2_href, 'scope': l_2_scope, 'line': l_1_line, 'source_file_range_reqs': l_0_source_file_range_reqs}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_begin = l_2_end = l_2_href = l_2_scope = missing
            yield '</div>\n            '
            for l_2_marker_ in environment.getattr(l_1_line, 'markers'):
                _loop_vars = {}
                pass
                yield '\n              '
                for l_3_node_uid_ in environment.getattr(l_2_marker_, 'reqs'):
                    _loop_vars = {}
                    pass
                    yield '\n                <div class="source-file__toc-range-node">\n                '
                    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_aside_requirement'), l_3_node_uid_, environment.getattr(l_2_marker_, 'ng_range_line_begin'), environment.getattr(l_2_marker_, 'ng_range_line_end'), _loop_vars=_loop_vars))
                    yield '\n                </div>\n              '
                l_3_node_uid_ = missing
                yield '\n            '
            l_2_marker_ = missing
            yield '\n          </div>'
    l_1_line = missing
    yield '</div>\n  </sdoc-tab-content>\n  </div>\n\n</div>'

blocks = {}
debug_info = '10=14&13=17&14=19&16=23&24=27&25=30&34=38&37=46&38=50&40=54'