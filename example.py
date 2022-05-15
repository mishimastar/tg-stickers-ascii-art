import tgsart
from tgsart import SymbolsPool

sticker = tgsart.WebPASCII()
sticker.load_image('doc/banana.webp')
sticker.process_image(cols=60, symbols=SymbolsPool.gscale29, add_color=True)
sticker.save('doc/banana60C.webp')