# config system device-status-monitor

Configure Device Status Monitor Profile.

## Syntax

```
config system device-status-monitor
    Description: Configure Device Status Monitor Profile.
    edit <name>
        set comment {var-string}
        config filters
            Description: List of filters to match.
            edit <id>
                set negate [enable|disable]
                set type [hardware-vendor|hardware-version|...]
                set value {string}
            next
        end
        set match-logic [and|or]
        set monitor-maclist {string}
        set offline-tolerance {integer}
        set online-duration {integer}
        set status [enable|disable]
    next
end
```

## Parameters

+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
| Parameter         | Description                       | Type               | Size               | Default            |
+===================+===================================+====================+====================+====================+
| comment           | Comment.                          | var-string         | Maximum length:    |                    |
|                   |                                   |                    | 255                |                    |
+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
| match-logic       | Filter matching logic.            | option             | \-                 | and                |
+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                   | +-------------+--------------------------------------------------------+                         |
|                   | | Option      | Description                                            |                         |
|                   | +=============+========================================================+                         |
|                   | | *and*       | Match all filters.                                     |                         |
|                   | +-------------+--------------------------------------------------------+                         |
|                   | | *or*        | Match any filters.                                     |                         |
|                   | +-------------+--------------------------------------------------------+                         |
+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
| monitor-maclist   | Monitor device list.              | string             | Maximum length: 35 |                    |
+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
| name              | Name.                             | string             | Maximum length: 47 |                    |
+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
| offline-tolerance | Maximum time, in percentage of    | integer            | Minimum value: 5   | 5                  |
|                   | online-duration that a monitored  |                    | Maximum value: 10  |                    |
|                   | device is allowed to be offline   |                    |                    |                    |
|                   | while still being considered      |                    |                    |                    |
|                   | online (5 - 10, default = 5).     |                    |                    |                    |
+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
| online-duration   | Configure the continuous online   | integer            | Minimum value:     | 3600               |
|                   | duration required for a monitored |                    | 1800 Maximum       |                    |
|                   | device to trigger a system log in |                    | value: 31536000    |                    |
|                   | seconds (1800 - 31536000 (30 min  |                    |                    |                    |
|                   | to 1 year), default = 3600).      |                    |                    |                    |
+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
| status            | Enable/disable the monitor        | option             | \-                 | enable             |
|                   | profile.                          |                    |                    |                    |
+-------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                   | +-------------+--------------------------------------------------------+                         |
|                   | | Option      | Description                                            |                         |
|                   | +=============+========================================================+                         |
|                   | | *enable*    | Enable setting.                                        |                         |
|                   | +-------------+--------------------------------------------------------+                         |
|                   | | *disable*   | Disable setting.                                       |                         |
|                   | +-------------+--------------------------------------------------------+                         |
+-------------------+--------------------------------------------------------------------------------------------------+

