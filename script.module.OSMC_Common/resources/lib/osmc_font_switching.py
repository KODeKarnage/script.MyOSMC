from collections import namedtuple
import os
import re
import xml.etree.ElementTree as ET

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


def match_addon_fonts_with_skin_fonts(addon_font_file, skin_font_file=None, threshold=9999):
    """ Returns a dictionary of name matches between the addon fonts and the skin fonts.

    Matching is done on the font size first, then the filename, then the spacing. 

    Provide the addon font file and optionally the skin font file. If no skin font file is
    provided, then the function will try and find it itself.

    threshold specifies the maximum font size (in points) that the skin font can be above the addon font.
    Set to 0 to prohibit any larger fonts being matched. 
    Set to 999 to select the closest skin font size regardless of whether it is bigger or smaller than 
    the addon font.

    """
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
        all_fonts = [x for x in skin_fonts if x.size - a_font.size <= threshold]

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


def replace_addon_fonts_in_lines(original_lines, font_name_matching_dict):
    """ Takes a list of strings, tries to identify the existing font names, replaces those with 
    the equivalent skin font name."""

    newlines = []

    for line in original_lines:

        # pass through lines that do not have the font tag
        if '<font>' not in line: 
            newlines.append(line)
            continue

        tag_contents = re.search(r'.*<font>(\w*).*', line, re.IGNORECASE)

        # pass through lines where a match is not found
        if not tag_contents:
            newlines.append(line)
            continue

        existing_font_name = tag_contents.group(1)

        if not existing_font_name:
            newlines.append(line)
            continue

        new_font_name = font_name_matching_dict.get(existing_font_name, None)

        if not new_font_name:
            newlines.append(line)
            continue

        line = line.replace(existing_font_name, new_font_name)

        newlines.append(line)

    return newlines


def replace_fonts_in_xml_with_skin_equivalents( original_xml, 
                                                font_name_matching_dict=None, 
                                                addon_font_file=None, 
                                                skin_font_file=None, 
                                                threshold=9999, 
                                                new_name=None):
    """ Reads the provided xml and replaces the fonts being used from the addon font names to the skin font names.

    Returns either 'failed' or 'completed'.

    original_xml: the full path location of the window xml we want to convert.

    font_name_matching_dict : optional, a dictionary matching the addon font names to the skin font names. If not provided, 
                                the function will generate this itself using addon_font_file and skin_font_file.

    addon_font_file : the full path location of the xml file with the fonts that are used in the addon. Same structure as a skings Font.xml

    skin_font_file : optional, the full path location of the Font.xml for the skin. Function will search for this file if not provided.
    
    threshold specifies the maximum font size (in points) that the skin font can be above the addon font.
    Set to 0 to prohibit any larger fonts being matched. 
    Set to 999 to select the closest skin font size regardless of whether it is bigger or smaller than the addon font.

    new_name: optional, the full path name of the new window xml. If the current name ends with '_template' then this will be removed
                    in the new name. If it doesnt, then the new name will be original_name_converted.xml
    """

    if '.xml' not in original_xml:
        return 'failed'

    try:
        with open(original_xml, 'r') as f:
            original_lines = f.readlines()
    except:
        return 'failed'

    if not original_lines:
        return 'failed'

    if font_name_matching_dict is None:
        if addon_font_file is None:
            return 'failed'
        else:
            font_name_matching_dict = match_addon_fonts_with_skin_fonts(addon_font_file, skin_font_file, threshold)

    # use the font name matching dict to swap out the existing font names with the skin font names
    new_lines = replace_addon_fonts_in_lines(original_lines, font_name_matching_dict)

    if not new_lines:
        return 'failed'

    # construct the new name if one is not already provided
    if new_name is None:

        if '_template' in original_xml:
            new_name = original_xml.replace('_template', '')

        else:
            new_name = original_xml.replace('.xml', '_converted.xml')

    # write the new file
    with open(new_name, 'w') as f:
        f.writelines(new_lines)
