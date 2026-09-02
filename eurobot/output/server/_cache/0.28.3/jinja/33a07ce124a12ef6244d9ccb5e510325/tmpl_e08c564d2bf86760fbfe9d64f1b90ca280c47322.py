from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/row_add_new_node.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_prev_node = resolve('prev_node')
    l_0_next_node = resolve('next_node')
    l_0_table_document_mid = l_0_can_add_first_node = l_0_can_use_separator = l_0_can_add_before_next = l_0_can_add_after_prev = l_0_can_add_child_of_prev = missing
    try:
        t_1 = environment.filters['lower']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'lower' found.")
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
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'), None, caller=caller)
    l_0_table_document_mid = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'reserved_mid')
    context.vars['table_document_mid'] = l_0_table_document_mid
    context.exported_vars.add('table_document_mid')
    l_0_can_add_first_node = ((t_2((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node)) and t_2((undefined(name='next_node') if l_0_next_node is missing else l_0_next_node))) and context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'can_add_node'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document')))
    context.vars['can_add_first_node'] = l_0_can_add_first_node
    context.exported_vars.add('can_add_first_node')
    l_0_can_use_separator = (((not t_2((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node))) or (not t_2((undefined(name='next_node') if l_0_next_node is missing else l_0_next_node)))) or (undefined(name='can_add_first_node') if l_0_can_add_first_node is missing else l_0_can_add_first_node))
    context.vars['can_use_separator'] = l_0_can_use_separator
    context.exported_vars.add('can_use_separator')
    l_0_can_add_before_next = ((not t_2((undefined(name='next_node') if l_0_next_node is missing else l_0_next_node))) and context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'can_insert_next_to_node'), (undefined(name='next_node') if l_0_next_node is missing else l_0_next_node)))
    context.vars['can_add_before_next'] = l_0_can_add_before_next
    context.exported_vars.add('can_add_before_next')
    l_0_can_add_after_prev = ((not t_2((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node))) and context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'can_insert_next_to_node'), (undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node)))
    context.vars['can_add_after_prev'] = l_0_can_add_after_prev
    context.exported_vars.add('can_add_after_prev')
    l_0_can_add_child_of_prev = (((not t_2((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node))) and (context.call(environment.getattr((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node), 'is_document_node')) or environment.getattr((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node), 'is_composite'))) and context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'can_add_node'), (undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node)))
    context.vars['can_add_child_of_prev'] = l_0_can_add_child_of_prev
    context.exported_vars.add('can_add_child_of_prev')
    yield '<tr class="content-view__add_new_row-TR"\n    data-testid="table-add-row"\n    '
    if (not t_2((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node))):
        pass
        yield '\n    data-prev-node-mid="'
        yield escape(environment.getattr((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node), 'reserved_mid'))
        yield '"\n    '
    yield '\n    '
    if (not t_2((undefined(name='next_node') if l_0_next_node is missing else l_0_next_node))):
        pass
        yield '\n    data-next-node-mid="'
        yield escape(environment.getattr((undefined(name='next_node') if l_0_next_node is missing else l_0_next_node), 'reserved_mid'))
        yield '"\n    '
    yield '>\n  <td class="content-view__add_new_row-TD" colspan="100%">\n    <div class="table-add-node"\n         js-table_view_edit-add-node\n         data-mode="closed">\n      <div class="add_new_row_handler"\n           js-table_view_edit-add-node-handle\n           data-testid="table-add-node-handle"\n           role="button"\n           tabindex="0"\n           aria-expanded="false"\n           aria-label="Add node"></div>\n      <div class="table-add-node__menu"\n           js-table_view_edit-add-node-menu\n           data-testid="table-add-node-menu"\n           hidden>\n        <div class="table-add-node__menu-body">'
    if (not (undefined(name='can_use_separator') if l_0_can_use_separator is missing else l_0_can_use_separator)):
        pass
        yield '\n            <p class="table-add-node__message"\n               js-table_view_edit-add-node-state>\n              Table Add is not available here.\n            </p>'
    else:
        pass
        yield '<div class="table-add-node__blockers"\n                 js-table_view_edit-add-node-blockers\n                 data-testid="table-add-node-blockers"\n                 hidden>\n            </div>\n            <p class="table-add-node__message table-add-node__message--hidden"\n               js-table_view_edit-add-node-state\n               hidden>\n            </p>\n            <ul class="table-add-node__actions"\n                js-table_view_edit-add-node-actions>'
        for l_1_element in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_grammar_elements')):
            _loop_vars = {}
            pass
            yield '<li class="table-add-node__element">'
            yield escape(environment.getattr(l_1_element, 'tag'))
            yield ':</li>'
            if (undefined(name='can_add_first_node') if l_0_can_add_first_node is missing else l_0_can_add_first_node):
                pass
                yield '<li class="table-add-node__action" data-whereto="child">\n                    <button class="table-add-node__action-button"\n                            type="button"\n                            js-table_view_edit-add-node-action\n                            data-testid="table-add-node-action-'
                yield escape(t_1(environment.getattr(l_1_element, 'tag')))
                yield '-child"\n                            data-context-document-mid="'
                yield escape((undefined(name='table_document_mid') if l_0_table_document_mid is missing else l_0_table_document_mid))
                yield '"\n                            data-reference-mid="'
                yield escape((undefined(name='table_document_mid') if l_0_table_document_mid is missing else l_0_table_document_mid))
                yield '"\n                            data-element-type="'
                yield escape(environment.getattr(l_1_element, 'tag'))
                yield '"\n                            data-whereto="child"\n                            title="Add first '
                yield escape(environment.getattr(l_1_element, 'tag'))
                yield '">\n                      '
                template = environment.get_template('icons/ico16_add.svg', 'screens/document/table/row_add_new_node.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'element': l_1_element, 'can_add_after_prev': l_0_can_add_after_prev, 'can_add_before_next': l_0_can_add_before_next, 'can_add_child_of_prev': l_0_can_add_child_of_prev, 'can_add_first_node': l_0_can_add_first_node, 'can_use_separator': l_0_can_use_separator, 'table_document_mid': l_0_table_document_mid}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n                    </button>\n                  </li>'
            if (undefined(name='can_add_before_next') if l_0_can_add_before_next is missing else l_0_can_add_before_next):
                pass
                yield '<li class="table-add-node__action" data-whereto="before">\n                    <button class="table-add-node__action-button"\n                            type="button"\n                            js-table_view_edit-add-node-action\n                            data-testid="table-add-node-action-'
                yield escape(t_1(environment.getattr(l_1_element, 'tag')))
                yield '-before"\n                            data-context-document-mid="'
                yield escape((undefined(name='table_document_mid') if l_0_table_document_mid is missing else l_0_table_document_mid))
                yield '"\n                            data-reference-mid="'
                yield escape(environment.getattr((undefined(name='next_node') if l_0_next_node is missing else l_0_next_node), 'reserved_mid'))
                yield '"\n                            data-element-type="'
                yield escape(environment.getattr(l_1_element, 'tag'))
                yield '"\n                            data-whereto="before"\n                            title="Add '
                yield escape(environment.getattr(l_1_element, 'tag'))
                yield ' before next">\n                      '
                template = environment.get_template('icons/ico16_add_above.svg', 'screens/document/table/row_add_new_node.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'element': l_1_element, 'can_add_after_prev': l_0_can_add_after_prev, 'can_add_before_next': l_0_can_add_before_next, 'can_add_child_of_prev': l_0_can_add_child_of_prev, 'can_add_first_node': l_0_can_add_first_node, 'can_use_separator': l_0_can_use_separator, 'table_document_mid': l_0_table_document_mid}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n                    </button>\n                  </li>'
            if (undefined(name='can_add_after_prev') if l_0_can_add_after_prev is missing else l_0_can_add_after_prev):
                pass
                yield '<li class="table-add-node__action" data-whereto="after">\n                    <button class="table-add-node__action-button"\n                            type="button"\n                            js-table_view_edit-add-node-action\n                            data-testid="table-add-node-action-'
                yield escape(t_1(environment.getattr(l_1_element, 'tag')))
                yield '-after"\n                            data-context-document-mid="'
                yield escape((undefined(name='table_document_mid') if l_0_table_document_mid is missing else l_0_table_document_mid))
                yield '"\n                            data-reference-mid="'
                yield escape(environment.getattr((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node), 'reserved_mid'))
                yield '"\n                            data-element-type="'
                yield escape(environment.getattr(l_1_element, 'tag'))
                yield '"\n                            data-whereto="after"\n                            title="Add '
                yield escape(environment.getattr(l_1_element, 'tag'))
                yield ' after previous">\n                      '
                template = environment.get_template('icons/ico16_add_below.svg', 'screens/document/table/row_add_new_node.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'element': l_1_element, 'can_add_after_prev': l_0_can_add_after_prev, 'can_add_before_next': l_0_can_add_before_next, 'can_add_child_of_prev': l_0_can_add_child_of_prev, 'can_add_first_node': l_0_can_add_first_node, 'can_use_separator': l_0_can_use_separator, 'table_document_mid': l_0_table_document_mid}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n                    </button>\n                  </li>'
            if (undefined(name='can_add_child_of_prev') if l_0_can_add_child_of_prev is missing else l_0_can_add_child_of_prev):
                pass
                yield '<li class="table-add-node__action" data-whereto="child">\n                    <button class="table-add-node__action-button"\n                            type="button"\n                            js-table_view_edit-add-node-action\n                            data-testid="table-add-node-action-'
                yield escape(t_1(environment.getattr(l_1_element, 'tag')))
                yield '-child"\n                            data-context-document-mid="'
                yield escape((undefined(name='table_document_mid') if l_0_table_document_mid is missing else l_0_table_document_mid))
                yield '"\n                            data-reference-mid="'
                yield escape(environment.getattr((undefined(name='prev_node') if l_0_prev_node is missing else l_0_prev_node), 'reserved_mid'))
                yield '"\n                            data-element-type="'
                yield escape(environment.getattr(l_1_element, 'tag'))
                yield '"\n                            data-whereto="child"\n                            title="Add '
                yield escape(environment.getattr(l_1_element, 'tag'))
                yield ' as child of previous">\n                      '
                template = environment.get_template('icons/ico16_add_child.svg', 'screens/document/table/row_add_new_node.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'element': l_1_element, 'can_add_after_prev': l_0_can_add_after_prev, 'can_add_before_next': l_0_can_add_before_next, 'can_add_child_of_prev': l_0_can_add_child_of_prev, 'can_add_first_node': l_0_can_add_first_node, 'can_use_separator': l_0_can_use_separator, 'table_document_mid': l_0_table_document_mid}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                yield '\n                    </button>\n                  </li>'
        l_1_element = missing
        yield '</ul>'
    yield '</div>\n      </div>\n    </div>\n  </td>\n</tr>'

blocks = {}
debug_info = '1=27&2=33&3=36&4=39&5=42&6=45&7=48&10=52&11=55&13=58&14=61&32=64&49=70&50=74&51=76&56=79&57=81&58=83&59=85&61=87&62=89&66=96&71=99&72=101&73=103&74=105&76=107&77=109&81=116&86=119&87=121&88=123&89=125&91=127&92=129&96=136&101=139&102=141&103=143&104=145&106=147&107=149'