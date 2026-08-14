import tkinter as tk
import output_processor
from tkinter import messagebox

from PIL import Image, ImageTk


from item_processor import (
    process_item,
    SIZE_PRESETS,
    RESIZE_METHODS,
    BACKGROUND_PRESETS,
    get_resize_method,
    resolve_size,
)


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


# ============================================================
# DEFAULT PROCESS SETTINGS
# ============================================================

DEFAULT_SIZE_PRESET = "24x24"

DEFAULT_RESIZE_METHOD = "LANCZOS"

DEFAULT_BACKGROUND = "PINK"


# ============================================================
# MAP RESIZE METHOD
# ============================================================

#fungsi itu sudah menjadi bagian dari engine.

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
# PROCESS SELECTED IMAGE
# ============================================================

# ============================================================
# PROCESS SELECTED IMAGE
# ============================================================

def process_selected_image(
    source_image,
    size,
    method,
    background
):
    """
    Memproses source image berdasarkan pilihan:

        SIZE
        RESIZE METHOD
        BACKGROUND
    """

    result = process_item(
        source_image,
        size=size,
        background=background,
        resize_method=method,
        allow_upscale=False,
        mode="ALPHA"
    )

    return result
    

# ============================================================
# CENTER WINDOW
# ============================================================

def center_window(
    window,
    parent
):
    """
    Menempatkan window di tengah terhadap parent window.
    """

    window.update_idletasks()

    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()

    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    window_width = window.winfo_width()
    window_height = window.winfo_height()

    x = (
        parent_x
        + (parent_width - window_width) // 2
    )

    y = (
        parent_y
        + (parent_height - window_height) // 2
    )

    window.geometry(
        f"+{x}+{y}"
    )
    

# ============================================================
# SHOW PROCESSED RESULT
# ============================================================

def show_processed_result(
    parent,
    result_image,
    size,
    method
):
    """
    Menampilkan hasil Process final.

    Ini bukan Comparison.
    Hanya menampilkan satu hasil berdasarkan
    pilihan SIZE dan RESIZE METHOD.
    """

    result_window = tk.Toplevel(
        parent
    )

    result_window.title(
        "Processed Result"
    )

    result_window.geometry(
        "400x450"
    )

    result_window.minsize(
        350,
        400
    )

    # ========================================================
    # TITLE
    # ========================================================

    title_label = tk.Label(
        result_window,
        text="PROCESSED RESULT",
        font=(
            "Arial",
            14,
            "bold"
        )
    )

    title_label.pack(
        pady=12
    )

    # ========================================================
    # INFO
    # ========================================================

    info_label = tk.Label(
        result_window,
        text=(
            f"Size : "
            f"{result_image.width} × "
            f"{result_image.height}\n"
            f"Method : {method}\n"
            f"Mode : ALPHA"
        ),
        justify="center"
    )

    info_label.pack(
        pady=5
    )

    # ========================================================
    # PREVIEW
    #
    # Hanya untuk tampilan.
    # Image sebenarnya tetap menggunakan ukuran
    # hasil process.
    # ========================================================

    preview_size = 240

    preview_image = result_image.copy()

    preview_image = preview_image.resize(
        (
            preview_size,
            preview_size
        ),
        Image.Resampling.NEAREST
    )

    photo = ImageTk.PhotoImage(
        preview_image
    )

    image_label = tk.Label(
        result_window,
        image=photo,
        relief="groove",
        bd=1
    )

    image_label.image = photo

    image_label.pack(
        pady=15
    )

    # ========================================================
    # CLOSE
    # ========================================================

    close_button = tk.Button(
        result_window,
        text="Close",
        width=15,
        command=result_window.destroy
    )

    close_button.pack(
        pady=10
    )
    
    
    # ========================================================
    # CENTER RESULT WINDOW
    # ========================================================

    center_window(
        result_window,
        parent
    )

# ============================================================
# PROCESS BUTTON CALLBACK
# ============================================================

# ============================================================
# PROCESS BUTTON CALLBACK
# ============================================================

def on_process(
    parent,
    source_image,
    size_var,
    method_var,
    background_var,
    custom_width_var,
    custom_height_var
):
    """
    Callback tombol Process.
    """

    try:

        selected_size = size_var.get()

        if selected_size == "Custom":

            try:

                custom_width = int(
                    custom_width_var.get()
                )

                custom_height = int(
                    custom_height_var.get()
                )

            except (
                ValueError,
                TypeError
            ):

                raise ValueError(
                    "Custom width dan height "
                    "harus berupa angka."
                )

            if (
                custom_width <= 0
                or custom_height <= 0
            ):

                raise ValueError(
                    "Custom width dan height "
                    "harus lebih besar dari 0."
                )

            selected_size = (
                custom_width,
                custom_height
            )

        selected_method = (
            method_var.get()
        )

        selected_background = (
            background_var.get()
        )

        result_image = (
            process_selected_image(
                source_image,
                selected_size,
                selected_method,
                selected_background
            )
        )

        show_processed_result(
            parent,
            result_image,
            selected_size,
            selected_method
        )

    except Exception as error:

        messagebox.showerror(
            "Process Error",
            str(error),
            parent=parent
        )
        

# ============================================================
# PROCESS CONTROLS
# ============================================================

# ============================================================
# PROCESS CONTROLS
# ============================================================

def build_process_controls(
    parent,
    size_var,
    method_var,
    background_var,
    custom_width_var,
    custom_height_var,
    output_format_var
):
    """
    Membuat kontrol:

        SIZE
        RESIZE METHOD
        BACKGROUND

    Kontrol ini hanya mengatur konfigurasi.
    Engine image tetap berada di item_processor.py.
    """

    controls_frame = tk.Frame(
        parent,
        relief="groove",
        bd=1
    )

    controls_frame.pack(
        fill="x",
        padx=20,
        pady=8
    )

    # ========================================================
    # SIZE
    # ========================================================

    size_label = tk.Label(
        controls_frame,
        text="SIZE"
    )

    size_label.grid(
        row=0,
        column=0,
        padx=(10, 5),
        pady=8
    )

    size_options = list(
        SIZE_PRESETS.keys()
    )

    size_options.append(
        "Custom"
    )

    size_menu = tk.OptionMenu(
        controls_frame,
        size_var,
        *size_options
    )

    size_menu.config(
        width=12
    )

    size_menu.grid(
        row=0,
        column=1,
        padx=5,
        pady=8
    )
    
    # ========================================================
    # CUSTOM SIZE
    # ========================================================

    custom_frame = tk.Frame(
        controls_frame
    )

    custom_width_label = tk.Label(
        custom_frame,
        text="W:"
    )

    custom_width_label.pack(
        side="left"
    )

    custom_width_entry = tk.Entry(
        custom_frame,
        textvariable=custom_width_var,
        width=5
    )

    custom_width_entry.pack(
        side="left",
        padx=(3, 8)
    )

    custom_height_label = tk.Label(
        custom_frame,
        text="H:"
    )

    custom_height_label.pack(
        side="left"
    )

    custom_height_entry = tk.Entry(
        custom_frame,
        textvariable=custom_height_var,
        width=5
    )

    custom_height_entry.pack(
        side="left",
        padx=3
    )

    def update_custom_size_visibility(
        *args
    ):

        if size_var.get() == "Custom":

            custom_frame.grid(
                row=1,
                column=0,
                columnspan=2,
                padx=5,
                pady=(0, 8),
                sticky="w"
            )

        else:

            custom_frame.grid_remove()


    size_var.trace_add(
        "write",
        update_custom_size_visibility
    )

    update_custom_size_visibility()



    # ========================================================
    # RESIZE METHOD
    # ========================================================

    method_label = tk.Label(
        controls_frame,
        text="RESIZE METHOD"
    )

    method_label.grid(
        row=0,
        column=2,
        padx=(20, 5),
        pady=8
    )

    method_menu = tk.OptionMenu(
        controls_frame,
        method_var,
        *RESIZE_METHODS
    )

    method_menu.config(
        width=12
    )

    method_menu.grid(
        row=0,
        column=3,
        padx=5,
        pady=8
    )

    # ========================================================
    # BACKGROUND
    # ========================================================

    background_label = tk.Label(
        controls_frame,
        text="BACKGROUND"
    )

    background_label.grid(
        row=0,
        column=4,
        padx=(20, 5),
        pady=8
    )

    background_menu = tk.OptionMenu(
        controls_frame,
        background_var,
        *BACKGROUND_PRESETS.keys()
    )

    background_menu.config(
        width=12
    )

    background_menu.grid(
        row=0,
        column=5,
        padx=5,
        pady=8
    )
    
    # ========================================================
    # OUTPUT FORMAT
    # ========================================================

    output_format_label = tk.Label(
        controls_frame,
        text="OUTPUT FORMAT"
    )

    output_format_label.grid(
        row=1,
        column=4,
        padx=(20, 5),
        pady=8
    )

    output_format_menu = tk.OptionMenu(
        controls_frame,
        output_format_var,
        *output_processor.OUTPUT_FORMATS
    )

    output_format_menu.config(
        width=12
    )

    output_format_menu.grid(
        row=1,
        column=5,
        padx=5,
        pady=8
    )

    # ========================================================
    # UPDATE BACKGROUND OPTIONS
    # ========================================================

    def update_background_options(
        selected_size
    ):
        """
        Mengatur pilihan background berdasarkan ukuran.

        CARD hanya tersedia untuk 100x100.
        """

        # ----------------------------------------------------
        # Ambil menu internal Tkinter
        # ----------------------------------------------------

        menu = (
            background_menu["menu"]
        )

        menu.delete(
            0,
            "end"
        )

        # ----------------------------------------------------
        # Tentukan apakah CARD boleh digunakan
        # ----------------------------------------------------

        try:

            if selected_size == "Custom":

                size_width = int(
                    custom_width_var.get()
                )

                size_height = int(
                    custom_height_var.get()
                )

            else:

                size_width, size_height = (
                    resolve_size(
                        selected_size
                    )
                )

        except (
            ValueError,
            TypeError
        ):

            size_width = 0
            size_height = 0
            
        is_card_size = (
            size_width == 100
            and size_height == 100
        )
        
        
        # ----------------------------------------------------
        # Buat daftar background
        # ----------------------------------------------------

        options = []

        for name in BACKGROUND_PRESETS.keys():

            if (
                name == "CARD"
                and not is_card_size
            ):
                continue

            options.append(
                name
            )

        # ----------------------------------------------------
        # Pastikan background saat ini masih valid
        # ----------------------------------------------------

        current_background = (
            background_var.get()
        )

        if (
            current_background
            not in options
        ):

            if "WHITE" in options:

                background_var.set(
                    "WHITE"
                )

            elif options:

                background_var.set(
                    options[0]
                )

        # ----------------------------------------------------
        # Masukkan pilihan ke menu
        # ----------------------------------------------------

        for option in options:

            menu.add_command(
                label=option,
                command=lambda value=option:
                    background_var.set(
                        value
                    )
            )



    # ========================================================
    # SIZE CHANGE CALLBACK
    # ========================================================

    def on_size_changed(
        *args
    ):

        update_background_options(
            size_var.get()
        )


    size_var.trace_add(
        "write",
        on_size_changed
    )

    update_background_options(
        size_var.get()
    )


    # ========================================================
    # RESPONSIVE
    # ========================================================
    controls_frame.columnconfigure(
        1,
        weight=1
    )

    controls_frame.columnconfigure(
        3,
        weight=1
    )

    controls_frame.columnconfigure(
        5,
        weight=1
    )

    return controls_frame



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
    # PROCESS SETTINGS
    # --------------------------------------------------------

    size_var = tk.StringVar(
        value=DEFAULT_SIZE_PRESET
    )
    
    custom_width_var = tk.StringVar(
        value="100"
    )

    custom_height_var = tk.StringVar(
        value="100"
    )

    method_var = tk.StringVar(
        value=DEFAULT_RESIZE_METHOD
    )
    
    background_var = tk.StringVar(
        value=DEFAULT_BACKGROUND
    )
    
    output_format_var = tk.StringVar(
        value="PNG"
    )

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
    # PROCESS CONTROLS
    # ========================================================

    build_process_controls(
        window,
        size_var,
        method_var,
        background_var,
        custom_width_var,
        custom_height_var,
        output_format_var
    )
    
    
    
    # ========================================================
    # PROCESS BUTTON
    # ========================================================

    process_button = tk.Button(
        window,
        text="Process",
        width=15,
        command=lambda: on_process(
            window,
            source_image,
            size_var,
            method_var,
            background_var,
            custom_width_var,
            custom_height_var
        )
    )

    process_button.pack(
        pady=8
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