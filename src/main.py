import flet as ft
import flet.canvas as cv
# import numpy as np
# import joblib
import os
import base64
# from PIL import Image, ImageDraw, ImageOps

class State:
    def __init__(self):
        self.points = []  # List of strokes. Each stroke is a list of (x, y) tuples.
        self.current_stroke = []

class ImageProcessor:
    @staticmethod
    def strokes_to_image_array(strokes, width=300, height=300):
        # Return dummy array (None) and None for image
        return [], None

class Predictor:
    def __init__(self):
        self.model = "Dummy"
        # self.load_model()

    def load_model(self):
        pass

    def predict(self, img_array):
        # Return dummy prediction
        return 7, 0.99

def main(page: ft.Page):
    page.title = "手書き数字判定アプリ (MNIST)"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLUE_GREY_50

    state = State()
    processor = ImageProcessor()
    predictor = Predictor()

    # --- UI Components ---
    
    result_text = ft.Text("数字を書いて「判定」を押してください", size=20, weight="bold", color=ft.colors.BLACK87)
    
    canvas_strokes = cv.Canvas(
        shapes=[],
        content=ft.GestureDetector(
            on_pan_start=lambda e: on_pan_start(e),
            on_pan_update=lambda e: on_pan_update(e),
            on_pan_end=lambda e: on_pan_end(e),
            drag_interval=10, # Reduce event frequency slightly for performance
        ),
        expand=False,
    )
    
    # Wrap Canvas in a container to give it size and background
    canvas_container = ft.Container(
        content=canvas_strokes,
        width=300,
        height=300,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        border=ft.border.all(2, ft.colors.BLUE_GREY_200),
        alignment=ft.alignment.top_left,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    debug_image = ft.Image(src_base64="", width=100, height=100, fit=ft.ImageFit.CONTAIN, visible=False)

    def redraw_canvas():
        # Recreate shapes from state.points
        # Note: In a production app with many points, this naivety might be slow.
        # But for single digit drawing, it's usually fine.
        new_shapes = []
        for stroke in state.points:
            # Simplify: connect points with lines
            # Flet's cv.Path using Path.moveTo and Path.lineTo
            if not stroke: continue
            
            path_elements = [cv.Path.MoveTo(stroke[0][0], stroke[0][1])]
            for i in range(1, len(stroke)):
                path_elements.append(cv.Path.LineTo(stroke[i][0], stroke[i][1]))
            
            new_shapes.append(
                cv.Path(
                    elements=path_elements,
                    paint=ft.Paint(
                        stroke_width=10,
                        style=ft.PaintingStyle.STROKE,
                        color=ft.colors.BLACK,
                        stroke_cap=ft.StrokeCap.ROUND,
                        stroke_join=ft.StrokeJoin.ROUND,
                    ),
                )
            )
        
        # Also draw the current stroke being drawn
        if state.current_stroke:
            stroke = state.current_stroke
            if len(stroke) > 0:
                 path_elements = [cv.Path.MoveTo(stroke[0][0], stroke[0][1])]
                 for i in range(1, len(stroke)):
                     path_elements.append(cv.Path.LineTo(stroke[i][0], stroke[i][1]))
                 
                 new_shapes.append(
                    cv.Path(
                        elements=path_elements,
                        paint=ft.Paint(
                            stroke_width=10,
                            style=ft.PaintingStyle.STROKE,
                            color=ft.colors.BLACK,
                            stroke_cap=ft.StrokeCap.ROUND,
                            stroke_join=ft.StrokeJoin.ROUND,
                        ),
                    )
                )

        canvas_strokes.shapes = new_shapes
        canvas_strokes.update()

    # --- Event Handlers ---

    def on_pan_start(e: ft.DragStartEvent):
        state.current_stroke = [(e.local_x, e.local_y)]
        redraw_canvas()

    def on_pan_update(e: ft.DragUpdateEvent):
        # Clip coordinates to canvas size
        x = max(0, min(e.local_x, 300))
        y = max(0, min(e.local_y, 300))
        state.current_stroke.append((x, y))
        redraw_canvas()

    def on_pan_end(e: ft.DragEndEvent):
        if state.current_stroke:
            state.points.append(state.current_stroke)
            state.current_stroke = []
            redraw_canvas()

    def clear_canvas(e):
        state.points = []
        state.current_stroke = []
        result_text.value = "数字を書いて「判定」を押してください"
        debug_image.visible = False
        redraw_canvas()
        page.update()

    def predict_digit(e):
        if not state.points:
            result_text.value = "文字が書かれていません"
            page.update()
            return
        
        result_text.value = "判定中..."
        page.update()

        # Generate image
        img_array, pil_bg = processor.strokes_to_image_array(state.points)
        
        if img_array is None:
             result_text.value = "画像生成エラー"
             page.update()
             return

        # Show debug image (what the AI sees)
        if pil_bg:
            import io
            buffered = io.BytesIO()
            pil_bg.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            debug_image.src_base64 = img_str
            debug_image.visible = True
        else:
            debug_image.visible = False

        # Predict
        digit, confidence = predictor.predict(img_array)
        
        if digit is not None:
             result_text.value = f"予測: {digit} (確信度: {confidence:.1%})"
        else:
             result_text.value = f"エラー: {confidence}"
        
        page.update()

    # --- Layout ---
    
    page.add(
        ft.Column(
            [
                ft.Text("手書き数字AI判定", size=30, weight="bold", color=ft.colors.BLUE_GREY_900),
                canvas_container,
                ft.Row(
                    [
                        ft.ElevatedButton("クリア", on_click=clear_canvas, color=ft.colors.RED),
                        ft.ElevatedButton("判定", on_click=predict_digit, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                ft.Divider(),
                result_text,
                ft.Text("AIが見ている画像 (28x28):", size=12, color=ft.colors.GREY),
                debug_image
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
