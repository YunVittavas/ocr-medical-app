import numpy as np
import cv2

class BaseClass:

    image_path: str
    image_shape: tuple
    image_for_processing: np.ndarray

    def __init__(self, image_path):
        BaseClass.image_path = image_path
        BaseClass.image_shape = cv2.imread(image_path).shape
        BaseClass.image_for_processing = cv2.imread(image_path, cv2.COLOR_GRAY2BGR)