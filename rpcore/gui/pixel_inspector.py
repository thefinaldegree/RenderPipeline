"""

RenderPipeline

Copyright (c) 2014-2016 tobspr <tobias.springer1@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from panda3d.core import CardMaker, NodePath, Shader, Vec2
from rpcore.gui.text import Text
from rpcore.rp_object import RPObject
from rpcore.globals import Globals

class PixelInspector(RPObject):

    """ Widget to analyze the rendered pixels, by zooming in """

    def __init__(self, pipeline):
        RPObject.__init__(self)
        self._pipeline = pipeline
        self._node = Globals.base.pixel2d.attach_new_node("ExposureWidgetNode")
        self._create_components()
        self.hide()

    def _create_components(self):
        """ Internal method to init the widgets components """
        cm = CardMaker("cm")
        cm.set_frame(-200, 200, -150, 150)
        self._zoomer = self._node.attach_new_node(cm.generate())

        # Defer the further loading
        Globals.base.taskMgr.doMethodLater(
            1.0, self._late_init, "PixelInspectorLateInit")
        Globals.base.accept("q", self.show)
        Globals.base.accept("q-up", self.hide)

    def show(self):
        """ Shows the inspector """
        self._node.show()

    def hide(self):
        """ Shows the inspector """
        self._node.hide()

    def _late_init(self, task):
        """ Gets called after the pipeline got initialized """
        scene_tex = self._pipeline.stage_mgr.get_pipe("ShadedScene")
        self._zoomer.set_shader(Shader.load(
            Shader.SL_GLSL,
            "$$shader/default_gui_shader.vert.glsl",
            "$$shader/pixel_inspector.frag.glsl"))
        self._zoomer.set_shader_input("SceneTex", scene_tex)

    def update(self):
        mouse = Globals.base.win.get_pointer(0)
        if mouse.get_in_window():
            pos = mouse.get_x(), 1, -mouse.get_y()
            self._node.set_pos(pos)
            self._zoomer.set_shader_input(
                "mousePos", Vec2(mouse.get_x(),
                    Globals.base.win.get_y_size() - mouse.get_y()))
