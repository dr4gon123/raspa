# config icap local-server

Configure ICAP local server.

## Syntax

```
config icap local-server
    Description: Configure ICAP local server.
    edit <icap-server-id>
        set icap-incoming-port {integer}
        set icap-incoming-ssl-port {integer}
        config icap-service
            Description: Set up services for local ICAP server.
            edit <service-id>
                set av-profile {string}
                set dlp-profile {string}
                set extension-headers {option1}, {option2}, ...
                set name {string}
                set profile-protocol-options {string}
                set webfilter-profile {string}
            next
        end
        set incoming-ip {ipv4-address-any}
        set incoming-ipv6 {ipv6-address}
        set interface {string}
        set message-preview [disable|enable]
        set secure-connection [disable|enable]
        set srcaddr {string}
        set ssl-cert <name1>, <name2>, ...
        set status [disable|enable]
        set status-ipv6 [disable|enable]
        set strict-scheme-check [disable|enable]
        set timeout {integer}
    next
end
```

## Parameters

+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| Parameter              | Description                       | Type               | Size               | Default            |
+========================+===================================+====================+====================+====================+
| icap-incoming-port     | Accept incoming ICAP requests on  | integer            | Minimum value: 1   | 1344               |
|                        | a port (1 - 65535, default =      |                    | Maximum value:     |                    |
|                        | 1344).                            |                    | 65535              |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| icap-incoming-ssl-port | Accept incoming secured ICAP      | integer            | Minimum value: 1   | 11344              |
|                        | requests on a port (1 - 65535,    |                    | Maximum value:     |                    |
|                        | default = 11344).                 |                    | 65535              |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| icap-server-id         | ICAP local server id.             | integer            | Minimum value: 0   | 0                  |
|                        |                                   |                    | Maximum value:     |                    |
|                        |                                   |                    | 65535              |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| incoming-ip            | Restrict the ICAP server to only  | ipv4-address-any   | Not Specified      | 0.0.0.0            |
|                        | accept sessions from this IP      |                    |                    |                    |
|                        | address. An interface must have   |                    |                    |                    |
|                        | this IP address.                  |                    |                    |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| incoming-ipv6          | Restrict the ICAP server to only  | ipv6-address       | Not Specified      | ::                 |
|                        | accept sessions from this IPv6    |                    |                    |                    |
|                        | address. An interface must have   |                    |                    |                    |
|                        | this IPv6 address.                |                    |                    |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| interface              | Interface name                    | string             | Maximum length: 15 |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| message-preview        | Enable/disable message preview    | option             | \-                 | enable             |
|                        | support. Max preview data length  |                    |                    |                    |
|                        | is 4096 bytes.                    |                    |                    |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | Option      | Description                                            |                         |
|                        | +=============+========================================================+                         |
|                        | | *disable*   | Disable message preview support.                       |                         |
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | *enable*    | Enable message preview support.                        |                         |
|                        | +-------------+--------------------------------------------------------+                         |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| secure-connection      | Enable/disable status for secured | option             | \-                 | disable            |
|                        | icap server network profile.      |                    |                    |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | Option      | Description                                            |                         |
|                        | +=============+========================================================+                         |
|                        | | *disable*   | Disable the status for IPv4 ssl in network-profile.    |                         |
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | *enable*    | Enable the status for IPv4 ssl in network-profile.     |                         |
|                        | +-------------+--------------------------------------------------------+                         |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| srcaddr                | Source address name.              | string             | Maximum length: 79 |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| ssl-cert `<name>`      | SSL certificate for SSL           | string             | Maximum length: 79 |                    |
|                        | interception.                     |                    |                    |                    |
|                        |                                   |                    |                    |                    |
|                        | Certificate list.                 |                    |                    |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| status                 | Enable/disable status for icap    | option             | \-                 | enable             |
|                        | server network profile.           |                    |                    |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | Option      | Description                                            |                         |
|                        | +=============+========================================================+                         |
|                        | | *disable*   | Disable the status for IPv4 in network-profile.        |                         |
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | *enable*    | Enable the status for IPv4 in network-profile.         |                         |
|                        | +-------------+--------------------------------------------------------+                         |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| status-ipv6            | Enable/disable status for icap    | option             | \-                 | disable            |
|                        | server service ipv6.              |                    |                    |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | Option      | Description                                            |                         |
|                        | +=============+========================================================+                         |
|                        | | *disable*   | Disable the status for IPv6 in network-profile.        |                         |
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | *enable*    | Enable the status for IPv6 in network-profile.         |                         |
|                        | +-------------+--------------------------------------------------------+                         |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| strict-scheme-check    | Enable/disable strict check of    | option             | \-                 | enable             |
|                        | scheme.                           |                    |                    |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | Option      | Description                                            |                         |
|                        | +=============+========================================================+                         |
|                        | | *disable*   | Disable strict check of scheme.                        |                         |
|                        | +-------------+--------------------------------------------------------+                         |
|                        | | *enable*    | Enable strict check of scheme.                         |                         |
|                        | +-------------+--------------------------------------------------------+                         |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+
| timeout                | ICAP server idle timeout in       | integer            | Minimum value: 30  | 300                |
|                        | seconds.                          |                    | Maximum value:     |                    |
|                        |                                   |                    | 3600               |                    |
+------------------------+-----------------------------------+--------------------+--------------------+--------------------+

