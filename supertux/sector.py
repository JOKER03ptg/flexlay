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


from flexlay.util import get_value_from_tree
from flexlay import ObjectLayer, EditorMap

from .data import create_gameobject_from_data
from .tilemap import SuperTuxTileMap
from .gameobj import PathNode


class Sector:

    def __init__(self, parent):
        self.parent = parent
        self.cameramode = "normal"
        self.name = None
        self.music = None
        self.gravity = 10.0
        self.init_script = ""
        self.ambient_light = [1, 1, 1]

        self.width = None
        self.height = None

        self.tilemaps = []

        self.objects = None
        # self.sketch = None
        self.editormap = None

    def get_some_solid_tilemap(self):
        for tilemap in self.tilemaps:
            if tilemap.solid:
                return tilemap

    def get_level(self):
        return self.parent

    def resize(self, size, pos):
        self.width = size.width
        self.height = size.height

        for tilemap in self.tilemaps:
            tilemap.resize(size, pos)

        for obj in self.objects.objects:
            p = obj.get_pos()
            p += 32 * pos
            obj.set_pos(p)

    def new_from_size(self, name, width, height):
        self.name = name
        self.music = ""
        self.gravity = 10.0

        self.width = width
        self.height = height

        self.tilemaps.append(SuperTuxTileMap.from_size(self.width, self.height))
        self.tilemaps.append(SuperTuxTileMap.from_size(self.width, self.height))
        self.tilemaps.append(SuperTuxTileMap.from_size(self.width, self.height))

        self.objects = ObjectLayer()
        # self.sketch  = SketchLayer()

        self.editormap = EditorMap()
        # self.editormap.set_background_color(Color(255, 255, 255))
        for tilemap in self.tilemaps:
            self.editormap.add_layer(tilemap.tilemap_layer)
        self.editormap.add_layer(self.objects)
        # self.editormap.add_layer(self.sketch)
        self.editormap.metadata = self
        return self

    def load_v1(self, data):
        self.name = "main"
        self.music = get_value_from_tree(["music", "_"], data, "")
        self.gravity = get_value_from_tree(["gravity", "_"], data, 10.0)

        self.width = get_value_from_tree(["width", "_"], data, 20)
        self.height = get_value_from_tree(["height", "_"], data, 15)

        foreground = SuperTuxTileMap.from_size(self.width, self.height)
        foreground.set_data(get_value_from_tree(["foreground-tm"], data, []))

        interactive = SuperTuxTileMap.from_size(self.width, self.height)
        interactive.set_data(get_value_from_tree(["interactive-tm"], data, []))

        background = SuperTuxTileMap.from_size(self.width, self.height)
        background.set_data(get_value_from_tree(["background-tm"], data, []))

        self.tilemaps.append(foreground)
        self.tilemaps.append(interactive)
        self.tilemaps.append(background)

        self.cameramode = "normal"

        self.editormap = EditorMap()

        self.objects = ObjectLayer()

        for i in get_value_from_tree(["objects"], data, []):
            (name, odata) = i[0], i[1:]
            # fix some old object names
            if name == "money":
                name = "jumpy"
            if name == "laptop":
                name = "mriceblock"
            create_gameobject_from_data(self.editormap, self.objects, name, odata)

        start_pos_x = get_value_from_tree(["start_pos_x", "_"], data, 0)
        start_pos_y = get_value_from_tree(["start_pos_y", "_"], data, 0)
        sexpr = [["name", "main"], ["x", start_pos_x], ["y", start_pos_y]]
        create_gameobject_from_data(self.editormap, self.objects, "spawnpoint", sexpr)

        background = get_value_from_tree(["background", "_"], data, "")
        if background != "":
            sexpr = [["image", background], ["speed", 0.5]]
            create_gameobject_from_data(self.editormap, self.objects, "background", sexpr)
        else:
            sexpr = [["top_color",
                      get_value_from_tree(["bkgd_red_top", "_"], data, 0),
                      get_value_from_tree(["bkgd_green_top", "_"], data, 0),
                      get_value_from_tree(["bkgd_blue_top", "_"], data, 0)],
                    ["bottom_color",
                     get_value_from_tree(["bkgd_red_bottom", "_"], data, 0),
                     get_value_from_tree(["bkgd_green_bottom", "_"], data, 0),
                     get_value_from_tree(["bkgd_blue_bottom", "_"], data, 0)],
                    ["speed", 0.5]]
            create_gameobject_from_data(self.editormap, self.objects, "background", sexpr)

        partsys = get_value_from_tree(["particle_system", "_"], data, "")
        if partsys == "snow":
            sexpr = []
            create_gameobject_from_data(self.editormap, self.objects, 'particles-snow', sexpr)
        elif partsys == "rain":
            sexpr = []
            create_gameobject_from_data(self.editormap, self.objects, 'particles-rain', sexpr)
        elif partsys == "clouds":
            sexpr = []
            create_gameobject_from_data(self.editormap, self.objects, 'particles-clouds', sexpr)
        elif partsys == "":
            pass
        else:
            print("Unknown particle system type %s" % partsys)

        for tilemap in self.tilemaps:
            self.editormap.add_layer(tilemap)
        self.editormap.add_layer(self.objects)

        # FIXME: Data might not get freed since its 'recursively' refcounted
        self.editormap.metadata = self

    def load_v2(self, data):
        self.name = "<No Name>"
        self.music = ""
        self.init_script = ""
        self.gravity = 10.0
        self.cameramode = "normal"

        self.width = 0
        self.height = 0

        self.tilemaps = []

        self.editormap = EditorMap()

        self.objects = ObjectLayer()
        # self.sketch = SketchLayer()

        for i in data:
            (name, data) = i[0], i[1:]
            if name == "name":
                self.name = data[0]
            elif name == "ambient-light":
                self.ambient_light = data
            elif name == "gravity":
                self.gravity = data[0]
            elif name == "ambient-light":
                pass  # GRUMBEL self.ambient_light = data[0]
            elif name == "music":
                self.music = data[0]
            elif name == "init-script":
                self.init_script = data[0]
            elif name == "tilemap":
                tilemap = SuperTuxTileMap.from_sexpr(data)
                self.tilemaps.append(tilemap)

                # GRUMBEL: incorrect
                if tilemap.solid:
                    self.width = tilemap.width
                    self.height = tilemap.height

            elif name == "camera":
                self.cameramode = "normal"
                # TODO...
            else:
                create_gameobject_from_data(self.editormap, self.objects, name, data)

        for tilemap in self.tilemaps:
            self.editormap.add_layer(tilemap.tilemap_layer)

        self.editormap.add_layer(self.objects)
        # self.editormap.add_layer(self.sketch)
        self.editormap.metadata = self

    def save(self, writer):
        writer.write_string("name", self.name)
        writer.write_string("music", self.music)
        writer.write_rgb("ambient-light", self.ambient_light)
        if self.init_script:
            writer.write_string("init-script", self.init_script)

        writer.begin_list("camera")
        writer.write_string("mode", self.cameramode)
        path_nodes = [obj for obj in self.objects.get_objects() if isinstance(obj, PathNode)]
        if path_nodes:
            writer.begin_list("path")
            for obj in path_nodes:
                pathnode = obj.get_data()
                if isinstance(pathnode, PathNode):
                    writer.begin_list("point")
                    writer.write_inline_point(obj.get_pos())
                    writer.write_int("speed", 1)
                    writer.end_list()
            writer.end_list()
        writer.end_list()

        for obj in self.objects.get_objects():
            obj.metadata.save(writer, obj)

        for tilemap in self.tilemaps:
            tilemap.save(writer)

        # save_strokelayer(writer, self.sketch)


# EOF #
