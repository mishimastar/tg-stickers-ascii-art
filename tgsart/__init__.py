try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print('ASCII Art requires "pillow" package.')
    print('Install it via command:')
    print('    pip install pillow')
    raise

try:
    import webp
except ImportError:
    print('ASCII Art requires "webp" package.')
    print('Install it via command:')
    print('    pip install webp')
    raise

try:
    import numpy as np
except ImportError:
    print('ASCII Art requires "numpy" package.')
    print('Install it via command:')
    print('    pip install numpy')
    raise



class SymbolsPool:
    gscale69 = """' ."`^",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"""
    gscale10 = " .:-=+*#%@"
    gscale29 = " _.,-=+:;cba!?0123456789$W#@Ñ"


class WebPASCII_Error(Exception):
    pass


class WebPASCII:
    def __init__(self):
        self._image_loaded = False
        self._image_processed = False
        self._text_size = 60
        self._out_image_width = None
        self._out_image_height = None

    # def __repr__(self):
    #     return ""

    def __str__(self):
        if self._image_processed:
            return f"Loaded image from: {self._image_loaded_source}\n\
                        Image mode: {self._imp_image_mode}\n\
                        Image dimensions (width, height): ({self._imp_image_width}, {self._imp_image_height})\n\
                        Calculated scale: {self._scale}\n\
                        Result image mode: {self._out_image}\n\
                        Result image dimensions: (width, height): ({self._out_image_width}, {self._out_image_height})\n\
                        Total symbols in image: {self._total_symbols}"
        if self._image_loaded:
            return f"Loaded image from: {self._image_loaded_source}\n\
            Image mode: {self._imp_image_mode}\n\
            Image dimensions (width, height): ({self._imp_image_width}, {self._imp_image_height})\n"
        else:
            return "No image loaded"

    def load_image(self, path_to_webp, mode='RGBA'):
        if path_to_webp.lower().endswith('.webp'):
            self._imp_image = webp.load_image(path_to_webp, mode)
        elif path_to_webp.lower().endswith('.png'):
            self._imp_image = Image.open(path_to_webp)
        else:
            raise WebPASCII_Error('Unknown file type')
        self._image_loaded_source = path_to_webp
        self._imp_image_mode = self._imp_image.mode
        self._imp_image_width = self._imp_image.size[0]
        self._imp_image_height = self._imp_image.size[1]
        if self._out_image_width == None:
            self._out_image_width = self._imp_image_width
        if self._out_image_height == None:
            self._out_image_height = self._imp_image_height
        self._scale = self._imp_image_width / self._imp_image_height - 0.2
        self._image_loaded = True


    def process_image(self, cols=60, symbols=SymbolsPool.gscale29, add_color=True):
        if self._image_loaded:
            if cols > self._imp_image_width:
                raise WebPASCII_Error("cols number must be less than original picture's width")
            self._imp_image_gray = self._imp_image.convert('L')
            self._black_img = Image.new("L", (self._imp_image_width, self._imp_image_height), 0)
            self._alpha_channel = self._imp_image.split()[-1]
            self._imp_image_gray = Image.composite(self._imp_image_gray, self._black_img, self._alpha_channel)
            self._w = self._imp_image_width / cols
            self._h = self._w / self._scale
            self._rows = int(self._imp_image_height / self._h)
            self._aslist = []
            self._total_symbols = 0
            symblen = len(symbols) - 1
            for j in range(self._rows):
                y1 = int(j * self._h)
                y2 = int((j + 1) * self._h)
                if j == self._rows - 1:
                    y2 = self._imp_image_height
                self._aslist.append("")
                for i in range(cols):
                    x1 = int(i * self._w)
                    x2 = int((i + 1) * self._w)
                    if i == cols - 1:
                        x2 = self._imp_image_width
                    img = self._imp_image_gray.crop((x1, y1, x2, y2))
                    buf = np.array(img)
                    w, h = buf.shape
                    avg = int(np.average(buf.reshape(w * h)))
                    gsval = symbols[int((avg * symblen) / 255)]
                    self._total_symbols += 1
                    self._aslist[j] += gsval
            self._asstring = ''
            for line in self._aslist:
                self._asstring = f'{self._asstring}{line}\n'
            self._asstring = self._asstring.strip('\n')
            self._out_image = Image.new('L', (int(cols * self._text_size / 1.819),
                                              self._text_size * int(0.82 * self._out_image_height / self._h) + int(
                                                  self._text_size / 2)))
            draw = ImageDraw.Draw(self._out_image)
            if add_color:
                font = ImageFont.truetype("consolab.ttf", self._text_size)
            else:
                font = ImageFont.truetype("consola.ttf", self._text_size)
            draw.text((0, 0), self._asstring, (255), font=font)
            self._out_image = self._out_image.resize((self._out_image_width, self._out_image_height),
                                                     Image.Resampling.LANCZOS)
            imgnp = np.asarray(self._out_image)
            imgnp[imgnp > 100] = 255
            self._out_image = Image.fromarray(imgnp, mode='L')
            self._background = Image.new("RGB", self._out_image.size, (24, 25, 29))
            if add_color:
                self._blured_rgb = self._imp_image.convert('RGB').filter(ImageFilter.GaussianBlur(radius=5))
                self._blured_rgb = self._blured_rgb.resize((self._out_image_width, self._out_image_height),
                                                         Image.Resampling.LANCZOS)
                self._out_image = Image.composite(self._blured_rgb, self._background, self._out_image)
            else:
                self._white_img = Image.new("RGB", self._out_image.size, (255, 255, 255))
                self._out_image = Image.composite(self._white_img, self._background, self._out_image)
            self._alpha_channel = self._alpha_channel.resize((self._out_image_width, self._out_image_height),
                                                       Image.Resampling.LANCZOS)
            self._out_image.putalpha(self._alpha_channel)
            self._image_processed = True
        else:
            raise WebPASCII_Error('No image object loaded to process!')

    @property
    def asstring(self):
        if self._image_processed:
            return self._asstring
        else:
            raise WebPASCII_Error('No image processed!')

    @property
    def aslist(self):
        if self._image_processed:
            return self._aslist
        else:
            raise WebPASCII_Error('No image processed!')

    @property
    def out_size(self):
        return f"({self._out_image_width}, {self._out_image_height})"

    @property
    def text_size(self):
        return f"{self._text_size} size of Consola Bold"

    def set_out_size(self, width, height):
        self._out_image_width = width
        self._out_image_height = height

    def set_text_size(self, new_text_size):
        self._text_size = int(new_text_size)

    def save(self, path_to_new_file, quality=100):
        if self._image_processed:
            webp.save_image(self._out_image, path_to_new_file, quality=quality, preset=webp.WebPPreset.TEXT)
        else:
            raise WebPASCII_Error('No image processed!')

    def save_as_png(self, path_to_new_file):
        if self._image_processed:
            self._out_image.save(path_to_new_file)
        else:
            raise WebPASCII_Error('No image processed!')

    def save_inp_as_png(self, path_to_new_file):
        """
        Use to save loaded image as .png file
        :param path_to_new_file:
        :return:
        """
        if self._image_loaded:
            self._imp_image.save(path_to_new_file)
        else:
            raise WebPASCII_Error('No image object loaded!')

    def save_inp_as_webp(self, path_to_new_file, quality=100, preset=webp.WebPPreset.TEXT):
        """
        Use to save loaded image as .webp file
        preset could be:
                webp.WebPPreset.DEFAULT     Default
                webp.WebPPreset.PICTURE     Indoor photo, portrait-like
                webp.WebPPreset.PHOTO       Outdoor photo with natural lighting
                webp.WebPPreset.DRAWING     Drawing with high-contrast details
                webp.WebPPreset.ICON        Small-sized colourful image
                webp.WebPPreset.TEXT        Text-like
        :param path_to_new_file:
        :return:
        """
        if self._image_loaded:
            webp.save_image(self._imp_image, path_to_new_file, quality=quality, preset=preset)
        else:
            raise WebPASCII_Error('No image object loaded!')

    def save_as_txt(self, path_to_new_file):
        if self._image_processed:
            with open(path_to_new_file, 'w', encoding='utf-8', errors='ignore') as file:
                file.write(self._asstring)
        else:
            raise WebPASCII_Error('No image processed!')

if __name__ == '__main__':
    pass
