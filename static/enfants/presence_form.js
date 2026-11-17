document.addEventListener("DOMContentLoaded", function () {
    const typeSelect = document.getElementById("id_type");
    const dateDebutInput = document.getElementById("id_date");
    const dateFinInput = document.getElementById("id_date_fin");
    const heureFinInput = document.getElementById("id_heure_fin");

    const conteneurDateFin =
        document.getElementById("conteneur-date-fin");

    const conteneurHeureFin =
        document.getElementById("conteneur-heure-fin");

    if (
        !typeSelect
        || !dateDebutInput
        || !dateFinInput
        || !heureFinInput
        || !conteneurDateFin
        || !conteneurHeureFin
    ) {
        return;
    }

    function mettreAJourChamps() {
        const estRetard = typeSelect.value === "retard";

        if (estRetard) {
            dateFinInput.value = dateDebutInput.value;
            dateFinInput.disabled = true;

            conteneurDateFin.classList.add("d-none");
            conteneurHeureFin.classList.remove("d-none");

            heureFinInput.disabled = false;
        } else {
            dateFinInput.disabled = false;

            conteneurDateFin.classList.remove("d-none");
            conteneurHeureFin.classList.add("d-none");

            heureFinInput.value = "";
            heureFinInput.disabled = true;
        }
    }

    typeSelect.addEventListener("change", function () {
        mettreAJourChamps();
    });

    dateDebutInput.addEventListener("change", function () {
        if (typeSelect.value === "retard") {
            dateFinInput.value = dateDebutInput.value;
        }
    });

    mettreAJourChamps();
});
