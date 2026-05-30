// Ajoute Select2 sur tous les <select> de la nomenclature dans les bons et le grand livre
function activateSelect2() {
    $("select[name^='line_material_']").each(function() {
        if (!$(this).hasClass('select2-hidden-accessible')) {
            $(this).select2({
                width: 'resolve',
                placeholder: 'Rechercher un compte...',
                allowClear: true
            });
        }
    });
    $("#material").select2({
        width: 'resolve',
        placeholder: 'Rechercher un compte...',
        allowClear: true
    });
}

$(document).ready(function() {
    activateSelect2();
    // Pour les lignes ajoutées dynamiquement dans le bon
    $(document).on('click', '#add-line-btn', function() {
        setTimeout(activateSelect2, 100); // Laisse le temps au DOM d'ajouter la ligne
    });
});
