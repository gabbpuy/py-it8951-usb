# py-it8951-usb
Python USB Drivers for the IT8951 e-paper interface for various WaveShare devices. I have the 9.7" version, YMMV, but
it should work for any of them.

Based on the c reference drivers, the 
[`IT8951_USB_ProgrammingGuide_v.0.4_20161114.pdf`](https://www.waveshare.com/w/upload/c/c9/IT8951_USB_ProgrammingGuide_v.0.4_20161114.pdf) and 
The Rust Drivers here; https://github.com/faassen/rust-it8951

Tested under Windows and Raspberry Pi 4 (Rasp Pi 5 USB stack does not see the device)

The device looks like a mass storage device, and you write to it and read from it using SCSI commands over the bulk 
USB endpoints. It's quirky, but it works fine.

I'm probably not going to upload this to PyPi, but if you want to use it in a project you, once your venv is set up;

```shell
$ (venv) cd py-it8951-usb
$ (venv) pip install -e .
```

Should install it into your project as a dependency.

These work for my home projects, and I hope it's useful to someone else. If you really want me to PyPi it let me know
(because you need it as a dependency for something you're also publishing) and I'll think about it. You can also copy
the code into your project though :-)

# Example

Example Grabs front page of Seattle Times from freedom forum and sets it as the full page.

```python
# Add to requirements
# beautifulsoup4
# lxml
# requests


from io import BytesIO

from PIL import Image

from it8951_usb.it8951_usb import IT8951_USB
from it8951_usb.it8951_scsi import IT8951_SCSI, Mode

from bs4 import SoupStrainer, element, BeautifulSoup
import requests

UserAgent = """Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X; en-us) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B176 Safari/7534.48.3"""


def fetch_newspaper(url: str) -> bytearray:
    headers = {
        'User-Agent': UserAgent
    }
    response = requests.get(url, headers=headers)
    page = response.text
    find = SoupStrainer('img', attrs={'alt': 'Front Page Image'})
    tags = BeautifulSoup(page, 'lxml', parse_only=find)
    image_buffer = bytearray()
    for t in (tag for tag in tags if isinstance(tag, element.Tag)):
        src = t.get('src')
        headers['Referer'] = url
        r = requests.get(src, stream=True, headers=headers)
        for chunk in r.iter_content(chunk_size=1024):
            image_buffer.extend(chunk)
    return image_buffer


def do_newspaper():
    img_buffer = BytesIO(fetch_newspaper('https://frontpages.freedomforum.org/newspapers/wa_st-The_Seattle_Times'))
    paper = get_paper()
    image = Image.open(img_buffer).convert('L').rotate(90, expand=True)
    image = image.resize((paper.system_info.width, paper.system_info.height))
    paper.update_region(image, 0, 0, Mode.GC16)


def get_paper():
    id_vendor = 0x048d
    id_product = 0x8951
    connection = IT8951_USB(id_vendor, id_product, 'E-Paper')
    paper = IT8951_SCSI(connection)
    return paper

if __name__ == '__main__':
    do_newspaper()
```
