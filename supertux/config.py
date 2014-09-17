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
import configparser


class Config:
    current = None

    @staticmethod
    def create(projectname):
        path = os.path.expanduser("~/.flexlay/")
        if not os.path.isdir(path):
            os.mkdir(path)

        return Config(os.path.join(path, projectname + ".cfg"))

    def __init__(self, filename):
        Config.current = self
        self.filename = filename

        self.datadir = ""
        self.recent_files = []

        if os.path.isfile(filename):
            self.load()

    def load(self, filename=None):
        if filename is None:
            filename = self.filename

        parser = configparser.ConfigParser()
        parser.read(filename)
        if "supertux-editor" in parser:
            self.datadir = parser["supertux-editor"]["datadir"]
            self.recent_files = []
            for i in range(0, 10):
                if ('recent_files%d' % i) in parser['supertux-editor']:
                    recent_file = parser['supertux-editor']['recent_files%d' % i]
                    self.recent_files.append(recent_file)
            print(self.recent_files)
        else:
            print("%s: [supertux-editor] section missing" % filename)

    def save(self, filename=None):
        if filename is None:
            filename = self.filename

        parser = configparser.ConfigParser()
        parser['supertux-editor'] = {}
        parser['supertux-editor']['datadir'] = self.datadir
        for i, recent_file in enumerate(self.recent_files):
            parser['supertux-editor']['recent_files%d' % i] = recent_file

        with open(filename, "w") as fout:
            parser.write(fout)


# EOF #
