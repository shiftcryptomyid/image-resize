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
# DEBUG ALPHA DISTRIBUTION
# ============================================================

def debug_alpha_distribution(image):

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    alpha = image.getchannel(
        "A"
    )

    buckets = {
        "0": 0,
        "1-64": 0,
        "65-128": 0,
        "129-160": 0,
        "161-192": 0,
        "193-224": 0,
        "225-254": 0,
        "255": 0,
    }

    for value in alpha.getdata():

        if value == 0:
            buckets["0"] += 1

        elif value <= 64:
            buckets["1-64"] += 1

        elif value <= 128:
            buckets["65-128"] += 1

        elif value <= 160:
            buckets["129-160"] += 1

        elif value <= 192:
            buckets["161-192"] += 1

        elif value <= 224:
            buckets["193-224"] += 1

        elif value <= 254:
            buckets["225-254"] += 1

        else:
            buckets["255"] += 1

    print()
    print(
        "========== ALPHA DISTRIBUTION =========="
    )

    for name, count in buckets.items():

        print(
            f"Alpha {name:>7}: {count}"
        )

    print(
        "========================================"
    )
    print()


# ============================================================
# DEBUG ALPHA NEIGHBORS
# ============================================================

def debug_alpha_neighbors(
    image,
    alpha_threshold=160
):
    """
    Menganalisis pixel visible yang berdekatan
    dengan pixel transparan.

    Tidak mengubah image.
    Hanya diagnostic untuk edge / halo BMP.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    alpha = image.getchannel(
        "A"
    )

    width, height = image.size

    pixels = alpha.load()

    buckets = {
        "161-192": 0,
        "193-224": 0,
        "225-254": 0,
    }

    total_candidates = 0

    # --------------------------------------------------------
    # PERIKSA SETIAP PIXEL VISIBLE
    # --------------------------------------------------------

    for y in range(height):

        for x in range(width):

            value = pixels[x, y]

            if value <= alpha_threshold:

                continue

            # ------------------------------------------------
            # CEK 4 TETANGGA
            # ------------------------------------------------

            neighbors = []

            if x > 0:
                neighbors.append(
                    pixels[x - 1, y]
                )

            if x < width - 1:
                neighbors.append(
                    pixels[x + 1, y]
                )

            if y > 0:
                neighbors.append(
                    pixels[x, y - 1]
                )

            if y < height - 1:
                neighbors.append(
                    pixels[x, y + 1]
                )

            # ------------------------------------------------
            # ADA TETANGGA TRANSPARAN?
            # ------------------------------------------------

            if 0 in neighbors:

                total_candidates += 1

                if value <= 192:

                    buckets["161-192"] += 1

                elif value <= 224:

                    buckets["193-224"] += 1

                else:

                    buckets["225-254"] += 1

    print()
    print(
        "========== ALPHA EDGE DIAGNOSTIC =========="
    )

    print(
        f"Visible > {alpha_threshold} "
        f"near alpha 0 : "
        f"{total_candidates}"
    )

    for name, count in buckets.items():

        print(
            f"Edge alpha {name:>7}: "
            f"{count}"
        )

    print(
        "============================================"
    )
    print()


# ============================================================
# DEBUG ALPHA LOW NEIGHBORS
# ============================================================

def debug_alpha_low_neighbors(
    image,
    alpha_threshold=160
):
    """
    Menganalisis pixel visible yang berdekatan
    dengan pixel alpha rendah.

    Tidak mengubah image.
    Hanya diagnostic untuk edge / halo BMP.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    alpha = image.getchannel(
        "A"
    )

    width, height = image.size

    pixels = alpha.load()

    visible_buckets = {
        "161-192": 0,
        "193-224": 0,
        "225-254": 0,
    }

    near_64 = 0
    near_128 = 0

    # --------------------------------------------------------
    # PERIKSA PIXEL VISIBLE
    # --------------------------------------------------------

    for y in range(height):

        for x in range(width):

            value = pixels[x, y]

            if value <= alpha_threshold:

                continue

            # ------------------------------------------------
            # 4 TETANGGA
            # ------------------------------------------------

            neighbors = []

            if x > 0:

                neighbors.append(
                    pixels[x - 1, y]
                )

            if x < width - 1:

                neighbors.append(
                    pixels[x + 1, y]
                )

            if y > 0:

                neighbors.append(
                    pixels[x, y - 1]
                )

            if y < height - 1:

                neighbors.append(
                    pixels[x, y + 1]
                )

            # ------------------------------------------------
            # CEK TETANGGA <= 64
            # ------------------------------------------------

            has_low_64 = any(
                neighbor <= 64
                for neighbor in neighbors
            )

            # ------------------------------------------------
            # CEK TETANGGA <= 128
            # ------------------------------------------------

            has_low_128 = any(
                neighbor <= 128
                for neighbor in neighbors
            )

            if has_low_64:

                near_64 += 1

            if has_low_128:

                near_128 += 1

            # ------------------------------------------------
            # BUCKET ALPHA PIXEL VISIBLE
            # ------------------------------------------------

            if value <= 192:

                visible_buckets[
                    "161-192"
                ] += 1

            elif value <= 224:

                visible_buckets[
                    "193-224"
                ] += 1

            else:

                visible_buckets[
                    "225-254"
                ] += 1

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print()
    print(
        "========== ALPHA LOW-NEIGHBOR DIAGNOSTIC =========="
    )

    print(
        f"Visible > {alpha_threshold} "
        f"near alpha <= 64  : {near_64}"
    )

    print(
        f"Visible > {alpha_threshold} "
        f"near alpha <= 128 : {near_128}"
    )

    print()

    print(
        "Visible alpha distribution:"
    )

    for name, count in visible_buckets.items():

        print(
            f"Alpha {name:>7}: {count}"
        )

    print(
        "===================================================="
    )
    print()


# ============================================================
# DEBUG ALPHA 3x3 NEIGHBORS
# ============================================================

def debug_alpha_3x3_neighbors(
    image,
    low_threshold=64,
    visible_threshold=160
):
    """
    Menganalisis hubungan pixel alpha rendah
    dengan pixel visible dalam radius 1 pixel.

    Tidak mengubah image.
    Hanya diagnostic edge / halo BMP.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    alpha = image.getchannel(
        "A"
    )

    width, height = image.size

    pixels = alpha.load()

    visible_buckets = {
        "161-192": 0,
        "193-224": 0,
        "225-254": 0,
    }

    low_pixel_count = 0

    near_visible_count = 0

    # --------------------------------------------------------
    # PERIKSA PIXEL ALPHA RENDAH
    # --------------------------------------------------------

    for y in range(height):

        for x in range(width):

            value = pixels[x, y]

            if value > low_threshold:

                continue

            low_pixel_count += 1

            max_visible_alpha = 0

            # ------------------------------------------------
            # AREA 3x3
            # ------------------------------------------------

            for dy in range(-1, 2):

                for dx in range(-1, 2):

                    if (
                        dx == 0
                        and
                        dy == 0
                    ):
                        continue

                    nx = x + dx
                    ny = y + dy

                    if (
                        nx < 0
                        or
                        nx >= width
                        or
                        ny < 0
                        or
                        ny >= height
                    ):
                        continue

                    neighbor_alpha = (
                        pixels[nx, ny]
                    )

                    if (
                        neighbor_alpha
                        >
                        max_visible_alpha
                    ):

                        max_visible_alpha = (
                            neighbor_alpha
                        )

            # ------------------------------------------------
            # ADA VISIBLE DI 3x3?
            # ------------------------------------------------

            if (
                max_visible_alpha
                >
                visible_threshold
            ):

                near_visible_count += 1

                if max_visible_alpha <= 192:

                    visible_buckets[
                        "161-192"
                    ] += 1

                elif max_visible_alpha <= 224:

                    visible_buckets[
                        "193-224"
                    ] += 1

                else:

                    visible_buckets[
                        "225-254"
                    ] += 1

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print()
    print(
        "========== ALPHA 3x3 DIAGNOSTIC =========="
    )

    print(
        f"Alpha <= {low_threshold} pixels : "
        f"{low_pixel_count}"
    )

    print(
        f"Low-alpha pixels near "
        f"visible > {visible_threshold} : "
        f"{near_visible_count}"
    )

    print()

    print(
        "Maximum visible alpha "
        "found around low-alpha pixels:"
    )

    for name, count in visible_buckets.items():

        print(
            f"Alpha {name:>7}: {count}"
        )

    print(
        "==========================================="
    )
    print()


# ============================================================
# DEBUG ALPHA 5x5 NEIGHBOR DIAGNOSTIC
# ============================================================

def debug_alpha_5x5_neighbors(
    image
):
    """
    Mencari pixel alpha rendah yang berada
    dekat dengan pixel visible.

    Radius 5x5.

    Tidak mengubah image.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    alpha = image.getchannel(
        "A"
    )

    width, height = image.size

    pixels = alpha.load()

    low_alpha_count = 0
    low_near_visible = 0

    visible_161_192 = 0
    visible_193_224 = 0
    visible_225_254 = 0

    for y in range(height):

        for x in range(width):

            current_alpha = pixels[x, y]

            # ------------------------------------------------
            # HANYA PIXEL ALPHA RENDAH
            # ------------------------------------------------

            if current_alpha > 64:
                continue

            low_alpha_count += 1

            max_visible_alpha = 0

            # ------------------------------------------------
            # CARI NEIGHBOR DALAM RADIUS 5x5
            # ------------------------------------------------

            for dy in range(-2, 3):

                for dx in range(-2, 3):

                    if (
                        dx == 0
                        and
                        dy == 0
                    ):
                        continue

                    nx = x + dx
                    ny = y + dy

                    if (
                        nx < 0
                        or
                        nx >= width
                        or
                        ny < 0
                        or
                        ny >= height
                    ):
                        continue

                    neighbor_alpha = (
                        pixels[nx, ny]
                    )

                    if (
                        neighbor_alpha > 160
                        and
                        neighbor_alpha >
                        max_visible_alpha
                    ):

                        max_visible_alpha = (
                            neighbor_alpha
                        )

            # ------------------------------------------------
            # ADA VISIBLE NEARBY
            # ------------------------------------------------

            if max_visible_alpha > 160:

                low_near_visible += 1

                if (
                    max_visible_alpha
                    <= 192
                ):

                    visible_161_192 += 1

                elif (
                    max_visible_alpha
                    <= 224
                ):

                    visible_193_224 += 1

                else:

                    visible_225_254 += 1

    print()

    print(
        "========== ALPHA 5x5 DIAGNOSTIC =========="
    )

    print(
        f"Alpha <= 64 pixels : "
        f"{low_alpha_count}"
    )

    print(
        f"Low-alpha pixels near "
        f"visible > 160 : "
        f"{low_near_visible}"
    )

    print()

    print(
        "Maximum visible alpha found "
        "around low-alpha pixels:"
    )

    print(
        f"Alpha 161-192: "
        f"{visible_161_192}"
    )

    print(
        f"Alpha 193-224: "
        f"{visible_193_224}"
    )

    print(
        f"Alpha 225-254: "
        f"{visible_225_254}"
    )

    print(
        "==========================================="
    )

    print()


# ============================================================
# DEBUG BMP EDGE MASK
# ============================================================

def debug_bmp_edge_mask(
    image,
    alpha_threshold=160,
    radius=2
):
    """
    Diagnostic edge-mask untuk BMP color-key.

    Tidak mengubah image.
    Tidak mengubah RGB.
    Hanya menghitung pixel visible
    yang berada dekat transparency.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    alpha = image.getchannel(
        "A"
    )

    width, height = image.size

    pixels = alpha.load()

    transparent_count = 0
    visible_count = 0
    edge_count = 0

    edge_161_192 = 0
    edge_193_224 = 0
    edge_225_254 = 0

    for y in range(height):

        for x in range(width):

            current_alpha = pixels[x, y]

            # ------------------------------------------------
            # TRANSPARENT / PINK CANDIDATE
            # ------------------------------------------------

            if current_alpha <= alpha_threshold:

                transparent_count += 1

                continue

            # ------------------------------------------------
            # VISIBLE PIXEL
            # ------------------------------------------------

            visible_count += 1

            is_edge = False

            # ------------------------------------------------
            # CARI TRANSPARENCY DI SEKITAR PIXEL
            # ------------------------------------------------

            for dy in range(
                -radius,
                radius + 1
            ):

                for dx in range(
                    -radius,
                    radius + 1
                ):

                    if (
                        dx == 0
                        and
                        dy == 0
                    ):
                        continue

                    nx = x + dx
                    ny = y + dy

                    if (
                        nx < 0
                        or
                        nx >= width
                        or
                        ny < 0
                        or
                        ny >= height
                    ):
                        continue

                    neighbor_alpha = (
                        pixels[nx, ny]
                    )

                    if (
                        neighbor_alpha
                        <= alpha_threshold
                    ):

                        is_edge = True

                        break

                if is_edge:
                    break

            # ------------------------------------------------
            # EDGE PIXEL
            # ------------------------------------------------

            if is_edge:

                edge_count += 1

                if current_alpha <= 192:

                    edge_161_192 += 1

                elif current_alpha <= 224:

                    edge_193_224 += 1

                else:

                    edge_225_254 += 1

    print()

    print(
        "========== BMP EDGE MASK DIAGNOSTIC =========="
    )

    print(
        f"Alpha <= {alpha_threshold} : "
        f"{transparent_count}"
    )

    print(
        f"Visible > {alpha_threshold} : "
        f"{visible_count}"
    )

    print(
        f"Visible edge pixels : "
        f"{edge_count}"
    )

    print()

    print(
        "EDGE VISIBLE ALPHA:"
    )

    print(
        f"161-192 : "
        f"{edge_161_192}"
    )

    print(
        f"193-224 : "
        f"{edge_193_224}"
    )

    print(
        f"225-254 : "
        f"{edge_225_254}"
    )

    print(
        "=============================================="
    )

    print()


# ============================================================
# DEBUG BMP EDGE RGB
# ============================================================

def debug_bmp_edge_rgb(
    image,
    alpha_threshold=160,
    radius=2
):
    """
    Audit RGB pada pixel visible edge
    yang memiliki alpha semi-transparent.

    TIDAK mengubah image.

    Tujuan:
        Melihat RGB asli pada pixel edge
        sebelum dikonversi menjadi BMP color-key.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    width, height = image.size

    pixels = image.load()

    print()
    print(
        "========== BMP EDGE RGB AUDIT =========="
    )

    total_edge = 0

    alpha_161_192 = 0
    alpha_193_224 = 0
    alpha_225_254 = 0

    samples_161_192 = []
    samples_193_224 = []
    samples_225_254 = []

    for y in range(height):

        for x in range(width):

            r, g, b, a = (
                pixels[x, y]
            )

            # ------------------------------------------------
            # HANYA SEMI-TRANSPARENT VISIBLE
            # ------------------------------------------------

            if (
                a <= alpha_threshold
                or
                a >= 255
            ):
                continue

            # ------------------------------------------------
            # CEK APAKAH DEKAT TRANSPARENCY
            # ------------------------------------------------

            is_edge = False

            for dy in range(
                -radius,
                radius + 1
            ):

                for dx in range(
                    -radius,
                    radius + 1
                ):

                    if (
                        dx == 0
                        and
                        dy == 0
                    ):
                        continue

                    nx = x + dx
                    ny = y + dy

                    if (
                        nx < 0
                        or
                        nx >= width
                        or
                        ny < 0
                        or
                        ny >= height
                    ):
                        continue

                    neighbor_alpha = (
                        pixels[nx, ny][3]
                    )

                    if (
                        neighbor_alpha
                        <= alpha_threshold
                    ):

                        is_edge = True

                        break

                if is_edge:
                    break

            if not is_edge:
                continue

            total_edge += 1

            # ------------------------------------------------
            # SIMPAN SAMPLE
            # ------------------------------------------------

            sample = (
                x,
                y,
                r,
                g,
                b,
                a
            )

            if a <= 192:

                alpha_161_192 += 1

                if len(
                    samples_161_192
                ) < 20:

                    samples_161_192.append(
                        sample
                    )

            elif a <= 224:

                alpha_193_224 += 1

                if len(
                    samples_193_224
                ) < 20:

                    samples_193_224.append(
                        sample
                    )

            else:

                alpha_225_254 += 1

                if len(
                    samples_225_254
                ) < 20:

                    samples_225_254.append(
                        sample
                    )

    print(
        f"Total semi-transparent edge : "
        f"{total_edge}"
    )

    print()

    print(
        f"Alpha 161-192 : "
        f"{alpha_161_192}"
    )

    print(
        f"Alpha 193-224 : "
        f"{alpha_193_224}"
    )

    print(
        f"Alpha 225-254 : "
        f"{alpha_225_254}"
    )

    print()

    # --------------------------------------------------------
    # SAMPLE RGB
    # --------------------------------------------------------

    print(
        "SAMPLES ALPHA 161-192:"
    )

    for sample in samples_161_192:

        print(
            "  "
            f"x={sample[0]:3d} "
            f"y={sample[1]:3d} "
            f"RGB=({sample[2]:3d},"
            f"{sample[3]:3d},"
            f"{sample[4]:3d}) "
            f"A={sample[5]:3d}"
        )

    print()

    print(
        "SAMPLES ALPHA 193-224:"
    )

    for sample in samples_193_224:

        print(
            "  "
            f"x={sample[0]:3d} "
            f"y={sample[1]:3d} "
            f"RGB=({sample[2]:3d},"
            f"{sample[3]:3d},"
            f"{sample[4]:3d}) "
            f"A={sample[5]:3d}"
        )

    print()

    print(
        "SAMPLES ALPHA 225-254:"
    )

    for sample in samples_225_254:

        print(
            "  "
            f"x={sample[0]:3d} "
            f"y={sample[1]:3d} "
            f"RGB=({sample[2]:3d},"
            f"{sample[3]:3d},"
            f"{sample[4]:3d}) "
            f"A={sample[5]:3d}"
        )

    print(
        "========================================"
    )

    print()
    


# ============================================================
# DEBUG BMP THRESHOLD SIMULATION
# ============================================================

def debug_bmp_threshold_simulation(
    image
):
    """
    Mensimulasikan BMP color-key untuk beberapa threshold.

    Tidak mengubah image.
    Tidak menyimpan file.
    Hanya menghitung jumlah pixel PINK
    dan VISIBLE.
    """

    if image is None:

        raise ValueError(
            "Image tidak tersedia."
        )

    image = image.convert(
        "RGBA"
    )

    alpha = image.getchannel(
        "A"
    )

    thresholds = (
        100,
        120,
        140,
        160,
        180,
        200,
        220
    )

    total_pixels = (
        image.width *
        image.height
    )

    alpha_values = list(
        alpha.getdata()
    )

    print()
    print(
        "========== BMP THRESHOLD SIMULATION =========="
    )

    print(
        f"Total pixels : {total_pixels}"
    )

    print()

    print(
        "Threshold | PINK | VISIBLE"
    )

    print(
        "----------+------+--------"
    )

    for threshold in thresholds:

        pink_count = 0

        visible_count = 0

        for value in alpha_values:

            if value <= threshold:

                pink_count += 1

            else:

                visible_count += 1

        print(
            f"{threshold:9} | "
            f"{pink_count:4} | "
            f"{visible_count:7}"
        )

    print(
        "=============================================="
    )
    print()



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
    # DEBUG ALPHA
    # ========================================================

    if mode == "ALPHA":

        debug_alpha_distribution(
            result
        )
        
        debug_alpha_neighbors(
            result
        )
        
        debug_alpha_low_neighbors(
            result
        )
        
        debug_alpha_3x3_neighbors(
            result
        )
        
        debug_alpha_5x5_neighbors(
            result
        )
        
        debug_bmp_edge_mask(
            result
        )
        
        debug_bmp_edge_rgb(
            result
        )
        
        debug_bmp_threshold_simulation(
            result
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