import tensorflow as tf
import os
import numpy as np
from typing import List

from tensorflow.python.saved_model import tag_constants


class ModelRunner:
    INPUT_TENSOR_NAME = 'images_bytes:0'
    OUTPUT_TENSOR_NAME = 'faces_bytes:0'

    _graph = None
    _session = None

    _input_tensor = None
    _output_tensor = None

    def __del__(self):
        if self._session is not None:
            self._session.close()

    def get_last_version(self, model_dir):
        listdir = np.array(os.listdir(model_dir))
        versions = listdir.copy()
        versions.astype(int)

        argmax = np.argmax(versions)
        last_version_dir = listdir[argmax]

        return os.path.join(model_dir, last_version_dir)

    def get_graph_dir(self, model_name, version):
        base_dir = os.path.join(os.path.dirname(__file__), 'models', model_name)

        return self.get_last_version(model_dir=base_dir) if version is None \
            else os.path.join(base_dir, version)

    def __init__(self, model_name, version):
        graph_dir = self.get_graph_dir(model_name=model_name, version=version)
        tf.reset_default_graph()
        config = tf.ConfigProto()
        config.gpu_options.allow_growth()

        session = tf.Session(config=config)
        tf.saved_model.loader.load(session,
                                   [tag_constants.SERVING],
                                   graph_dir)
        self._input_tensor = tf.get_default_graph().get_tensor_by_name(self.INPUT_TENSOR_NAME)
        self._output_tensor = tf.get_default_graph().get_tensor_by_name(self.OUTPUT_TENSOR_NAME)

    def detect(self, images: List[bytes]):
        faces = self._session.run(self._output_tensor,
                                  feed_dict={self._input_tensor: images})
        return list(faces)
