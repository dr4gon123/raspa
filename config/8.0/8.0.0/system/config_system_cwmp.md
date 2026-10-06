# config system cwmp

Configure CPE WAN Management Protocol (CWMP) daemon.

## Syntax

```
config system cwmp
    Description: Configure CPE WAN Management Protocol (CWMP) daemon.
    set acs-url {text}
    set connection-request-password {password}
    set connection-request-username {text}
    set local-interface {string}
    set password {password}
    set periodic-inform-interval {integer}
    set status [enable|disable]
    set username {text}
end
```

## Parameters

+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| Parameter                   | Description                       | Type               | Size               | Default            |
+=============================+===================================+====================+====================+====================+
| acs-url                     | ACS server URL or IP address.     | text               | Not Specified      |                    |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| connection-request-password | ACS connection request password.  | password           | Not Specified      |                    |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| connection-request-username | ACS connection request username.  | text               | Not Specified      |                    |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| local-interface             | Local interface.                  | string             | Maximum length: 15 |                    |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| password                    | ACS server password.              | password           | Not Specified      |                    |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| periodic-inform-interval    | Periodic inform interval in       | integer            | Minimum value: 60  | 300                |
|                             | seconds (60 - 86400, default =    |                    | Maximum value:     |                    |
|                             | 300).                             |                    | 86400              |                    |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| status                      | Enable/disable CPE WAN Management | option             | \-                 | disable            |
|                             | Protocol (CWMP) daemon.           |                    |                    |                    |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                             | +-------------+--------------------------------------------------------+                         |
|                             | | Option      | Description                                            |                         |
|                             | +=============+========================================================+                         |
|                             | | *enable*    | Enable CPE WAN Management Protocol (CWMP) daemon.      |                         |
|                             | +-------------+--------------------------------------------------------+                         |
|                             | | *disable*   | Disable CPE WAN Management Protocol (CWMP) daemon.     |                         |
|                             | +-------------+--------------------------------------------------------+                         |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| username                    | ACS server username.              | text               | Not Specified      |                    |
+-----------------------------+-----------------------------------+--------------------+--------------------+--------------------+

