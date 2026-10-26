"""用图片信息理解类、实例、self、初始化和简单继承。"""


class ImageInfo:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def pixel_count(self):
        return self.width * self.height


class RGBImageInfo(ImageInfo):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.channels = 3

    def value_count(self):
        return self.pixel_count() * self.channels


image = RGBImageInfo(3, 2)
print(f"宽={image.width}, 高={image.height}")
print("像素数:", image.pixel_count())
print("RGB 通道数:", image.channels)
print("通道数值总数:", image.value_count())
