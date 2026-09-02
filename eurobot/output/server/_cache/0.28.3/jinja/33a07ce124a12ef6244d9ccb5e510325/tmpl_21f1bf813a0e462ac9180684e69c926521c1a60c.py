from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node_field/links/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_sdoc_entity = resolve('sdoc_entity')
    l_0_view_object = resolve('view_object')
    l_0_current_sdoc_entity = missing
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    l_0_current_sdoc_entity = (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)
    context.vars['current_sdoc_entity'] = l_0_current_sdoc_entity
    context.exported_vars.add('current_sdoc_entity')
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'has_parent_requirements'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)):
        pass
        yield '\n    <sdoc-node-field-label>RELATIONS (Parent):</sdoc-node-field-label>\n    <sdoc-node-field data-field-label="parent relations">\n      <ul class="requirement__link">'
        for (l_1_sdoc_entity, l_1_relation_role_) in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_parent_relations_with_roles'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)):
            l_1_display_role_ = missing
            _loop_vars = {}
            pass
            l_1_display_role_ = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_display_role_for_parent_relation'), (undefined(name='current_sdoc_entity') if l_0_current_sdoc_entity is missing else l_0_current_sdoc_entity), l_1_sdoc_entity, l_1_relation_role_, _loop_vars=_loop_vars)
            _loop_vars['display_role_'] = l_1_display_role_
            yield '\n        <li>\n          <a data-turbo="false" class="requirement__link-parent" href="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_link'), l_1_sdoc_entity, _loop_vars=_loop_vars))
            yield '">'
            if environment.getattr(l_1_sdoc_entity, 'reserved_uid'):
                pass
                yield '\n            <span class="requirement__parent-uid">'
                yield escape(environment.getattr(l_1_sdoc_entity, 'reserved_uid'))
                yield '</span>'
            yield '\n            '
            yield escape((environment.getattr(l_1_sdoc_entity, 'reserved_title') if environment.getattr(l_1_sdoc_entity, 'reserved_title') else ''))
            yield '\n            '
            if (not t_1((undefined(name='display_role_') if l_1_display_role_ is missing else l_1_display_role_))):
                pass
                yield '\n              <span class="requirement__type-tag">('
                yield escape((undefined(name='display_role_') if l_1_display_role_ is missing else l_1_display_role_))
                yield ')</span>\n            '
            yield '\n          </a>\n        </li>'
        l_1_sdoc_entity = l_1_relation_role_ = l_1_display_role_ = missing
        yield '\n      </ul>\n    </sdoc-node-field>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'has_children_requirements'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)):
        pass
        yield '\n    <sdoc-node-field-label>RELATIONS (Child):</sdoc-node-field-label>\n    <sdoc-node-field data-field-label="child relations">\n      <ul class="requirement__link">'
        for (l_1_sdoc_entity, l_1_relation_role_) in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_child_relations_with_roles'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity)):
            l_1_display_role_ = missing
            _loop_vars = {}
            pass
            l_1_display_role_ = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_display_role_for_child_relation'), (undefined(name='current_sdoc_entity') if l_0_current_sdoc_entity is missing else l_0_current_sdoc_entity), l_1_sdoc_entity, l_1_relation_role_, _loop_vars=_loop_vars)
            _loop_vars['display_role_'] = l_1_display_role_
            yield '\n        <li>\n          <a data-turbo="false" class="requirement__link-child" href="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_link'), l_1_sdoc_entity, _loop_vars=_loop_vars))
            yield '">'
            if environment.getattr(l_1_sdoc_entity, 'reserved_uid'):
                pass
                yield '\n            <span class="requirement__child-uid">'
                yield escape(environment.getattr(l_1_sdoc_entity, 'reserved_uid'))
                yield '</span>'
            yield '\n            '
            yield escape((environment.getattr(l_1_sdoc_entity, 'reserved_title') if environment.getattr(l_1_sdoc_entity, 'reserved_title') else ''))
            yield '\n            '
            if (not t_1((undefined(name='display_role_') if l_1_display_role_ is missing else l_1_display_role_))):
                pass
                yield '\n              <span class="requirement__type-tag">('
                yield escape((undefined(name='display_role_') if l_1_display_role_ is missing else l_1_display_role_))
                yield ')</span>\n            '
            yield '\n          </a>\n        </li>'
        l_1_sdoc_entity = l_1_relation_role_ = l_1_display_role_ = missing
        yield '\n      </ul>\n    </sdoc-node-field>'

blocks = {}
debug_info = '2=20&3=23&7=26&8=30&10=33&11=35&12=38&14=41&15=43&16=46&25=51&29=54&30=58&32=61&33=63&34=66&36=69&37=71&38=74'