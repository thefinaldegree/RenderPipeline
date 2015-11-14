
from .. import RenderStage

from panda3d.core import LVecBase2i, PNMImage, Texture
from random import random

class AOStage(RenderStage):

    required_pipes = ["ShadedScene", "GBufferDepth", "GBuffer0", "GBuffer1", "GBuffer2"]
    required_inputs = ["mainCam", "mainRender", "currentProjMat", "cameraPosition"]

    def __init__(self, pipeline):
        RenderStage.__init__(self, "AOStage", pipeline)

    def get_produced_pipes(self):
        return {"AmbientOcclusion": self._target_blur_h['color']}

    def create(self):
        
        # TODO: 8 bits should be enough I think
        self._target = self._create_target("AOSample")
        self._target.set_half_resolution()
        self._target.add_color_texture(bits=16)
        self._target.prepare_offscreen_buffer()

        self._target_upscale = self._create_target("AOUpscale")
        self._target_upscale.add_color_texture(bits=16)
        self._target_upscale.prepare_offscreen_buffer()

        self._target_blur_v = self._create_target("AOBlurV")
        self._target_blur_v.add_color_texture(bits=16)
        self._target_blur_v.prepare_offscreen_buffer()

        self._target_blur_h = self._create_target("AOBlurH")
        self._target_blur_h.add_color_texture(bits=16)
        self._target_blur_h.prepare_offscreen_buffer()

        self._target_upscale.set_shader_input("SourceTex", self._target["color"])
        self._target_blur_v.set_shader_input("SourceTex", self._target_upscale["color"])
        self._target_blur_h.set_shader_input("SourceTex", self._target_blur_v["color"])

        self._target_blur_v.set_shader_input("blur_direction", LVecBase2i(0, 1))
        self._target_blur_h.set_shader_input("blur_direction", LVecBase2i(1, 0))

        self.create_noise_textures()

    def create_noise_textures(self):
        img = PNMImage(4, 4, 3)
        for x in range(4):
            for y in range(4):
                img.set_xel(x, y, random(), random(), random())
        tex = Texture("Rand4x4")
        tex.load(img)
        self._target.set_shader_input("Noise4x4", tex)

    def set_shaders(self):
        self._target.set_shader(self.load_plugin_shader("AOSample.frag.glsl"))
        self._target_upscale.set_shader(self.load_plugin_shader("AOUpscale.frag.glsl"))

        blur_shader = self.load_plugin_shader("AOBlur.frag.glsl")
        self._target_blur_v.set_shader(blur_shader)
        self._target_blur_h.set_shader(blur_shader)

    def resize(self):
        RenderStage.resize(self)
        self.debug("Resizing pass")

    def cleanup(self):
        RenderStage.cleanup(self)
        self.debug("Cleanup pass")