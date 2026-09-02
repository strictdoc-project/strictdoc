from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_file_view/requirement.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_requirement = resolve('requirement')
    l_0_view_object = resolve('view_object')
    l_0_range_begin = resolve('range_begin')
    l_0_range_end = resolve('range_end')
    l_0_ranged = l_0_requirement_file_links = missing
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    def macro():
        t_2 = []
        pass
        return concat(t_2)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, (environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), '__class__'), '__name__') in ('SDocNode', 'SDocCompositeNode')), 'Expected requirement', caller=caller)
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, (environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), '__class__'), '__name__') == 'LinkRenderer'), 'Expected link renderer', caller=caller)
    l_0_ranged = False
    context.vars['ranged'] = l_0_ranged
    context.exported_vars.add('ranged')
    yield '\n'
    if ((not t_1((undefined(name='range_begin') if l_0_range_begin is missing else l_0_range_begin))) and (not t_1((undefined(name='range_end') if l_0_range_end is missing else l_0_range_end)))):
        pass
        yield '\n  '
        l_0_ranged = True
        context.vars['ranged'] = l_0_ranged
        context.exported_vars.add('ranged')
        yield '\n'
    yield '\n\n<div\n  id="requirement:'
    yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid'))
    yield '"\n  class="source-file__requirement"\n  data-reqid="'
    yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid'))
    yield '"\n  '
    if (undefined(name='ranged') if l_0_ranged is missing else l_0_ranged):
        pass
        yield '\n    data-begin="'
        yield escape((undefined(name='range_begin') if l_0_range_begin is missing else l_0_range_begin))
        yield '"\n    data-end="'
        yield escape((undefined(name='range_end') if l_0_range_end is missing else l_0_range_end))
        yield '"\n  '
    yield '\n>\n  '
    if (undefined(name='ranged') if l_0_ranged is missing else l_0_ranged):
        pass
        yield '\n  <details>\n    <summary>\n  '
    yield '\n  <div class="source-file__requirement-header">\n    <a\n      class="action_icon secondary"\n      href="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), 'render_requirement_link_from_source_file'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'source_file')))
    yield '"\n      title="Go to requirement in document"\n    >'
    template = environment.get_template('icons/ico16_go_to_doc.svg', 'features/source_file_view/requirement.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'ranged': l_0_ranged, 'requirement_file_links': l_0_requirement_file_links}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</a>\n    <div class="source-file__requirement-info">'
    if environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid'):
        pass
        yield '\n      <div class="source-file__requirement-uid">'
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid'))
        yield '</div>'
    if (not t_1(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_title'))):
        pass
        yield '\n        '
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_title'))
    yield '\n    </div>\n  </div>\n  '
    if (undefined(name='ranged') if l_0_ranged is missing else l_0_ranged):
        pass
        yield '\n    </summary>\n  '
    l_0_requirement_file_links = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_requirement_file_links'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement))
    context.vars['requirement_file_links'] = l_0_requirement_file_links
    context.exported_vars.add('requirement_file_links')
    if (undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links):
        pass
        yield '\n\n <div class="source-file__requirement-links">'
        for (l_1_link, l_1_markers) in (undefined(name='requirement_file_links') if l_0_requirement_file_links is missing else l_0_requirement_file_links):
            l_1_this_file_or_other = l_1_traceability_file_type = missing
            _loop_vars = {}
            pass
            def macro():
                t_4 = []
                pass
                return concat(t_4)
            caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
            yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, (environment.getattr(environment.getattr(l_1_link, '__class__'), '__name__') == 'str'), 'Expected str', caller=caller, _loop_vars=_loop_vars)
            l_1_this_file_or_other = (environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'source_file'), 'in_doctree_source_file_rel_path_posix') == l_1_link)
            _loop_vars['this_file_or_other'] = l_1_this_file_or_other
            l_1_traceability_file_type = ('this_file' if (undefined(name='this_file_or_other') if l_1_this_file_or_other is missing else l_1_this_file_or_other) else 'other_file')
            _loop_vars['traceability_file_type'] = l_1_traceability_file_type
            if l_1_markers:
                pass
                for l_2_range in l_1_markers:
                    l_2_description = resolve('description')
                    _loop_vars = {}
                    pass
                    yield '\n\n          <a\n            class="source__range-pointer"\n            data-begin="'
                    yield escape(environment.getattr(l_2_range, 'ng_range_line_begin'))
                    yield '"\n            data-end="'
                    yield escape(environment.getattr(l_2_range, 'ng_range_line_end'))
                    yield '"\n            data-traceability-file-type="'
                    yield escape((undefined(name='traceability_file_type') if l_1_traceability_file_type is missing else l_1_traceability_file_type))
                    yield '"\n            href="'
                    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), 'render_requirement_in_source_file_range_link'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), l_1_link, environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'source_file'), l_2_range, _loop_vars=_loop_vars))
                    yield '"\n            title="lines '
                    yield escape(environment.getattr(l_2_range, 'ng_range_line_begin'))
                    yield '-'
                    yield escape(environment.getattr(l_2_range, 'ng_range_line_end'))
                    yield ' in file '
                    yield escape(l_1_link)
                    yield '"\n          >\n            '
                    if context.call(environment.getattr(l_2_range, 'is_range_marker'), _loop_vars=_loop_vars):
                        pass
                        yield '\n            <b>[ '
                        yield escape(environment.getattr(l_2_range, 'ng_range_line_begin'))
                        yield '-'
                        yield escape(environment.getattr(l_2_range, 'ng_range_line_end'))
                        yield ' ]</b>\n            <span class="source__range-pointer_description">'
                        yield escape(l_1_link)
                        l_2_description = context.call(environment.getattr(l_2_range, 'get_description'), _loop_vars=_loop_vars)
                        _loop_vars['description'] = l_2_description
                        if (undefined(name='description') if l_2_description is missing else l_2_description):
                            pass
                            yield ', '
                            yield escape((undefined(name='description') if l_2_description is missing else l_2_description))
                        yield '</span>\n            '
                    elif context.call(environment.getattr(l_2_range, 'is_line_marker'), _loop_vars=_loop_vars):
                        pass
                        yield '\n            <b>[ '
                        yield escape(environment.getattr(l_2_range, 'ng_range_line_begin'))
                        yield '-'
                        yield escape(environment.getattr(l_2_range, 'ng_range_line_end'))
                        yield ' ]</b>\n            <span class="source__range-pointer_description">'
                        yield escape(l_1_link)
                        yield ', line</span>\n            '
                    yield '\n          </a>'
                l_2_range = l_2_description = missing
            else:
                pass
                if (undefined(name='this_file_or_other') if l_1_this_file_or_other is missing else l_1_this_file_or_other):
                    pass
                    yield '<div>\n            <span class="current_file_pseudolink">\n              '
                    yield escape(l_1_link)
                    yield '\n            </span>\n          </div>'
                else:
                    pass
                    yield '<div>\n          <a href="'
                    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), 'render_requirement_in_source_file_link'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), l_1_link, environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'source_file'), _loop_vars=_loop_vars))
                    yield '" >\n          '
                    yield escape(l_1_link)
                    yield '\n          </a>\n          </div>'
        l_1_link = l_1_markers = l_1_this_file_or_other = l_1_traceability_file_type = missing
        yield '</div>\n\n  '
        if (undefined(name='ranged') if l_0_ranged is missing else l_0_ranged):
            pass
            yield '\n  </details>\n  '
    yield '\n</div>'

blocks = {}
debug_info = '1=22&5=28&10=34&11=38&12=41&16=46&18=48&19=50&20=53&21=55&24=58&31=62&33=64&35=71&36=74&38=76&39=79&43=81&47=84&48=87&52=90&53=94&55=100&56=102&58=104&59=106&63=111&64=113&65=115&66=117&67=119&69=125&70=128&71=132&72=133&73=135&74=138&77=140&78=143&79=147&85=153&89=156&96=161&97=163&107=167'