from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_file_view/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_namespace = resolve('namespace')
    l_0_ns = resolve('ns')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    pass
    yield '<div class="main">\n\n<div id="sourceContainer" class="source-file__source">\n\n  '
    template = environment.get_template('features/source_file_view/file_stats.jinja', 'features/source_file_view/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'ns': l_0_ns}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    if (t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'pygmented_source_file_lines')) > 0):
        pass
        yield '<div id="source" class="source">'
        l_0_ns = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), prev_line=None)
        context.vars['ns'] = l_0_ns
        context.exported_vars.add('ns')
        l_1_loop = missing
        for l_1_line, l_1_loop in LoopContext(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'pygmented_source_file_lines'), undefined):
            l_1_current_marker_link = resolve('current_marker_link')
            l_1_current_range_begin = resolve('current_range_begin')
            l_1_current_range_end = resolve('current_range_end')
            l_1_range_closer_line = resolve('range_closer_line')
            l_1_is_marker = l_1_is_markup = l_1_marker_is_end = l_1_implicit_close = missing
            _loop_vars = {}
            pass
            l_1_is_marker = (environment.getattr(environment.getattr(l_1_line, '__class__'), '__name__') == 'SourceMarkerTuple')
            _loop_vars['is_marker'] = l_1_is_marker
            l_1_is_markup = (environment.getattr(environment.getattr(l_1_line, '__class__'), '__name__') == 'Markup')
            _loop_vars['is_markup'] = l_1_is_markup
            if ((undefined(name='is_marker') if l_1_is_marker is missing else l_1_is_marker) and (not context.call(environment.getattr(l_1_line, 'is_end'), _loop_vars=_loop_vars))):
                pass
                l_1_current_marker_link = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_marker_range_link'), l_1_line, _loop_vars=_loop_vars)
                _loop_vars['current_marker_link'] = l_1_current_marker_link
                l_1_current_range_begin = environment.getattr(l_1_line, 'ng_range_line_begin')
                _loop_vars['current_range_begin'] = l_1_current_range_begin
                l_1_current_range_end = environment.getattr(l_1_line, 'ng_range_line_end')
                _loop_vars['current_range_end'] = l_1_current_range_end
                yield '<div\n          class="source__range collapsed"\n          data-begin="'
                yield escape((undefined(name='current_range_begin') if l_1_current_range_begin is missing else l_1_current_range_begin))
                yield '"\n          data-end="'
                yield escape((undefined(name='current_range_end') if l_1_current_range_end is missing else l_1_current_range_end))
                yield '"\n        >\n          <div class="source__range-header">'
                l_2_begin = (undefined(name='current_range_begin') if l_1_current_range_begin is missing else l_1_current_range_begin)
                l_2_end = (undefined(name='current_range_end') if l_1_current_range_end is missing else l_1_current_range_end)
                l_2_href = (undefined(name='current_marker_link') if l_1_current_marker_link is missing else l_1_current_marker_link)
                l_2_scope = context.call(environment.getattr(environment.getitem(environment.getattr(l_1_line, 'markers'), 0), 'get_description'), _loop_vars=_loop_vars)
                pass
                template = environment.get_template('features/source_file_view/range_button.jinja', 'features/source_file_view/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'begin': l_2_begin, 'end': l_2_end, 'href': l_2_href, 'scope': l_2_scope, 'current_marker_link': l_1_current_marker_link, 'current_range_begin': l_1_current_range_begin, 'current_range_end': l_1_current_range_end, 'implicit_close': l_1_implicit_close, 'is_marker': l_1_is_marker, 'is_markup': l_1_is_markup, 'line': l_1_line, 'loop': l_1_loop, 'marker_is_end': l_1_marker_is_end, 'range_closer_line': l_1_range_closer_line, 'ns': l_0_ns}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_begin = l_2_end = l_2_href = l_2_scope = missing
                yield '</div>\n          <div class="source__range-cell">\n            <div\n              class="source__range-handler"\n              data-begin="'
                yield escape((undefined(name='current_range_begin') if l_1_current_range_begin is missing else l_1_current_range_begin))
                yield '"\n              data-end="'
                yield escape((undefined(name='current_range_end') if l_1_current_range_end is missing else l_1_current_range_end))
                yield '"\n            >'
                template = environment.get_template('icons/ico16_section_collapse.svg', 'features/source_file_view/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'current_marker_link': l_1_current_marker_link, 'current_range_begin': l_1_current_range_begin, 'current_range_end': l_1_current_range_end, 'implicit_close': l_1_implicit_close, 'is_marker': l_1_is_marker, 'is_markup': l_1_is_markup, 'line': l_1_line, 'loop': l_1_loop, 'marker_is_end': l_1_marker_is_end, 'range_closer_line': l_1_range_closer_line, 'ns': l_0_ns}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '</div>\n          </div>\n          <div class="source__range-cell">\n            <ul class="source__range-titles-list">'
                for l_2_marker_ in environment.getattr(l_1_line, 'markers'):
                    _loop_vars = {}
                    pass
                    for l_3_req in environment.getattr(l_2_marker_, 'reqs_objs'):
                        _loop_vars = {}
                        pass
                        yield '<li>\n                  '
                        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_title_for_banner_header'), l_2_marker_, environment.getattr(l_3_req, 'uid'), _loop_vars=_loop_vars))
                        yield '\n                </li>'
                    l_3_req = missing
                l_2_marker_ = missing
                yield '</ul>\n            <div class="source__range-banner source__range-start">'
                for l_2_marker_ in environment.getattr(l_1_line, 'markers'):
                    _loop_vars = {}
                    pass
                    for l_3_req in environment.getattr(l_2_marker_, 'reqs_objs'):
                        _loop_vars = {}
                        pass
                        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_detailed_node_for_banner'), environment.getattr(l_3_req, 'uid'), _loop_vars=_loop_vars))
                    l_3_req = missing
                l_2_marker_ = missing
                yield '</div>\n          </div>\n        </div>\n      '
            yield '\n\n      <div data-line="'
            yield escape(environment.getattr(l_1_loop, 'index'))
            yield '" class="source__line">\n        <div data-line="'
            yield escape(environment.getattr(l_1_loop, 'index'))
            yield '" id="line-'
            yield escape(environment.getattr(l_1_loop, 'index'))
            yield '" class="source__line-number"><pre>'
            yield escape(environment.getattr(l_1_loop, 'index'))
            yield '</pre></div>\n        <div data-line="'
            yield escape(environment.getattr(l_1_loop, 'index'))
            yield '" class="source__line-content">'
            if (environment.getattr(environment.getattr(l_1_line, '__class__'), '__name__') == 'SourceMarkerTuple'):
                pass
                yield '\n            <pre class="highlight">'
                yield escape(environment.getattr(l_1_line, 'source_line'))
                yield '</pre>'
            elif (l_1_line != ''):
                pass
                yield '\n            <pre class="highlight">'
                yield escape(l_1_line)
                yield '</pre>'
            else:
                pass
                yield '<pre data-state="empty" style="user-select: none">&nbsp;</pre>'
            yield '</div>\n      </div>'
            if ((undefined(name='is_marker') if l_1_is_marker is missing else l_1_is_marker) and context.call(environment.getattr(l_1_line, 'is_line_marker'), _loop_vars=_loop_vars)):
                pass
                if not isinstance(l_0_ns, Namespace):
                    raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                l_0_ns['prev_line'] = l_1_line
            l_1_marker_is_end = (((undefined(name='is_marker') if l_1_is_marker is missing else l_1_is_marker) and context.call(environment.getattr(l_1_line, 'is_range_marker'), _loop_vars=_loop_vars)) and context.call(environment.getattr(l_1_line, 'is_end'), _loop_vars=_loop_vars))
            _loop_vars['marker_is_end'] = l_1_marker_is_end
            l_1_implicit_close = (((undefined(name='is_markup') if l_1_is_markup is missing else l_1_is_markup) and (environment.getattr((undefined(name='ns') if l_0_ns is missing else l_0_ns), 'prev_line') != None)) and (environment.getattr(environment.getattr((undefined(name='ns') if l_0_ns is missing else l_0_ns), 'prev_line'), 'ng_range_line_end') == environment.getattr(l_1_loop, 'index')))
            _loop_vars['implicit_close'] = l_1_implicit_close
            if (undefined(name='marker_is_end') if l_1_marker_is_end is missing else l_1_marker_is_end):
                pass
                l_1_range_closer_line = l_1_line
                _loop_vars['range_closer_line'] = l_1_range_closer_line
            elif (undefined(name='implicit_close') if l_1_implicit_close is missing else l_1_implicit_close):
                pass
                l_1_range_closer_line = environment.getattr((undefined(name='ns') if l_0_ns is missing else l_0_ns), 'prev_line')
                _loop_vars['range_closer_line'] = l_1_range_closer_line
                if not isinstance(l_0_ns, Namespace):
                    raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                l_0_ns['prev_line'] = None
            else:
                pass
                l_1_range_closer_line = None
                _loop_vars['range_closer_line'] = l_1_range_closer_line
            if ((undefined(name='range_closer_line') if l_1_range_closer_line is missing else l_1_range_closer_line) != None):
                pass
                yield '\n        <div\n          class="source__range-closer"\n          data-end="'
                yield escape(environment.getattr(environment.getitem(environment.getattr((undefined(name='range_closer_line') if l_1_range_closer_line is missing else l_1_range_closer_line), 'markers'), 0), 'ng_range_line_end'))
                yield '"\n        >\n          <div class="source__range-closer-label">'
                l_2_begin = environment.getattr(environment.getitem(environment.getattr((undefined(name='range_closer_line') if l_1_range_closer_line is missing else l_1_range_closer_line), 'markers'), 0), 'ng_range_line_begin')
                l_2_end = environment.getattr(environment.getitem(environment.getattr((undefined(name='range_closer_line') if l_1_range_closer_line is missing else l_1_range_closer_line), 'markers'), 0), 'ng_range_line_end')
                l_2_href = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_marker_range_link'), (undefined(name='range_closer_line') if l_1_range_closer_line is missing else l_1_range_closer_line), _loop_vars=_loop_vars)
                l_2_scope = context.call(environment.getattr(environment.getitem(environment.getattr((undefined(name='range_closer_line') if l_1_range_closer_line is missing else l_1_range_closer_line), 'markers'), 0), 'get_description'), _loop_vars=_loop_vars)
                pass
                template = environment.get_template('features/source_file_view/range_button.jinja', 'features/source_file_view/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'begin': l_2_begin, 'end': l_2_end, 'href': l_2_href, 'scope': l_2_scope, 'current_marker_link': l_1_current_marker_link, 'current_range_begin': l_1_current_range_begin, 'current_range_end': l_1_current_range_end, 'implicit_close': l_1_implicit_close, 'is_marker': l_1_is_marker, 'is_markup': l_1_is_markup, 'line': l_1_line, 'loop': l_1_loop, 'marker_is_end': l_1_marker_is_end, 'range_closer_line': l_1_range_closer_line, 'ns': l_0_ns}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_2_begin = l_2_end = l_2_href = l_2_scope = missing
                yield '</div>\n        </div>\n      '
        l_1_loop = l_1_line = l_1_is_marker = l_1_is_markup = l_1_current_marker_link = l_1_current_range_begin = l_1_current_range_end = l_1_marker_is_end = l_1_implicit_close = l_1_range_closer_line = missing
        yield '</div>'
    else:
        pass
        yield '<div style="text-align: center">\n    Source file is empty.\n  </div>'
    yield '</div>\n</div>'

blocks = {}
debug_info = '5=21&7=27&9=30&10=34&11=42&12=44&14=46&15=48&16=50&17=52&20=55&21=57&31=64&38=72&39=74&40=76&44=83&45=86&47=90&53=95&54=98&55=101&63=106&64=108&65=114&66=116&68=119&69=121&71=124&79=130&80=134&84=135&85=137&87=139&88=141&89=143&90=145&91=149&93=152&96=154&99=157&108=164'