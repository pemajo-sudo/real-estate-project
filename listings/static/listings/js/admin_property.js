document.addEventListener('DOMContentLoaded', function() {
    function toggleRoomsField() {
        const typeField = document.getElementById('id_property_type');
        if (!typeField) return;

        const typeValue = typeField.value;
        const roomsRow = document.querySelector('.field-number_of_rooms');
        const bathsRow = document.querySelector('.field-number_of_bathrooms');

        if (roomsRow) {
            if (typeValue === 'Land' || typeValue === 'Commercial') {
                roomsRow.style.display = 'none';
            } else {
                roomsRow.style.display = 'block';
            }
        }
        
        if (bathsRow) {
            if (typeValue === 'Land') {
                bathsRow.style.display = 'none';
            } else {
                bathsRow.style.display = 'block';
            }
        }
    }

    const typeField = document.getElementById('id_property_type');
    if (typeField) {
        typeField.addEventListener('change', toggleRoomsField);
        // Call it initially to set correct state
        toggleRoomsField();
    }
});
