#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Polychromatic is free software: you can redistribute it and/or modify
# it under the temms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Polychromatic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Polychromatic. If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2015-2016 Terry Cain <terry@terrys-home.co.uk>
#               2015-2017 Luke Horwell <luke@ubuntu-mate.org>
#

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, Gdk, AppIndicator3 as appindicator
import argparse
import collections
import os
import sys
import signal
import gettext
import setproctitle
from subprocess import Popen as background_process
from subprocess import call as foreground_process
from shutil import which

"""
GTK-based tray applet to control devices from the user's desktop environment.
"""

# Functions for populating the indicator menus.
def create_menu_item(label, enabled, function=None, function_params=None, icon_path=None):
    """
    Returns a Gtk menu item for use in menus.
        label               str     Text to display to the user.
        enabled             bool    Whether the selection should be highlighted or not.
        function            obj     Callback when button is clicked.
        function_params     obj     Functions to pass the callback function.
        icon_path           str     Path to image file.
    """
    if icon_path and os.path.exists(icon_path):
        item = Gtk.ImageMenuItem(Gtk.STOCK_NEW, label=label)
        item.set_sensitive(enabled)
        item.show()

        img = Gtk.Image()
        img.set_from_file(icon_path)
        item.set_image(img)
    else:
        item = Gtk.MenuItem(label=label)
        item.set_sensitive(enabled)
        item.show()

    if function and not function_params:
        item.connect("activate", function)
    elif function and function_params:
        item.connect("activate", function, function_params)

    return item

def create_submenu(label, enabled):
    """
    Returns a Gtk menu item for sub-menu options.
        label               str     Text to display to the user.
        enabled             bool    Whether the selection should be highlighted or not.

    Returns objects:
        item                MenuItem (for parent menu)
        menu                Menu (containing child menu items)
    """

    item = Gtk.MenuItem(label=label)
    item.set_sensitive(enabled)
    item.show()

    menu = Gtk.Menu()
    menu.show()
    item.set_submenu(menu)

    return[item, menu]

def create_seperator():
    """
    Returns a Gtk seperator object.
    """
    sep = Gtk.SeparatorMenuItem()
    sep.show()
    return sep


class AppIndicator(object):
    """
    Indicator applet that provides quick access configuration
    options from the system tray.
    """
    def __init__(self):

        self.menu_root = None
        self.menu_brightness = None

        self.current_brightness = 0

        self.indicator = appindicator.Indicator.new("nvidia-card-status-applet", self._get_tray_icon(), appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

    def set_brightness(self, kk, value):
        print("Setting brightness to {}".format(value))
        self.current_brightness = value

    def setup(self):

        # Ensure correct tray icon is loaded
        self.indicator.set_icon_full(self._get_tray_icon(), "Main icon")

        # Populate root menu and submenus.
        self.rebuild_all_submenus()
        self.rebuild_root_menu()

    def rebuild_all_submenus(self):
        """
        Rebuilds the submenus based on the currently active device.
        If a device does not require this menu, this returns None.
        """
        self.menu_brightness = self._build_brightness_menu()

    def rebuild_root_menu(self):
        """
        Rebuilds the parent "tray" menu.
        """
        root = Gtk.Menu()

        root.append(create_seperator())
        root.append(self.menu_brightness)
        root.append(create_seperator())

        self.indicator.set_title("Nvidia Card Status Applet")
        self.indicator.set_menu(root)

    def _get_tray_icon(self):
        """
        Returns path or filename for tray icon.

        Icon Sources
            "tray_icon": {"type": "?"}
                builtin     = One provided by Polychromatic.    "humanity-light"
                custom      = One specified by user.            "/path/to/file"
                gtk         = Use icon by GTK name.             "keyboard"
        """
        return "nvidia.png"

    def _build_brightness_menu(self):
        root_submenu = create_submenu("Brightness", True)

        target_submenu = create_submenu("Backlight", True)
    
        target_submenu[1].append(create_menu_item("Full (100%)", True, self.set_brightness, 100))
        target_submenu[1].append(create_menu_item("Bright (75%)", True, self.set_brightness, 75))
        target_submenu[1].append(create_menu_item("Medium (50%)", True, self.set_brightness, 50))
        target_submenu[1].append(create_menu_item("Dim (25%)", True, self.set_brightness, 25))
        target_submenu[1].append(create_menu_item("Off (0%)", True, self.set_brightness, 0))

        root_submenu[1].append(target_submenu[0])

        return root_submenu[0]

    @staticmethod
    def _colour_to_hex(colour):
        """
        Converts a tuple input to #RRGGBB format
            colour = [red, green, blue]
        """
        return "#{0:02X}{1:02X}{2:02X}".format(*colour)



if __name__ == "__main__":
    # Appear as its own process.
    
    setproctitle.setproctitle("nvidia-card-status-applet")

    # Kill the process when CTRL+C'd.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    indicator = AppIndicator()
    indicator.setup()

    Gtk.main()
    exit(0)