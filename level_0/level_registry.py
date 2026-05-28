# Автоматически сгенерированный реестр уровней и боксов
# Не редактируйте вручную

LEVELS = [
    {
        "name": "LoggerLevel",
        "module": "level_1_logger",
        "class": "LoggerLevelWrapper",
        "deps": [],
        "boxes": [
            "box_logger"
        ]
    },
    {
        "name": "DeviceLevel",
        "module": "level_2_device",
        "class": "DeviceLevelWrapper",
        "deps": [],
        "boxes": [
            "box_cpu",
            "box_gpu",
            "box_memory"
        ]
    },
    {
        "name": "ResourceLevel",
        "module": "level_3_resource",
        "class": "ResourceLevelWrapper",
        "deps": [
            "DeviceLevel"
        ],
        "boxes": [
            "box_balancer",
            "box_task_mgr"
        ]
    },
    {
        "name": "InputLevel",
        "module": "level_4_input",
        "class": "InputLevelWrapper",
        "deps": [],
        "boxes": [
            "box_hotkeys",
            "box_mouse"
        ]
    },
    {
        "name": "ManagerLevel",
        "module": "level_5_manager",
        "class": "ManagerLevelWrapper",
        "deps": [],
        "boxes": [
            "box_reloader"
        ]
    },
    {
        "name": "FileLevel",
        "module": "level_6_file",
        "class": "FileLevelWrapper",
        "deps": [],
        "boxes": [
            "box_checker"
        ]
    },
    {
        "name": "SettingsLevel",
        "module": "level_7_settings",
        "class": "SettingsLevelWrapper",
        "deps": [],
        "boxes": [
            "box_config",
            "box_io",
            "box_locale",
            "box_validation"
        ]
    },
    {
        "name": "UserLevel",
        "module": "level_8_user",
        "class": "UserLevelWrapper",
        "deps": [
            "SettingsLevel"
        ],
        "boxes": [
            "box_profile"
        ]
    },
    {
        "name": "SessionLevel",
        "module": "level_9_session",
        "class": "SessionLevelWrapper",
        "deps": [
            "UserLevel"
        ],
        "boxes": [
            "box_bookmarks",
            "box_buffer",
            "box_history",
            "box_state"
        ]
    },
    {
        "name": "ExtensionsLevel",
        "module": "level_10_extensions",
        "class": "ExtensionsLevelWrapper",
        "deps": [
            "UserLevel"
        ],
        "boxes": [
            "box_loader",
            "box_manager"
        ]
    },
    {
        "name": "ScriptLevel",
        "module": "level_11_scripts",
        "class": "ScriptLevelWrapper",
        "deps": [
            "UserLevel"
        ],
        "boxes": [
            "box_script"
        ]
    },
    {
        "name": "UILevel",
        "module": "level_12_ui",
        "class": "UILevelWrapper",
        "deps": [
            "UserLevel",
            "SessionLevel",
            "ExtensionsLevel",
            "ScriptLevel"
        ],
        "boxes": [
            "box_bookmarks_tab",
            "box_context_menu",
            "box_history_tab",
            "box_main_tabs",
            "box_navigation",
            "box_scripts_tab",
            "box_settings_tab",
            "box_style",
            "box_style_script",
            "box_tabs",
            "box_toolbar",
            "box_webview",
            "box_window"
        ]
    },
    {
        "name": "NetworkLevel",
        "module": "level_13_network",
        "class": "NetworkLevelWrapper",
        "deps": [],
        "boxes": [
            "box_cache",
            "box_proxy"
        ]
    },
    {
        "name": "DownloadLevel",
        "module": "level_14_download",
        "class": "DownloadLevelWrapper",
        "deps": [],
        "boxes": [
            "box_manager"
        ]
    }
]
