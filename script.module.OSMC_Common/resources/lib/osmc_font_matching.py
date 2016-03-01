import xml.etree.ElementTree as ET
import os
from collections import namedtuple
try:
    import xbmc
except: 
    pass



def extract_fonts_from_file(filename):
    """ Returns a list of Font namedtuples extracted from the Font.xml provided"""

    Font = namedtuple('Font', 'name size filename linespacing')
    
    tree = ET.parse(filename)
    root = tree.getroot()

    retrieved_fonts = []

    for fontset in root:

        fontset_name = fontset.attrib['id']

        for font in fontset:
            try:
                name = font.find('name').text
            except:
                continue
            try:
                size = int(font.find('size').text)
            except:
                continue                
            try:
                filename = font.find('filename').text
            except:
                continue        
            try:
                linespacing = font.find('linespacing').text
            except:
                linespacing = 0    

            retrieved_fonts.append(Font(name=name, size=size, filename=filename, linespacing=linespacing))                

    return retrieved_fonts


def find_font_file():

    skin_folder = xbmc.translatePath("special://skin")

    for subfolder in [x[1] for x in os.walk(skin_folder)][0]:
        font_file = os.path.join(skin_folder, subfolder, 'Font.xml')
    
        if os.path.isfile(font_file):
            return font_file


def match_fonts(addon_font_file, skin_font_file=None, prefer_smaller=True):
    # loop through the list of fonts that we need replacements for
    # find the skin font closest to the size of our font
    # if tied, try and match filename
    # if still tied, match the line spacing
    # finally choose the first font in the list

    if skin_font_file is None:

        try:
            skin_font_file = find_font_file()
        except:
            skin_font_file = None

        if skin_font_file is None:

            return {}

    skin_fonts  = extract_fonts_from_file(skin_font_file)
    addon_fonts = extract_fonts_from_file(addon_font_file)

    font_matches = {}

    # iterate over all fontsets and fonts in the osmc Font.xml
    for a_font in addon_fonts:

        # eliminate any larger fonts, if prefered
        if prefer_smaller:
            all_fonts = [x for x in skin_fonts if x.size <= a_font.size]
        else:
            all_fonts = skin_fonts

        # if there are no smaller fonts then ignore this addon font, it will probably be replaced by font13
        if not all_fonts:
            continue

        closest_size = min(all_fonts, key = lambda x: abs(x.size - a_font.size)).size

        closest_fonts = [x for x in all_fonts if x.size == closest_size]

        # if we dont have any closest font, then we just wont match those and font13 would be used instead
        if not closest_fonts:
            continue

        elif len(closest_fonts) == 1:

            font_matches[a_font.name] = closest_fonts[0].name
            continue


        else: # choose between the fonts that are closest to the target size

            name_matches = [x for x in closest_fonts if x.filename == a_font.filename]

            # if there is a single name match, use that
            if len(name_matches) == 1:

                font_matches[a_font.name] = name_matches[0].name
                continue    

            # if there are no name matches, use the full, closest font list
            if not name_matches:
                name_matches == closest_fonts

            # if there are multiple name matches (or none), then reduce the list to those matching the linespacing
            line_matches = [x for x in name_matches if x.linespacing == a_font.linespacing]

            # if there is one that matches the linespacing, use that
            if len(line_matches) == 1:
                font_matches[ofontname] = line_matches[0].name
                continue

            else: # otherwise, just use the first font in the closest list
                font_matches[ofontname] = closest_fonts[0].name
                continue

    return font_matches


# skin = "C:\\t\\fnt.xml"
# osmc = "C:\\t\\ofnt.xml"

# print match_fonts(osmc, skin, False)
