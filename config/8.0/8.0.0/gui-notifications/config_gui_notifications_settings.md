# config gui-notifications settings

Settings for GUI notification event alerts.

## Syntax

```
config gui-notifications settings
    Description: Settings for GUI notification event alerts.
    set override-sync [enable|disable]
end
```

## Parameters

+---------------+-----------------------------------+--------------------+--------------------+--------------------+
| Parameter     | Description                       | Type               | Size               | Default            |
+===============+===================================+====================+====================+====================+
| override-sync | Enable/disable overriding GUI     | option             | \-                 | disable            |
|               | event alert notification settings |                    |                    |                    |
|               | synced from the Security          |                    |                    |                    |
|               | Fabric\'s root FortiGate.         |                    |                    |                    |
+---------------+-----------------------------------+--------------------+--------------------+--------------------+
|               | +-------------+--------------------------------------------------------+                         |
|               | | Option      | Description                                            |                         |
|               | +=============+========================================================+                         |
|               | | *enable*    | Enable overriding the GUI event alert notification     |                         |
|               | |             | settings synced from the Security Fabric root          |                         |
|               | |             | FortiGate.                                             |                         |
|               | +-------------+--------------------------------------------------------+                         |
|               | | *disable*   | Disable overriding the GUI event alert notification    |                         |
|               | |             | settings synced from the Security Fabric root          |                         |
|               | |             | FortiGate.                                             |                         |
|               | +-------------+--------------------------------------------------------+                         |
+---------------+--------------------------------------------------------------------------------------------------+

