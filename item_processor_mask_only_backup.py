from pathlib import Path

from PIL import Image

from card_processor import (
    create_collection_card
)


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

    # Khusus Collection 100x100
    "CARD": "CARD",
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

    Untuk RGBA:
        Menggunakan premultiplied alpha
        agar mengurangi halo / warna kotor
        pada tepi transparency.
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

    # ========================================================
    # TIDAK PERLU RESIZE
    # ========================================================

    if (
        new_width == image.width
        and
        new_height == image.height
    ):

        return image.copy()

    # ========================================================
    # ALPHA-SAFE RESIZE
    # ========================================================

    if image.mode == "RGBA":

        premultiplied = image.convert(
            "RGBa"
        )

        resized = premultiplied.resize(
            (
                new_width,
                new_height
            ),
            resize_method
        )

        resized = resized.convert(
            "RGBA"
        )

        return resized
        
        
    # ========================================================
    # NORMAL RESIZE
    # ========================================================

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
# CLEAN ALPHA RESIZE
# ============================================================

def resize_rgba_clean(
    image,
    size,
    resample=Image.Resampling.LANCZOS
):
    """
    Resize RGBA dengan premultiplied alpha.

    Tujuan:
        Mengurangi halo / pixel kotor
        pada area transparency setelah resize.

    RGB pada pixel transparan tidak ikut
    mencemari pixel tepi saat interpolasi.
    """

    image = image.convert(
        "RGBA"
    )

    width, height = image.size

    if width <= 0 or height <= 0:

        raise ValueError(
            "Ukuran image tidak valid."
        )

    # --------------------------------------------------------
    # SPLIT CHANNEL
    # --------------------------------------------------------

    r, g, b, a = image.split()

    # --------------------------------------------------------
    # PREMULTIPLY RGB DENGAN ALPHA
    # --------------------------------------------------------

    alpha = a.load()

    r = r.load()
    g = g.load()
    b = b.load()

    premult_r = Image.new(
        "L",
        image.size
    )

    premult_g = Image.new(
        "L",
        image.size
    )

    premult_b = Image.new(
        "L",
        image.size
    )

    pr = premult_r.load()
    pg = premult_g.load()
    pb = premult_b.load()

    for y in range(height):

        for x in range(width):

            alpha_value = alpha[x, y]

            pr[x, y] = (
                r[x, y] *
                alpha_value //
                255
            )

            pg[x, y] = (
                g[x, y] *
                alpha_value //
                255
            )

            pb[x, y] = (
                b[x, y] *
                alpha_value //
                255
            )

    # --------------------------------------------------------
    # RESIZE
    # --------------------------------------------------------

    premult_r = premult_r.resize(
        size,
        resample
    )

    premult_g = premult_g.resize(
        size,
        resample
    )

    premult_b = premult_b.resize(
        size,
        resample
    )

    alpha_resized = a.resize(
        size,
        resample
    )

    # --------------------------------------------------------
    # UNPREMULTIPLY
    # --------------------------------------------------------

    pr = premult_r.load()
    pg = premult_g.load()
    pb = premult_b.load()

    alpha = alpha_resized.load()

    final_r = Image.new(
        "L",
        size
    )

    final_g = Image.new(
        "L",
        size
    )

    final_b = Image.new(
        "L",
        size
    )

    fr = final_r.load()
    fg = final_g.load()
    fb = final_b.load()

    new_width, new_height = size

    for y in range(new_height):

        for x in range(new_width):

            alpha_value = alpha[x, y]

            if alpha_value == 0:

                fr[x, y] = 0
                fg[x, y] = 0
                fb[x, y] = 0

            else:

                fr[x, y] = min(
                    255,
                    (
                        pr[x, y] *
                        255 +
                        alpha_value // 2
                    ) //
                    alpha_value
                )

                fg[x, y] = min(
                    255,
                    (
                        pg[x, y] *
                        255 +
                        alpha_value // 2
                    ) //
                    alpha_value
                )

                fb[x, y] = min(
                    255,
                    (
                        pb[x, y] *
                        255 +
                        alpha_value // 2
                    ) //
                    alpha_value
                )

    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    return Image.merge(
        "RGBA",
        (
            final_r,
            final_g,
            final_b,
            alpha_resized
        )
    )


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
    # CARD MODE
    # ========================================================

    if (
        isinstance(background, str)
        and background.upper() == "CARD"
    ):

        target_width, target_height = (
            resolve_size(size)
        )

        # ----------------------------------------------------
        # CARD hanya untuk 100x100
        # ----------------------------------------------------

        if (
            target_width != 100
            or target_height != 100
        ):
            raise ValueError(
                "Background CARD hanya tersedia "
                "untuk ukuran 100x100."
            )

        # ----------------------------------------------------
        # Resize image terlebih dahulu.
        #
        # Maksimal 60x60 sesuai desain collection card.
        # ----------------------------------------------------

        working_image = image.convert(
            "RGBA"
        )

        source_width = (
            working_image.width
        )

        source_height = (
            working_image.height
        )

        new_width, new_height = (
            calculate_fit_size(
                source_width,
                source_height,
                60,
                60,
                allow_upscale=allow_upscale
            )
        )

        resized_image = resize_rgba_clean(
            working_image,
            (
                new_width,
                new_height
            ),
            get_resize_method(
                resize_method
            )
        )
        

        # ----------------------------------------------------
        # Buat CARD
        # ----------------------------------------------------

        return create_collection_card(
            resized_image,
            output_size=(
                target_width,
                target_height
            ),
            max_image_size=(
                60,
                60
            )
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

    if working_image.mode == "RGBA":

        resized_image = resize_rgba_clean(
            working_image,
            (
                new_width,
                new_height
            ),
            resampling
        )

    else:

        resized_image = resize_image(
            working_image,
            new_width,
            new_height,
            resampling
        )

    # ========================================================
    # CENTER IMAGE
    # ========================================================

    if mode == "ALPHA":

        result = center_image(
            resized_image,
            target_width,
            target_height,
            None
        )

    else:

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
# TEST MANUAL
# ============================================================

if __name__ == "__main__":

    print(
        "item_processor.py"
    )

    print(
        "Engine image processor siap."
    )