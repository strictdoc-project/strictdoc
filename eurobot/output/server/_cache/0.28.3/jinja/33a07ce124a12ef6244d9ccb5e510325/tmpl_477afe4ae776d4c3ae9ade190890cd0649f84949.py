from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/move_node/_project_move_tree.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_moved_node = resolve('moved_node')
    l_0_source_document = resolve('source_document')
    l_0_view_object = resolve('view_object')
    l_0_render_tree_item = l_0_render_node = missing
    try:
        t_1 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_2 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_3 = environment.filters['string']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'string' found.")
    pass
    yield '\n'
    def macro(l_1_item_, l_1_item_kind_, l_1_title_, l_1_child_nodes_, l_1_is_incompatible):
        t_4 = []
        l_1_subtree_mids = resolve('subtree_mids')
        l_1_initially_expanded_mids = resolve('initially_expanded_mids')
        l_1_incompatible_document_mids = resolve('incompatible_document_mids')
        l_1_mid_str = l_1_is_moved = l_1_is_in_moved_branch = l_1_can_contain_children = l_1_is_target = l_1_is_expanded = missing
        if l_1_item_ is missing:
            l_1_item_ = undefined("parameter 'item_' was not provided", name='item_')
        if l_1_item_kind_ is missing:
            l_1_item_kind_ = undefined("parameter 'item_kind_' was not provided", name='item_kind_')
        if l_1_title_ is missing:
            l_1_title_ = undefined("parameter 'title_' was not provided", name='title_')
        if l_1_child_nodes_ is missing:
            l_1_child_nodes_ = undefined("parameter 'child_nodes_' was not provided", name='child_nodes_')
        if l_1_is_incompatible is missing:
            l_1_is_incompatible = False
        pass
        l_1_mid_str = t_3(environment.getattr(l_1_item_, 'reserved_mid'))
        l_1_is_moved = ((l_1_item_kind_ == 'node') and ((undefined(name='mid_str') if l_1_mid_str is missing else l_1_mid_str) == t_3(environment.getattr((undefined(name='moved_node') if l_0_moved_node is missing else l_0_moved_node), 'reserved_mid'))))
        l_1_is_in_moved_branch = ((l_1_item_kind_ == 'node') and ((undefined(name='mid_str') if l_1_mid_str is missing else l_1_mid_str) in (undefined(name='subtree_mids') if l_1_subtree_mids is missing else l_1_subtree_mids)))
        l_1_can_contain_children = ((l_1_item_kind_ == 'document') or environment.getattr(l_1_item_, 'is_composite'))
        l_1_is_target = ((not l_1_is_incompatible) and (not (undefined(name='is_in_moved_branch') if l_1_is_in_moved_branch is missing else l_1_is_in_moved_branch)))
        l_1_is_expanded = ((undefined(name='mid_str') if l_1_mid_str is missing else l_1_mid_str) in (undefined(name='initially_expanded_mids') if l_1_initially_expanded_mids is missing else l_1_initially_expanded_mids))
        t_4.append(
            '<li\n    class="move_node_tree__item',
        )
        if (l_1_item_kind_ == 'document'):
            pass
            t_4.append(
                ' move_node_tree__item--document',
            )
        if (undefined(name='is_moved') if l_1_is_moved is missing else l_1_is_moved):
            pass
            t_4.append(
                ' move_node_tree__item--moved',
            )
        if (undefined(name='is_in_moved_branch') if l_1_is_in_moved_branch is missing else l_1_is_in_moved_branch):
            pass
            t_4.append(
                ' move_node_tree__item--moved_branch',
            )
        if l_1_is_incompatible:
            pass
            t_4.append(
                ' move_node_tree__item--incompatible',
            )
        t_4.extend((
            '"\n    data-js-move-node-tree-item\n    data-js-move-node-tree-node-mid="',
            escape((undefined(name='mid_str') if l_1_mid_str is missing else l_1_mid_str)),
            '"\n    data-js-move-node-tree-label="',
            escape(l_1_title_),
            '"\n    ',
        ))
        if (l_1_item_kind_ == 'node'):
            pass
            t_4.extend((
                'data-js-move-node-tree-node-type="',
                escape(environment.getattr(l_1_item_, 'node_type')),
                '"',
            ))
        t_4.append(
            '\n    ',
        )
        if (l_1_item_kind_ == 'document'):
            pass
            t_4.append(
                'data-js-move-node-tree-document',
            )
        t_4.append(
            '\n    ',
        )
        if (undefined(name='is_moved') if l_1_is_moved is missing else l_1_is_moved):
            pass
            t_4.append(
                'data-js-move-node-tree-moved',
            )
        t_4.append(
            '\n    ',
        )
        if (undefined(name='is_in_moved_branch') if l_1_is_in_moved_branch is missing else l_1_is_in_moved_branch):
            pass
            t_4.append(
                'data-js-move-node-tree-moved-branch',
            )
        t_4.append(
            '\n    ',
        )
        if l_1_is_incompatible:
            pass
            t_4.append(
                'data-js-move-node-tree-incompatible',
            )
        t_4.append(
            '\n    ',
        )
        if l_1_is_incompatible:
            pass
            t_4.extend((
                '\n      title="Grammar mismatch: ',
                escape(t_1(context.eval_ctx, environment.getitem((undefined(name='incompatible_document_mids') if l_1_incompatible_document_mids is missing else l_1_incompatible_document_mids), (undefined(name='mid_str') if l_1_mid_str is missing else l_1_mid_str)), '; ')),
                '"\n    ',
            ))
        t_4.append(
            '\n    ',
        )
        if (l_1_item_kind_ == 'document'):
            pass
            t_4.append(
                '\n      data-testid="move-node-document"\n    ',
            )
        else:
            pass
            t_4.append(
                '\n      data-testid="move-node-row"\n    ',
            )
        t_4.append(
            '\n  >\n    <div\n      class="move_node_tree__row"\n      ',
        )
        if (undefined(name='is_target') if l_1_is_target is missing else l_1_is_target):
            pass
            t_4.extend((
                '\n        data-js-move-node-tree-target\n        data-js-move-node-tree-target-mid="',
                escape((undefined(name='mid_str') if l_1_mid_str is missing else l_1_mid_str)),
                '"\n        data-js-move-node-tree-target-placements="',
            ))
            if (l_1_item_kind_ == 'document'):
                pass
                t_4.append(
                    'child',
                )
            elif (undefined(name='can_contain_children') if l_1_can_contain_children is missing else l_1_can_contain_children):
                pass
                t_4.append(
                    'before child after',
                )
            else:
                pass
                t_4.append(
                    'before after',
                )
            t_4.append(
                '"\n      ',
            )
        t_4.append(
            '\n    >\n      ',
        )
        if (t_2(l_1_child_nodes_) > 0):
            pass
            t_4.extend((
                '\n        <button\n          type="button"\n          class="move_node_tree__collapse"\n          data-js-move-node-tree-collapse\n          aria-expanded="',
                escape(('true' if (undefined(name='is_expanded') if l_1_is_expanded is missing else l_1_is_expanded) else 'false')),
                '"\n          aria-label="',
                escape(('Collapse' if (undefined(name='is_expanded') if l_1_is_expanded is missing else l_1_is_expanded) else 'Expand')),
                ' ',
                escape(l_1_title_),
                '"\n        ></button>\n      ',
            ))
        else:
            pass
            t_4.append(
                '\n        <span class="move_node_tree__collapse_spacer" aria-hidden="true"></span>\n      ',
            )
        t_4.append(
            '\n\n      ',
        )
        if (l_1_item_kind_ == 'document'):
            pass
            t_4.append(
                '\n        <span class="move_node_tree__document_icon" aria-hidden="true">',
            )
            template = environment.get_template('icons/ico16_document.svg', 'actions/document/move_node/_project_move_tree.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'can_contain_children': l_1_can_contain_children, 'child_nodes_': l_1_child_nodes_, 'is_expanded': l_1_is_expanded, 'is_in_moved_branch': l_1_is_in_moved_branch, 'is_incompatible': l_1_is_incompatible, 'is_moved': l_1_is_moved, 'is_target': l_1_is_target, 'item_': l_1_item_, 'item_kind_': l_1_item_kind_, 'mid_str': l_1_mid_str, 'title_': l_1_title_, 'render_node': l_0_render_node, 'render_tree_item': l_0_render_tree_item}))
            try:
                for event in gen:
                    t_4.append(event)
            finally: gen.close()
            t_4.append(
                '</span>\n      ',
            )
        else:
            pass
            t_4.append(
                '\n        <span data-testid="move-node-type">\n          ',
            )
            l_2_badge_text = environment.getattr(l_1_item_, 'node_type')
            pass
            t_4.append(
                '\n            ',
            )
            template = environment.get_template('components/badge/index.jinja', 'actions/document/move_node/_project_move_tree.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_2_badge_text, 'can_contain_children': l_1_can_contain_children, 'child_nodes_': l_1_child_nodes_, 'is_expanded': l_1_is_expanded, 'is_in_moved_branch': l_1_is_in_moved_branch, 'is_incompatible': l_1_is_incompatible, 'is_moved': l_1_is_moved, 'is_target': l_1_is_target, 'item_': l_1_item_, 'item_kind_': l_1_item_kind_, 'mid_str': l_1_mid_str, 'title_': l_1_title_, 'render_node': l_0_render_node, 'render_tree_item': l_0_render_tree_item}))
            try:
                for event in gen:
                    t_4.append(event)
            finally: gen.close()
            t_4.append(
                '\n          ',
            )
            l_2_badge_text = missing
            t_4.append(
                '\n        </span>\n      ',
            )
        t_4.extend((
            '\n\n      <span\n        class="move_node_tree__title"\n        data-js-move-node-tree-title\n        data-testid="move-node-title"\n      >',
            escape(l_1_title_),
            '</span>\n    </div>\n\n    ',
        ))
        if (t_2(l_1_child_nodes_) > 0):
            pass
            t_4.append(
                '\n      <ul\n        class="move_node_tree__children"\n        data-js-move-node-tree-children\n        ',
            )
            if (not (undefined(name='is_expanded') if l_1_is_expanded is missing else l_1_is_expanded)):
                pass
                t_4.append(
                    'hidden',
                )
            t_4.append(
                '\n      >\n        ',
            )
            for l_2_child_ in l_1_child_nodes_:
                _loop_vars = {}
                pass
                t_4.extend((
                    '\n          ',
                    escape(context.call((undefined(name='render_node') if l_0_render_node is missing else l_0_render_node), l_2_child_, _loop_vars=_loop_vars)),
                    '\n        ',
                ))
            l_2_child_ = missing
            t_4.append(
                '\n      </ul>\n    ',
            )
        t_4.append(
            '\n  </li>\n',
        )
        return concat(t_4)
    context.exported_vars.add('render_tree_item')
    context.vars['render_tree_item'] = l_0_render_tree_item = Macro(environment, macro, 'render_tree_item', ('item_', 'item_kind_', 'title_', 'child_nodes_', 'is_incompatible'), False, False, False, context.eval_ctx.autoescape)
    yield '\n\n'
    def macro(l_1_node_):
        t_5 = []
        if l_1_node_ is missing:
            l_1_node_ = undefined("parameter 'node_' was not provided", name='node_')
        pass
        t_5.extend((
            '\n  ',
            escape(context.call((undefined(name='render_tree_item') if l_0_render_tree_item is missing else l_0_render_tree_item), l_1_node_, 'node', context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_move_node_tree_title'), l_1_node_), context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_move_node_tree_child_nodes'), l_1_node_))),
            '\n',
        ))
        return concat(t_5)
    context.exported_vars.add('render_node')
    context.vars['render_node'] = l_0_render_node = Macro(environment, macro, 'render_node', ('node_',), False, False, False, context.eval_ctx.autoescape)
    yield '\n\n<div\n  class="move_node_tree"\n  data-js-move-node-tree\n  data-testid="move-node-tree"\n  data-js-move-node-tree-moved-node-mid="'
    yield escape(environment.getattr((undefined(name='moved_node') if l_0_moved_node is missing else l_0_moved_node), 'reserved_mid'))
    yield '"\n  data-js-move-node-tree-context-document-mid="'
    yield escape(environment.getattr((undefined(name='source_document') if l_0_source_document is missing else l_0_source_document), 'reserved_mid'))
    yield '"\n  data-js-move-node-tree-endpoint="/actions/document/move_node_across_documents"\n>\n  <p class="move_node_tree__instructions" id="move-node-tree-instructions">\n    Point to a node to choose before or after. Composite nodes and documents\n    also accept the node inside them.\n  </p>\n  <div\n    class="move_node_tree__status"\n    data-js-move-node-tree-status\n    role="status"\n    aria-live="polite"\n  ></div>\n  <div\n    class="move_node_tree__confirmation"\n    data-js-move-node-tree-confirmation\n    data-testid="move-node-confirmation"\n    role="dialog"\n    aria-modal="true"\n    aria-labelledby="move-node-confirmation-title"\n    hidden\n  >\n    <div class="move_node_tree__confirmation_dialog">\n      <div\n        class="move_node_tree__confirmation_title"\n        id="move-node-confirmation-title"\n      >\n        Confirm move\n      </div>\n      <sdoc-modal-message\n        class="move_node_modal_confirmation_message"\n        data-js-move-node-tree-confirmation-message\n        data-testid="move-node-confirmation-message"\n      >\n        '
    template = environment.get_template('actions/document/move_node/_move_node_modal_confirmation_message.jinja', 'actions/document/move_node/_project_move_tree.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'render_node': l_0_render_node, 'render_tree_item': l_0_render_tree_item}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n      </sdoc-modal-message>\n      <div class="move_node_tree__confirmation_actions">\n        <button\n          type="button"\n          class="action_button"\n          data-action-type="confirm_move"\n          data-js-move-node-tree-confirm\n          data-testid="move-node-confirm"\n        >Yes</button>\n        <button\n          type="button"\n          class="action_button"\n          data-action-type="cancel"\n          data-js-move-node-tree-cancel\n          data-testid="move-node-cancel"\n        >Cancel</button>\n      </div>\n    </div>\n  </div>\n  <ul class="move_node_tree__list" aria-describedby="move-node-tree-instructions">'
    for l_1_document_ in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_project_documents')):
        l_1_incompatible_document_mids = resolve('incompatible_document_mids')
        l_1_document_mid_str = missing
        _loop_vars = {}
        pass
        l_1_document_mid_str = t_3(environment.getattr(l_1_document_, 'reserved_mid'))
        _loop_vars['document_mid_str'] = l_1_document_mid_str
        yield escape(context.call((undefined(name='render_tree_item') if l_0_render_tree_item is missing else l_0_render_tree_item), l_1_document_, 'document', environment.getattr(l_1_document_, 'title'), context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_move_node_tree_child_nodes'), l_1_document_, _loop_vars=_loop_vars), ((undefined(name='document_mid_str') if l_1_document_mid_str is missing else l_1_document_mid_str) in (undefined(name='incompatible_document_mids') if l_1_incompatible_document_mids is missing else l_1_incompatible_document_mids)), _loop_vars=_loop_vars))
    l_1_document_ = l_1_document_mid_str = l_1_incompatible_document_mids = missing
    yield '\n  </ul>\n</div>'

blocks = {}
debug_info = '8=34&9=51&10=52&11=53&12=54&13=55&14=56&16=60&18=82&19=84&20=87&21=97&22=105&23=113&24=121&25=129&26=133&28=139&36=152&38=156&39=159&42=180&47=184&48=186&54=199&56=204&61=223&70=238&73=241&77=246&79=254&80=259&87=273&88=280&100=287&101=289&135=291&156=298&157=303&158=305'