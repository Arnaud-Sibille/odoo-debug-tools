from lxml import etree

def add_page(notebook_el, title, fields):
    page_el = etree.SubElement(notebook_el, "page")
    page_el.set("string", title)
    group_el = etree.SubElement(page_el, "group")
    for field in fields:
        field_el = etree.SubElement(group_el, "field")
        field_el.set("name", field.name)
        if field.ttype == 'many2many':
            field_el.set("widget", "many2many_tags")
        if field.related:
            field_el.set("readonly", "1")

views = env['ir.ui.view'].search([('inherit_id', '=', False), ('type', '=', 'form'), ('arch_db', 'like', '%<sheet%')])
for view in views:
    view_name = f'{view.name}.{view.id}.odt.all_fields_in_form_view'
    if not env['ir.ui.view'].search([('name', '=', view_name)]):
        root = etree.Element("sheet")
        root.set("position", "inside")
        notebook_el = etree.SubElement(root, "notebook")

        fields = view.model_id.field_id.filtered_domain([('ttype', 'not in', ('binary', 'json'))])

        add_page(notebook_el, "Almost all fields", fields.filtered_domain([('ttype', '!=', 'one2many')]))
        for field in fields.filtered_domain([('ttype', '=', 'one2many')]):
            add_page(notebook_el, field.name , field)

        arch_db = etree.tostring(root, pretty_print=True, encoding="utf-8").decode("utf-8")
        env['ir.ui.view'].create({
            'name': view_name,
            'type': view.type,
            'model': view.model,
            'inherit_id': view.id,
            'arch_db': arch_db,
        })

env.cr.commit()
