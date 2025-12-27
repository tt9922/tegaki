import flet as ft
print("Script loaded - Top level")

def main(page: ft.Page):
    print("Main function started")
    page.title = "Hello World"
    page.add(ft.Text("Hello, World! from Flet on GitHub Pages"))

if __name__ == "__main__":
    ft.app(target=main)
