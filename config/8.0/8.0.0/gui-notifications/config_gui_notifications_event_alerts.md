# config gui-notifications event-alerts

Settings for administrative GUI event alert notifications.

## Syntax

```
config gui-notifications event-alerts
    Description: Settings for administrative GUI event alert notifications.
    edit <name>
        set display-alert [enable|disable]
    next
end
```

## Parameters

+---------------+-----------------------------------+--------------------+--------------------+--------------------+
| Parameter     | Description                       | Type               | Size               | Default            |
+===============+===================================+====================+====================+====================+
| display-alert | Enable/disable display of the     | option             | \-                 | enable             |
|               | event alert on the administrative |                    |                    |                    |
|               | GUI.                              |                    |                    |                    |
+---------------+-----------------------------------+--------------------+--------------------+--------------------+
|               | +-------------+--------------------------------------------------------+                         |
|               | | Option      | Description                                            |                         |
|               | +=============+========================================================+                         |
|               | | *enable*    | Enable display of the event alert on the               |                         |
|               | |             | administrative GUI.                                    |                         |
|               | +-------------+--------------------------------------------------------+                         |
|               | | *disable*   | Disable display of the event alert on the              |                         |
|               | |             | administrative GUI.                                    |                         |
|               | +-------------+--------------------------------------------------------+                         |
+---------------+-----------------------------------+--------------------+--------------------+--------------------+
| name          | GUI event alert notification      | string             | Maximum length: 35 |                    |
|               | name.                             |                    |                    |                    |
+---------------+-----------------------------------+--------------------+--------------------+--------------------+

