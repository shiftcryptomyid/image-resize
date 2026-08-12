import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from item_processor import process_item


# ============================================================
# KONFIGURASI
# ============================================================

ITEM_SIZE = 24

BACKGROUND_COLOR = (
    255,
    0,
    255
)

# Preview hasil 24x24
COMPARISON_PREVIEW_SIZE = 24

# Preview original
ORIGINAL_PREVIEW_SIZE = 150

RESIZE_METHODS = (
    "NEAREST",
    "BOX",
    "BILINEAR",
    "BICUBIC",
    "LANCZOS",
)


# ============================================================
# MAP RESIZE METHOD
# ============================================================

def get_resize_method(
    method_name
):
    """
    Mengubah nama metode menjadi
    Image.Resampling milik Pillow.
    """

    methods = {
        "NEAREST": Image.Resampling.NEAREST,
        "BOX": Image.Resampling.BOX,
        "BILINEAR": Image.Resampling.BILINEAR,
        "BICUBIC": Image.Resampling.BICUBIC,
        "LANCZOS": Image.Resampling.LANCZOS,
    }

    if method_name not in methods:
        raise ValueError(
            f"Resize method tidak dikenal: "
            f"{method_name}"
        )

    return methods[
        method_name
    ]


# ============================================================
# CREATE PREVIEW
# ============================================================

def create_preview(
    image,
    size=COMPARISON_PREVIEW_SIZE
):
    """
    Membesarkan hasil 24x24 hanya untuk
    tampilan preview.

    Image hasil sebenarnya tetap 24x24.
    """

    return image.resize(
        (
            size,
            size
        ),
        Image.Resampling.NEAREST
    )


# ============================================================
# CREATE COMPARISON
# ============================================================

def create_comparison_images(
    source_image
):
    """
    Membuat 10 hasil:

        5 metode + flatten
        5 metode + alpha

    flatten:
        Transparency dikompositkan ke
        background sebelum resize.

    alpha:
        Transparency dipertahankan ketika
        resize.
    """

    results = []

    for method_name in RESIZE_METHODS:

        resize_method = (
            get_resize_method(
                method_name
            )
        )

        # ----------------------------------------------------
        # MODE A
        # FLATTEN BEFORE RESIZE
        # ----------------------------------------------------

        result_flatten = process_item(
            source_image,
            size=ITEM_SIZE,
            background=BACKGROUND_COLOR,
            resize_method=resize_method,
            allow_upscale=False,
            flatten_before_resize=True
        )

        results.append(
            (
                f"{method_name}\n"
                "FLATTEN",
                result_flatten
            )
        )

        # ----------------------------------------------------
        # MODE B
        # RESIZE ALPHA
        # ----------------------------------------------------

        result_alpha = process_item(
            source_image,
            size=ITEM_SIZE,
            background=BACKGROUND_COLOR,
            resize_method=resize_method,
            allow_upscale=False,
            flatten_before_resize=False
        )

        results.append(
            (
                f"{method_name}\n"
                "ALPHA",
                result_alpha
            )
        )

    return results


# ============================================================
# SINGLE ITEM WINDOW
# ============================================================

def open_single_item(
    parent,
    selected_source
):

    if selected_source is None:

        messagebox.showwarning(
            "Source belum dipilih",
            "Silakan pilih image terlebih dahulu.",
            parent=parent
        )

        return

    # --------------------------------------------------------
    # DATA SOURCE
    # --------------------------------------------------------

    image_type = selected_source[
        "type"
    ]

    image_index = selected_source[
        "index"
    ]

    source_image = selected_source[
        "image"
    ]

    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    window = tk.Toplevel(
        parent
    )

    window.title(
        "Item Processor - Comparison"
    )

    window.geometry(
        "1050x950"
    )

    window.minsize(
        900,
        750
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title_label = tk.Label(
        window,
        text="ITEM RESIZE COMPARISON",
        font=(
            "Arial",
            16,
            "bold"
        )
    )

    title_label.pack(
        pady=12
    )

    # --------------------------------------------------------
    # INFO SOURCE
    # --------------------------------------------------------

    info_label = tk.Label(
        window,
        text=(
            f"Source : {image_type} "
            f"#{image_index}\n"
            f"Original : "
            f"{source_image.width} × "
            f"{source_image.height}\n"
            f"Output : "
            f"{ITEM_SIZE} × {ITEM_SIZE}"
        ),
        justify="center"
    )

    info_label.pack(
        pady=5
    )

    # ========================================================
    # ORIGINAL
    # ========================================================

    original_frame = tk.Frame(
        window,
        relief="groove",
        bd=1
    )

    original_frame.pack(
        fill="x",
        padx=20,
        pady=8
    )

    original_title = tk.Label(
        original_frame,
        text="ORIGINAL",
        font=(
            "Arial",
            11,
            "bold"
        )
    )

    original_title.pack(
        pady=6
    )

    original_preview = (
        source_image.copy()
    )

    original_preview.thumbnail(
        (
            ORIGINAL_PREVIEW_SIZE,
            ORIGINAL_PREVIEW_SIZE
        ),
        Image.Resampling.NEAREST
    )

    original_photo = ImageTk.PhotoImage(
        original_preview
    )

    original_label = tk.Label(
        original_frame,
        image=original_photo
    )

    original_label.image = (
        original_photo
    )

    original_label.pack(
        pady=8
    )

    # ========================================================
    # COMPARISON CONTAINER
    # ========================================================

    comparison_container = tk.Frame(
        window
    )

    comparison_container.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    # --------------------------------------------------------
    # CANVAS
    # --------------------------------------------------------

    canvas = tk.Canvas(
        comparison_container
    )

    scrollbar = tk.Scrollbar(
        comparison_container,
        orient="vertical",
        command=canvas.yview
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    # --------------------------------------------------------
    # SCROLLABLE FRAME
    # --------------------------------------------------------

    comparison_frame = tk.Frame(
        canvas
    )

    canvas_window = canvas.create_window(
        (
            0,
            0
        ),
        window=comparison_frame,
        anchor="nw"
    )

    def update_scroll_region(
        event=None
    ):

        canvas.configure(
            scrollregion=canvas.bbox(
                "all"
            )
        )

    comparison_frame.bind(
        "<Configure>",
        update_scroll_region
    )

    def resize_canvas_frame(
        event
    ):

        canvas.itemconfigure(
            canvas_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_canvas_frame
    )

    # ========================================================
    # PROCESS
    # ========================================================

    try:

        results = (
            create_comparison_images(
                source_image
            )
        )

    except Exception as error:

        window.destroy()

        messagebox.showerror(
            "Process Error",
            str(error),
            parent=parent
        )

        return

    # --------------------------------------------------------
    # PHOTO REFERENCE
    # --------------------------------------------------------

    comparison_photos = []

    # ========================================================
    # GRID
    # ========================================================

    for index, (
        method_label,
        result_image
    ) in enumerate(results):

        row = index // 5
        column = index % 5

        card = tk.Frame(
            comparison_frame,
            relief="groove",
            bd=1
        )

        card.grid(
            row=row,
            column=column,
            padx=8,
            pady=8,
            sticky="nsew"
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            card,
            text=method_label,
            font=(
                "Arial",
                10,
                "bold"
            ),
            justify="center"
        )

        title.pack(
            pady=6
        )

        # ----------------------------------------------------
        # PREVIEW
        # ----------------------------------------------------

        preview_image = (
            create_preview(
                result_image
            )
        )

        photo = ImageTk.PhotoImage(
            preview_image
        )

        comparison_photos.append(
            photo
        )

        image_label = tk.Label(
            card,
            image=photo
        )

        image_label.pack(
            padx=8,
            pady=5
        )

        # ----------------------------------------------------
        # SIZE INFO
        # ----------------------------------------------------

        size_label = tk.Label(
            card,
            text=(
                f"{result_image.width}"
                f" × "
                f"{result_image.height}"
            )
        )

        size_label.pack(
            pady=(0, 8)
        )

    # --------------------------------------------------------
    # KEEP PHOTO REFERENCES
    # --------------------------------------------------------

    comparison_frame.photos = (
        comparison_photos
    )

    # --------------------------------------------------------
    # RESPONSIVE GRID
    # --------------------------------------------------------

    for column in range(5):

        comparison_frame.columnconfigure(
            column,
            weight=1
        )

    # ========================================================
    # CLOSE
    # ========================================================

    close_button = tk.Button(
        window,
        text="Close",
        width=15,
        command=window.destroy
    )

    close_button.pack(
        pady=12
    )