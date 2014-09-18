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


from flexlay.util import get_value_from_tree, sexpr_filter

from .sector import Sector
from .util import load_lisp


class Level:

    @staticmethod
    def from_file(filename):
        level = Level(0, 0)

        level.filename = filename

        tree = load_lisp(level.filename, "supertux-level")
        data = tree[1:]

        level.version = get_value_from_tree(["version", "_"], data, 0)

        print("VERSION:", level.filename, " ",  level.version)

        if level.version == 1:
            level.parse_v1(data)
        else:
            level.parse_v2(data)

        return level

    def __init__(self, width, height):
        self.version = 2
        self.filename = None
        self.name = "No Name"
        self.author = "No Author"
        self.target_time = 0

        self.current_sector = Sector(self)
        self.current_sector.new_from_size("main", width, height)
        self.sectors = []
        self.sectors.append(self.current_sector)

    def parse_v2(self, data):
        self.name = get_value_from_tree(["name", "_"], data, "no name")
        self.author = get_value_from_tree(["author", "_"], data, "no author")
        self.target_time = get_value_from_tree(["target-time", "_"], data, 0)

        self.current_sector = None
        self.sectors = []
        for sec in sexpr_filter("sector", data):
            sector = Sector(self)
            sector.load_v2(sec)
            self.sectors.append(sector)
            if sector.name == "main":
                self.current_sector = sector

        if self.current_sector is None:
            print("Error: No main sector defined:", self.sectors)
            self.current_sector = self.sectors[0]

    def parse_v1(self, data):
        sector = Sector(self)
        sector.load_v1(data)

        self.sectors = []
        self.sectors.append(sector)
        self.current_sector = sector

        self.name = get_value_from_tree(["name", "_"], data, "no name")
        self.author = get_value_from_tree(["author", "_"], data, "no author")

    def save(self, filename):
        self.save_v2(filename)

    def save_v2(self, filename):
        with open(filename, "w") as f:
            self.save_io(f)

    def save_io(self, f):
        f.write("(supertux-level\n")
        f.write("  (version 2)\n")
        f.write("  (name   (_ \"%s\"))\n" % self.name)
        f.write("  (author \"%s\")\n" % self.author)

        for sector in self.sectors:
            f.write("  (sector\n")
            sector.save(f)
            f.write("   )\n")

        f.write(" )\n\n;; EOF ;;\n")

    def activate_sector(self, sectorname, workspace):
        for sec in self.sectors:
            if sec.name == sectorname:
                sec.activate(workspace)
                self.current_sector = sec
                break

    def activate(self, workspace):
        self.current_sector.activate(workspace)

    def add_sector(self, sector):
        self.sectors.append(sector)

    def remove_sector(self, name):
        if len(self.sectors) > 1:
            self.sectors = [sec for sec in self.sectors if sec.name != name]
        else:
            print("Only one sector left, can't delete it")

    def get_sectors(self):
        return [sec.name for sec in self.sectors]


# EOF #
