from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/document/move_node/_move_node_modal_confirmation_message.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<div\n  class="move_node_confirmation_target_document"\n>\n  <span\n    class="move_node_confirmation_message_label"\n    data-js-move-node-tree-confirm-message-label\n    data-testid="move-node-confirm-message-label"\n  ></span>\n  <span class="move_node_tree__document_icon" aria-hidden="true">'
    template = environment.get_template('icons/ico16_document.svg', 'actions/document/move_node/_move_node_modal_confirmation_message.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</span>\n  <span\n    class="move_node_tree__title"\n    data-js-move-node-tree-confirm-target-document-title\n    data-testid="move-node-confirm-target-document-title"\n    title=""\n  ></span>\n</div>\n\n<div\n  class="move_node_confirmation_target_node"\n  data-js-move-node-tree-confirm-target-node-info\n>\n  <span\n    class="move_node_confirmation_placement_label"\n    data-js-move-node-tree-confirm-placement-label\n    data-testid="move-node-confirm-placement-label"\n  ></span>\n  <span\n    data-js-move-node-tree-confirm-target-node-type\n    data-testid="move-node-confirm-target-node-type"\n  >\n    '
    l_1_badge_text = '→'
    pass
    yield '\n      '
    template = environment.get_template('components/badge/index.jinja', 'actions/document/move_node/_move_node_modal_confirmation_message.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_1_badge_text}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    '
    l_1_badge_text = missing
    yield '\n  </span>\n  <span\n    class="move_node_confirmation_target_node_title"\n    data-js-move-node-tree-confirm-target-node-title\n    data-testid="move-node-confirm-target-node-title"\n  ></span>\n</div>'

blocks = {}
debug_info = '10=12&34=22'