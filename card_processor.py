"""
card_processor.py

Engine untuk membuat Collection Card 100x100.

Fungsi utama:
    create_collection_card()

Desain:
    - Canvas 100x100
    - Background putih
    - Rounded corner
    - Border abu-abu
    - Shadow tipis
    - Image maksimal 60x60
    - Image tetap proporsional
    - Image ditempatkan di tengah
    - Output RGBA internal
"""

from PIL import Image, ImageDraw


# ============================================================
# CARD CONFIGURATION
# ============================================================

CARD_SIZE = (
    100,
    100
)

CARD_IMAGE_MAX_SIZE = (
    60,
    60
)

CARD_BACKGROUND = (
    255,
    255,
    255,
    255
)

CARD_BORDER_COLOR = (
    210,
    210,
    210,
    255
)

CARD_BORDER_WIDTH = 2

CARD_RADIUS = 10

CARD_SHADOW_COLOR = (
    190,
    190,
    190,
    100
)

CARD_SHADOW_OFFSET = 2


# ============================================================
# CREATE COLLECTION CARD
# ============================================================

# ============================================================
# CREATE COLLECTION CARD
# ============================================================

def create_collection_card(
    image,
    output_size=CARD_SIZE,
    max_image_size=CARD_IMAGE_MAX_SIZE
):
    """
    Membuat Collection Card.

    Resize image dilakukan oleh item_processor.py.
    Fungsi ini hanya bertanggung jawab untuk:

        - membuat canvas kartu
        - membuat shadow
        - membuat rounded corner
        - membuat border
        - menempatkan image di tengah

    Parameters
    ----------
    image : PIL.Image.Image
        Image yang sudah diproses oleh engine utama.

    output_size : tuple
        Ukuran canvas kartu.
        Default: 100x100.

    max_image_size : tuple
        Batas ukuran image.
        Digunakan sebagai validasi.
    """

    # ========================================================
    # VALIDATE IMAGE
    # ========================================================

    if image is None:

        raise ValueError(
            "Image source tidak boleh None."
        )

    if not isinstance(
        image,
        Image.Image
    ):

        raise TypeError(
            "image harus berupa PIL.Image.Image."
        )

    width, height = output_size

    max_width, max_height = (
        max_image_size
    )

    # ========================================================
    # VALIDATE IMAGE SIZE
    # ========================================================

    if (
        image.width > max_width
        or image.height > max_height
    ):

        raise ValueError(
            "Image untuk Collection Card "
            f"tidak boleh lebih besar dari "
            f"{max_width}x{max_height}."
        )

    # ========================================================
    # CARD CANVAS
    # ========================================================

    card = Image.new(
        "RGBA",
        (
            width,
            height
        ),
        (
            0,
            0,
            0,
            0
        )
    )

    draw = ImageDraw.Draw(
        card
    )

    # ========================================================
    # CARD RADIUS
    # ========================================================

    radius = min(
        CARD_RADIUS,
        width // 2,
        height // 2
    )

    # ========================================================
    # SHADOW
    # ========================================================

    shadow_offset = min(
        CARD_SHADOW_OFFSET,
        max(
            1,
            min(width, height) // 20
        )
    )

    draw.rounded_rectangle(
        (
            shadow_offset,
            shadow_offset,
            width - 1,
            height - 1
        ),
        radius=radius,
        fill=CARD_SHADOW_COLOR
    )

    # ========================================================
    # CARD BODY
    # ========================================================

    body_right = (
        width
        - 1
        - shadow_offset
    )

    body_bottom = (
        height
        - 1
        - shadow_offset
    )

    draw.rounded_rectangle(
        (
            0,
            0,
            body_right,
            body_bottom
        ),
        radius=radius,
        fill=CARD_BACKGROUND,
        outline=CARD_BORDER_COLOR,
        width=CARD_BORDER_WIDTH
    )

    # ========================================================
    # PREPARE IMAGE
    # ========================================================

    source = image.convert(
        "RGBA"
    )

    # ========================================================
    # CENTER IMAGE
    # ========================================================

    x = (
        width
        - source.width
    ) // 2

    y = (
        height
        - source.height
    ) // 2

    # ========================================================
    # COMPOSITE IMAGE
    # ========================================================

    card.alpha_composite(
        source,
        (
            x,
            y
        )
    )

    return card


# ============================================================
# TEST
# ============================================================

# ============================================================
# TEST VISUAL
# ============================================================

if __name__ == "__main__":

    from pathlib import Path

    test_folder = Path(
        "data"
    )

    test_images = list(
        test_folder.rglob("*.png")
    )

    if not test_images:

        print(
            "Tidak ditemukan image PNG untuk test."
        )

    else:

        source_path = (
            test_images[0]
        )

        print(
            f"Test image : {source_path}"
        )

        source_image = Image.open(
            source_path
        )

        test_image = source_image.convert(
            "RGBA"
        )

        test_image.thumbnail(
            (
                60,
                60
            ),
            Image.Resampling.LANCZOS
        )

        result = create_collection_card(
            test_image
        )

        output_path = Path(
            "test_card.png"
        )

        result.save(
            output_path
        )

        print(
            f"Card berhasil dibuat : "
            f"{output_path}"
        )