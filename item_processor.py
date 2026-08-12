from pathlib import Path

from PIL import Image


# ============================================================
# KONFIGURASI DEFAULT
# ============================================================

DEFAULT_SIZE = 24

DEFAULT_BACKGROUND = (
    255,
    0,
    255,
    255
)

DEFAULT_RESIZE_METHOD = (
    Image.Resampling.LANCZOS
)


# ============================================================
# NORMALIZE BACKGROUND
# ============================================================

def normalize_background(
    background
):
    """
    Mengubah background menjadi format RGBA.

    background dapat berupa:

        None
        (R, G, B)
        (R, G, B, A)

    None berarti background transparan.
    """

    if background is None:
        return (
            0,
            0,
            0,
            0
        )

    if len(background) == 3:

        return (
            background[0],
            background[1],
            background[2],
            255
        )

    if len(background) == 4:

        return (
            background[0],
            background[1],
            background[2],
            background[3]
        )

    raise ValueError(
        "Background harus berupa "
        "(R, G, B), (R, G, B, A), "
        "atau None."
    )


# ============================================================
# FLATTEN TRANSPARENCY
# ============================================================

def flatten_transparency(
    image,
    background
):
    """
    Menggabungkan image RGBA dengan background.

    Jika background=None, transparency
    tetap dipertahankan.

    Jika background diberikan, alpha image
    akan dikompositkan ke background.
    """

    image = image.convert(
        "RGBA"
    )

    if background is None:

        return image

    background_rgba = (
        normalize_background(
            background
        )
    )

    canvas = Image.new(
        "RGBA",
        image.size,
        background_rgba
    )

    canvas.alpha_composite(
        image
    )

    return canvas


# ============================================================
# HITUNG UKURAN PROPORSIONAL
# ============================================================

def calculate_fit_size(
    width,
    height,
    target_width,
    target_height,
    allow_upscale=False
):
    """
    Menghitung ukuran baru secara proporsional.

    allow_upscale=False:
        Image kecil tidak diperbesar.

    allow_upscale=True:
        Image boleh diperbesar.
    """

    if width <= 0 or height <= 0:

        raise ValueError(
            "Ukuran image tidak valid."
        )

    if target_width <= 0:
        raise ValueError(
            "Target width harus lebih besar "
            "dari 0."
        )

    if target_height <= 0:
        raise ValueError(
            "Target height harus lebih besar "
            "dari 0."
        )

    scale_x = (
        target_width / width
    )

    scale_y = (
        target_height / height
    )

    scale = min(
        scale_x,
        scale_y
    )

    if not allow_upscale:

        scale = min(
            scale,
            1.0
        )

    new_width = max(
        1,
        round(
            width * scale
        )
    )

    new_height = max(
        1,
        round(
            height * scale
        )
    )

    return (
        new_width,
        new_height
    )


# ============================================================
# RESIZE IMAGE
# ============================================================

def resize_image(
    image,
    target_width,
    target_height,
    resize_method=DEFAULT_RESIZE_METHOD,
    allow_upscale=False
):
    """
    Resize image secara proporsional.

    Image tidak akan diperbesar jika
    allow_upscale=False.
    """

    new_width, new_height = (
        calculate_fit_size(
            image.width,
            image.height,
            target_width,
            target_height,
            allow_upscale
        )
    )

    if (
        new_width == image.width
        and
        new_height == image.height
    ):

        return image.copy()

    return image.resize(
        (
            new_width,
            new_height
        ),
        resize_method
    )


# ============================================================
# CENTER IMAGE
# ============================================================

def center_image(
    image,
    canvas_width,
    canvas_height,
    background=None
):
    """
    Menempatkan image di tengah canvas.

    background=None:
        Canvas transparan.

    background warna:
        Canvas menggunakan warna tersebut.
    """

    if canvas_width <= 0:
        raise ValueError(
            "Canvas width tidak valid."
        )

    if canvas_height <= 0:
        raise ValueError(
            "Canvas height tidak valid."
        )

    background_rgba = (
        normalize_background(
            background
        )
    )

    canvas = Image.new(
        "RGBA",
        (
            canvas_width,
            canvas_height
        ),
        background_rgba
    )

    x = (
        canvas_width
        -
        image.width
    ) // 2

    y = (
        canvas_height
        -
        image.height
    ) // 2

    canvas.alpha_composite(
        image,
        (
            x,
            y
        )
    )

    return canvas


# ============================================================
# PROCESS ITEM
# ============================================================

def process_item(
    source_image,
    size=DEFAULT_SIZE,
    background=DEFAULT_BACKGROUND,
    resize_method=DEFAULT_RESIZE_METHOD,
    allow_upscale=False,
    flatten_before_resize=True
):
    """
    Engine utama pemrosesan image.

    Parameter
    ---------

    source_image:
        PIL.Image.

    size:
        Ukuran canvas output.
        Contoh:
            24
            100

    background:
        Warna background.

        Contoh:
            (255, 0, 255)

        atau:

            (255, 255, 255, 255)

        atau:

            None

    resize_method:
        Metode resize PIL.

    allow_upscale:
        False = image kecil tidak diperbesar.

    flatten_before_resize:
        True:
            transparency dikompositkan ke
            background sebelum resize.

        False:
            transparency dipertahankan selama
            resize.

    Return
    ------

    PIL.Image RGBA
    """

    if source_image is None:

        raise ValueError(
            "Source image tidak tersedia."
        )

    if size <= 0:

        raise ValueError(
            "Size harus lebih besar "
            "dari 0."
        )

    source_image = (
        source_image.convert(
            "RGBA"
        )
    )

    # --------------------------------------------------------
    # FLATTEN TRANSPARENCY
    # --------------------------------------------------------

    if flatten_before_resize:

        working_image = (
            flatten_transparency(
                source_image,
                background
            )
        )

    else:

        working_image = (
            source_image.copy()
        )

    # --------------------------------------------------------
    # RESIZE PROPORSIONAL
    # --------------------------------------------------------

    resized = resize_image(
        working_image,
        size,
        size,
        resize_method,
        allow_upscale
    )

    # --------------------------------------------------------
    # CENTER
    # --------------------------------------------------------

    result = center_image(
        resized,
        size,
        size,
        background
    )

    return result


# ============================================================
# SAVE IMAGE
# ============================================================

def save_image(
    image,
    output_path,
    format=None
):
    """
    Menyimpan image.

    Jika format tidak diberikan,
    PIL akan menentukan berdasarkan extension.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image.save(
        output_path,
        format=format
    )


# ============================================================
# SAVE BMP
# ============================================================

def save_bmp(
    image,
    output_path,
    background=None
):
    """
    Menyimpan image sebagai BMP.

    BMP tidak digunakan dengan alpha
    untuk output item.

    Jika image masih RGBA, maka akan
    dikonversi menjadi RGB.

    background=None:
        Alpha akan dibuang secara langsung.

    background diberikan:
        Image akan dikompositkan terlebih
        dahulu ke background.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    if background is not None:

        image = (
            flatten_transparency(
                image,
                background
            )
        )

    image = image.convert(
        "RGB"
    )

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image.save(
        output_path,
        "BMP"
    )


# ============================================================
# TEST MANUAL
# ============================================================

if __name__ == "__main__":

    print(
        "item_processor.py"
    )

    print(
        "Engine image processor siap."
    )