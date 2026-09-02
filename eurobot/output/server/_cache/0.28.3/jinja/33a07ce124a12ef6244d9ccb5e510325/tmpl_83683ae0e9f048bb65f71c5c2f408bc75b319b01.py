from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/static_search/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<div id="search" class="search-box">\n  <div class="search-input">\n      <input type="text" id="userinput" tabindex="2" placeholder="Search" autocorrect="off" spellcheck="false" autocomplete="off" data-testid="static-html-search-input">\n  </div>\n  <div id="search_results" class="search-results">\n    <div id="results_navigation" class="search-results-navigation">\n      <div id="results_count" class="search-results-count"></div>\n      <div class="search-results-navigation-buttons">\n        <span class="search-results-navigation-button" id="start" data-testid="static-html-search-button-start"></span>\n        <span class="search-results-navigation-button" id="previous" data-testid="static-html-search-button-previous"></span>\n        <span class="search-results-navigation-button" id="next" data-testid="static-html-search-button-next"></span>\n        <span class="search-results-navigation-button" id="end" data-testid="static-html-search-button-end"></span>\n      </div>\n    </div>\n    <div id="suggestions" class="search-suggestions"></div>\n  </div>\n</div>'

blocks = {}
debug_info = ''