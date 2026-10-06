# config system device-monitor-maclist

Configure Device Monitor MAC List.

## Syntax

```
config system device-monitor-maclist
    Description: Configure Device Monitor MAC List.
    edit <name>
        set comment {var-string}
        config entries
            Description: MAC addresses.
            edit <id>
                set macaddr {string}
            next
        end
        set type [monitor-list|monitor-exempt-list]
    next
end
```

## Parameters

+-----------+-----------------------------------+------------------------+------------------------+------------------------+
| Parameter | Description                       | Type                   | Size                   | Default                |
+===========+===================================+========================+========================+========================+
| comment   | Comment.                          | var-string             | Maximum length: 255    |                        |
+-----------+-----------------------------------+------------------------+------------------------+------------------------+
| name      | Name.                             | string                 | Maximum length: 35     |                        |
+-----------+-----------------------------------+------------------------+------------------------+------------------------+
| type      | Set monitor list as a             | option                 | \-                     | monitor-exempt-list    |
|           | monitor-list or                   |                        |                        |                        |
|           | monitor-exempt-list.              |                        |                        |                        |
+-----------+-----------------------------------+------------------------+------------------------+------------------------+
|           | +-----------------------+--------------------------------------------------------+                           |
|           | | Option                | Description                                            |                           |
|           | +=======================+========================================================+                           |
|           | | *monitor-list*        | Monitor MAC addresses in the list.                     |                           |
|           | +-----------------------+--------------------------------------------------------+                           |
|           | | *monitor-exempt-list* | Monitor MAC addresses NOT in the list.                 |                           |
|           | +-----------------------+--------------------------------------------------------+                           |
+-----------+--------------------------------------------------------------------------------------------------------------+

