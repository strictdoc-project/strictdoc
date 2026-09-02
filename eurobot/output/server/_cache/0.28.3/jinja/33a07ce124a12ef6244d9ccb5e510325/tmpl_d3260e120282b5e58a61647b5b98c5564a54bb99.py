from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/fields/requirement_fields.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_requirement_change = resolve('requirement_change')
    l_0_requirement = resolve('requirement')
    l_0_traceability_index = resolve('traceability_index')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_1((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change)), None, caller=caller)
    yield '\n\n<div class="diff_node_fields">'
    for l_1_requirement_field_triple_ in context.call(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'enumerate_all_fields')):
        l_1_field_change = resolve('field_change')
        l_1_side = resolve('side')
        l_1_colored_diff = resolve('colored_diff')
        l_1_is_multiline = missing
        _loop_vars = {}
        pass
        l_1_is_multiline = context.call(environment.getattr(environment.getitem(l_1_requirement_field_triple_, 0), 'is_multiline'), _loop_vars=_loop_vars)
        _loop_vars['is_multiline'] = l_1_is_multiline
        if (not t_2((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change))):
            pass
            l_1_field_change = context.call(environment.getattr((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change), 'get_field_change'), environment.getitem(l_1_requirement_field_triple_, 0), _loop_vars=_loop_vars)
            _loop_vars['field_change'] = l_1_field_change
        else:
            pass
            l_1_field_change = None
            _loop_vars['field_change'] = l_1_field_change
        yield '\n    <div\n      class="diff_node_field"\n      '
        if (undefined(name='is_multiline') if l_1_is_multiline is missing else l_1_is_multiline):
            pass
            yield '\n        multiline\n      '
        yield '\n      '
        if ((not t_2((undefined(name='field_change') if l_1_field_change is missing else l_1_field_change))) or ((not t_2((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change))) and (not context.call(environment.getattr((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change), 'is_paired_change'), _loop_vars=_loop_vars)))):
            pass
            yield '\n        modified="'
            yield escape((undefined(name='side') if l_1_side is missing else l_1_side))
            yield '"\n      '
        yield '\n    >'
        l_2_badge_text = environment.getitem(l_1_requirement_field_triple_, 1)
        pass
        template = environment.get_template('components/badge/index.jinja', 'features/diff_and_changelog/fields/requirement_fields.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_2_badge_text, 'colored_diff': l_1_colored_diff, 'field_change': l_1_field_change, 'is_multiline': l_1_is_multiline, 'requirement_field_triple_': l_1_requirement_field_triple_}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_2_badge_text = missing
        yield '<span class="sdoc_pre_content">'
        if (not t_2((undefined(name='field_change') if l_1_field_change is missing else l_1_field_change))):
            pass
            l_1_colored_diff = context.call(environment.getattr((undefined(name='field_change') if l_1_field_change is missing else l_1_field_change), 'get_colored_free_text_diff'), (undefined(name='side') if l_1_side is missing else l_1_side), _loop_vars=_loop_vars)
            _loop_vars['colored_diff'] = l_1_colored_diff
            if (not t_2((undefined(name='colored_diff') if l_1_colored_diff is missing else l_1_colored_diff))):
                pass
                yield escape(context.call(environment.getattr((undefined(name='field_change') if l_1_field_change is missing else l_1_field_change), 'get_colored_free_text_diff'), (undefined(name='side') if l_1_side is missing else l_1_side), _loop_vars=_loop_vars))
            else:
                pass
                yield escape(environment.getitem(l_1_requirement_field_triple_, 2))
        else:
            pass
            yield escape(environment.getitem(l_1_requirement_field_triple_, 2))
        yield '</span>\n    </div>'
    l_1_requirement_field_triple_ = l_1_is_multiline = l_1_field_change = l_1_side = l_1_colored_diff = missing
    if context.call(environment.getattr((undefined(name='traceability_index') if l_0_traceability_index is missing else l_0_traceability_index), 'has_parent_requirements'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
        pass
        for (l_1_parent_requirement_, l_1_relation_role_) in context.call(environment.getattr((undefined(name='traceability_index') if l_0_traceability_index is missing else l_0_traceability_index), 'get_parent_relations_with_roles'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
            l_1_other_stats = resolve('other_stats')
            l_1_side = resolve('side')
            l_1_display_role_ = missing
            _loop_vars = {}
            pass
            l_1_display_role_ = context.call(environment.getattr((undefined(name='traceability_index') if l_0_traceability_index is missing else l_0_traceability_index), 'get_display_role_for_parent_relation'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), l_1_parent_requirement_, l_1_relation_role_, _loop_vars=_loop_vars)
            _loop_vars['display_role_'] = l_1_display_role_
            yield '\n      \n      <div class="diff_node_field"\n        '
            if ((not t_2((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change))) and (not context.call(environment.getattr((undefined(name='other_stats') if l_1_other_stats is missing else l_1_other_stats), 'contains_requirement_relations'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), environment.getattr(l_1_parent_requirement_, 'reserved_uid'), l_1_relation_role_, _loop_vars=_loop_vars))):
                pass
                yield '\n          modified="'
                yield escape((undefined(name='side') if l_1_side is missing else l_1_side))
                yield '"\n        '
            yield '\n      >'
            l_2_badge_text = 'relation'
            pass
            template = environment.get_template('components/badge/index.jinja', 'features/diff_and_changelog/fields/requirement_fields.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_2_badge_text, 'display_role_': l_1_display_role_, 'parent_requirement_': l_1_parent_requirement_, 'relation_role_': l_1_relation_role_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_badge_text = missing
            yield '<div class="sdoc_pre_content">'
            if True:
                pass
                yield '<b>'
                yield escape(environment.getattr(l_1_parent_requirement_, 'reserved_uid'))
                yield '</b>\n'
                yield escape((environment.getattr(l_1_parent_requirement_, 'reserved_title') if environment.getattr(l_1_parent_requirement_, 'reserved_title') else ''))
            if (not t_2((undefined(name='display_role_') if l_1_display_role_ is missing else l_1_display_role_))):
                pass
                yield '<span class="requirement__type-tag">('
                yield escape((undefined(name='display_role_') if l_1_display_role_ is missing else l_1_display_role_))
                yield ')</span>'
            yield '</div>\n      </div>'
        l_1_parent_requirement_ = l_1_relation_role_ = l_1_display_role_ = l_1_other_stats = l_1_side = missing
    if context.call(environment.getattr((undefined(name='traceability_index') if l_0_traceability_index is missing else l_0_traceability_index), 'has_children_requirements'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
        pass
        for (l_1_child_requirement_, l_1_relation_role_) in context.call(environment.getattr((undefined(name='traceability_index') if l_0_traceability_index is missing else l_0_traceability_index), 'get_child_relations_with_roles'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
            l_1_other_stats = resolve('other_stats')
            l_1_side = resolve('side')
            l_1_display_role_ = missing
            _loop_vars = {}
            pass
            l_1_display_role_ = context.call(environment.getattr((undefined(name='traceability_index') if l_0_traceability_index is missing else l_0_traceability_index), 'get_display_role_for_child_relation'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), l_1_child_requirement_, l_1_relation_role_, _loop_vars=_loop_vars)
            _loop_vars['display_role_'] = l_1_display_role_
            yield '\n      <div class="diff_node_field"\n        '
            if ((not t_2((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change))) and (not context.call(environment.getattr((undefined(name='other_stats') if l_1_other_stats is missing else l_1_other_stats), 'contains_requirement_relations'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), environment.getattr(l_1_child_requirement_, 'reserved_uid'), l_1_relation_role_, _loop_vars=_loop_vars))):
                pass
                yield '\nmodified="'
                yield escape((undefined(name='side') if l_1_side is missing else l_1_side))
                yield '"\n        '
            yield '\n>'
            l_2_badge_text = 'child-relation'
            pass
            template = environment.get_template('components/badge/index.jinja', 'features/diff_and_changelog/fields/requirement_fields.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_2_badge_text, 'child_requirement_': l_1_child_requirement_, 'display_role_': l_1_display_role_, 'relation_role_': l_1_relation_role_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_2_badge_text = missing
            yield '<div class="sdoc_pre_content">'
            if True:
                pass
                yield '<b>'
                yield escape(environment.getattr(l_1_child_requirement_, 'reserved_uid'))
                yield '</b>\n'
                yield escape((environment.getattr(l_1_child_requirement_, 'reserved_title') if environment.getattr(l_1_child_requirement_, 'reserved_title') else ''))
            if (not t_2((undefined(name='display_role_') if l_1_display_role_ is missing else l_1_display_role_))):
                pass
                yield '<span class="requirement__type-tag">('
                yield escape((undefined(name='display_role_') if l_1_display_role_ is missing else l_1_display_role_))
                yield ')</span>'
            yield '</div>\n      </div>'
        l_1_child_requirement_ = l_1_relation_role_ = l_1_display_role_ = l_1_other_stats = l_1_side = missing
    yield '</div>'

blocks = {}
debug_info = '1=26&4=33&5=40&7=42&8=44&10=48&14=51&17=55&18=58&22=63&25=71&26=73&27=75&28=77&30=80&33=83&39=86&40=88&41=94&44=97&45=100&49=105&52=113&53=116&54=118&56=119&57=122&63=126&64=128&65=134&67=137&68=140&72=145&75=153&76=156&77=158&79=159&80=162'