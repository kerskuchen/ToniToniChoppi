import math
from xml.etree import ElementTree


# http://betweenborders.com/wordsmithing/a4-vs-us-letter/
#           Width    Length
# A4        210.0mm  297.0mm
# US-Letter 215.9mm  279.4mm
PAGE_INNER_WIDTH_MM = 180.0
PAGE_INNER_HEIGHT_MM = 250.0
PAGE_BORDER_MM = 15.0
PAGE_WIDTH_MM = PAGE_INNER_WIDTH_MM + 2.0 * PAGE_BORDER_MM
PAGE_HEIGHT_MM = PAGE_INNER_HEIGHT_MM + 2.0 * PAGE_BORDER_MM

SVG_NAMESPACE = {"svg": "http://www.w3.org/2000/svg"}

tree = ElementTree.parse("test-a0.svg")
svg_node = tree.getroot()
assert svg_node.tag.endswith("svg"), "Input file is not a valid SVG image"
assert svg_node.get("x") == None, "SVG image with 'x' attribute is not supported"
assert svg_node.get("y") == None, "SVG image with 'y' attribute is not supported"

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
print("Resulting page count: {}x{}".format(page_count_x, page_count_y))
assert page_count_x > 0, "Image has invalid horizontal dimensions"
assert page_count_y > 0, "Image has invalid horizontal dimensions"

page_index_x = 0
page_index_y = 0

clip_rect_x = page_index_x * PAGE_INNER_WIDTH_MM
clip_rect_y = page_index_y * PAGE_INNER_WIDTH_MM
clip_rect_width = PAGE_INNER_WIDTH_MM
clip_rect_height = PAGE_INNER_WIDTH_MM

svg_node.set("width", str(PAGE_WIDTH_MM))
svg_node.set("height", str(PAGE_HEIGHT_MM))
svg_node.set(
    "viewBox",
    "{} {} {} {}".format(
        clip_rect_x - PAGE_BORDER_MM,
        clip_rect_y - PAGE_BORDER_MM,
        PAGE_WIDTH_MM,
        PAGE_HEIGHT_MM,
    ),
)

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
