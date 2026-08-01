# -*- coding: utf-8 -*-
"""
===============================================================================
Noise Prediction — Construction Noise Assessment
QGIS Plugin
===============================================================================

Author      : Htet Arkar Soe
Copyright   : (C) 2022–2026 Htet Arkar Soe
Version     : 0.5.0 Beta
Repository  : https://github.com/htet-coder/Noise-Prediction-Algorithm
License     : GNU General Public License v2 or later (GPL-2.0-or-later)

Description
-----------
A QGIS plugin for predicting construction noise at receptor locations using
a simplified BS 5228-inspired methodology.

Current Features
----------------
• Cumulative noise prediction from multiple construction sources
• Distance attenuation
• Ground attenuation
• Manual screening correction
• Manual reflection correction
• Temporary and permanent output layers
• Sample dataset loader

Notes
-----
This plugin is intended for preliminary construction noise assessments.
It is not an official implementation of BS 5228 and should not be used as
a substitute for detailed acoustic modelling where such analyses are required.

===============================================================================
"""

__author__ = 'Htet Arkar Soe'
__date__ = '2022-02-19'
__copyright__ = '(C) 2022 by Htet Arkar Soe'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon,QDesktopServices

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QUrl
from .gui.noise_prediction_dialog import NoisePredictionDialog
cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class NoisePredictionPlugin(object):

    def __init__(self, iface):
        self.iface = iface
        self.dialog = None
        

    def initGui(self):
        icon = os.path.join(os.path.join(cmd_folder, 'logo.png'))
        self.action = QAction(
          QIcon(icon),
          u"Construction Noise Assessment", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu(u"&Noise Prediction", self.action)
        self.iface.addToolBarIcon(self.action)
              
    def unload(self):
        self.iface.removePluginMenu(u"&Noise Prediction", self.action)
        self.iface.removeToolBarIcon(self.action)
                              
    def run(self):
        """Open the new BS 5228 prediction dialog."""

        if self.dialog is None:
            self.dialog = NoisePredictionDialog(
                self.iface.mainWindow()
            )

        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
    
