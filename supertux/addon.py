# Flexlay - A Generic 2D Game Editor
# Copyright (C) 2014 Ingo Ruhnke <grumbel@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging

from flexlay import Config
from flexlay.util import get_value_from_tree, sexpr_filter, SExprWriter
from .sector import Sector
from .util import load_lisp


class Addon:
    @staticmethod
    def from_file(filename):
        addon = Addon()

        #if filename.endswith(".stwm"):
        #    level.is_worldmap = True
        #else:
        #    level.is_worldmap = False

        #level.filename = filename

        tree = load_lisp(addon.filename, "supertux-addoninfo")
        data = tree[1:]

        addon.id = get_value_from_tree(["id", "_"], data, "")
        addon.version = get_value_from_tree(["version", "_"], data, "")
        addon.type = get_value_from_tree(["type", "_"], data, "")
        addon.title = get_value_from_tree(["title", "_"], data, "")
        addon.author = get_value_from_tree(["author", "_"], data, "")
        addon.license = get_value_from_tree(["license", "_"], data, "")

        # print("VERSION:", level.filename, " ", level.version)

        #if level.version == 1:
        #    raise Exception("version 1 levels not supported at the moment")
        #else:
        #    level.parse_v2(data)

        return addon

    def __init__(self):
        self.id = "no-id"
        self.version = 1
        self.type = "levelset"
        self.title = "No Title"
        self.author = "No Author"
        self.license = "GPL 2+ / CC-by-sa 3.0"
        self.filename = None

    def parse_v2(self, data):
        self.name = get_value_from_tree(["id", "_"], data, "")
        self.version = get_value_from_tree(["version", "_"], data, "")
        self.type = get_value_from_tree(["type", "_"], data, "")
        self.title = get_value_from_tree(["title", "_"], data, "")
        self.author = get_value_from_tree(["author", "_"], data, "")
        self.license = get_value_from_tree(["license", "_"], data, "")

    def save(self, filename):
        with open(filename, "w") as f:
            self.save_io(f)

    def save_io(self, f):
        writer = SExprWriter(f)
        writer.write_comment("Generated by Flexlay Level Editor (Development Version)")
        writer.begin_list("supertux-addoninfo")
        writer.write_string("id", self.id)
        writer.write_int("version", self.version)
        writer.write_string("type", self.type)
        writer.write_string("title", self.title)
        writer.write_string("author", self.author)
        if self.contact:
            writer.write_string("contact", self.contact)
        if self.license:
            writer.write_string("license", self.license)
        writer.end_list()

# EOF #
