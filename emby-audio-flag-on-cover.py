#!/usr/bin/python3
import os
import xml.etree.ElementTree as ET
from PIL import Image
import pwd
import grp

# TODO: better identification of nfo metadata files
# TODO: keep original image files as a backup (and use it for next generations)
# TODO: dynamic cross-language flag generation

# Path to search for "poster.jpg" files
search_path = '/var/lib/emby'
flag_resize_factor = 7

def write_flag_to_poster(languages, poster_filepath):
    if len(languages) == 2:
        if 'eng' in languages and 'fre' in languages:
            flag_file = os.path.dirname(__file__) + '/flags/FRAENG.png'
        else:
            print('    ERROR: unknown language combination')
            return False
    
    elif len(languages) == 1:
    	flag_file = os.path.dirname(__file__) + '/flags/' + list(languages)[0].upper() + '.png'

    elif len(languages) == 0:
        print('    ERROR: no language detected')
        return False

    elif len(languages) > 2:
        print('    ERROR: too many languages detected')
        return False    

    if os.path.isfile(flag_file):
        # Open poster
        poster = Image.open(poster_filepath)

        # Open flag
        flag = Image.open(flag_file)
        flag = flag.convert('RGBA')

        # Resize flag - factor 5
        flag_ratio = flag.size[0] / flag.size[1]

        target_flag_size = (
            round(poster.size[0]/flag_resize_factor),
            round(poster.size[0]/flag_resize_factor/flag_ratio)
        )
        flag.thumbnail(target_flag_size)

        # Insert flag at correct position (5ths of flag dimensions used)
        flag_position = (
            round(target_flag_size[0]/5),
            round(poster.size[1] - target_flag_size[1] - target_flag_size[1]/5)
        )
        poster.paste(flag, flag_position)
        poster.save(poster_filepath)

        # File permissions
        uid = pwd.getpwnam("emby").pw_uid
        gid = grp.getgrnam("emby").gr_gid
        os.chown(poster_filepath, uid, gid)

        print('    Poster written to: %s' % poster_filepath)

    else:
        print('    ERROR: flag file not found: %s' % flag_file)
        return False

for root, dir, files in os.walk(search_path):
    for filename in files:
        if filename.endswith('-poster.jpg') or filename == 'poster.jpg':
            poster_filepath = root + '/' + filename
            print('\n%s' % (poster_filepath))

            if filename.endswith('-poster.jpg'):
                media_basename = poster_filepath[:-11]
                nfo_file = media_basename + '.nfo'

            elif filename == 'poster.jpg':
                media_basename = poster_filepath[:-10]

                # Search for nfo file
                onlyfiles = [f for f in os.listdir(media_basename) if os.path.isfile(os.path.join(media_basename, f))]
                for potential_nfo in onlyfiles:
                    if potential_nfo.endswith('.nfo'):
                        nfo_file = media_basename + '/' + potential_nfo

            if os.path.isfile(nfo_file):
                languages = set()
                tree = ET.parse(nfo_file)
                xmlroot = tree.getroot()
                for audio in xmlroot.iter('audio'):
                    language = audio.find('language')
                    if language != None:
                        languages.add(language.text)

                print('    available audio tracks: %s' % ', '.join(languages))
                write_flag_to_poster(languages, poster_filepath)

            else:
                print('    ERROR: no nfo file: %s' % media_basename + '.nfo')
