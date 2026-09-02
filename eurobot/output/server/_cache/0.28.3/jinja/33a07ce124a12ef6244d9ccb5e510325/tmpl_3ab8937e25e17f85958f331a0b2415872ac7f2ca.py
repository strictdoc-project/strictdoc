from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/frame_diff_result.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<turbo-frame id="diff_result">\n'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'results'):
        pass
        yield '\n  <div class="diff preloaded">\n    '
        template = environment.get_template('features/diff_and_changelog/diff_controls.jinja', 'features/diff_and_changelog/frame_diff_result.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n\n    <div class="diff_column" left>\n      <div class="diff_inner">'
        l_1_document_tree = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_tree_lhs')
        l_1_document_tree_iterator = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'documents_iterator_lhs')
        l_1_traceability_index = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index_lhs')
        l_1_self_stats = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'lhs_stats')
        l_1_other_stats = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'rhs_stats')
        l_1_tab = 'diff'
        l_1_side = 'left'
        pass
        template = environment.get_template('features/diff_and_changelog/diff_content.jinja', 'features/diff_and_changelog/frame_diff_result.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'document_tree': l_1_document_tree, 'document_tree_iterator': l_1_document_tree_iterator, 'other_stats': l_1_other_stats, 'self_stats': l_1_self_stats, 'side': l_1_side, 'tab': l_1_tab, 'traceability_index': l_1_traceability_index}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_document_tree = l_1_document_tree_iterator = l_1_traceability_index = l_1_self_stats = l_1_other_stats = l_1_tab = l_1_side = missing
        yield '</div>\n    </div>\n    <div class="diff_column" right>\n      <div class="diff_inner">'
        l_1_document_tree = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_tree_rhs')
        l_1_document_tree_iterator = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'documents_iterator_rhs')
        l_1_traceability_index = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index_rhs')
        l_1_self_stats = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'rhs_stats')
        l_1_other_stats = environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'lhs_stats')
        l_1_tab = 'diff'
        l_1_side = 'right'
        pass
        template = environment.get_template('features/diff_and_changelog/diff_content.jinja', 'features/diff_and_changelog/frame_diff_result.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'document_tree': l_1_document_tree, 'document_tree_iterator': l_1_document_tree_iterator, 'other_stats': l_1_other_stats, 'self_stats': l_1_self_stats, 'side': l_1_side, 'tab': l_1_tab, 'traceability_index': l_1_traceability_index}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_document_tree = l_1_document_tree_iterator = l_1_traceability_index = l_1_self_stats = l_1_other_stats = l_1_tab = l_1_side = missing
        yield '</div>\n    </div>\n  </div>\n'
    yield '\n</turbo-frame>'

blocks = {}
debug_info = '2=13&4=16&17=31&32=47'