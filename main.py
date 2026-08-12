import tkinter as tk

from spr_viewer import SprViewer


def main():

    root = tk.Tk()

    app = SprViewer(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()