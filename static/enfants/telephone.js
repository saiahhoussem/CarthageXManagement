document.addEventListener("DOMContentLoaded", function () {
    const champsTelephone = document.querySelectorAll(
        'input[name="telephone"]'
    );

    champsTelephone.forEach(function (champ) {
        champ.addEventListener("input", function () {
            let valeur = champ.value.replace(/\D/g, "");

            if (valeur.length > 3 && valeur.length <= 6) {
                valeur =
                    valeur.slice(0, 3) +
                    "-" +
                    valeur.slice(3);
            } else if (valeur.length > 6) {
                valeur =
                    valeur.slice(0, 3) +
                    "-" +
                    valeur.slice(3, 6) +
                    "-" +
                    valeur.slice(6, 10);
            }

            champ.value = valeur;
        });
    });
});