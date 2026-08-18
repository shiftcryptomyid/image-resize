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
# BMP TRANSPARENCY MODES
# ============================================================

BMP_TRANSPARENCY_MODE_COLOR_KEY = "COLOR_KEY"
BMP_TRANSPARENCY_MODE_DITHER = "DITHER"

# ============================================================
# BAYER MATRIX 8x8
#
# Nilai berkisar dari 0 hingga 63.
# Digunakan untuk Ordered Dithering.
# ============================================================

BAYER_MATRIX_8x8 = [
    [ 0, 32,  8, 40,  2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44,  4, 36, 14, 46,  6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [ 3, 35, 11, 43,  1, 33,  9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47,  7, 39, 13, 45,  5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21],
]

# ============================================================
# RESOLVE OUTPUT FORMAT
# ============================================================

def resolve_output_format(output_format):
    """
    Mengubah nama format menjadi format standar.
    """
    if not isinstance(output_format, str):
        raise TypeError("Output format harus berupa string.")

    output_format = output_format.strip().upper()

    if output_format not in OUTPUT_FORMATS:
        raise ValueError(f"Format output tidak didukung: {output_format}")

    return output_format

# ============================================================
# BMP EDGE MASK (DIAGNOSTIC - TIDAK DIPAKAI DI PRODUKSI)
# ============================================================

def build_bmp_edge_mask(image, alpha_threshold=160):
    """
    Membuat mask untuk menentukan pixel visible
    yang berada di tepi transparency.
    """
    image = image.convert("RGBA")
    alpha = image.getchannel("A")
    width, height = image.size
    mask = Image.new("L", image.size, 0)
    source = alpha.load()
    result = mask.load()

    for y in range(height):
        for x in range(width):
            current_alpha = source[x, y]
            if current_alpha <= alpha_threshold:
                continue
            is_edge = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx = x + dx
                    ny = y + dy
                    if nx < 0 or nx >= width or ny < 0 or ny >= height:
                        continue
                    neighbor_alpha = source[nx, ny]
                    if neighbor_alpha <= alpha_threshold:
                        is_edge = True
                        break
                if is_edge:
                    break
            if is_edge:
                result[x, y] = 255
    return mask

# ============================================================
# BMP COLOR KEY (LEGACY - TIDAK DIPAKAI DI PRODUKSI)
# ============================================================

BMP_ALPHA_THRESHOLD = 100

def prepare_bmp_color_key(image, transparent_color, alpha_threshold=BMP_ALPHA_THRESHOLD):
    """
    Menyiapkan RGBA menjadi BMP color-key.
    """
    if image is None:
        raise ValueError("Image tidak tersedia.")

    image = image.convert("RGBA")
    transparent_rgb = (transparent_color[0], transparent_color[1], transparent_color[2])
    result = Image.new("RGB", image.size, transparent_rgb)
    source_pixels = image.load()
    result_pixels = result.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = source_pixels[x, y]
            if a <= alpha_threshold:
                result_pixels[x, y] = transparent_rgb
            else:
                result_pixels[x, y] = (r, g, b)
    return result

# ============================================================
# BMP ALPHA COLOR KEY - AURA RADIUS (BASELINE / COLOR_KEY)
# ============================================================

def prepare_bmp_alpha_dither(
    image,
    transparent_color,
    transparency_limit=32,
    edge_alpha_min=32,
    aura_radius=2
):
    """
    BASELINE MODE (COLOR_KEY).

    Mengubah RGBA menjadi BMP color-key dengan
    mempertahankan sebagian pixel aura berdasarkan
    jaraknya terhadap pixel solid.
    """
    if image is None:
        raise ValueError("Image tidak tersedia.")

    image = image.convert("RGBA")

    if transparency_limit < 0: transparency_limit = 0
    if transparency_limit > 255: transparency_limit = 255
    if edge_alpha_min < 0: edge_alpha_min = 0
    if edge_alpha_min > 255: edge_alpha_min = 255
    if edge_alpha_min > transparency_limit: edge_alpha_min = transparency_limit
    if aura_radius < 0: aura_radius = 0
    aura_radius = int(aura_radius)

    transparent_rgb = (
        transparent_color[0],
        transparent_color[1],
        transparent_color[2]
    )

    result = Image.new("RGB", image.size, transparent_rgb)
    source_pixels = image.load()
    result_pixels = result.load()
    width, height = image.size

    def has_solid_neighbor(x, y):
        if aura_radius <= 0:
            return False
        radius_squared = aura_radius * aura_radius
        for dy in range(-aura_radius, aura_radius + 1):
            for dx in range(-aura_radius, aura_radius + 1):
                distance_squared = dx * dx + dy * dy
                if distance_squared > radius_squared:
                    continue
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                neighbor_alpha = source_pixels[nx, ny][3]
                if neighbor_alpha > transparency_limit:
                    return True
        return False

    for y in range(height):
        for x in range(width):
            r, g, b, a = source_pixels[x, y]

            if a < edge_alpha_min:
                result_pixels[x, y] = transparent_rgb
                continue

            if a > transparency_limit:
                result_pixels[x, y] = (r, g, b)
                continue

            if has_solid_neighbor(x, y):
                result_pixels[x, y] = (r, g, b)
            else:
                result_pixels[x, y] = transparent_rgb

    return result

# ============================================================
# BMP ORDERED DITHER - 4 ZONA (EKSPERIMEN)
# ============================================================

def prepare_bmp_ordered_dither(
    image,
    transparent_color,
    transparency_limit=32,
    edge_alpha_min=128
):
    """
    EKSPERIMEN MODE (DITHER).

    Mengubah RGBA menjadi BMP color-key menggunakan
    Ordered Dithering (Bayer Matrix 8x8) dengan
    4 zona alpha:

        ZONA A  (alpha = 0)
            → 100% PINK (area benar-benar kosong)

        ZONA B  (0 < alpha < transparency_limit)
            → Dithering ringan
            → Threshold Bayer: 1–31
            → Aura tipis, fill 1–50%

        ZONA C  (transparency_limit <= alpha < 255)
            → Dithering padat
            → Threshold Bayer: 32–63
            → Aura tebal, fill 50–100%

        ZONA D  (alpha = 255)
            → 100% RGB asli (inti sprite, solid)

    RGB asli TIDAK PERNAH diubah.
    Hanya keputusan RGB atau PINK yang ditentukan
    oleh Bayer Matrix.

    Parameter:
        transparency_limit
            Pivot antara zona B dan zona C.
            Default 128 (konsisten dengan baseline).

        edge_alpha_min
            Saat ini disamakan dengan transparency_limit
            untuk konsistensi dengan setting Anda.
            Zona B dimulai dari alpha = 1.
    """
    if image is None:
        raise ValueError("Image tidak tersedia.")

    image = image.convert("RGBA")

    # --------------------------------------------------------
    # VALIDASI PARAMETER
    # --------------------------------------------------------
    if transparency_limit < 1:
        transparency_limit = 1
    if transparency_limit > 254:
        transparency_limit = 254
    if edge_alpha_min < 1:
        edge_alpha_min = 1
    if edge_alpha_min > transparency_limit:
        edge_alpha_min = transparency_limit

    transparent_rgb = (
        transparent_color[0],
        transparent_color[1],
        transparent_color[2]
    )

    result = Image.new("RGB", image.size, transparent_rgb)
    source_pixels = image.load()
    result_pixels = result.load()

    width, height = image.size

    # --------------------------------------------------------
    # BATAS ZONA
    # --------------------------------------------------------
    zone_b_max = transparency_limit - 1       # 127 (jika limit=128)
    zone_c_min = transparency_limit           # 128
    zone_c_max = 254

    # Rentang untuk pemetaan linear ke threshold Bayer
    zone_b_range = zone_b_max                 # 127
    zone_c_range = zone_c_max - zone_c_min + 1  # 127

    for y in range(height):
        for x in range(width):
            r, g, b, a = source_pixels[x, y]

            # --------------------------------------------
            # ZONA A: alpha = 0 → PINK murni
            # --------------------------------------------
            if a == 0:
                result_pixels[x, y] = transparent_rgb
                continue

            # --------------------------------------------
            # ZONA D: alpha = 255 → RGB murni (solid)
            # --------------------------------------------
            if a == 255:
                result_pixels[x, y] = (r, g, b)
                continue

            # --------------------------------------------
            # ZONA B: alpha rendah → dithering ringan
            # Threshold Bayer: 1–31
            # --------------------------------------------
            if a < transparency_limit:
                threshold = 1 + ((a - 1) * 30) // zone_b_range

            # --------------------------------------------
            # ZONA C: alpha menengah/tinggi → dithering padat
            # Threshold Bayer: 32–63
            # --------------------------------------------
            else:
                threshold = 32 + ((a - zone_c_min) * 31) // zone_c_range

            # --------------------------------------------
            # BAYER MATRIX 8x8
            # --------------------------------------------
            bayer_value = BAYER_MATRIX_8x8[y % 8][x % 8]

            if bayer_value < threshold:
                result_pixels[x, y] = (r, g, b)
            else:
                result_pixels[x, y] = transparent_rgb

    return result

# ============================================================
# PREPARE IMAGE FOR OUTPUT
# ============================================================

def prepare_image_for_output(
    image,
    output_format,
    background=(255, 255, 255),
    transparency_mode=BMP_TRANSPARENCY_MODE_COLOR_KEY,
    transparency_limit=32,
    edge_alpha_min=128,
    aura_radius=2
):
    """
    Menyiapkan PIL Image sebelum disimpan.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Image harus berupa PIL Image.")

    output_format = resolve_output_format(output_format)

    # --------------------------------------------------------
    # PNG
    # --------------------------------------------------------
    if output_format == "PNG":
        if image.mode in ("RGBA", "LA", "P"):
            return image.copy()
        return image.convert("RGB")

    # --------------------------------------------------------
    # BMP
    # --------------------------------------------------------
    if output_format == "BMP":
        if image.mode == "RGBA":
            # BMP + PINK (Color-key transparency khusus ACTOR)
            if (
                background[0] == 255 and
                background[1] == 0 and
                background[2] == 255
            ):
                if transparency_mode == BMP_TRANSPARENCY_MODE_DITHER:
                    return prepare_bmp_ordered_dither(
                        image,
                        background,
                        transparency_limit=transparency_limit,
                        edge_alpha_min=edge_alpha_min
                    )
                else:
                    return prepare_bmp_alpha_dither(
                        image,
                        background,
                        transparency_limit=transparency_limit,
                        edge_alpha_min=edge_alpha_min,
                        aura_radius=aura_radius
                    )

            # BMP background biasa
            background_image = Image.new(
                "RGBA", image.size,
                (background[0], background[1], background[2], 255)
            )
            composited_image = Image.alpha_composite(background_image, image)
            return composited_image.convert("RGB")

        if image.mode == "LA":
            rgba_image = image.convert("RGBA")
            background_image = Image.new(
                "RGBA", image.size,
                (background[0], background[1], background[2], 255)
            )
            composited_image = Image.alpha_composite(background_image, rgba_image)
            return composited_image.convert("RGB")

        if image.mode == "P":
            if "transparency" in image.info:
                rgba_image = image.convert("RGBA")
                background_image = Image.new(
                    "RGBA", image.size,
                    (background[0], background[1], background[2], 255)
                )
                composited_image = Image.alpha_composite(background_image, rgba_image)
                return composited_image.convert("RGB")
            return image.convert("RGB")

        if image.mode != "RGB":
            return image.convert("RGB")

        return image.copy()

    raise ValueError("Format output tidak didukung.")

# ============================================================
# PREPARE PREVIEW IMAGE
# ============================================================

def prepare_preview_image(
    image,
    output_format,
    background=None,
    transparency_mode=BMP_TRANSPARENCY_MODE_COLOR_KEY,
    transparency_limit=32,
    edge_alpha_min=128,
    aura_radius=2
):
    """
    Membuat image khusus untuk preview.
    """
    if image is None:
        raise ValueError("Image tidak tersedia.")

    output_format = output_format.upper()

    if output_format == "PNG":
        return image.convert("RGBA")

    prepared = prepare_image_for_output(
        image,
        "BMP",
        background,
        transparency_mode=transparency_mode,
        transparency_limit=transparency_limit,
        edge_alpha_min=edge_alpha_min,
        aura_radius=aura_radius
    )

    # BMP + PINK: Simulasikan transparency ACTOR untuk preview UI
    if (
        background is not None and
        background[0] == 255 and
        background[1] == 0 and
        background[2] == 255
    ):
        prepared = prepared.convert("RGB")
        result = Image.new("RGBA", prepared.size, (0, 0, 0, 0))
        source_pixels = prepared.load()
        result_pixels = result.load()
        width, height = prepared.size

        for y in range(height):
            for x in range(width):
                r, g, b = source_pixels[x, y]
                if r == 255 and g == 0 and b == 255:
                    result_pixels[x, y] = (0, 0, 0, 0)
                else:
                    result_pixels[x, y] = (r, g, b, 255)
        return result

    return prepared.convert("RGBA")

# ============================================================
# SAVE IMAGE
# ============================================================

def save_image(
    image,
    output_path,
    output_format=None,
    background=(255, 255, 255),
    transparency_mode=BMP_TRANSPARENCY_MODE_COLOR_KEY,
    transparency_limit=32,
    edge_alpha_min=128,
    aura_radius=2
):
    """
    Menyimpan PIL Image ke PNG atau BMP.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Image harus berupa PIL Image.")

    output_path = Path(output_path)

    if output_format is None:
        extension = output_path.suffix.lower()
        if extension == ".png":
            output_format = "PNG"
        elif extension == ".bmp":
            output_format = "BMP"
        else:
            raise ValueError("Format output tidak dapat ditentukan dari extension.")
    else:
        output_format = resolve_output_format(output_format)

    prepared_image = prepare_image_for_output(
        image,
        output_format,
        background,
        transparency_mode=transparency_mode,
        transparency_limit=transparency_limit,
        edge_alpha_min=edge_alpha_min,
        aura_radius=aura_radius
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared_image.save(output_path, format=output_format)

    return output_path

if __name__ == "__main__":
    print("Output processor siap dengan mode COLOR_KEY dan DITHER.")