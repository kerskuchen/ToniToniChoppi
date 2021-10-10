import math
import copy
import os
import sys
import shutil
import ctypes
from xml.etree import ElementTree

g_current_image_filepath = ""


def exit_error(message: str):
    MB_OK = 0x0
    ICON_STOP = 0x10
    final_message = "Error processing '{}':\n{}".format(g_current_image_filepath, message)
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, final_message, "ToniToniChoppi", MB_OK | ICON_STOP)
    sys.exit(final_message)


def exit_success():
    MB_OK = 0x0
    ICON_INFO = 0x40
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, "Finished creating sheets. Enjoy!", "ToniToniChoppi", MB_OK | ICON_INFO)
    sys.exit()


SVG_NAMESPACE = {"svg": "http://www.w3.org/2000/svg"}
SVG_NAMESPACE_PREFIX = "{http://www.w3.org/2000/svg}"


class Rect:
    x: float
    y: float
    width: float
    height: float

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


# Dimensions are in Millimeters
class PageChoppingDimensions:
    image_width: float
    image_height: float
    page_inner_width: float
    page_inner_height: float
    page_border: float
    page_outer_width: float
    page_outer_height: float
    count_page_inner_x: int
    count_page_inner_y: int
    last_column_width: float
    last_row_height: float

    # Dimensions are in Millimeters
    def __init__(
        self,
        image_width: float,
        image_height: float,
        page_inner_width: float,
        page_inner_height: float,
        page_border: float,
    ):
        self.image_width = image_width
        self.image_height = image_height
        self.page_inner_width = page_inner_width
        self.page_inner_height = page_inner_height
        self.page_border = page_border

        self.page_outer_width = page_inner_width + 2.0 * page_border
        self.page_outer_height = page_inner_height + 2.0 * page_border

        self.page_count_x = math.ceil(image_width / page_inner_width)
        self.page_count_y = math.ceil(image_height / page_inner_height)
        self.last_column_width = image_width % page_inner_width
        self.last_row_height = image_height % page_inner_height
        if self.last_column_width == 0.0:
            self.last_column_width = page_inner_width
        if self.last_row_height == 0.0:
            self.last_row_height = page_inner_height

        print("Resulting page count: {}x{}".format(self.page_count_x, self.page_count_y))
        print("Last column width: {}mm".format(self.last_column_width))
        print("Last row height: {}mm".format(self.last_row_height))
        if self.page_count_x <= 0:
            exit_error("Image has invalid horizontal dimensions")
        if self.page_count_y <= 0:
            exit_error("Image has invalid vertical dimensions")

    def get_clipping_rect_for_page_index(self, page_index_x: int, page_index_y: int):
        assert 0 <= page_index_x and page_index_x < self.page_count_x
        assert 0 <= page_index_y and page_index_y < self.page_count_y

        if page_index_x == self.page_count_x - 1:
            page_width = self.last_column_width
        else:
            page_width = self.page_inner_width

        if page_index_y == self.page_count_y - 1:
            page_height = self.last_row_height
        else:
            page_height = self.page_inner_height

        return Rect(
            page_index_x * self.page_inner_width,
            page_index_y * self.page_inner_height,
            page_width,
            page_height,
        )


def svg_draw_marker_horizontal(
    svg_parent_node: ElementTree.Element,
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

    svg_parent_node.append(group)


def svg_draw_marker_vertical(
    svg_parent_node: ElementTree.Element,
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

    svg_parent_node.append(group)


def svg_validate_and_get_image_dimensions(svg_node) -> tuple[float]:
    if not svg_node.tag.endswith("svg"):
        exit_error("Input file is not a valid SVG image")
    if svg_node.get("x") != None:
        if not svg_node.get("x").endswith("mm"):
            exit_error("Input image x is not given im Millimeters")
        if float(svg_node.get("x").removesuffix("mm")) != 0.0:
            exit_error("Input image x must be zero")
    if svg_node.get("y") != None:
        if not svg_node.get("y").endswith("mm"):
            exit_error("Input image y is not given im Millimeters")
        if float(svg_node.get("y").removesuffix("mm")) != 0.0:
            exit_error("Input image y must be zero")

    if not svg_node.get("width").endswith("mm"):
        exit_error("Input image width is not given im Millimeters")
    if not svg_node.get("height").endswith("mm"):
        exit_error("Input image height is not given im Millimeters")
    image_width = float(svg_node.get("width").removesuffix("mm"))
    image_height = float(svg_node.get("height").removesuffix("mm"))
    print("SVG image dimensions: {}mm x {}mm ".format(image_width, image_height))

    if svg_node.get("viewBox") == None:
        exit_error("SVG image is missing a 'viewBox' attribute")
    viewbox_x, viewbox_y, viewbox_width, viewbox_height = map(
        float, svg_node.get("viewBox").split(" ")
    )
    print(
        "SVG view box dimensions: {}mm x {}mm {}mm x {}mm".format(
            viewbox_x, viewbox_y, viewbox_width, viewbox_height
        )
    )
    if viewbox_x != 0:
        exit_error("SVG image viewBox.x must be zero")
    if viewbox_y != 0:
        exit_error("SVG image viewBox.y must be zero")
    if viewbox_width != image_width:
        exit_error("SVG image viewBox.width must be the same as the image width")
    if viewbox_height != image_height:
        exit_error("SVG image viewBox.height must be the same as the image height")

    return image_width, image_height


def svg_draw_grid_and_markers(
    svg_node: ElementTree.Element,
    dimensions: PageChoppingDimensions,
    grid_line_thickness: float,
    use_half_grid_thickness: bool,
):
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

    # DRAW GRID
    rect_line = ElementTree.Element(SVG_NAMESPACE_PREFIX + "rect")
    rect_line.set("stroke", "#000")
    rect_line.set("fill", "none")
    rect_line.set("stroke-width", str(grid_line_thickness))
    rect_line.set("x", "0")
    rect_line.set("y", "0")
    rect_line.set("width", str(dimensions.image_width))
    rect_line.set("height", str(dimensions.image_height))
    svg_node.append(rect_line)
    for page_index_x in range(1, dimensions.page_count_x):
        vertical_line = ElementTree.Element(SVG_NAMESPACE_PREFIX + "path")
        vertical_line.set("stroke", "#000")
        if use_half_grid_thickness:
            vertical_line.set("stroke-width", str(grid_line_thickness / 2.0))
        else:
            vertical_line.set("stroke-width", str(grid_line_thickness))
        vertical_line.set(
            "d",
            "M{} 0 V{}".format(page_index_x * dimensions.page_inner_width, dimensions.image_height),
        )
        svg_node.append(vertical_line)
    for page_index_y in range(1, dimensions.page_count_y):
        horizontal_line = ElementTree.Element(SVG_NAMESPACE_PREFIX + "path")
        horizontal_line.set("stroke", "#000")
        if use_half_grid_thickness:
            horizontal_line.set("stroke-width", str(grid_line_thickness / 2.0))
        else:
            horizontal_line.set("stroke-width", str(grid_line_thickness))
        horizontal_line.set(
            "d",
            "M0 {} H{}".format(page_index_y * dimensions.page_inner_height, dimensions.image_width),
        )
        svg_node.append(horizontal_line)

    # HORIZONTAL MARKERS
    for page_index_y in range(0, dimensions.page_count_y):
        for page_index_x in range(0, dimensions.page_count_x - 1):
            col_index = ALPHABET_LETTERS[page_index_x]
            row_index = str(1 + 2 * page_index_y)
            text = row_index + col_index
            pos_x = (page_index_x + 1) * dimensions.page_inner_width
            if page_index_y == dimensions.page_count_y - 1:
                # Last row may be smaller in height
                pos_y = (
                    page_index_y * dimensions.page_inner_height + 0.5 * dimensions.last_row_height
                )
            else:
                pos_y = (
                    page_index_y * dimensions.page_inner_height + 0.5 * dimensions.page_inner_height
                )
            svg_draw_marker_horizontal(
                svg_node, text, pos_x, pos_y, color="#000", opacity=0.30, fill_diamonds=True
            )

    # VERTICAL MARKERS
    for page_index_y in range(0, dimensions.page_count_y - 1):
        for page_index_x in range(0, dimensions.page_count_x):
            col_index = ALPHABET_LETTERS[page_index_x]
            row_index = str(2 * (page_index_y + 1))
            text = row_index + col_index
            if page_index_x == dimensions.page_count_x - 1:
                # Last column may be smaller in width
                pos_x = (
                    page_index_x * dimensions.page_inner_width + 0.5 * dimensions.last_column_width
                )
            else:
                pos_x = (
                    page_index_x * dimensions.page_inner_width + 0.5 * dimensions.page_inner_width
                )
            pos_y = (page_index_y + 1) * dimensions.page_inner_height
            svg_draw_marker_vertical(
                svg_node, text, pos_x, pos_y, color="#000", opacity=0.30, fill_diamonds=True
            )


def svg_create_page(
    svg_tree_readonly: ElementTree,
    dimensions: PageChoppingDimensions,
    page_index_x: int,
    page_index_y: int,
    enable_debug_color: bool = False,
):
    svg_tree = copy.deepcopy(svg_tree_readonly)
    svg_root_node = svg_tree.getroot()
    clip_rect = dimensions.get_clipping_rect_for_page_index(page_index_x, page_index_y)

    svg_root_node.set("width", str(dimensions.page_outer_width))
    svg_root_node.set("height", str(dimensions.page_outer_height))
    svg_root_node.set(
        "viewBox",
        "{} {} {} {}".format(
            clip_rect.x - dimensions.page_border,
            clip_rect.y - dimensions.page_border,
            dimensions.page_outer_width,
            dimensions.page_outer_height,
        ),
    )

    clip_rect_node = ElementTree.Element(SVG_NAMESPACE_PREFIX + "rect")
    clip_rect_node.set("x", str(clip_rect.x))
    clip_rect_node.set("y", str(clip_rect.y))
    clip_rect_node.set("width", str(clip_rect.width))
    clip_rect_node.set("height", str(clip_rect.height))
    clip_rect_node.set("stroke_width", "0")
    clip_rect_node.set("fill", "#000")

    clip_path_node_page = ElementTree.Element(SVG_NAMESPACE_PREFIX + "clipPath")
    clip_path_node_page.set("id", "page_clipping_rect")
    clip_path_node_page.append(clip_rect_node)

    defs_node = svg_root_node.find("svg:defs", SVG_NAMESPACE)
    if defs_node == None:
        defs_node = ElementTree.Element(SVG_NAMESPACE_PREFIX + "defs")
        svg_root_node.append(defs_node)
    defs_node.append(clip_path_node_page)

    tags_to_reparent = [
        SVG_NAMESPACE_PREFIX + "text",
        SVG_NAMESPACE_PREFIX + "ellipse",
        SVG_NAMESPACE_PREFIX + "image",
        SVG_NAMESPACE_PREFIX + "line",
        SVG_NAMESPACE_PREFIX + "polyon",
        SVG_NAMESPACE_PREFIX + "polyline",
        SVG_NAMESPACE_PREFIX + "rect",
        SVG_NAMESPACE_PREFIX + "circle",
        SVG_NAMESPACE_PREFIX + "g",
        SVG_NAMESPACE_PREFIX + "path",
    ]
    elements_to_reparent = []
    for child in svg_root_node:
        if child.tag in tags_to_reparent:
            elements_to_reparent.append(child)

    clipping_group_node = ElementTree.Element(SVG_NAMESPACE_PREFIX + "g")
    clipping_group_node.set("clip-path", "url(#page_clipping_rect)")
    svg_root_node.append(clipping_group_node)

    for element in elements_to_reparent:
        svg_root_node.remove(element)
        clipping_group_node.append(element)

    ###
    if enable_debug_color:
        back_rect = ElementTree.Element(SVG_NAMESPACE_PREFIX + "rect")
        back_rect.set("x", str(clip_rect.x - dimensions.page_border))
        back_rect.set("y", str(clip_rect.y - dimensions.page_border))
        back_rect.set("width", str(dimensions.page_outer_width))
        back_rect.set("height", str(dimensions.page_outer_height))
        back_rect.set("stroke_width", "0")
        back_rect.set("fill", "#ff00ff")
        back_rect.set("opacity", "0.2")
        svg_root_node.append(back_rect)
    ###

    return svg_tree


def process_image(
    image_filepath: str,
    page_inner_width_mm: float,
    page_inner_height_mm: float,
    page_border_mm: float,
):
    global g_current_image_filepath
    g_current_image_filepath = image_filepath
    print("==============\nProcessing image file: '{}'".format(image_filepath))
    svg_tree = ElementTree.parse(image_filepath)
    svg_root_node = svg_tree.getroot()
    image_width, image_height = svg_validate_and_get_image_dimensions(svg_root_node)
    dimensions = PageChoppingDimensions(
        image_width, image_height, page_inner_width_mm, page_inner_height_mm, page_border_mm
    )

    svg_tree_overview = copy.deepcopy(svg_tree)
    svg_root_node_overview = svg_tree_overview.getroot()
    svg_draw_grid_and_markers(svg_root_node_overview, dimensions, 1.0, True)

    svg_tree_page = svg_tree
    svg_root_node_page = svg_tree_page.getroot()
    svg_draw_grid_and_markers(svg_root_node_page, dimensions, 1.0, False)

    svg_trees_pages = {}
    for page_index_y in range(dimensions.page_count_y):
        for page_index_x in range(dimensions.page_count_x):
            svg_trees_pages[(page_index_x, page_index_y)] = svg_create_page(
                svg_tree_page, dimensions, page_index_x, page_index_y, enable_debug_color=False
            )

    image_filename = os.path.splitext(os.path.basename(image_filepath))[0]
    output_dir = image_filename
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    svg_tree_overview.write(os.path.join(output_dir, image_filename + "__overview.svg"))
    for (page_index_x, page_index_y), svg_tree_page in svg_trees_pages.items():
        svg_tree_page.write(
            os.path.join(
                output_dir,
                "{}__{}x{}.svg".format(image_filename, page_index_x, page_index_y),
            )
        )


def main():
    # http://betweenborders.com/wordsmithing/a4-vs-us-letter/
    #           Width    Length
    # A4        210.0mm  297.0mm
    # US-Letter 215.9mm  279.4mm
    PAGE_INNER_WIDTH_MM = 180.0
    PAGE_INNER_HEIGHT_MM = 250.0
    PAGE_BORDER_MM = 14.0

    # NOTE: This prevents writing "ns0" on each tag in the output file
    ElementTree.register_namespace("", "http://www.w3.org/2000/svg")

    image_filepaths = [each for each in os.listdir("./") if each.endswith(".svg")]
    for image_filepath in image_filepaths:
        process_image(image_filepath, PAGE_INNER_WIDTH_MM, PAGE_INNER_HEIGHT_MM, PAGE_BORDER_MM)

    exit_success()


main()
