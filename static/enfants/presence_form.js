document.addEventListener("DOMContentLoaded", function () {
    const typeSelect = document.getElementById("id_type");
    const dateDebutInput = document.getElementById("id_date");
    const dateFinInput = document.getElementById("id_date_fin");

    if (!typeSelect || !dateDebutInput || !dateFinInput) {
        return;
    }

    function mettreAJourDateFin() {
        const estRetard = typeSelect.value === "retard";

        if (estRetard) {
            // Pour un retard, la date de fin correspond
            // automatiquement à la date de début.
            dateFinInput.value = dateDebutInput.value;
            dateFinInput.disabled = true;
        } else {
            
            dateFinInput.disabled = false;
        }
    }

    typeSelect.addEventListener("change", function () {
        mettreAJourDateFin();
    });

    dateDebutInput.addEventListener("change", function () {
        if (typeSelect.value === "retard") {
            dateFinInput.value = dateDebutInput.value;
        }
    });

    // Pour les formulaires de modification :
    // applique immédiatement l'état correspondant à la valeur existante.
    mettreAJourDateFin();
});