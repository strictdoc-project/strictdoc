from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_coverage/file.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_file = resolve('file')
    l_0_folder = resolve('folder')
    l_0_source_file = l_0_lines_all = l_0_lines_total = l_0_lines_covered = l_0_lines_percent = l_0_func_total = l_0_func_covered = l_0_func_percent = missing
    pass
    l_0_source_file = context.call(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'document_tree'), 'source_tree'), 'get_source_for_file'), (undefined(name='file') if l_0_file is missing else l_0_file))
    context.vars['source_file'] = l_0_source_file
    context.exported_vars.add('source_file')
    l_0_lines_all = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_lines_total'), (undefined(name='source_file') if l_0_source_file is missing else l_0_source_file))
    context.vars['lines_all'] = l_0_lines_all
    context.exported_vars.add('lines_all')
    yield '\n'
    l_0_lines_total = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_lines_total_non_empty'), (undefined(name='source_file') if l_0_source_file is missing else l_0_source_file))
    context.vars['lines_total'] = l_0_lines_total
    context.exported_vars.add('lines_total')
    yield '\n'
    l_0_lines_covered = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_non_empty_lines_covered'), (undefined(name='source_file') if l_0_source_file is missing else l_0_source_file))
    context.vars['lines_covered'] = l_0_lines_covered
    context.exported_vars.add('lines_covered')
    yield '\n'
    l_0_lines_percent = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_non_empty_lines_covered_percentage'), (undefined(name='source_file') if l_0_source_file is missing else l_0_source_file))
    context.vars['lines_percent'] = l_0_lines_percent
    context.exported_vars.add('lines_percent')
    yield '\n'
    l_0_func_total = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_functions_total'), (undefined(name='source_file') if l_0_source_file is missing else l_0_source_file))
    context.vars['func_total'] = l_0_func_total
    context.exported_vars.add('func_total')
    yield '\n'
    l_0_func_covered = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_functions_covered'), (undefined(name='source_file') if l_0_source_file is missing else l_0_source_file))
    context.vars['func_covered'] = l_0_func_covered
    context.exported_vars.add('func_covered')
    yield '\n'
    l_0_func_percent = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_file_stats_functions_covered_percentage'), (undefined(name='source_file') if l_0_source_file is missing else l_0_source_file))
    context.vars['func_percent'] = l_0_func_percent
    context.exported_vars.add('func_percent')
    yield '\n\n<tr class="project_coverage-file '
    if ((undefined(name='lines_covered') if l_0_lines_covered is missing else l_0_lines_covered) == '0'):
        pass
        yield 'project_coverage-file_uncovered'
    yield '">\n  <td>\n    <a\n      class="project_coverage-file-link"\n      '
    if environment.getattr((undefined(name='source_file') if l_0_source_file is missing else l_0_source_file), 'is_referenced'):
        pass
        yield 'href="'
        yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'link_renderer'), 'render_source_file_link_from_root_2'), (undefined(name='source_file') if l_0_source_file is missing else l_0_source_file)))
        yield '"'
    yield 'title="'
    yield escape(environment.getattr((undefined(name='source_file') if l_0_source_file is missing else l_0_source_file), 'in_doctree_source_file_rel_path_posix'))
    yield '"\n    >\n      <div class="project_coverage-file-indent" style="padding-left:'
    yield escape(environment.getattr((undefined(name='folder') if l_0_folder is missing else l_0_folder), 'level'))
    yield '0px"></div>\n      <div class="project_coverage-file-details">\n        <div class="project_coverage-file-title">\n          <span class="project_coverage-file-icon">'
    template = environment.get_template('icons/ico16_file.svg', 'features/source_coverage/file.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'func_covered': l_0_func_covered, 'func_percent': l_0_func_percent, 'func_total': l_0_func_total, 'lines_all': l_0_lines_all, 'lines_covered': l_0_lines_covered, 'lines_percent': l_0_lines_percent, 'lines_total': l_0_lines_total, 'source_file': l_0_source_file}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</span>\n          '
    yield escape(environment.getattr((undefined(name='file') if l_0_file is missing else l_0_file), 'file_name'))
    yield '\n        </div>\n        <div class="project_coverage-file-path">\n          '
    yield escape(environment.getattr((undefined(name='source_file') if l_0_source_file is missing else l_0_source_file), 'in_doctree_source_file_rel_path_posix'))
    yield '\n        </div>\n      </div>\n\n    </a>\n  </td>\n\n  \n\n  <td data-id="lines_percent" data-value="'
    yield escape((undefined(name='lines_percent') if l_0_lines_percent is missing else l_0_lines_percent))
    yield '"><span class="value_extended '
    if ((undefined(name='lines_covered') if l_0_lines_covered is missing else l_0_lines_covered) == '0'):
        pass
        yield 'color-uncovered'
    yield '" data-ext="%">'
    yield escape((undefined(name='lines_percent') if l_0_lines_percent is missing else l_0_lines_percent))
    yield '</span></td>\n  <td data-id="lines_covered" data-value="'
    yield escape((undefined(name='lines_covered') if l_0_lines_covered is missing else l_0_lines_covered))
    yield '"><span class="value_extended '
    if ((undefined(name='lines_covered') if l_0_lines_covered is missing else l_0_lines_covered) == '0'):
        pass
        yield 'color-uncovered'
    yield '">'
    yield escape((undefined(name='lines_covered') if l_0_lines_covered is missing else l_0_lines_covered))
    yield '</span></td>\n  <td data-id="lines_total" data-value="'
    yield escape((undefined(name='lines_total') if l_0_lines_total is missing else l_0_lines_total))
    yield '"><span class="value_extended">'
    yield escape((undefined(name='lines_total') if l_0_lines_total is missing else l_0_lines_total))
    yield '</span></td>\n  <td data-id="lines_all" data-value="'
    yield escape((undefined(name='lines_all') if l_0_lines_all is missing else l_0_lines_all))
    yield '"><span class="value_extended color-secondary">'
    yield escape((undefined(name='lines_all') if l_0_lines_all is missing else l_0_lines_all))
    yield '</span></td>\n  <td data-id="func_percent" data-value="'
    yield escape((undefined(name='func_percent') if l_0_func_percent is missing else l_0_func_percent))
    yield '"><span class="value_extended" data-ext="%">'
    yield escape((undefined(name='func_percent') if l_0_func_percent is missing else l_0_func_percent))
    yield '</span></td>\n  <td data-id="func_covered" data-value="'
    yield escape((undefined(name='func_covered') if l_0_func_covered is missing else l_0_func_covered))
    yield '"><span class="value_extended">'
    yield escape((undefined(name='func_covered') if l_0_func_covered is missing else l_0_func_covered))
    yield '</span></td>\n  <td data-id="func_total" data-value="'
    yield escape((undefined(name='func_total') if l_0_func_total is missing else l_0_func_total))
    yield '"><span class="value_extended">'
    yield escape((undefined(name='func_total') if l_0_func_total is missing else l_0_func_total))
    yield '</span></td>\n\n  \n</tr>'

blocks = {}
debug_info = '1=15&3=18&4=22&5=26&6=30&7=34&8=38&9=42&11=46&15=50&16=53&18=56&20=58&24=60&26=67&29=69&43=71&44=79&45=87&46=91&47=95&48=99&49=103'