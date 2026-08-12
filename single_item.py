import tkinter as tk


def open_single_item(
    parent,
    selected_source
):

    window = tk.Toplevel(
        parent
    )

    window.title(
        "Item Processor - Single"
    )

    window.geometry(
        "700x600"
    )

    title = tk.Label(
        window,
        text="ITEM PROCESSOR - SINGLE",
        font=(
            "Arial",
            16,
            "bold"
        )
    )

    title.pack(
        pady=20
    )

    image_type = selected_source[
        "type"
    ]

    image_index = selected_source[
        "index"
    ]

    image = selected_source[
        "image"
    ]

    info = tk.Label(
        window,
        text=(
            f"Source : {image_type} "
            f"#{image_index}\n"
            f"Size   : "
            f"{image.width} × "
            f"{image.height}"
        )
    )

    info.pack(
        pady=10
    )

    placeholder = tk.Label(
        window,
        text=(
            "Single Item Processor\n\n"
            "Engine 24×24 akan dibuat "
            "di tahap berikutnya."
        ),
        relief="groove",
        width=50,
        height=15
    )

    placeholder.pack(
        padx=20,
        pady=20,
        fill="both",
        expand=True
    )

    close_button = tk.Button(
        window,
        text="Close",
        width=15,
        command=window.destroy
    )

    close_button.pack(
        pady=15
    )