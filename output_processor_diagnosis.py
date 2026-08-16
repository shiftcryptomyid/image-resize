from pathlib import Path

from PIL import Image


# ============================================================
# OUTPUT FORMATS
# ============================================================

OUTPUT_FORMATS = (
    "PNG",
    "BMP",
)


# ============================================================
# RESOLVE OUTPUT FORMAT
# ============================================================

def resolve_output_format(
    output_format
):
    """
    Mengubah nama format menjadi format standar.

    Mendukung:

        "PNG"
        "BMP"
        "png"
        "bmp"
    """

    if not isinstance(
        output_format,
        str
    ):
        raise TypeError(
            "Output format harus berupa string."
        )

    output_format = (
        output_format
        .strip()
        .upper()
    )

    if output_format not in OUTPUT_FORMATS:
        raise ValueError(
            f"Format output tidak didukung: "
            f"{output_format}"
        )

    return output_format

# ============================================================
# BMP COLOR KEY
# ============================================================

BMP_ALPHA_THRESHOLD = 160


def prepare_bmp_color_key(
    image,
    transparent_color,
    alpha_threshold=BMP_ALPHA_THRESHOLD
):
    """
    Menyiapkan RGBA menjadi BMP color-key.

    Alpha hanya digunakan sebagai MASK.

    alpha <= threshold:
        menjadi transparent_color.

    alpha > threshold:
        RGB asli dipertahankan.

    Tidak ada color blending.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    transparent_rgb = (
        transparent_color[0],
        transparent_color[1],
        transparent_color[2]
    )

    result = Image.new(
        "RGB",
        image.size,
        transparent_rgb
    )

    source_pixels = image.load()
    result_pixels = result.load()

    width, height = image.size

    for y in range(height):

        for x in range(width):

            r, g, b, a = (
                source_pixels[x, y]
            )

            # ------------------------------------------------
            # TRANSPARENT
            # ------------------------------------------------

            if a <= alpha_threshold:

                result_pixels[x, y] = (
                    transparent_rgb
                )

            # ------------------------------------------------
            # VISIBLE
            # RGB ASLI
            # ------------------------------------------------

            else:

                result_pixels[x, y] = (
                    r,
                    g,
                    b
                )

    return result
    
    
# ============================================================
# PREPARE IMAGE FOR OUTPUT
# ============================================================

def prepare_image_for_output(
    image,
    output_format,
    background=(255, 255, 255)
):
    """
    Menyiapkan PIL Image sebelum disimpan.

    PNG:
        Transparency dipertahankan.

    BMP:
        BMP tidak menggunakan alpha.
        Image RGBA/RGB dengan transparency
        akan dikompositkan ke background.
    """

    if not isinstance(
        image,
        Image.Image
    ):
        raise TypeError(
            "Image harus berupa PIL Image."
        )

    output_format = (
        resolve_output_format(
            output_format
        )
    )

    # --------------------------------------------------------
    # PNG
    # --------------------------------------------------------

    if output_format == "PNG":

        if image.mode in (
            "RGBA",
            "LA",
            "P",
        ):
            return image.copy()

        return image.convert(
            "RGB"
        )

    # --------------------------------------------------------
    # BMP
    # --------------------------------------------------------

    if output_format == "BMP":

        # ----------------------------------------------------
        # RGBA
        # ----------------------------------------------------

        if image.mode == "RGBA":

            # ----------------------------------------------------
            # BMP + PINK
            #
            # PINK digunakan sebagai color-key
            # transparency untuk ACTOR.
            # ----------------------------------------------------

            if (
                background[0] == 255
                and
                background[1] == 0
                and
                background[2] == 255
            ):

                return prepare_bmp_color_key(
                    image,
                    background,
                    BMP_ALPHA_THRESHOLD
                )

            # ----------------------------------------------------
            # BMP background biasa
            #
            # WHITE / BLACK / warna lain tetap
            # menggunakan alpha compositing.
            # ----------------------------------------------------

            background_image = Image.new(
                "RGBA",
                image.size,
                (
                    background[0],
                    background[1],
                    background[2],
                    255
                )
            )

            composited_image = Image.alpha_composite(
                background_image,
                image
            )

            return composited_image.convert(
                "RGB"
            )
        
        # ----------------------------------------------------
        # LA
        # ----------------------------------------------------

        if image.mode == "LA":

            rgba_image = image.convert(
                "RGBA"
            )

            background_image = Image.new(
                "RGBA",
                image.size,
                (
                    background[0],
                    background[1],
                    background[2],
                    255
                )
            )

            composited_image = Image.alpha_composite(
                background_image,
                rgba_image
            )

            return composited_image.convert(
                "RGB"
            )
        
        
        # ----------------------------------------------------
        # P
        # ----------------------------------------------------

        if image.mode == "P":

            if "transparency" in image.info:

                rgba_image = image.convert(
                    "RGBA"
                )

                background_image = Image.new(
                    "RGBA",
                    image.size,
                    (
                        background[0],
                        background[1],
                        background[2],
                        255
                    )
                )

                composited_image = Image.alpha_composite(
                    background_image,
                    rgba_image
                )

                return composited_image.convert(
                    "RGB"
                )

            return image.convert(
                "RGB"
            )

        # ----------------------------------------------------
        # Other modes
        # ----------------------------------------------------

        if image.mode != "RGB":

            return image.convert(
                "RGB"
            )

        return image.copy()

    raise ValueError(
        "Format output tidak didukung."
    )


# ============================================================
# PREPARE PREVIEW IMAGE
# ============================================================

def prepare_preview_image(
    image,
    output_format,
    background=None
):
    """
    Membuat image khusus untuk preview.

    PNG:
        Menampilkan RGBA asli.

    BMP + PINK:
        Mensimulasikan color-key BMP.
        Warna #FF00FF akan ditampilkan
        sebagai transparent.

    BMP + background lain:
        Menampilkan hasil flatten sesuai
        background.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    output_format = (
        output_format.upper()
    )

    # ========================================================
    # PNG
    # ========================================================

    if output_format == "PNG":

        return image.convert(
            "RGBA"
        )

    # ========================================================
    # BMP
    # ========================================================

    prepared = prepare_image_for_output(
        image,
        "BMP",
        background
    )

    # ========================================================
    # BMP + PINK
    #
    # Simulasikan transparency ACTOR.
    # ========================================================

    if (
        background is not None
        and
        background[0] == 255
        and
        background[1] == 0
        and
        background[2] == 255
    ):

        prepared = prepared.convert(
            "RGB"
        )

        result = Image.new(
            "RGBA",
            prepared.size,
            (
                0,
                0,
                0,
                0
            )
        )

        source_pixels = prepared.load()
        result_pixels = result.load()

        width, height = prepared.size

        for y in range(height):

            for x in range(width):

                r, g, b = (
                    source_pixels[x, y]
                )

                # --------------------------------------------
                # PINK = TRANSPARENT
                # --------------------------------------------

                if (
                    r == 255
                    and
                    g == 0
                    and
                    b == 255
                ):

                    result_pixels[x, y] = (
                        0,
                        0,
                        0,
                        0
                    )

                else:

                    result_pixels[x, y] = (
                        r,
                        g,
                        b,
                        255
                    )

        return result

    # ========================================================
    # BMP BACKGROUND BIASA
    # ========================================================

    return prepared.convert(
        "RGBA"
    )



# ============================================================
# SAVE IMAGE
# ============================================================

def save_image(
    image,
    output_path,
    output_format=None,
    background=(255, 255, 255)
):
    """
    Menyimpan PIL Image ke PNG atau BMP.

    Parameters
    ----------
    image:
        PIL Image.

    output_path:
        Path file output.

    output_format:
        "PNG" atau "BMP".

        Jika None:
        format ditentukan dari extension.

    background:
        Warna background untuk BMP
        ketika image memiliki transparency.

    Returns
    -------
    Path
        Path file yang berhasil disimpan.
    """

    if not isinstance(
        image,
        Image.Image
    ):
        raise TypeError(
            "Image harus berupa PIL Image."
        )

    output_path = Path(
        output_path
    )

    # --------------------------------------------------------
    # FORMAT
    # --------------------------------------------------------

    if output_format is None:

        extension = (
            output_path.suffix
            .lower()
        )

        if extension == ".png":

            output_format = "PNG"

        elif extension == ".bmp":

            output_format = "BMP"

        else:

            raise ValueError(
                "Format output tidak dapat "
                "ditentukan dari extension."
            )

    else:

        output_format = (
            resolve_output_format(
                output_format
            )
        )

    # --------------------------------------------------------
    # PREPARE
    # --------------------------------------------------------

    prepared_image = (
        prepare_image_for_output(
            image,
            output_format,
            background
        )
    )

    # --------------------------------------------------------
    # CREATE DIRECTORY
    # --------------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    prepared_image.save(
        output_path,
        format=output_format
    )

    return output_path

if __name__ == "__main__":

    print(
        "Output processor siap."
    )