import struct
import tkinter as tk

from single_item import open_single_item
from batch_item import open_batch_item

from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox

from PIL import Image
from PIL import ImageTk


# ============================================================
# KONFIGURASI
# ============================================================

THUMBNAIL_SIZE = 100

PREVIEW_SIZE = 300

THUMBNAIL_CELL_WIDTH = 125

BACKGROUND_COLOR = (
    255,
    255,
    255,
    255
)

# Warna background checker untuk preview
# transparansi agar lebih mudah terlihat.
CHECKER_COLOR_1 = (
    235,
    235,
    235,
    255
)

CHECKER_COLOR_2 = (
    255,
    255,
    255,
    255
)


# ============================================================
# BACA DATA BINARY
# ============================================================

def read_exact(file, size):

    data = file.read(size)

    if len(data) != size:

        raise EOFError(
            f"Data tidak cukup. "
            f"Diminta {size} byte, "
            f"mendapat {len(data)} byte."
        )

    return data


def read_u16(file):

    return struct.unpack(
        "<H",
        read_exact(file, 2)
    )[0]


# ============================================================
# DECOMPRESS RLE SPR 2.1+
# ============================================================

def decompress_rle(
    data,
    expected_size
):

    result = bytearray()

    position = 0

    while position < len(data):

        if len(result) >= expected_size:
            break

        value = data[position]

        position += 1

        if value == 0:

            if position >= len(data):

                raise ValueError(
                    "RLE rusak: "
                    "byte 0 tanpa "
                    "run length."
                )

            count = data[position]

            position += 1

            if count > 0:

                result.extend(
                    b"\x00" * count
                )

        else:

            result.append(value)

    if len(result) != expected_size:

        raise ValueError(
            f"Hasil RLE tidak sesuai. "
            f"Expected {expected_size} "
            f"pixel, hasil "
            f"{len(result)} pixel."
        )

    return bytes(result)


# ============================================================
# BACA PALETTE
# ============================================================

def read_palette(spr_path):

    file_size = spr_path.stat().st_size

    if file_size < 1024:

        raise ValueError(
            "File terlalu kecil "
            "untuk memiliki palette."
        )

    with open(
        spr_path,
        "rb"
    ) as file:

        file.seek(
            file_size - 1024
        )

        palette_data = read_exact(
            file,
            1024
        )

    return palette_data


# ============================================================
# INDEXED IMAGE -> RGBA
# ============================================================

def indexed_to_rgba(
    width,
    height,
    pixel_indices,
    palette_data
):

    pixel_count = (
        width * height
    )

    if width <= 0 or height <= 0:

        raise ValueError(
            f"Ukuran image tidak valid: "
            f"{width} x {height}"
        )

    if len(pixel_indices) != pixel_count:

        raise ValueError(
            f"Jumlah pixel tidak sesuai. "
            f"Expected {pixel_count}, "
            f"mendapat "
            f"{len(pixel_indices)}."
        )

    rgba_data = bytearray(
        pixel_count * 4
    )

    for i, color_index in enumerate(
        pixel_indices
    ):

        palette_position = (
            color_index * 4
        )

        if (
            palette_position + 3
            >= len(palette_data)
        ):

            raise ValueError(
                f"Palette index tidak valid: "
                f"{color_index}"
            )

        # Palette Ragnarok yang kita gunakan
        # berdasarkan hasil extractor yang
        # sebelumnya sudah berhasil.
        #
        # Format:
        # R, G, B, A

        r = palette_data[
            palette_position
        ]

        g = palette_data[
            palette_position + 1
        ]

        b = palette_data[
            palette_position + 2
        ]

        a = palette_data[
            palette_position + 3
        ]

        # Index 0 dianggap transparan.
        if color_index == 0:

            a = 0

        destination = i * 4

        rgba_data[
            destination
        ] = r

        rgba_data[
            destination + 1
        ] = g

        rgba_data[
            destination + 2
        ] = b

        rgba_data[
            destination + 3
        ] = a

    image = Image.frombytes(
        "RGBA",
        (
            width,
            height
        ),
        bytes(rgba_data)
    )

    return image


# ============================================================
# BACA SATU INDEXED IMAGE
# ============================================================

def read_indexed_sprite(
    file,
    version,
    palette_data
):

    width = read_u16(file)

    height = read_u16(file)

    if width <= 0 or height <= 0:

        raise ValueError(
            f"Ukuran indexed image "
            f"tidak valid: "
            f"{width} x {height}"
        )

    pixel_count = (
        width * height
    )

    # --------------------------------------------------------
    # SPR 2.1+
    # --------------------------------------------------------

    if version >= 2.1:

        encoded_size = read_u16(
            file
        )

        encoded_data = read_exact(
            file,
            encoded_size
        )

        pixel_indices = (
            decompress_rle(
                encoded_data,
                pixel_count
            )
        )

    # --------------------------------------------------------
    # SPR 1.x dan 2.0
    # --------------------------------------------------------

    else:

        pixel_indices = read_exact(
            file,
            pixel_count
        )

    image = indexed_to_rgba(
        width,
        height,
        pixel_indices,
        palette_data
    )

    return image


# ============================================================
# BACA SATU TRUE-COLOR / BGRA IMAGE
# ============================================================

def read_truecolor_sprite(file):

    width = read_u16(file)

    height = read_u16(file)

    if width <= 0 or height <= 0:

        raise ValueError(
            f"Ukuran true-color image "
            f"tidak valid: "
            f"{width} x {height}"
        )

    pixel_count = (
        width * height
    )

    pixel_size = (
        pixel_count * 4
    )

    pixel_data = read_exact(
        file,
        pixel_size
    )

    rgba_data = bytearray(
        pixel_size
    )

    for i in range(pixel_count):

        position = i * 4

        # Format SPR:
        #
        # A, B, G, R

        a = pixel_data[
            position
        ]

        b = pixel_data[
            position + 1
        ]

        g = pixel_data[
            position + 2
        ]

        r = pixel_data[
            position + 3
        ]

        # Format RGBA:

        rgba_data[
            position
        ] = r

        rgba_data[
            position + 1
        ] = g

        rgba_data[
            position + 2
        ] = b

        rgba_data[
            position + 3
        ] = a

    image = Image.frombytes(
        "RGBA",
        (
            width,
            height
        ),
        bytes(rgba_data)
    )

    return image


# ============================================================
# BACA SEMUA IMAGE DARI SPR
# ============================================================

def read_spr(spr_path):

    palette_data = read_palette(
        spr_path
    )

    indexed_images = []

    truecolor_images = []

    with open(
        spr_path,
        "rb"
    ) as file:

        # ----------------------------------------------------
        # SIGNATURE
        # ----------------------------------------------------

        signature = read_exact(
            file,
            2
        )

        if signature != b"SP":

            raise ValueError(
                f"Bukan file SPR valid: "
                f"{signature!r}"
            )

        # ----------------------------------------------------
        # VERSION
        #
        # Urutan:
        # minor, major
        # ----------------------------------------------------

        minor, major = struct.unpack(
            "BB",
            read_exact(file, 2)
        )

        version = (
            major +
            (minor / 10)
        )

        # ----------------------------------------------------
        # JUMLAH INDEXED
        # ----------------------------------------------------

        indexed_count = read_u16(
            file
        )

        # ----------------------------------------------------
        # JUMLAH TRUE-COLOR
        # ----------------------------------------------------

        truecolor_count = 0

        if version >= 2.0:

            truecolor_count = (
                read_u16(file)
            )

        # ----------------------------------------------------
        # BACA SEMUA INDEXED
        # ----------------------------------------------------

        for index in range(
            indexed_count
        ):

            image = read_indexed_sprite(
                file,
                version,
                palette_data
            )

            indexed_images.append(
                {
                    "type": "Indexed",
                    "index": index,
                    "image": image
                }
            )

        # ----------------------------------------------------
        # BACA SEMUA TRUE-COLOR
        # ----------------------------------------------------

        for index in range(
            truecolor_count
        ):

            image = (
                read_truecolor_sprite(
                    file
                )
            )

            truecolor_images.append(
                {
                    "type": "BGRA",
                    "index": index,
                    "image": image
                }
            )

    return {
        "version": version,
        "indexed": indexed_images,
        "truecolor": truecolor_images
    }


# ============================================================
# BUAT THUMBNAIL
# ============================================================

def create_thumbnail(image):

    thumbnail = image.copy()

    thumbnail.thumbnail(
        (
            THUMBNAIL_SIZE,
            THUMBNAIL_SIZE
        ),
        Image.Resampling.NEAREST
    )

    # Canvas thumbnail.
    canvas = Image.new(
        "RGBA",
        (
            THUMBNAIL_SIZE,
            THUMBNAIL_SIZE
        ),
        BACKGROUND_COLOR
    )

    x = (
        THUMBNAIL_SIZE
        - thumbnail.width
    ) // 2

    y = (
        THUMBNAIL_SIZE
        - thumbnail.height
    ) // 2

    canvas.alpha_composite(
        thumbnail,
        (
            x,
            y
        )
    )

    return canvas


# ============================================================
# BUAT CHECKERBOARD PREVIEW
# ============================================================

def create_checkerboard(
    width,
    height,
    cell_size=12
):

    image = Image.new(
        "RGBA",
        (
            width,
            height
        ),
        CHECKER_COLOR_1
    )

    pixels = image.load()

    for y in range(
        0,
        height,
        cell_size
    ):

        for x in range(
            0,
            width,
            cell_size
        ):

            cell_x = (
                x // cell_size
            )

            cell_y = (
                y // cell_size
            )

            if (
                (cell_x + cell_y) % 2
                == 1
            ):

                for py in range(
                    y,
                    min(
                        y + cell_size,
                        height
                    )
                ):

                    for px in range(
                        x,
                        min(
                            x + cell_size,
                            width
                        )
                    ):

                        pixels[
                            px,
                            py
                        ] = CHECKER_COLOR_2

    return image


# ============================================================
# BUAT PREVIEW BESAR
# ============================================================

def create_preview(image):

    preview = image.copy()

    preview.thumbnail(
        (
            PREVIEW_SIZE,
            PREVIEW_SIZE
        ),
        Image.Resampling.NEAREST
    )

    background = (
        create_checkerboard(
            PREVIEW_SIZE,
            PREVIEW_SIZE
        )
    )

    x = (
        PREVIEW_SIZE
        - preview.width
    ) // 2

    y = (
        PREVIEW_SIZE
        - preview.height
    ) // 2

    background.alpha_composite(
        preview,
        (
            x,
            y
        )
    )

    return background


# ============================================================
# APLIKASI SPR VIEWER
# ============================================================

class SprViewer:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Ragnarok SPR Viewer"
        )

        self.root.geometry(
            "1200x800"
        )

        # Data SPR.
        self.spr_data = None

        self.spr_path = None

        # Source yang sedang dipilih.
        self.selected_source = None

        # Simpan PhotoImage agar tidak
        # dihapus oleh garbage collector.
        self.thumbnail_references = []

        self.preview_reference = None
        
        self.current_grid_width = 0

        self.grid_resize_job = None

        self.build_ui()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------

        top_frame = tk.Frame(
            self.root
        )

        top_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        open_button = tk.Button(
            top_frame,
            text="Open SPR",
            width=12,
            command=self.open_spr
        )

        open_button.pack(
            side="left"
        )

        self.filename_label = tk.Label(
            top_frame,
            text="Belum ada file SPR",
            anchor="w"
        )

        self.filename_label.pack(
            side="left",
            padx=15
        )
        
        open_button.pack(
            side="left"
        )

        batch_button = tk.Button(
            top_frame,
            text="Batch",
            width=12,
            command=self.open_batch
        )

        batch_button.pack(
            side="left",
            padx=(5, 0)
        )

        # ----------------------------------------------------
        # INFO SPR
        # ----------------------------------------------------

        self.info_label = tk.Label(
            self.root,
            text="",
            anchor="w",
            justify="left"
        )

        self.info_label.pack(
            fill="x",
            padx=10,
            pady=(0, 5)
        )

        # ----------------------------------------------------
        # MAIN AREA
        # ----------------------------------------------------

        main_frame = tk.Frame(
            self.root
        )

        main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        # ----------------------------------------------------
        # IMAGE AREA
        # ----------------------------------------------------

        image_frame = tk.Frame(
            main_frame,
            bd=1,
            relief="sunken"
        )

        image_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Canvas untuk scroll.
        self.canvas = tk.Canvas(
            image_frame,
            highlightthickness=0
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            image_frame,
            orient="vertical",
            command=self.canvas.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        # Frame di dalam canvas.
        self.images_frame = tk.Frame(
            self.canvas
        )

        self.canvas_window = (
            self.canvas.create_window(
                (
                    0,
                    0
                ),
                window=self.images_frame,
                anchor="nw"
            )
        )

        self.images_frame.bind(
            "<Configure>",
            self.on_images_frame_configure
        )

        self.canvas.bind(
            "<Configure>",
            self.on_canvas_configure
        )

        # Mouse wheel.
        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

        # Linux mouse wheel.
        self.canvas.bind_all(
            "<Button-4>",
            self.on_mousewheel_linux
        )

        self.canvas.bind_all(
            "<Button-5>",
            self.on_mousewheel_linux
        )

        # ----------------------------------------------------
        # PREVIEW AREA
        # ----------------------------------------------------

        preview_frame = tk.Frame(
            main_frame,
            width=360
        )

        preview_frame.pack(
            side="right",
            fill="y",
            padx=(10, 0)
        )

        preview_frame.pack_propagate(
            False
        )

        preview_title = tk.Label(
            preview_frame,
            text="Preview",
            font=(
                "Arial",
                14,
                "bold"
            )
        )

        preview_title.pack(
            pady=(10, 5)
        )

        self.preview_label = tk.Label(
            preview_frame,
            text="Pilih image",
            bd=1,
            relief="sunken"
        )

        self.preview_label.pack(
            padx=10,
            pady=10
        )

        self.source_info_label = tk.Label(
            preview_frame,
            text="",
            justify="left",
            anchor="w"
        )

        self.source_info_label.pack(
            fill="x",
            padx=10,
            pady=10
        )
        
        self.process_button = tk.Button(
            preview_frame,
            text="Process",
            width=20,
            state="disabled",
            command=self.process_selected
        )

        self.process_button.pack(
            padx=10,
            pady=10
        )

    # ========================================================
    # OPEN SPR
    # ========================================================

    def open_spr(self):

        file_path = filedialog.askopenfilename(
            title="Pilih file SPR",
            filetypes=[
                (
                    "Ragnarok SPR",
                    "*.spr"
                ),
                (
                    "All Files",
                    "*.*"
                )
            ]
        )

        if not file_path:

            return

        try:

            spr_path = Path(
                file_path
            )

            self.filename_label.config(
                text=(
                    spr_path.name
                )
            )

            self.root.config(
                cursor="watch"
            )

            self.root.update_idletasks()

            spr_data = read_spr(
                spr_path
            )

            self.spr_data = spr_data

            self.spr_path = (
                spr_path
            )

            self.selected_source = None

            self.show_spr_info()

            self.display_images()

        except Exception as error:

            messagebox.showerror(
                "Error membaca SPR",
                str(error)
            )

        finally:

            self.root.config(
                cursor=""
            )

    # ========================================================
    # TAMPILKAN INFO SPR
    # ========================================================

    def show_spr_info(self):

        if not self.spr_data:

            return

        version = (
            self.spr_data[
                "version"
            ]
        )

        indexed_count = len(
            self.spr_data[
                "indexed"
            ]
        )

        truecolor_count = len(
            self.spr_data[
                "truecolor"
            ]
        )

        text = (
            f"SPR Version: "
            f"{version:.1f}    |    "
            f"Indexed: "
            f"{indexed_count}    |    "
            f"BGRA: "
            f"{truecolor_count}"
        )

        self.info_label.config(
            text=text
        )

    # ========================================================
    # HAPUS THUMBNAIL LAMA
    # ========================================================

    def clear_images(self):

        for widget in (
            self.images_frame.winfo_children()
        ):

            widget.destroy()

        self.thumbnail_references.clear()

    # ========================================================
    # TAMPILKAN SEMUA IMAGE
    # ========================================================

    def display_images(self):

        self.clear_images()

        if not self.spr_data:

            return
        
        self.images_frame.update_idletasks()

        self.canvas.configure(
            scrollregion=(
                self.canvas.bbox(
                    "all"
                )
            )
        )

        # ----------------------------------------------------
        # INDEXED
        # ----------------------------------------------------

        indexed_images = (
            self.spr_data[
                "indexed"
            ]
        )

        if indexed_images:

            self.create_section_title(
                "Indexed Images"
            )

            self.create_thumbnail_grid(
                indexed_images
            )

        # ----------------------------------------------------
        # TRUE COLOR
        # ----------------------------------------------------

        truecolor_images = (
            self.spr_data[
                "truecolor"
            ]
        )

        if truecolor_images:

            self.create_section_title(
                "True Color / BGRA"
            )

            self.create_thumbnail_grid(
                truecolor_images
            )

        # Update scroll region.
        self.images_frame.update_idletasks()

        self.canvas.configure(
            scrollregion=(
                self.canvas.bbox(
                    "all"
                )
            )
        )

        self.canvas.yview_moveto(
            0
        )

    # ========================================================
    # JUDUL SECTION
    # ========================================================

    def create_section_title(
        self,
        title
    ):

        label = tk.Label(
            self.images_frame,
            text=title,
            font=(
                "Arial",
                12,
                "bold"
            ),
            anchor="w"
        )

        label.pack(
            fill="x",
            padx=10,
            pady=(
                15,
                5
            )
        )

    # ========================================================
    # GRID THUMBNAIL
    # ========================================================

    def create_thumbnail_grid(
        self,
        image_list
    ):

        grid_frame = tk.Frame(
            self.images_frame
        )

        grid_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        canvas_width = (
            self.canvas.winfo_width()
        )

        if canvas_width <= 1:

            columns = 1

        else:

            columns = max(
                1,
                canvas_width
                // THUMBNAIL_CELL_WIDTH
            )

        for position, item in enumerate(
            image_list
        ):

            row = (
                position
                // columns
            )

            column = (
                position
                % columns
            )

            self.create_thumbnail(
                grid_frame,
                item,
                row,
                column
            )
    
    
    # ========================================================
    # BUAT SATU THUMBNAIL
    # ========================================================

    def create_thumbnail(
        self,
        parent,
        item,
        row,
        column
    ):

        image = item[
            "image"
        ]

        image_type = item[
            "type"
        ]

        index = item[
            "index"
        ]

        thumbnail = (
            create_thumbnail(
                image
            )
        )

        photo = ImageTk.PhotoImage(
            thumbnail
        )

        self.thumbnail_references.append(
            photo
        )

        frame = tk.Frame(
            parent,
            bd=1,
            relief="solid",
            padx=3,
            pady=3
        )

        frame.grid(
            row=row,
            column=column,
            padx=5,
            pady=5,
            sticky="n"
        )

        image_label = tk.Label(
            frame,
            image=photo,
            cursor="hand2"
        )

        image_label.pack()

        type_text = (
            f"{image_type} "
            f"#{index}"
        )

        type_label = tk.Label(
            frame,
            text=type_text,
            font=(
                "Arial",
                8
            )
        )

        type_label.pack()

        size_label = tk.Label(
            frame,
            text=(
                f"{image.width} x "
                f"{image.height}"
            ),
            font=(
                "Arial",
                8
            )
        )

        size_label.pack()

        # Simpan data item pada event.
        image_label.bind(
            "<Button-1>",
            lambda event,
            selected_item=item:
            self.select_image(
                selected_item
            )
        )

        frame.bind(
            "<Button-1>",
            lambda event,
            selected_item=item:
            self.select_image(
                selected_item
            )
        )

        type_label.bind(
            "<Button-1>",
            lambda event,
            selected_item=item:
            self.select_image(
                selected_item
            )
        )

        size_label.bind(
            "<Button-1>",
            lambda event,
            selected_item=item:
            self.select_image(
                selected_item
            )
        )

    # ========================================================
    # PILIH IMAGE
    # ========================================================

    def select_image(
        self,
        item
    ):

        self.selected_source = item
        
        self.process_button.config(
            state="normal"
        )

        image = item[
            "image"
        ]

        image_type = item[
            "type"
        ]

        index = item[
            "index"
        ]

        preview = create_preview(
            image
        )

        photo = ImageTk.PhotoImage(
            preview
        )

        self.preview_reference = (
            photo
        )

        self.preview_label.config(
            image=photo,
            text=""
        )

        info_text = (
            f"Type   : {image_type}\n"
            f"Index  : {index}\n"
            f"Size   : "
            f"{image.width} x "
            f"{image.height}"
        )

        self.source_info_label.config(
            text=info_text
        )

    # ========================================================
    # UPDATE SCROLL REGION
    # ========================================================

    def on_images_frame_configure(
        self,
        event
    ):

        self.canvas.configure(
            scrollregion=(
                self.canvas.bbox(
                    "all"
                )
            )
        )

    # ========================================================
    # UPDATE WIDTH CANVAS
    # ========================================================

    def on_canvas_configure(
        self,
        event
    ):

        self.canvas.itemconfigure(
            self.canvas_window,
            width=event.width
        )

        if not self.spr_data:
            return

        # Hindari rebuild grid setiap pixel
        # ketika window sedang di-resize.
        if self.grid_resize_job is not None:

            self.root.after_cancel(
                self.grid_resize_job
            )

        self.grid_resize_job = (
            self.root.after(
                100,
                self.responsive_grid
            )
        )
    
    
    # ========================================================
    # MOUSE WHEEL WINDOWS
    # ========================================================

    def on_mousewheel(
        self,
        event
    ):

        self.canvas.yview_scroll(
            int(
                -1 *
                (event.delta / 120)
            ),
            "units"
        )

    # ========================================================
    # MOUSE WHEEL LINUX
    # ========================================================

    def on_mousewheel_linux(
        self,
        event
    ):

        if event.num == 4:

            self.canvas.yview_scroll(
                -3,
                "units"
            )

        elif event.num == 5:

            self.canvas.yview_scroll(
                3,
                "units"
            )
            
    def responsive_grid(self):

        self.grid_resize_job = None

        if not self.spr_data:
            return

        canvas_width = (
            self.canvas.winfo_width()
        )

        if canvas_width <= 1:
            return

        # Hitung jumlah kolom yang muat.
        columns = max(
            1,
            canvas_width
            // THUMBNAIL_CELL_WIDTH
        )

        # Jika jumlah kolom tidak berubah,
        # tidak perlu membuat ulang grid.
        if columns == self.current_grid_width:
            return

        self.current_grid_width = columns

        # Simpan posisi scroll.
        scroll_position = (
            self.canvas.yview()
        )

        self.display_images()

        # Kembalikan posisi scroll.
        if scroll_position:

            self.canvas.yview_moveto(
                scroll_position[0]
            )
            
    def process_selected(self):

        if self.selected_source is None:

            messagebox.showwarning(
                "Source belum dipilih",
                "Silakan pilih image terlebih dahulu."
            )

            return

        open_single_item(
            self.root,
            self.selected_source
        )
    
    
    def open_batch(self):

        open_batch_item(
            self.root
        )
    

# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    app = SprViewer(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()