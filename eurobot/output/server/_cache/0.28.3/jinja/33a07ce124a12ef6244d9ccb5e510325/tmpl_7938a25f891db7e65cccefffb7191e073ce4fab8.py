from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/type_level.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_requirement = resolve('requirement')
    l_0__level = missing
    pass
    l_0__level = environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'context'), 'title_number_string')
    context.vars['_level'] = l_0__level
    if (undefined(name='_level') if l_0__level is missing else l_0__level):
        pass
        yield '\n  <td id="cell-'
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_mid'))
        yield '-LEVEL" class="content-view-td content-view-td-level">\n    '
        yield escape((undefined(name='_level') if l_0__level is missing else l_0__level))
        yield '\n  </td>'
    else:
        pass
        yield '\n  <td id="cell-'
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_mid'))
        yield '-LEVEL" class="content-view-td content-view-td-level content-view-td--dimmed">\n    <div class="content-view-td--dimmed_tips"></div>\n  </td>'

blocks = {}
debug_info = '1=13&2=15&3=18&4=20&7=25'