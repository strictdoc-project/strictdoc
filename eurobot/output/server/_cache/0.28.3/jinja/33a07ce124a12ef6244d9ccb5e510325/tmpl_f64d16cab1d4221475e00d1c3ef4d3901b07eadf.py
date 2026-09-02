from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_file_view/file_stats.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<div class="sdoc-table_key_value">\n  \n  <div class="sdoc-table_key_value-key">Path:</div>\n  <div class="sdoc-table_key_value-value">'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_source_file_path')))
    yield '</div>\n  <div class="sdoc-table_key_value-key">Lines:</div>\n  <div class="sdoc-table_key_value-value">'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_lines_total')))
    yield '</div>\n  <div class="sdoc-table_key_value-key">Non-empty lines:</div>\n  <div class="sdoc-table_key_value-value">'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_lines_total_non_empty')))
    yield '</div>\n  <div class="sdoc-table_key_value-key">Non-empty lines covered with requirements:</div>\n  <div class="sdoc-table_key_value-value">'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_non_empty_lines_covered')))
    yield '</div>\n  <div class="sdoc-table_key_value-key">Functions:</div>\n  <div class="sdoc-table_key_value-value">'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_functions_total')))
    yield '</div>\n  <div class="sdoc-table_key_value-key">Functions covered by requirements:</div>\n  <div class="sdoc-table_key_value-value">'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_functions_covered')))
    yield '</div>\n</div>'

blocks = {}
debug_info = '4=13&6=15&8=17&10=19&12=21&14=23'