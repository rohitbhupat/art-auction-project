document.addEventListener('DOMContentLoaded', function() {
    var dimensionUnitField = document.querySelector('#id_dimension_unit');
    var lengthInCentimetersField = document.querySelector('#id_length_in_centimeters').closest('.form-row');
    var widthInCentimetersField = document.querySelector('#id_width_in_centimeters').closest('.form-row');
    var footField = document.querySelector('#id_foot').closest('.form-row');
    var inchesField = document.querySelector('#id_inches').closest('.form-row');

    function toggleDimensionFields() {
        var selectedUnit = dimensionUnitField.value;
        if (selectedUnit === 'cm') {
            lengthInCentimetersField.style.display = '';
            widthInCentimetersField.style.display = '';
            footField.style.display = 'none';
            inchesField.style.display = 'none';
        } else if (selectedUnit === 'ft') {
            lengthInCentimetersField.style.display = 'none';
            widthInCentimetersField.style.display = 'none';
            footField.style.display = '';
            inchesField.style.display = '';
        }
    }

    dimensionUnitField.addEventListener('change', toggleDimensionFields);

    // Initial call to set the correct fields based on the current selection
    toggleDimensionFields();
});
