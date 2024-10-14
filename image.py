import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import io

def main():
    st.title("Fotolitógrafo v.0.1 - alpha")
    
    # Step 1: Upload Image
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height
        
        st.write(f"Original Dimensions: {original_width}x{original_height}")
        st.write(f"Aspect Ratio: {aspect_ratio:.2f}")
        
        # Step 2: Check Aspect Ratio and Offer Resize Options
        if original_width == 1920 and original_height == 1080:
            st.success("The image is already 1920x1080. No resizing needed.")
            save_image_options(image)
        else:
            if aspect_ratio == 16 / 9:
                st.info("The image has a 16:9 aspect ratio.")
                if original_width > 1920 or original_height > 1080:
                    image = resize_image(image, 1920, 1080)
                    st.image(image, caption="Resized Image (1920x1080)", use_column_width=True)
                    save_image_options(image)
                else:
                    st.success("The image is smaller than or equal to 1920x1080.")
                    save_image_options(image)
            else:
                st.warning("The image does not have a 16:9 aspect ratio.")
                cols = st.columns(2)
                with cols[0]:
                    option = st.selectbox("Choose Adjustment Method", ["Crop", "Fit on Canvas"], key="adjustment_method")
                    background_option = st.selectbox("Choose Background Option", ["Solid Color", "Blur"], key="background_option")
                    if background_option == "Solid Color":
                        color = st.color_picker("Choose Background Color", value="#ffffff")
                        canvas = Image.new("RGB", (1920, 1080), color=color)
                    elif background_option == "Blur":
                        blur_amount = st.selectbox("Choose Blur Amount", [0, 20, 50, 100])
                        canvas = fit_on_canvas(image, 1920, 1080, blur=True, blur_amount=blur_amount)
                
                with cols[1]:
                    # Allow user to reposition the image and resize
                    center_horizontal = st.checkbox("Center Horizontally")
                    center_vertical = st.checkbox("Center Vertically")
                    
                    x_offset = st.slider("Move Horizontally", -1920 // 2, 1920 // 2, 0) if not center_horizontal else 0
                    y_offset = -st.slider("Move Vertically", -1080 // 2, 1080 // 2, 0) if not center_vertical else 0
                    scale = st.slider("Scale Image", 0.5, 10.0, 1.0)  # Allow scaling beyond canvas size
                    new_width = int(image.width * scale)
                    new_height = int(image.height * scale)
                    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
                
                try:
                    canvas.paste(resized_image, (x_offset + (1920 - new_width) // 2, y_offset + (1080 - new_height) // 2))
                except ValueError as e:
                    st.error(f"Error pasting image: {str(e)}. Ensure that the offsets do not move the image beyond the canvas boundaries.")
                st.image(canvas, caption="Cropped Image with Adjustments (1920x1080)", use_column_width=True)
                save_image_options(canvas)

# Function to resize the image
def resize_image(image, target_width, target_height):
    return image.resize((target_width, target_height), Image.LANCZOS)

# Function to crop the image
def crop_image(image, target_width, target_height):
    return ImageOps.fit(image, (target_width, target_height), method=Image.LANCZOS)

# Function to fit the image on a canvas
def fit_on_canvas(image, canvas_width, canvas_height, repeat=False, blur=False, blur_amount=0, color=None):
    canvas = Image.new("RGB", (canvas_width, canvas_height), color=(255, 255, 255))
    if color:
        canvas = Image.new("RGB", (canvas_width, canvas_height), color=color)
    elif blur:
        background = image.resize((canvas_width, canvas_height), Image.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(blur_amount))
        canvas.paste(background)
    
    return canvas

# Function to offer save options
def save_image_options(image):
    cols = st.columns(2)
    with cols[0]:
        file_format = st.selectbox("Select file format to save", ["WEBP", "JPEG", "PNG"])
    with cols[1]:
        quality = st.slider("Choose Quality (Higher means larger file size)", 10, 100, 85)
    output = io.BytesIO()
    try:
        image.save(output, format=file_format, quality=quality)
    except KeyError as e:
        st.error(f"Error saving image: Unsupported file format '{file_format}'.")
        return
    image_size = len(output.getvalue()) / 1024  # Size in KB
    cols = st.columns(2)
    with cols[0]:
        st.write(f"Estimated File Size: {image_size:.2f} KB")
    if image_size > 500:
        with cols[1]:
            st.markdown('<span style="color: red; font-weight: bold;">Warning: File size exceeds 500 KB!</span>', unsafe_allow_html=True)
    st.download_button(label="Download Image", data=output.getvalue(), file_name=f"resized_image.{file_format.lower()}", mime=f"image/{file_format.lower()}")

if __name__ == "__main__":
    main()