from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'actions/project_index/edit_project_title/stream_save_project_title.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_project_config = resolve('project_config')
    pass
    yield '<turbo-stream action="replace" target="header-project-name">\n  <template>\n    <div\n      class="header__project_name"\n      id="header-project-name"\n      title="'
    yield escape(environment.getattr((undefined(name='project_config') if l_0_project_config is missing else l_0_project_config), 'project_title'))
    yield '"\n    >'
    yield escape(environment.getattr((undefined(name='project_config') if l_0_project_config is missing else l_0_project_config), 'project_title'))
    yield '\n    </div>\n  </template>\n</turbo-stream>\n\n<turbo-stream action="update" target="modal">\n  <template></template>\n</turbo-stream>'

blocks = {}
debug_info = '6=13&7=15'