from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/traceability_matrix/main.jinja'

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
    yield '<div\n  class="main"\n  js-pan_with_space="true"\n>\n\n  <table class="traceability_matrix">\n    <thead class="traceability_matrix__thead">\n      <tr>\n        <th>\n          Node\n        </th>\n\n        '
    for l_1_known_relation_ in environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'known_relations_list'):
        _loop_vars = {}
        pass
        yield '\n          <th>\n          '
        yield escape(environment.getitem(l_1_known_relation_, 0))
        yield '\n          '
        if (not t_1(environment.getitem(l_1_known_relation_, 1))):
            pass
            yield '\n          ['
            yield escape(environment.getitem(l_1_known_relation_, 1))
            yield ']\n          '
        yield '\n          </th>\n        '
    l_1_known_relation_ = missing
    yield '\n      </tr>\n    </thead>\n\n    <tbody>'
    l_1_loop = missing
    for l_1_document, l_1_loop in LoopContext(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'iterate_documents')), undefined):
        l_1_document_iterator = missing
        _loop_vars = {}
        pass
        yield '<tr class="traceability_matrix__anchor" id="'
        yield escape(environment.getattr(l_1_loop, 'index'))
        yield '">\n        <td class="traceability_matrix__document" colspan="100">\n          <div class="traceability_matrix__document_line">\n          '
        template = environment.get_template('icons/ico16_document.svg', 'features/traceability_matrix/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_1_document, 'document_iterator': l_1_document_iterator, 'loop': l_1_loop}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n            '
        yield escape(environment.getattr(l_1_document, 'title'))
        yield '\n            <div class="traceability_matrix__document_stat">\n              \n            </div>\n          </div>\n        </td>\n      </tr>'
        l_1_document_iterator = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_document_iterator'), l_1_document, _loop_vars=_loop_vars)
        _loop_vars['document_iterator'] = l_1_document_iterator
        for (l_2_section_or_requirement, l_2__) in context.call(environment.getattr((undefined(name='document_iterator') if l_1_document_iterator is missing else l_1_document_iterator), 'all_content'), print_fragments=True, _loop_vars=_loop_vars):
            l_2_requirement = resolve('requirement')
            _loop_vars = {}
            pass
            if context.call(environment.getattr(l_2_section_or_requirement, 'is_normative_node'), _loop_vars=_loop_vars):
                pass
                yield '\n          <tr>\n            <td>'
                l_2_requirement = l_2_section_or_requirement
                _loop_vars['requirement'] = l_2_requirement
                l_3_anchor = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), l_2_section_or_requirement, _loop_vars=_loop_vars)
                pass
                template = environment.get_template('features/traceability_matrix/requirement.jinja.html', 'features/traceability_matrix/main.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'anchor': l_3_anchor, '_': l_2__, 'requirement': l_2_requirement, 'section_or_requirement': l_2_section_or_requirement, 'document': l_1_document, 'document_iterator': l_1_document_iterator, 'loop': l_1_loop}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_3_anchor = missing
                yield '</td>\n\n            '
                for l_3_known_relation_ in environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'known_relations_list'):
                    _loop_vars = {}
                    pass
                    yield '\n              <td>\n              '
                    if (environment.getitem(l_3_known_relation_, 0) == 'Parent'):
                        pass
                        yield '\n                '
                        for (l_4_parent_requirement_, l_4__) in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_parent_relations_with_role'), (undefined(name='requirement') if l_2_requirement is missing else l_2_requirement), environment.getitem(l_3_known_relation_, 1), _loop_vars=_loop_vars):
                            _loop_vars = {}
                            pass
                            l_5_relation_type = 'parent'
                            l_5_anchor = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), l_4_parent_requirement_, _loop_vars=_loop_vars)
                            l_5_requirement = l_4_parent_requirement_
                            pass
                            template = environment.get_template('features/traceability_matrix/requirement.jinja.html', 'features/traceability_matrix/main.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'anchor': l_5_anchor, 'relation_type': l_5_relation_type, 'requirement': l_5_requirement, '_': l_4__, 'parent_requirement_': l_4_parent_requirement_, 'known_relation_': l_3_known_relation_, 'section_or_requirement': l_2_section_or_requirement, 'document': l_1_document, 'document_iterator': l_1_document_iterator, 'loop': l_1_loop}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            l_5_relation_type = l_5_anchor = l_5_requirement = missing
                        l_4_parent_requirement_ = l_4__ = missing
                        yield '\n\n                '
                        for (l_4_child_requirement_, l_4__) in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_child_relations_with_role'), (undefined(name='requirement') if l_2_requirement is missing else l_2_requirement), environment.getitem(l_3_known_relation_, 1), _loop_vars=_loop_vars):
                            _loop_vars = {}
                            pass
                            l_5_relation_type = 'child'
                            l_5_anchor = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), l_4_child_requirement_, _loop_vars=_loop_vars)
                            l_5_requirement = l_4_child_requirement_
                            pass
                            template = environment.get_template('features/traceability_matrix/requirement.jinja.html', 'features/traceability_matrix/main.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'anchor': l_5_anchor, 'relation_type': l_5_relation_type, 'requirement': l_5_requirement, '_': l_4__, 'child_requirement_': l_4_child_requirement_, 'known_relation_': l_3_known_relation_, 'section_or_requirement': l_2_section_or_requirement, 'document': l_1_document, 'document_iterator': l_1_document_iterator, 'loop': l_1_loop}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            l_5_relation_type = l_5_anchor = l_5_requirement = missing
                        l_4_child_requirement_ = l_4__ = missing
                        yield '\n              '
                    elif (environment.getitem(l_3_known_relation_, 0) == 'File'):
                        pass
                        yield '\n                '
                        if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_requirements_to_source_traceability'), _loop_vars=_loop_vars):
                            pass
                            yield '\n                  '
                            template = environment.get_template('features/traceability_matrix/file.jinja', 'features/traceability_matrix/main.jinja')
                            gen = template.root_render_func(template.new_context(context.get_all(), True, {'known_relation_': l_3_known_relation_, '_': l_2__, 'requirement': l_2_requirement, 'section_or_requirement': l_2_section_or_requirement, 'document': l_1_document, 'document_iterator': l_1_document_iterator, 'loop': l_1_loop}))
                            try:
                                for event in gen:
                                    yield event
                            finally: gen.close()
                            yield '\n                '
                        yield '\n              '
                    yield '\n              </td>\n            '
                l_3_known_relation_ = missing
                yield '\n\n          </tr>'
        l_2_section_or_requirement = l_2__ = l_2_requirement = missing
        if (not context.call(environment.getattr(l_1_document, 'has_any_requirements'), _loop_vars=_loop_vars)):
            pass
            yield '\n        <tr>\n          <td colspan="100"><div class="traceability_matrix__placeholder">No traceable content.</div></td>\n        </tr>'
        yield '\n\n      <tr>\n        <td class="traceability_matrix__null" colspan="100"></td>\n      </tr>'
    l_1_loop = l_1_document = l_1_document_iterator = missing
    yield '\n    </tbody>\n  </table>\n</div>\n'

blocks = {}
debug_info = '13=19&15=23&16=25&17=28&25=34&26=39&29=41&30=48&38=50&40=52&41=56&44=59&48=63&52=71&54=75&55=78&61=85&65=94&71=101&74=110&75=113&76=116&86=128'