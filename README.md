## odoo.conf

    [options]
    addons_path = D:\HelpDesk\odoo-18.0\odoo\addons, D:\HelpDesk\odoo-18.0\addons, D:\HelpDesk\tutorials
    db_host = localhost
    db_port = 5433
    db_user = odoo
    db_password = odoo
    db_name = mydb

## Commande démarrage odoo

    python odoo-bin -c odoo.conf

## Commande update 

    python odoo-bin -c odoo.conf -u estate