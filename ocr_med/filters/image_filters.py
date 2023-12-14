import cv2
import numpy as np

class ImageFilter:

    @staticmethod
    def convert_to_grayscale(image):

        grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        return grayscale_image
    
    @staticmethod
    def measure_quality(original_image, unrotated_image):
        
        hist_original = cv2.calcHist([original_image], [0], None, [256], [0, 256])
        hist_unrotated = cv2.calcHist([unrotated_image], [0], None, [256], [0, 256])

        quality = cv2.compareHist(hist_original, hist_unrotated, cv2.HISTCMP_INTERSECT)

        return quality
    
    @staticmethod
    def unrotate_image(image, angle_degrees):

        rows, cols = image.shape[:2]
        
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle_degrees, 1)
        
        unrotated_image = cv2.warpAffine(image, M, (cols, rows))
        
        return unrotated_image

    @staticmethod
    def blurry_filter(image):

        sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        filtered_img = cv2.filter2D(image, -1, sharpen_kernel)

        return filtered_img
    
    @staticmethod
    def shadow_filter(image):

        rgb_planes = cv2.split(image)
        result_norm_planes = []

        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_norm_planes.append(norm_img)
            
        result_norm = cv2.merge(result_norm_planes)

        return result_norm
    
    @staticmethod
    def noise_filter(image):
        
        kernel = np.ones((3, 3), np.uint8)
        eroded_image = cv2.erode(image, kernel)
        opened_image = cv2.dilate(kernel=kernel, src=eroded_image)

        return opened_image
    
    @staticmethod
    def salt_and_pepper_filter(image):

        median_blur = cv2.medianBlur(image, 3)

        return median_blur
    
    @classmethod
    def rotation_filter(cls, image): # WIP not finished yet
        best_unrotated_image = None
        best_quality = 1.0
        
        for angle in range(-45, 46, 1):
            unrotated_image = cls.unrotate_image(image, angle)
            quality = cls.measure_quality(image, unrotated_image)
            
            if quality > best_quality:
                best_quality = quality
                best_unrotated_image = unrotated_image
                print(angle)
        
        return best_unrotated_image
    
    @staticmethod
    def wrinkle_filter(image):

        kernel = np.ones((5, 5), np.uint8)
        kernel2 = np.ones((3, 3), np.uint8)

        image = ImageFilter.convert_to_grayscale(image)

        morph_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=3)
    
        # Invert the image to enhance wrinkles
        inverted_image = cv2.bitwise_not(morph_image)
        
        # Combine the inverted image with the original using a weighted average
        alpha = 0.5
        beta = 1.0 - alpha
        unwrinkled_image = cv2.addWeighted(inverted_image, alpha, image, beta, 0.0)
        brighten_image = cv2.convertScaleAbs(unwrinkled_image, alpha=1.5, beta=30)
        filtered_image = cv2.erode(brighten_image, kernel2, iterations=1)
        
        return filtered_image
    
if __name__ == '__main__':
    pass
