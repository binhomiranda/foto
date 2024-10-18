import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import io

def main():
    st.set_page_config(layout="wide")
    st.title("Fotolitógrafo v.0.5 - alpha")
    
    # Inicializar um canvas vazio padrão
    canvas = Image.new("RGB", (1920, 1080), color=(45, 45, 45))
    
    with st.sidebar:
        # Passo 1: Carregar Imagem
        uploaded_file = st.file_uploader("Carregar uma Imagem", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            
            st.write(f"Dimensões Originais: {original_width}x{original_height}")
            st.write(f"Proporção: {aspect_ratio:.2f}")
            
            # Verificar tamanho do arquivo
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Tamanho em MB
            
            # Passo 2: Limitar escala da imagem
            max_scale = 3.0
            if original_width > 3000 or file_size > 5:
                st.warning("Esta é uma imagem de alta resolução. A escala está limitada a um máximo de 3x para evitar instabilidade do sistema.")
                max_scale = min(max_scale, 3.0)
            
            # Redimensionar automaticamente a imagem para caber dentro do tamanho da tela (1920x1080) mantendo a proporção
            if original_width > 1920 or original_height > 1080:
                image = resize_to_fit_canvas(image, 1920, 1080)
                st.info("A imagem foi automaticamente redimensionada para caber dentro de 1920x1080, mantendo sua proporção.")
            
            # Passo 3: Exibir a imagem e oferecer opções de edição
            fit_on_canvas_option = st.checkbox("Ajustar na Tela")
            background_option = st.selectbox("Escolha a Opção de Fundo", ["Cor Sólida", "Desfocar"], key="background_option_unique")
            color = (45, 45, 45)
            blur_amount = 50

            if background_option == "Cor Sólida":
                color = st.color_picker("Escolha a Cor de Fundo", value="#909090", key="color_picker_unique")
            elif background_option == "Desfocar":
                blur_amount = st.selectbox("Escolha a Quantidade de Desfoque", [20, 50, 100], key="blur_amount_unique")
            
            # Permitir que o usuário reposicione a imagem e redimensione
            center_horizontal = st.checkbox("Centrar Horizontalmente", key="center_horizontal_unique")
            center_vertical = st.checkbox("Centrar Verticalmente", key="center_vertical_unique")
            
            x_offset = st.slider("Mover Horizontalmente", -1920 // 2, 1920 // 2, 0, key="x_offset_unique") if not center_horizontal else 0
            y_offset = -st.slider("Mover Verticalmente", -1080 // 2, 1080 // 2, 0, key="y_offset_unique") if not center_vertical else 0
            scale = st.slider("Escalar Imagem", 0.1, max_scale, 1.0, key="scale_unique")  # Permitir redução de escala
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        
            # Criar tela com base na escolha do usuário
            canvas = Image.new("RGB", (1920, 1080), color=color)
            if background_option == "Desfocar":
                background = image.resize((1920, 1080), Image.LANCZOS)
                background = background.filter(ImageFilter.GaussianBlur(blur_amount))
                canvas.paste(background, (0, 0))
            
            try:
                # Aplicar a lógica de reposicionamento e escala adequadamente
                if fit_on_canvas_option:
                # Limitar a imagem a se ajustar dentro dos limites do canvas
                    x_offset = (1920 - new_width) // 2
                    y_offset = (1080 - new_height) // 2
                else:
                    if center_horizontal:
                     x_offset = (1920 - new_width) // 2
                canvas.paste(resized_image, (x_offset, y_offset), resized_image.convert('RGBA'))
            except ValueError as e:
                st.error(f"Erro ao colar a imagem: {str(e)}. Certifique-se de que os deslocamentos não movam a imagem além dos limites da tela.")
    
    # Exibir o canvas no meio da tela
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.image(canvas, caption="Imagem Recortada com Ajustes (1920x1080)", use_column_width=False, width=800)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_file is not None:
        save_image_options(canvas)

# Função para redimensionar a imagem mantendo a proporção para caber dentro das dimensões alvo
def resize_to_fit_canvas(image, target_width, target_height):
    image.thumbnail((target_width, target_height), Image.LANCZOS)
    return image

# Função para redimensionar a imagem
def resize_image(image, target_width, target_height):
    return image.resize((target_width, target_height), Image.LANCZOS)

# Função para recortar a imagem
def crop_image(image, target_width, target_height):
    return ImageOps.fit(image, (target_width, target_height), method=Image.LANCZOS)

# Função para ajustar a imagem em uma tela
def fit_on_canvas(image, canvas_width, canvas_height, repeat=False, blur=False, blur_amount=0, color=None):
    canvas = Image.new("RGB", (canvas_width, canvas_height), color=(255, 255, 255))
    if blur:
        background = image.resize((canvas_width, canvas_height), Image.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(blur_amount))
        canvas.paste(background, (0, 0))
    elif color:
        canvas = Image.new("RGB", (canvas_width, canvas_height), color=color)
    
    return canvas

# Função para oferecer opções de salvar a imagem
def save_image_options(image):
    empty_col1, col1, empty_col2 = st.columns([0.01, 1, 2])
    with col1:
        file_format = st.selectbox("Selecione o formato do arquivo para salvar", ["WEBP", "JPEG", "PNG"], key="file_format_save")
        quality = st.slider("Escolha a Qualidade (Maior significa maior tamanho do arquivo)", 10, 100, 85, key="quality_save")
    output = io.BytesIO()
    try:
        image.save(output, format=file_format, quality=quality)
    except KeyError as e:
        st.error(f"Erro ao salvar a imagem: Formato de arquivo não suportado '{file_format}'.")
        return
    image_size = len(output.getvalue()) / 1024  # Tamanho em KB
    empty_col1, col2, empty_col3 = st.columns([0.01, 1, 2])
    with col2:
        st.write(f"Tamanho Estimado do Arquivo: {image_size:.2f} KB")
    if image_size > 500:
        with col2:
            st.markdown('<span style="color: red; font-weight: bold;">Aviso: O tamanho do arquivo excede 500 KB!</span>', unsafe_allow_html=True)
    st.download_button(label="Baixar Imagem", data=output.getvalue(), file_name=f"resized_image.{file_format.lower()}", mime=f"image/{file_format.lower()}")

if __name__ == "__main__":
    main()
