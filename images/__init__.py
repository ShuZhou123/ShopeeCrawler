import os
import sys


frozen_img_dir = 'images'
about_img_name = 'About.png'
logo_img_name = 'logo_48x48.ico'
frozen_about_img_path = os.path.join(frozen_img_dir, about_img_name)
frozen_logo_img_path = os.path.join(frozen_img_dir, logo_img_name)

font_file_name = 'simfang.ttf'
frozen_font_file_path = os.path.join(frozen_img_dir, font_file_name)


def get_img_path(t):
    if t == 'about':
        cur_path = frozen_about_img_path
        cur_name = about_img_name
    elif t == 'logo':
        cur_path = frozen_logo_img_path
        cur_name = logo_img_name
    elif t == 'font':
        cur_path = frozen_font_file_path
        cur_name = font_file_name
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        img_file = os.path.join(base_path, cur_path)
        # print('About: 1st Try - Read from Bundle Resource')
        if os.path.exists(img_file):
            return img_file
        else:
            # print('About: 1st Read Error - No such file "%s"' % img_file)
            # print('About: 2nd Try - Read from Absolute Path')
            pass

    here = os.path.dirname(os.path.abspath(__file__))
    img_file = os.path.join(here, cur_name)
    if os.path.exists(img_file):
        # print('About: Read from Absolute Path succeed!')
        return img_file
    else:
        # print('About: 2nd Read Error - No such file "%s"' % img_file)
        return None
