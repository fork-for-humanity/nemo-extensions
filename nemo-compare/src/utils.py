#!/usr/bin/python3
# -*- coding: utf-8 -*-
#    nemo-compare --- Context menu extension for Nemo file manager
#    Copyright (C) 2011  Guido Tabbernuk <boamaod@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import configparser
from gi.repository import GLib

APP = 'nemo-compare'

# settings
CONFIG_FILES = []
CONFIG_FILES = [os.path.join(GLib.get_user_config_dir(), APP + ".conf"), os.path.join("/etc", APP + ".conf")]
CONFIG_FILE = CONFIG_FILES[0]
SETTINGS_MAIN = 'Settings'

DIFF_PATH = 'diff_engine_path'
DIFF_PATH_3WAY = 'diff_engine_path_3way'
DIFF_PATH_MULTI = 'diff_engine_path_multi'

COMPARATORS = 'defined_comparators'
# ordered by preference
PREDEFINED_ENGINES = ['meld', 'kdiff3', 'diffuse', 'kompare', 'fldiff', 'tkdiff']
DEFAULT_DIFF_ENGINE = "meld"

# where comparator engines are sought
COMPARATOR_PATHS = ['/usr/bin', '/usr/local/bin']

class NemoCompareConfig:

    diff_engine = DEFAULT_DIFF_ENGINE
    diff_engine_3way = DEFAULT_DIFF_ENGINE
    diff_engine_multi = ""
    engines = []

    config = None

    def load(self):
        '''Loads config options if available. If not, creates them using the best heuristics availabe.'''
        self.config = configparser.ConfigParser()

        self.config['DEFAULT'] = {DIFF_PATH: 'meld',
                                  DIFF_PATH_3WAY: 'meld',
                                  DIFF_PATH_MULTI: '',
                                  COMPARATORS: 'meld'}

        # allow system-wide default settings from /etc/*
        if os.path.isfile(CONFIG_FILES[0]):
            self.config.read(CONFIG_FILES[0])
        else:
            self.config.read(CONFIG_FILES[1])

        # read from start or flush from the point where cancelled
        try:
            main = self.config[SETTINGS_MAIN]
            self.diff_engine = main[DIFF_PATH]
            self.diff_engine_3way = main[DIFF_PATH_3WAY]
            self.diff_engine_multi = main[DIFF_PATH_MULTI]
            self.engines = main[COMPARATORS].split(',')
        except KeyError:
            # maybe settings were half loaded when exception was thrown
            try:
                self.config.add_section(SETTINGS_MAIN)
            except configparser.DuplicateSectionError:
                pass

            self.add_missing_predefined_engines()

            # add choice for "engine not enabled"
            # (always needed, because at least self.engines cannot be loaded)
            self.engines.insert(0, "")

            # if default engine is not installed, replace with preferred installed engine
            if len(self.engines) > 0:
                if self.diff_engine not in self.engines:
                    self.diff_engine = self.engines[0]
                if self.diff_engine_3way not in self.engines:
                    self.diff_engine_3way = self.engines[0]
                if self.diff_engine_multi not in self.engines:
                    self.diff_engine_multi = self.engines[0]

            self.engines.sort()

            main = self.config[SETTINGS_MAIN]
            main[DIFF_PATH] = self.diff_engine
            main[DIFF_PATH_3WAY] = self.diff_engine_3way
            main[DIFF_PATH_MULTI] = self.diff_engine_multi

            strlist = ",".join(self.engines)

            main[COMPARATORS] = strlist

            with open(CONFIG_FILE, 'w') as f:
                self.config.write(f)

    def add_missing_predefined_engines(self):
        '''Adds predefined engines which are installed, but missing in engines list.'''
        system_utils = []
        for path in COMPARATOR_PATHS:
            try:
                system_utils += os.listdir(path)
            except:
                pass
        for engine in PREDEFINED_ENGINES:
            if engine not in self.engines and engine in system_utils:
                self.engines.append(engine)


    def save(self):
        '''Saves config options'''
        try:
            self.config.add_section(SETTINGS_MAIN)
        except configparser.DuplicateSectionError:
            pass

        main = self.config[SETTINGS_MAIN]
        main[DIFF_PATH] = self.diff_engine
        main[DIFF_PATH_3WAY] = self.diff_engine_3way
        main[DIFF_PATH_MULTI] = self.diff_engine_multi

        if self.diff_engine not in self.engines:
            self.engines.append(self.diff_engine)
        if self.diff_engine_3way not in self.engines:
            self.engines.append(self.diff_engine_3way)
        if self.diff_engine_multi not in self.engines:
            self.engines.append(self.diff_engine_multi)

        system_utils = []
        for path in COMPARATOR_PATHS:
            try:
                system_utils += os.listdir(path)
            except:
                pass
        for engine in self.engines:
            if engine not in system_utils:
                self.engines.remove(engine)

        strlist = ",".join(self.engines)

        main[COMPARATORS] = strlist

        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)
