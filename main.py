import math
from xml.etree import ElementTree


# http://betweenborders.com/wordsmithing/a4-vs-us-letter/
#           Width    Length
# A4        210.0mm  297.0mm
# US-Letter 215.9mm  279.4mm
PAGE_INNER_WIDTH_MM = 180.0
PAGE_INNER_HEIGHT_MM = 250.0
PAGE_BORDER_MM = 14.0
PAGE_WIDTH_MM = PAGE_INNER_WIDTH_MM + 2.0 * PAGE_BORDER_MM
PAGE_HEIGHT_MM = PAGE_INNER_HEIGHT_MM + 2.0 * PAGE_BORDER_MM

SVG_NAMESPACE = {"svg": "http://www.w3.org/2000/svg"}
SVG_NAMESPACE_PREFIX = "{http://www.w3.org/2000/svg}"

ALPHABET_LETTERS = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]

# NOTE: This prevents writing "ns0" on each tag in the output file
ElementTree.register_namespace("", "http://www.w3.org/2000/svg")

tree = ElementTree.parse("test-a0.svg")
svg_node = tree.getroot()
assert svg_node.tag.endswith("svg"), "Input file is not a valid SVG image"
assert (
    svg_node.get("x") == None or float(svg_node.get("x")) == 0.0
), "SVG image with 'x' attribute is not supported"
assert (
    svg_node.get("x") == None or float(svg_node.get("x")) == 0.0
), "SVG image with 'y' attribute is not supported"

assert svg_node.get("width").endswith("mm"), "Input image width is not given im Millimeters"
assert svg_node.get("height").endswith("mm"), "Input image height is not given im Millimeters"
image_width = float(svg_node.get("width").removesuffix("mm"))
image_height = float(svg_node.get("height").removesuffix("mm"))
print("SVG image dimensions: {}mm x {}mm ".format(image_width, image_height))

assert svg_node.get("viewBox") != None, "SVG image is missing a 'viewBox' attribute"
viewbox_x, viewbox_y, viewbox_width, viewbox_height = map(float, svg_node.get("viewBox").split(" "))
print(
    "SVG view box dimensions: {}mm x {}mm {}mm x {}mm".format(
        viewbox_x, viewbox_y, viewbox_width, viewbox_height
    )
)
assert viewbox_x == 0, "SVG image viewBox.x must be zero"
assert viewbox_y == 0, "SVG image viewBox.y must be zero"
assert viewbox_width == image_width, "SVG image viewBox.width must be the same as the image width"
assert (
    viewbox_height == image_height
), "SVG image viewBox.height must be the same as the image height"

page_count_x = math.ceil(image_width / PAGE_INNER_WIDTH_MM)
page_count_y = math.ceil(image_height / PAGE_INNER_HEIGHT_MM)
last_page_width = image_width % PAGE_INNER_WIDTH_MM
last_page_height = image_height % PAGE_INNER_HEIGHT_MM
if last_page_width == 0.0:
    last_page_width = PAGE_INNER_WIDTH_MM
if last_page_height == 0.0:
    last_page_height = PAGE_INNER_HEIGHT_MM
print("Resulting page count: {}x{}".format(page_count_x, page_count_y))
assert page_count_x > 0, "Image has invalid horizontal dimensions"
assert page_count_y > 0, "Image has invalid vertical dimensions"

# DRAW GRID
rect_line = ElementTree.Element(SVG_NAMESPACE_PREFIX + "rect")
rect_line.set("stroke", "#000")
rect_line.set("fill", "none")
rect_line.set("stroke-width", "1")
rect_line.set("x", "0")
rect_line.set("y", "0")
rect_line.set("width", str(image_width))
rect_line.set("height", str(image_height))
svg_node.append(rect_line)
for page_index_x in range(1, page_count_x):
    vertical_line = ElementTree.Element(SVG_NAMESPACE_PREFIX + "path")
    vertical_line.set("stroke", "#000")
    vertical_line.set("stroke-width", "1")
    vertical_line.set("d", "M{} 0 V{}".format(page_index_x * PAGE_INNER_WIDTH_MM, image_height))
    svg_node.append(vertical_line)
for page_index_y in range(1, page_count_y):
    horizontal_line = ElementTree.Element(SVG_NAMESPACE_PREFIX + "path")
    horizontal_line.set("stroke", "#000")
    horizontal_line.set("stroke-width", "1")
    horizontal_line.set("d", "M0 {} H{}".format(page_index_y * PAGE_INNER_HEIGHT_MM, image_width))
    svg_node.append(horizontal_line)

# DRAW MARKERS
def draw_marker_horizontal(
    svg: any,
    text: str,
    pos_x: float,
    pos_y: float,
    color: str = "#555",
    fill_diamonds: bool = True,
    opacity: float = 0.7,
    marker_size: float = 7.0,
):
    text_left = ElementTree.Element(SVG_NAMESPACE_PREFIX + "text")
    text_left.set("x", str(pos_x - (marker_size + 2.0)))
    text_left.set("y", str(pos_y))
    text_left.set("font-family", "sans-serif")
    text_left.set("font-size", "10")
    text_left.set("dominant-baseline", "middle")
    text_left.set("text-anchor", "end")
    text_left.set("stroke-width", "0")
    text_left.set("stroke", color)
    text_left.set("fill", color)
    text_left.text = text

    text_right = ElementTree.Element(SVG_NAMESPACE_PREFIX + "text")
    text_right.set("x", str(pos_x + (marker_size + 2.0)))
    text_right.set("y", str(pos_y))
    text_right.set("font-family", "sans-serif")
    text_right.set("font-size", "10")
    text_right.set("dominant-baseline", "middle")
    text_right.set("text-anchor", "start")
    text_right.set("stroke-width", "0")
    text_right.set("stroke", color)
    text_right.set("fill", color)
    text_right.text = text

    diamond = ElementTree.Element(SVG_NAMESPACE_PREFIX + "path")
    diamond.set(
        "d",
        "M{} {} L{} {} L{} {} L{} {} L{} {}".format(
            pos_x - marker_size,
            pos_y,
            pos_x,
            pos_y + marker_size / 2.0,
            pos_x + marker_size,
            pos_y,
            pos_x,
            pos_y - marker_size / 2.0,
            pos_x - marker_size,
            pos_y,
        ),
    )
    diamond.set("stroke-width", "0.5")
    diamond.set("stroke", color)
    if fill_diamonds:
        diamond.set("fill", color)
    else:
        diamond.set("fill", "none")
    diamond.text = text

    group = ElementTree.Element(SVG_NAMESPACE_PREFIX + "g")
    group.set("opacity", str(opacity))
    group.append(text_left)
    group.append(text_right)
    group.append(diamond)

    svg_node.append(group)


def draw_marker_vertical(
    svg: any,
    text: str,
    pos_x: float,
    pos_y: float,
    color: str = "#555",
    fill_diamonds: bool = True,
    opacity: float = 0.7,
    marker_size: float = 7.0,
):
    text_top = ElementTree.Element(SVG_NAMESPACE_PREFIX + "text")
    text_top.set("x", str(pos_x))
    text_top.set("y", str(pos_y - (marker_size + 5.0)))
    text_top.set("font-family", "sans-serif")
    text_top.set("font-size", "10")
    text_top.set("dominant-baseline", "middle")
    text_top.set("text-anchor", "middle")
    text_top.set("stroke-width", "0")
    text_top.set("stroke", color)
    text_top.set("fill", color)
    text_top.text = text

    text_bottom = ElementTree.Element(SVG_NAMESPACE_PREFIX + "text")
    text_bottom.set("x", str(pos_x))
    text_bottom.set("y", str(pos_y + (marker_size + 7.0)))
    text_bottom.set("font-family", "sans-serif")
    text_bottom.set("font-size", "10")
    text_bottom.set("dominant-baseline", "middle")
    text_bottom.set("text-anchor", "middle")
    text_bottom.set("stroke-width", "0")
    text_bottom.set("stroke", color)
    text_bottom.set("fill", color)
    text_bottom.text = text

    diamond = ElementTree.Element(SVG_NAMESPACE_PREFIX + "path")
    diamond.set(
        "d",
        "M{} {} L{} {} L{} {} L{} {} L{} {}".format(
            pos_x,
            pos_y - marker_size,
            pos_x + marker_size / 2.0,
            pos_y,
            pos_x,
            pos_y + marker_size,
            pos_x - marker_size / 2.0,
            pos_y,
            pos_x,
            pos_y - marker_size,
        ),
    )
    diamond.set("stroke-width", "0.5")
    diamond.set("stroke", color)
    if fill_diamonds:
        diamond.set("fill", color)
    else:
        diamond.set("fill", "none")
    diamond.text = text

    group = ElementTree.Element(SVG_NAMESPACE_PREFIX + "g")
    group.set("opacity", str(opacity))
    group.append(text_top)
    group.append(text_bottom)
    group.append(diamond)

    svg_node.append(group)


# HORIZONTAL MARKERS
for page_index_y in range(0, page_count_y):
    for page_index_x in range(0, page_count_x - 1):
        col_index = ALPHABET_LETTERS[page_index_x]
        row_index = str(1 + 2 * page_index_y)
        text = row_index + col_index
        pos_x = (page_index_x + 1) * PAGE_INNER_WIDTH_MM
        if page_index_y == page_count_y - 1:
            # Last row may be smaller in height
            pos_y = page_index_y * PAGE_INNER_HEIGHT_MM + 0.5 * last_page_height
        else:
            pos_y = page_index_y * PAGE_INNER_HEIGHT_MM + 0.5 * PAGE_INNER_HEIGHT_MM
        draw_marker_horizontal(
            svg_node, text, pos_x, pos_y, color="#000", opacity=0.30, fill_diamonds=True
        )

# VERTICAL MARKERS
for page_index_y in range(0, page_count_y - 1):
    for page_index_x in range(0, page_count_x):
        col_index = ALPHABET_LETTERS[page_index_x]
        row_index = str(2 * (page_index_y + 1))
        text = row_index + col_index
        if page_index_x == page_count_x - 1:
            # Last column may be smaller in width
            pos_x = page_index_x * PAGE_INNER_WIDTH_MM + 0.5 * last_page_width
        else:
            pos_x = page_index_x * PAGE_INNER_WIDTH_MM + 0.5 * PAGE_INNER_WIDTH_MM
        pos_y = (page_index_y + 1) * PAGE_INNER_HEIGHT_MM
        draw_marker_vertical(
            svg_node, text, pos_x, pos_y, color="#000", opacity=0.30, fill_diamonds=True
        )

clip_rect_x = page_index_x * PAGE_INNER_WIDTH_MM
clip_rect_y = page_index_y * PAGE_INNER_HEIGHT_MM
clip_rect_width = PAGE_INNER_WIDTH_MM
clip_rect_height = PAGE_INNER_HEIGHT_MM

# svg_node.set("width", str(PAGE_WIDTH_MM))
# svg_node.set("height", str(PAGE_HEIGHT_MM))
# svg_node.set(
#     "viewBox",
#     "{} {} {} {}".format(
#         clip_rect_x - PAGE_BORDER_MM,
#         clip_rect_y - PAGE_BORDER_MM,
#         PAGE_WIDTH_MM,
#         PAGE_HEIGHT_MM,
#     ),
# )

# print(svg_node.text)
# print(svg_node.tail)
# print(svg_node.attrib)
# for child in svg_node:
#     print(child.tag, child.attrib)

defs_node = svg_node.find("svg:defs", SVG_NAMESPACE)
assert defs_node != None
if defs_node != None:
    for clippath_node in defs_node.findall("svg:clipPath", SVG_NAMESPACE):
        print(clippath_node.tag, clippath_node.attrib)

tree.write("output.svg")
