# config voice-controller managed-voice

Configure FortiVoice devices that are managed by this FortiGate.

## Syntax

```
config voice-controller managed-voice
    Description: Configure FortiVoice devices that are managed by this FortiGate.
    edit <voice-id>
        config auto-attendant
            Description: Configure auto attendant service.
            edit <name>
                set auto-attendant-name {string}
                set greeting {string}
                set greeting-mode [simple|scheduled]
                set invalid-input-action [dial-extension|dial-operator|...]
                set invalid-input-extension {string}
                config key-action
                    Description: Configuration key actions.
                    edit <name>
                        set action [auto-attendant|call-queue|...]
                        set auto-attendant {string}
                        set call-queue {string}
                        set comments {string}
                        set directory-category [system|business-group|...]
                        set extension {string}
                        set external-number {string}
                        set followed-action [start-over|auto-attendant|...]
                        set prompt-language {string}
                    next
                end
                set max-invalid-input-allowed {integer}
                set max-start-over-times {integer}
                set ring-duration {integer}
                set timeout {integer}
                set timeout-action [call-queue|dial-extension|...]
                set timeout-call-queue {string}
                set timeout-extension {string}
            next
        end
        set description {string}
        config dialplan-quick-setup
            Description: Simplified and brief dialplan for quick setup.
            set announcement {string}
            set auto-attendant {string}
            set emergency-call-trunk {string}
            set incoming-call-action [auto-attendant|dial-local-number|...]
            set local-number {string}
            set outgoing-digits-pattern <outgoing-digits-pattern-name1>, <outgoing-digits-pattern-name2>, ...
            set status [disable|enable]
            set trunk {string}
        end
        config extension-ring-group
            Description: Configure extension ring-group.
            edit <name>
                set caller-id-option [no-change|prefix|...]
                set display-name {string}
                set external-numbers {string}
                set members <member-name1>, <member-name2>, ...
                set mode [ring-all|ring-sequential]
                set number {string}
                set status [disable|enable]
                set timeout {integer}
            next
        end
        config extension-user
            Description: Configure extension users.
            edit <name>
                set display-name {string}
                set mac-main {mac-address}
                set number {string}
                set sip-password {password}
                set softclient-license {integer}
                set softclient-status [disable|enable]
                set sound-language {string}
                set status [disable|enable]
            next
        end
        set fve-admin [discovered|disable|...]
        set fve-peer {string}
        config pbx-location
            Description: Configure location of PBX.
            set area-code <area-name1>, <area-name2>, ...
            set contact-email {string}
            set contact-phone {string}
            set country {string}
            set default-timezone {integer}
            set emergency-email <emergency-email-name1>, <emergency-email-name2>, ...
            set emergency-number <emergency-number-name1>, <emergency-number-name2>, ...
            set main-display-name {string}
            set main-number {string}
            set pbx-address-city {string}
            set pbx-address-province {string}
            set pbx-address-street {string}
        end
        config router-static
            Description: Configure static routes.
            edit <id>
                set comment {string}
                set dst {ipv4-classnet}
                set gateway {ipv4-address}
                set interface {string}
                set status [disable|enable]
                set voice-id {string}
            next
        end
        set sn {string}
        config sound-file
            Description: Configure sound file object.
            edit <name>
            next
        end
        config system-interface
            Description: Configure system interface.
            edit <name>
                set allowaccess {option1}, {option2}, ...
                set ip {ipv4-classnet-host}
                set mode [static|dhcp]
                set status [disable|enable]
                set webaccess {option1}, {option2}, ...
            next
        end
        config trunk-sip-peer
            Description: Configure FortiVoice trunk sip peer.
            edit <name>
                set caller-name {string}
                set caller-number {string}
                set max-channel {integer}
                set password {password}
                set sip-port {integer}
                set sip-server {string}
                set status [disable|enable]
                set username {string}
            next
        end
        set voice-profile {string}
    next
end
```

## Parameters

+---------------+-----------------------------------+---------------------+---------------------+---------------------+
| Parameter     | Description                       | Type                | Size                | Default             |
+===============+===================================+=====================+=====================+=====================+
| description   | Description.                      | string              | Maximum length: 63  |                     |
+---------------+-----------------------------------+---------------------+---------------------+---------------------+
| fve-admin     | FortiVoice admin status; enable   | option              | \-                  | discovered          |
|               | to authorize the FortiVoice as a  |                     |                     |                     |
|               | managed voice.                    |                     |                     |                     |
+---------------+-----------------------------------+---------------------+---------------------+---------------------+
|               | +--------------+--------------------------------------------------------+                           |
|               | | Option       | Description                                            |                           |
|               | +==============+========================================================+                           |
|               | | *discovered* | Link waiting to be authorized.                         |                           |
|               | +--------------+--------------------------------------------------------+                           |
|               | | *disable*    | Link unauthorized.                                     |                           |
|               | +--------------+--------------------------------------------------------+                           |
|               | | *enable*     | Link authorized.                                       |                           |
|               | +--------------+--------------------------------------------------------+                           |
+---------------+-----------------------------------+---------------------+---------------------+---------------------+
| fve-peer      | FortiVoice peer port.             | string              | Maximum length: 35  |                     |
+---------------+-----------------------------------+---------------------+---------------------+---------------------+
| sn            | Managed-voice serial number.      | string              | Maximum length: 16  |                     |
+---------------+-----------------------------------+---------------------+---------------------+---------------------+
| voice-id      | Managed-voice name.               | string              | Maximum length: 35  |                     |
+---------------+-----------------------------------+---------------------+---------------------+---------------------+
| voice-profile | FortiVoice profile.               | string              | Maximum length: 35  |                     |
+---------------+-----------------------------------+---------------------+---------------------+---------------------+

