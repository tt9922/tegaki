import flet as ft

def main(page: ft.Page):
    page.title = "Hello World"
    page.add(ft.Text("Hello, World! from Flet on GitHub Pages"))

if __name__ == "__main__":
    ft.app(target=main)
