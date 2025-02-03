// Función para obtener los datos cifrados desde la API
function fetchSecureData() {
    fetch('/secure-data/')
        .then(response => response.json())
        .then(data => {
            console.log("Estado:", data.status);
            console.log("Mensaje:", data.message);
            console.log("Datos cifrados:", data.encrypted_data);
            document.getElementById('secure-data-container').innerText = data.encrypted_data;
        })
        .catch(error => {
            console.error("Error al obtener los datos:", error);
        });
}

document.addEventListener('DOMContentLoaded', function () {
    fetchSecureData();
});


// Creacion principal para el manejo del modal
        $(document).ready(function () {
            $('#openTerms').click(function () {
                $('#termsModal').modal('show');
            });

            $('#openPrivacy').click(function () {
                $('#privacyModal').modal('show');
            });
        });


// Función genérica para manejar la apertura de un modal
function openModal(modalId, contentId, contentUrl) {
    const modal = document.getElementById(modalId);
    const closeButton = modal.querySelector('.close');
    const checkbox = modal.querySelector('input[type="checkbox"]');
    const continueButton = modal.querySelector('button');

    modal.style.display = "block";

    $.ajax({
        url: contentUrl,
        success: function (data) {
            document.getElementById(contentId).innerHTML = data;
        },
        error: function () {
            document.getElementById(contentId).innerHTML = '<p>Error al cargar el contenido.</p>';
        }
    });

    closeButton.onclick = function () {
        modal.style.display = "none";
    };

    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    checkbox.onchange = function () {
        continueButton.disabled = !checkbox.checked;
    };

    continueButton.onclick = function () {
        modal.style.display = "none";
        alert('Has aceptado los términos.');
    };
}

document.getElementById('openTerms').onclick = function () {
    openModal('termsModal', 'termsContent', '/static/html/terminocondicion.html');
};

document.getElementById('openPrivacy').onclick = function () {
    openModal('privacyModal', 'privacyContent', '/static/html/politicaprivacidad.html');
};
