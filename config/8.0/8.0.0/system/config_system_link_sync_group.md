# config system link-sync-group

Configure link sync group.

## Syntax

```
config system link-sync-group
    Description: Configure link sync group.
    edit <name>
        set members <name1>, <name2>, ...
    next
end
```

## Parameters

+-----------+-----------------------------------+--------+---------+---------+
| Parameter | Description                       | Type   | Size    | Default |
+===========+===================================+========+=========+=========+
| members   | Members in the group.             | string | Maximum |         |
| `<name>`  |                                   |        | length: |         |
|           | Name of the interface.            |        | 79      |         |
+-----------+-----------------------------------+--------+---------+---------+
| name      | Link sync group name.             | string | Maximum |         |
|           |                                   |        | length: |         |
|           |                                   |        | 35      |         |
+-----------+-----------------------------------+--------+---------+---------+

