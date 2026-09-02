from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/td_by_edit_mode.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_cell_edit_mode = resolve('cell_edit_mode')
    l_0_td_class = resolve('td_class')
    l_0_field_title = resolve('field_title')
    l_0_view_object = resolve('view_object')
    l_0_requirement = resolve('requirement')
    l_0_field_value = resolve('field_value')
    pass
    if ((undefined(name='cell_edit_mode') if l_0_cell_edit_mode is missing else l_0_cell_edit_mode) == 'autocomplete'):
        pass
        yield '\n\n<td class="'
        yield escape((undefined(name='td_class') if l_0_td_class is missing else l_0_td_class))
        yield '"\n    data-field-name="'
        yield escape((undefined(name='field_title') if l_0_field_title is missing else l_0_field_title))
        yield '"'
        if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
            pass
            yield '\n    data-node-mid="'
            yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_mid'))
            yield '"\n    data-field-type="autocomplete"\n    js-table_view_edit-field="autocomplete"\n    data-current-value="'
            yield escape(((undefined(name='field_value') if l_0_field_value is missing else l_0_field_value) if (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value) else ''))
            yield '"\n    data-url="/actions/table/get_node_autocomplete_inline?node_mid='
            yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_mid'))
            yield '&amp;field_name='
            yield escape((undefined(name='field_title') if l_0_field_title is missing else l_0_field_title))
            yield '"'
        yield '\n>'
        if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
            pass
            yield '<div class="editable-cell-indicator"></div>'
        yield '\n  <div id="cell-'
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_mid'))
        yield '-'
        yield escape((undefined(name='field_title') if l_0_field_title is missing else l_0_field_title))
        yield '" wrapper-field-type="autocomplete">'
        if (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value):
            pass
            l_1_field_content = (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value)
            pass
            template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'screens/document/table/td_by_edit_mode.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            l_1_field_content = missing
        yield '\n  </div>\n</td>'
    elif ((undefined(name='cell_edit_mode') if l_0_cell_edit_mode is missing else l_0_cell_edit_mode) in ('singleline', 'multiline')):
        pass
        yield '\n<td class="'
        yield escape((undefined(name='td_class') if l_0_td_class is missing else l_0_td_class))
        yield '"\n    data-field-name="'
        yield escape((undefined(name='field_title') if l_0_field_title is missing else l_0_field_title))
        yield '"'
        if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
            pass
            yield '\n    data-node-mid="'
            yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_mid'))
            yield '"\n    data-field-type="contenteditable"\n    js-table_view_edit-field="contenteditable"\n    data-url="/actions/table/get_node_contenteditable_inline?node_mid='
            yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_mid'))
            yield '&amp;field_name='
            yield escape((undefined(name='field_title') if l_0_field_title is missing else l_0_field_title))
            yield '"'
        yield '\n>'
        if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
            pass
            yield '<div class="editable-cell-indicator"></div>'
        yield '\n  <div id="cell-'
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_mid'))
        yield '-'
        yield escape((undefined(name='field_title') if l_0_field_title is missing else l_0_field_title))
        yield '" wrapper-field-type="contenteditable">'
        if (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value):
            pass
            if ((undefined(name='cell_edit_mode') if l_0_cell_edit_mode is missing else l_0_cell_edit_mode) == 'multiline'):
                pass
                l_1_field_content = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_node_field'), environment.getitem(environment.getitem(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'ordered_fields_lookup'), (undefined(name='field_title') if l_0_field_title is missing else l_0_field_title)), 0))
                pass
                template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'screens/document/table/td_by_edit_mode.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_1_field_content = missing
            else:
                pass
                l_1_field_content = (undefined(name='field_value') if l_0_field_value is missing else l_0_field_value)
                pass
                template = environment.get_template('screens/document/table/field_display_mode/_base_field_component.jinja', 'screens/document/table/td_by_edit_mode.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_1_field_content = missing
        yield '\n  </div>\n</td>'
    else:
        pass
        yield '\n\n<td class="'
        yield escape((undefined(name='td_class') if l_0_td_class is missing else l_0_td_class))
        yield ' content-view-td--dimmed"\n    data-field-name="'
        yield escape((undefined(name='field_title') if l_0_field_title is missing else l_0_field_title))
        yield '">\n  <div class="content-view-td--dimmed_tips"></div>\n</td>'

blocks = {}
debug_info = '26=17&34=20&35=22&36=24&37=27&40=29&41=31&44=36&45=40&46=44&48=48&54=56&55=59&56=61&57=63&58=66&61=68&64=73&65=77&66=81&67=83&69=87&73=98&86=109&87=111'