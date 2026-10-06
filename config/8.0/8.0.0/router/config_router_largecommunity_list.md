# config router largecommunity-list

Configure large community lists.

## Syntax

```
config router largecommunity-list
    Description: Configure large community lists.
    edit <name>
        config rule
            Description: Large community list rule.
            edit <id>
                set action [deny|permit]
                set match {string}
                set regexp {string}
            next
        end
        set type [standard|expanded]
    next
end
```

## Parameters

+-----------+-----------------------------------+--------------------+--------------------+--------------------+
| Parameter | Description                       | Type               | Size               | Default            |
+===========+===================================+====================+====================+====================+
| name      | Large community list name.        | string             | Maximum length: 35 |                    |
+-----------+-----------------------------------+--------------------+--------------------+--------------------+
| type      | Large community list type         | option             | \-                 | standard           |
|           | (standard or expanded).           |                    |                    |                    |
+-----------+-----------------------------------+--------------------+--------------------+--------------------+
|           | +-------------+--------------------------------------------------------+                         |
|           | | Option      | Description                                            |                         |
|           | +=============+========================================================+                         |
|           | | *standard*  | Standard large community list type.                    |                         |
|           | +-------------+--------------------------------------------------------+                         |
|           | | *expanded*  | Expanded large community list type.                    |                         |
|           | +-------------+--------------------------------------------------------+                         |
+-----------+--------------------------------------------------------------------------------------------------+

