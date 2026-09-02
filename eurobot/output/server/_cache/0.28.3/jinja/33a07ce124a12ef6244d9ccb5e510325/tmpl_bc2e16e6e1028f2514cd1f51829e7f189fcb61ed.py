from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_coverage/thead.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '\n\n<colgroup>\n  <col />\n  <col data-id="lines_percent" class="project_coverage-col-line" />\n  <col data-id="lines_covered" class="project_coverage-col-line" />\n  <col data-id="lines_total" class="project_coverage-col-line" />\n  <col data-id="lines_all" class="project_coverage-col-line" />\n  <col data-id="func_percent" class="project_coverage-col-func" />\n  <col data-id="func_covered" class="project_coverage-col-func" />\n  <col data-id="func_total" class="project_coverage-col-func" />\n</colgroup>\n<thead>\n  <tr>\n    <th rowspan="2"><div class="project_coverage-sort_reset">File path</div></th>\n    <th colspan="4" class="project_coverage-col-line">Code lines covered by&nbsp;requirements</th>\n    <th colspan="3" class="project_coverage-col-func">Functions covered by&nbsp;requirements</th>\n  </tr>\n  <tr>\n    \n    <th class="project_coverage-col-line">\n      <div data-id="lines_percent" class="project_coverage-sort_handler">%</div>\n    </th>\n    <th class="project_coverage-col-line">\n      <div data-id="lines_covered" class="project_coverage-sort_handler">#</div>\n    </th>\n    <th class="project_coverage-col-line">\n      <div data-id="lines_total" class="project_coverage-sort_handler">Code LOC</div>\n    </th>\n    <th class="project_coverage-col-line color-secondary">\n      <div data-id="lines_all" class="project_coverage-sort_handler">Total LOC</div>\n    </th>\n    <th class="project_coverage-col-func">\n      <div data-id="func_percent" class="project_coverage-sort_handler">%</div>\n    </th>\n    <th class="project_coverage-col-func">\n      <div data-id="func_covered" class="project_coverage-sort_handler">#</div>\n    </th>\n    <th class="project_coverage-col-func">\n      <div data-id="func_total" class="project_coverage-sort_handler">Total func.</div>\n    </th>\n  </tr>\n</thead>'

blocks = {}
debug_info = ''