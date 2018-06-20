# -*- coding: utf-8 -*-
"""
GPG Sync
Helps users have up-to-date public keys for everyone in their organization
https://github.com/firstlookmedia/gpgsync
Copyright (C) 2016 First Look Media

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import datetime
import os
import sys
import re
import platform
import inspect
import requests
import socket
from PyQt5 import QtCore, QtWidgets, QtGui


class Common(object):
    """
    The Common class is a singleton of shared functionality throughout the app
    """
    def __init__(self, debug):
        self.debug = debug

        # Preload icons
        self.icon = QtGui.QIcon(self.get_resource_path('gpgsync.png'))
        if platform.system() == 'Darwin':
            self.systray_icon = QtGui.QIcon(self.get_resource_path('gpgsync-bw.png'))
            self.systray_syncing_icon = QtGui.QIcon(self.get_resource_path('syncing-bw.png'))
            self.systray_error_icon = QtGui.QIcon(self.get_resource_path('error-bw.png'))
        else:
            self.systray_icon = QtGui.QIcon(self.get_resource_path('gpgsync.png'))
            self.systray_syncing_icon = QtGui.QIcon(self.get_resource_path('syncing.png'))
            self.systray_error_icon = QtGui.QIcon(self.get_resource_path('error.png'))

        # Stylesheets
        self.css = {
            'GPGSync add_button': """
                QPushButton {
                    font-weight: normal;
                }
                """,

            'GPGSync add_button_first': """
                QPushButton {
                    font-weight: bold;
                }
                """,

            'EndpointDialog sig_url': """
                QLabel {
                    font-style: italic;
                    color: #666666;
                    font-size: 11px;
                }
                """,

            'EndpointDialog advanced_button': """
                QPushButton {
                    text-decoration: underline;
                    color: #225dbf;
                }
                """
        }

    def log(self, module, func, msg=''):
        if self.debug:
            final_msg = "[{}] {}".format(module, func)
            if msg:
                final_msg = "{}: {}".format(final_msg, msg)
            print(final_msg)

    def alert(self, msg, details='', icon=QtWidgets.QMessageBox.Warning):
        d = QtWidgets.QMessageBox()
        d.setWindowTitle('GPG Sync')
        d.setText(msg)

        if details:
            d.setDetailedText(details)

        d.setIcon(icon)
        d.exec_()

    def update_alert(self, curr_version, latest_version, url):
        d = QtWidgets.QMessageBox()
        d.setWindowTitle('GPG Sync')
        d.setText('GPG Sync v{} is now available.<span style="font-weight:normal;">' \
                  '<br><br>You are currently running v{}. Click Update to' \
                  ' download the latest version </span>'.format(latest_version, curr_version))

        d.addButton(QtWidgets.QPushButton('Cancel'), QtWidgets.QMessageBox.NoRole)
        d.addButton(QtWidgets.QPushButton('Update'), QtWidgets.QMessageBox.YesRole)

        d.setIconPixmap(QtGui.QPixmap(self.get_resource_path('gpgsync.png')))
        res = d.exec_()

        if res == 1:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def valid_fp(self, fp):
        return re.match(b'^[A-F\d]{40}$', clean_fp(fp))

    def clean_fp(self, fp):
        return fp.strip().replace(b' ', b'').upper()

    def fp_to_keyid(self, fp):
        return '0x{}'.format(clean_fp(fp)[-16:].decode()).encode()

    def clean_keyserver(self, keyserver):
        if b'://' not in keyserver:
            return b'hkp://' + keyserver
        return keyserver

    def get_resource_path(self, filename):
        if getattr(sys, 'gpgsync_dev', False):
            # Look for resources directory relative to python file
            prefix = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))), 'share')

        elif platform.system() == 'Linux':
            prefix = os.path.join(sys.prefix, 'share/gpgsync')

        elif platform.system() == 'Darwin':
            # Check if app is "frozen"
            # https://pythonhosted.org/PyInstaller/#run-time-information
            if getattr(sys, 'frozen', False):
                prefix = os.path.join(os.path.dirname(sys.executable), 'share')
            else:
                prefix = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'share')

        resource_path = os.path.join(prefix, filename)
        return resource_path

    def requests_get(self, url, proxies=None):
        # When creating an OSX app bundle, the requests module can't seem to find
        # the location of cacerts.pem. Here's a hack to let it know where it is.
        # https://stackoverflow.com/questions/17158529/fixing-ssl-certificate-error-in-exe-compiled-with-py2exe-or-pyinstaller
        if getattr(sys, 'frozen', False):
            verify = os.path.join(os.path.dirname(sys.executable), 'requests/cacert.pem')
            return requests.get(url, proxies=proxies, verify=verify)
        else:
            return requests.get(url, proxies=proxies)

    def serialize_settings(self, o):
        if isinstance(o, bytes):
            return o.decode()
        if isinstance(o, datetime.datetime):
            return o.isoformat()

    def internet_available(self):
        try:
            host = socket.gethostbyname("www.example.com")
            s = socket.create_connection((host, 80), 2)
            return True
        except:
            pass

        return False
