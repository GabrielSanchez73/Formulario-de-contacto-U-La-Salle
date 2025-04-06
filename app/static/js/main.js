// Script para manejar la funcionalidad de la página

document.addEventListener('DOMContentLoaded', function() {
    // Manejo del slider
    const sliderBtns = document.querySelectorAll('.slider-btn');
    const pages = document.querySelectorAll('.page');
    
    // Actualmente la página 1 está activa
    let currentPage = 1;
    
    // Manejador para los botones de paginación
    pages.forEach((page, index) => {
        page.addEventListener('click', () => {
            // Desactivar la página actual
            document.querySelector('.page.active').classList.remove('active');
            // Activar la página seleccionada
            page.classList.add('active');
            currentPage = index + 1;
            // Aquí iría la lógica para cambiar el contenido del slider
        });
    });
    
    // Manejador para los botones de control (anterior, pausa/play, siguiente)
    sliderBtns.forEach((btn, index) => {
        btn.addEventListener('click', () => {
            if (index === 0) { // Anterior
                if (currentPage > 1) {
                    document.querySelector('.page.active').classList.remove('active');
                    currentPage--;
                    pages[currentPage - 1].classList.add('active');
                    // Aquí iría la lógica para cambiar al slide anterior
                }
            } else if (index === 1) { // Pausa/Play
                // Lógica para pausar/reproducir el slider
                const icon = btn.querySelector('i');
                if (icon.classList.contains('fa-pause')) {
                    icon.classList.remove('fa-pause');
                    icon.classList.add('fa-play');
                    // Pausar slider
                } else {
                    icon.classList.remove('fa-play');
                    icon.classList.add('fa-pause');
                    // Reanudar slider
                }
            } else if (index === 2) { // Siguiente
                if (currentPage < pages.length) {
                    document.querySelector('.page.active').classList.remove('active');
                    currentPage++;
                    pages[currentPage - 1].classList.add('active');
                    // Aquí iría la lógica para cambiar al siguiente slide
                }
            }
        });
    });
    
    // Comportamiento del formulario de registro
    const registrationForm = document.querySelector('.registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(event) {
            // Aquí se podría agregar validación del formulario
        });
    }
});
