import imageio
import os
import numpy as np
import sys
from multiprocessing import Process, Manager

import utils


def _render_async(render_method, arg_list, path, fps):
    frames = []
    for i, args in enumerate(arg_list):
        frames.append(render_method(args))
    imageio.mimsave(path, frames, fps=fps)

class VideoRecorder(object):
    def __init__(self, root_dir, height=256, width=256, camera_id=0, fps=30):
        self.save_dir = utils.make_dir(root_dir, 'video') if root_dir else None
        self.height = height
        self.width = width
        self.camera_id = camera_id
        self.fps = fps
        self.frames = []

    def init(self, enabled=True, async_recorder=True):
        self.frames = []
        self.enabled = self.save_dir is not None and enabled
        self.async_recorder = async_recorder
        self.frame_args = []
        self.render_method = None
        self.process_manager = Manager()

    def record(self, env):
        if self.enabled:
            '''frame = env.render(mode='rgb_array',
                               height=self.height,
                               width=self.width,
                               camera_id=self.camera_id)'''

            if self.async_recorder:
                self.frame_args.append(env.get_render_args())
                if self.render_method is None:
                    self.render_method = type(env).render_async
            else:
                frame = env.render(mode='rgb_array')
                self.frames.append(frame)

    def save(self, file_name):
        if self.enabled:
            if self.async_recorder:
                pr = Process(
                    target=_render_async,
                    args=(self.render_method, self.frame_args, os.path.join(self.save_dir, file_name), self.fps)
                )
                pr.start()
            else:
                path = os.path.join(self.save_dir, file_name)
                imageio.mimsave(path, self.frames, fps=self.fps)


