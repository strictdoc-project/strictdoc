from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/node/node_controls/card.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_sdoc_entity = resolve('sdoc_entity')
    pass
    yield '\n\n\n\n<sdoc-node-controls data-direction="row">\n  <a\n    href="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), 'render_node_link'), (undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_document_type'), allow_local=False))
    yield '"\n    class="action_button"\n    title="Find it in the document view"\n    data-testid="'
    yield escape(context.call(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'get_type_string')))
    yield '-find-in-document"\n  >'
    template = environment.get_template('icons/ico16_go_to_doc.svg', 'components/node/node_controls/card.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</a>\n  <turbo-frame>\n    <a\n      href="/actions/show_full_node?reference_mid='
    yield escape(environment.getattr((undefined(name='sdoc_entity') if l_0_sdoc_entity is missing else l_0_sdoc_entity), 'reserved_mid'))
    yield '"\n      class="action_button"\n      data-turbo="true"\n      data-turbo-action="replace"\n      title="Show in full in modal"\n      data-testid="node-show-more-action"\n    >'
    template = environment.get_template('icons/ico16_maximize.svg', 'components/node/node_controls/card.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</a>\n  </turbo-frame>\n</sdoc-node-controls>'

blocks = {}
debug_info = '17=14&20=16&21=18&24=25&30=27'