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
# SIZE PRESETS
# ============================================================

SIZE_PRESETS = {
    "24x24": (24, 24),
    "60x60": (60, 60),
    "100x100": (100, 100),
}

# ============================================================
# RESIZE METHODS
# ============================================================

RESIZE_METHODS = {
    "NEAREST": Image.Resampling.NEAREST,
    "BOX": Image.Resampling.BOX,
    "BILINEAR": Image.Resampling.BILINEAR,
    "BICUBIC": Image.Resampling.BICUBIC,
    "LANCZOS": Image.Resampling.LANCZOS,
}

def get_resize_method(method_name):
    """
    Mengambil metode resize.

    Mendukung dua format:

    Format baru:
        "LANCZOS"
        "BICUBIC"
        "BILINEAR"
        "BOX"
        "NEAREST"

    Format lama:
        Image.Resampling.LANCZOS
        Image.Resampling.BICUBIC
        dst.
    """

    # ========================================================
    # FORMAT PILLOW LANGSUNG
    #
    # Kompatibilitas dengan kode lama.
    #
    # Contoh:
    #     Image.Resampling.LANCZOS
    # ========================================================

    if isinstance(
        method_name,
        Image.Resampling
    ):
        return method_name

    # ========================================================
    # FORMAT STRING
    #
    # Contoh:
    #     "LANCZOS"
    # ========================================================

    if isinstance(method_name, str):

        method_name = method_name.upper()

        if method_name not in RESIZE_METHODS:
            raise ValueError(
                f"Resize method tidak dikenal: "
                f"{method_name}"
            )

        return RESIZE_METHODS[
            method_name
        ]

    # ========================================================
    # FORMAT TIDAK DIDUKUNG
    # ========================================================

    raise TypeError(
        "resize method harus berupa "
        "nama string atau Image.Resampling."
    )


# ============================================================
# BACKGROUND PRESETS
# ============================================================

BACKGROUND_PRESETS = {
    "PINK": (255, 0, 255, 255),
    "WHITE": (255, 255, 255, 255),
    "BLACK": (0, 0, 0, 255),
    "TRANSPARENT": None,
}

def get_background(background):
    """
    Mengambil warna background berdasarkan nama preset.

    Bisa juga menerima tuple RGB/RGBA secara langsung.

    Contoh:

        get_background("PINK")

    atau:

        get_background((255, 128, 0, 255))
    """

    if background is None:
        return None

    if isinstance(background, str):

        background_name = background.upper()

        if background_name not in BACKGROUND_PRESETS:
            raise ValueError(
                f"Background tidak dikenal: "
                f"{background_name}"
            )

        return BACKGROUND_PRESETS[
            background_name
        ]

    if isinstance(background, tuple):

        if len(background) not in (3, 4):
            raise ValueError(
                "Background tuple harus "
                "berisi 3 atau 4 nilai."
            )

        return background

    raise TypeError(
        "Background harus berupa "
        "nama preset atau tuple RGB/RGBA."
    )

# ============================================================
# SIZE RESOLVER
# ============================================================

def resolve_size(size):
    """
    Mengubah ukuran menjadi tuple:

        (width, height)

    Mendukung:

        "24x24"
        "60x60"
        "100x100"

    Custom:

        (32, 48)

    Dan format lama:

        24
        60
        100
    """

    # ========================================================
    # FORMAT LAMA
    #
    # Contoh:
    #     size=24
    #
    # Dianggap sebagai:
    #     24 x 24
    # ========================================================

    if isinstance(size, int):

        if size <= 0:
            raise ValueError(
                "Size harus lebih besar dari 0."
            )

        return (
            size,
            size
        )

    # ========================================================
    # STRING PRESET
    #
    # Contoh:
    #     "24x24"
    # ========================================================

    if isinstance(size, str):

        size_name = size.lower()

        if size_name not in SIZE_PRESETS:
            raise ValueError(
                f"Size preset tidak dikenal: "
                f"{size}"
            )

        return SIZE_PRESETS[
            size_name
        ]

    # ========================================================
    # CUSTOM SIZE
    #
    # Contoh:
    #     (32, 48)
    # ========================================================

    if isinstance(size, tuple):

        if len(size) != 2:
            raise ValueError(
                "Custom size harus "
                "berisi (width, height)."
            )

        width, height = size

        if width <= 0 or height <= 0:
            raise ValueError(
                "Width dan height harus "
                "lebih besar dari 0."
            )

        return (
            int(width),
            int(height)
        )

    # ========================================================
    # FORMAT TIDAK DIDUKUNG
    # ========================================================

    raise TypeError(
        "Size harus berupa integer, "
        "nama preset, atau tuple "
        "(width, height)."
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
    source_width,
    source_height,
    target_width,
    target_height,
    allow_upscale=False
):
    """
    Menghitung ukuran image baru dengan
    mempertahankan aspect ratio.

    Jika allow_upscale=False:
        image tidak akan diperbesar.

    Jika allow_upscale=True:
        image boleh diperbesar.
    """

    if source_width <= 0 or source_height <= 0:
        raise ValueError(
            "Ukuran source image tidak valid."
        )

    if target_width <= 0 or target_height <= 0:
        raise ValueError(
            "Ukuran target tidak valid."
        )

    scale_x = (
        target_width / source_width
    )

    scale_y = (
        target_height / source_height
    )

    scale = min(
        scale_x,
        scale_y
    )

    # Jangan upscale jika tidak diizinkan.
    if not allow_upscale:
        scale = min(
            scale,
            1.0
        )

    new_width = max(
        1,
        round(source_width * scale)
    )

    new_height = max(
        1,
        round(source_height * scale)
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
    image,
    size="24x24",
    resize_method="LANCZOS",
    background="PINK",
    mode="ALPHA",
    allow_upscale=False,
    flatten_before_resize=None
):
    """
    Memproses image menjadi ukuran target.

    Parameter:

        image
            PIL Image sebagai source.

        size
            Bisa berupa:
                "24x24"
                "60x60"
                "100x100"

            atau custom:
                (32, 32)

        resize_method
            Bisa berupa:
                "NEAREST"
                "BOX"
                "BILINEAR"
                "BICUBIC"
                "LANCZOS"

        background
            Bisa berupa:
                "PINK"
                "WHITE"
                "BLACK"
                "TRANSPARENT"

            atau tuple RGB/RGBA.

        mode
            "ALPHA"
                Mempertahankan transparency.

            "FLATTEN"
                Transparency diratakan ke
                background sebelum resize.

        allow_upscale
            False:
                Image yang lebih kecil dari
                target tidak diperbesar.

            True:
                Image boleh diperbesar.

        flatten_before_resize
            Parameter lama untuk kompatibilitas
            dengan kode yang sudah ada.

            True  -> mode FLATTEN
            False -> mode ALPHA
    """

    # ========================================================
    # VALIDASI SOURCE
    # ========================================================

    if not isinstance(image, Image.Image):
        raise TypeError(
            "image harus berupa PIL.Image.Image."
        )

    # ========================================================
    # KOMPATIBILITAS PARAMETER LAMA
    # ========================================================

    if flatten_before_resize is not None:

        if flatten_before_resize:
            mode = "FLATTEN"
        else:
            mode = "ALPHA"

    # ========================================================
    # RESOLVE SIZE
    # ========================================================

    target_width, target_height = resolve_size(
        size
    )

    # ========================================================
    # RESOLVE RESIZE METHOD
    # ========================================================

    resampling = get_resize_method(
        resize_method
    )

    # ========================================================
    # RESOLVE BACKGROUND
    # ========================================================

    background_color = get_background(
        background
    )

    # ========================================================
    # VALIDASI MODE
    # ========================================================

    if not isinstance(mode, str):
        raise TypeError(
            "mode harus berupa string."
        )

    mode = mode.upper()

    if mode not in (
        "ALPHA",
        "FLATTEN"
    ):
        raise ValueError(
            f"Mode tidak dikenal: {mode}. "
            f"Gunakan 'ALPHA' atau 'FLATTEN'."
        )

    # ========================================================
    # COPY SOURCE
    # ========================================================

    working_image = image.copy()

    # ========================================================
    # NORMALIZE BACKGROUND
    # ========================================================

    background_color = normalize_background(
        background_color
    )

    # ========================================================
    # FLATTEN TRANSPARENCY
    # ========================================================

    if mode == "FLATTEN":

        if background_color is None:
            raise ValueError(
                "Mode FLATTEN membutuhkan "
                "background."
            )

        working_image = flatten_transparency(
            working_image,
            background_color
        )

    # ========================================================
    # CALCULATE FIT SIZE
    # ========================================================

    source_width, source_height = (
        working_image.size
    )

    new_width, new_height = (
        calculate_fit_size(
            source_width,
            source_height,
            target_width,
            target_height,
            allow_upscale=allow_upscale
        )
    )

    # ========================================================
    # RESIZE
    # ========================================================

    resized_image = resize_image(
        working_image,
        new_width,
        new_height,
        resampling
    )

    # ========================================================
    # CENTER IMAGE
    # ========================================================

    result = center_image(
        resized_image,
        target_width,
        target_height,
        background_color
    )

    # ========================================================
    # PASTIKAN RGBA
    # ========================================================

    if result.mode != "RGBA":
        result = result.convert(
            "RGBA"
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