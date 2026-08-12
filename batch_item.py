import tkinter as tk


def open_batch_item(
    parent
):

    window = tk.Toplevel(
        parent
    )

    window.title(
        "Item Processor - Batch"
    )

    window.geometry(
        "800x600"
    )

    title = tk.Label(
        window,
        text="ITEM PROCESSOR - BATCH",
        font=(
            "Arial",
            16,
            "bold"
        )
    )

    title.pack(
        pady=20
    )

    info = tk.Label(
        window,
        text=(
            "Source otomatis:\n"
            "BGRA pertama → "
            "Indexed pertama"
        )
    )

    info.pack(
        pady=10
    )

    placeholder = tk.Label(
        window,
        text=(
            "Batch Item Processor\n\n"
            "Open Folder / Drag & Drop\n\n"
            "Engine Batch akan dibuat "
            "di tahap berikutnya."
        ),
        relief="groove",
        width=60,
        height=18
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