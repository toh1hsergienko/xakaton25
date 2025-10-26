import streamlit as st
from streamlit_folium import st_folium
import folium

# ==============================
# Настройка страницы
# ==============================
st.set_page_config(
    page_title="City Routes",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# Инициализация состояния
# ==============================
if "user_nickname" not in st.session_state:
    st.session_state.user_nickname = ""
if "current_page" not in st.session_state:
    st.session_state.current_page = "start"  # "start" или "map"
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Категория"  # По умолчанию

# ==============================
# Стили: меню в левом верхнем углу
# ==============================
st.markdown("""
    <style>
    .top-left-menu {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 999;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        padding: 0.5rem 0;
        min-width: 200px;
    }
    .menu-item {
        display: block;
        padding: 0.6rem 1rem;
        text-decoration: none;
        color: #333;
        cursor: pointer;
        transition: background 0.2s;
    }
    .menu-item:hover {
        background-color: #f0f7ff;
        color: #1976d2;
    }
    .menu-item.active {
        background-color: #e3f2fd;
        font-weight: bold;
        color: #1976d2;
    }
    .stApp {
        background-color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================
# Стартовая страница
# ==============================
def show_start_page():
    st.markdown("<div style='text-align: center; padding-top: 100px;'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2521/2521535.png", width=100)
    st.markdown("<h1 style='color: #1976d2; font-size: 2.5rem;'>Постройте свой<br>первый маршрут!</h1>", unsafe_allow_html=True)
    
    nickname = st.text_input("Введите ваш ник", value=st.session_state.user_nickname, key="nickname_input")
    if st.button("Начать", type="primary", use_container_width=True, key="start_btn"):
        if nickname.strip():
            st.session_state.user_nickname = nickname.strip()
            st.session_state.current_page = "map"
            st.rerun()
        else:
            st.error("Пожалуйста, введите ваш ник")
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# Содержимое вкладок (заглушки)
# ==============================
def render_tab_content():
    tab = st.session_state.active_tab
    st.subheader(tab)
    
    if tab == "Категория":
        st.write("Здесь будет фильтрация мест по категориям: музеи, парки, рестораны и т.д.")
        st.info("Заглушка: выбор категорий")
    
    elif tab == "Маршрут пользователя":
        st.write("Здесь вы сможете построить и настроить свой персонализированный маршрут.")
        st.info("Заглушка: генерация маршрута через ваш бэкенд")
    
    elif tab == "Маршруты других":
        st.write("Просмотр популярных маршрутов других пользователей в Ростове-на-Дону.")
        st.info("Заглушка: лента маршрутов")
    
    elif tab == "Профиль":
        st.write(f"**Профиль пользователя:** {st.session_state.user_nickname}")
        st.write("История ваших маршрутов, избранное, настройки.")
        st.info("Заглушка: профиль")

# ==============================
# Страница карты
# ==============================
def show_map_page():
    # Обработка query_params для переключения вкладок
    tab_from_url = st.query_params.get("tab")
    if tab_from_url in ["Категория", "Маршрут пользователя", "Маршруты других", "Профиль"]:
        st.session_state.active_tab = tab_from_url

    # Меню в левом верхнем углу
    active = st.session_state.active_tab
    menu_html = f"""
    <div class="top-left-menu">
        <div class="menu-item {'active' if active == 'Категория' else ''}" 
             onclick="window.location.search='?tab=Категория'">Категория</div>
        <div class="menu-item {'active' if active == 'Маршрут пользователя' else ''}" 
             onclick="window.location.search='?tab=Маршрут пользователя'">Маршрут пользователя</div>
        <div class="menu-item {'active' if active == 'Маршруты других' else ''}" 
             onclick="window.location.search='?tab=Маршруты других'">Маршруты других</div>
        <div class="menu-item {'active' if active == 'Профиль' else ''}" 
             onclick="window.location.search='?tab=Профиль'">Профиль</div>
    </div>
    """
    st.markdown(menu_html, unsafe_allow_html=True)

    # Основной контент: карта + вкладка
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown("### Карта Ростова-на-Дону")
        m = folium.Map(location=[47.2312, 39.7086], zoom_start=12, tiles="OpenStreetMap")
        folium.Marker([47.2312, 39.7086], popup="Набережная реки Дон").add_to(m)
        st_folium(m, width="100%", height=600)
    
    with col2:
        render_tab_content()

# ==============================
# Основной поток
# ==============================
def main():
    if st.session_state.current_page == "start":
        show_start_page()
    else:
        show_map_page()

if __name__ == "__main__":
    main()