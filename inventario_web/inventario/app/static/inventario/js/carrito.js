function eliminar_item_lista(id){
    Swal.fire({
        'title':'¿Estas seguro?',
        'text':'esta acción no se puede deshacer',
        'icon':'question',
        'showCancelButton':true,
        'cancelButtonText':'No, cancelar',
        'confirmButtonText':'Si, eliminar',
        'reverseButtons':true,
        'confirmButtonColor':'#dc3545'
    })

    .then(function(result){
        if(result.isConfirmed){
            window.location.href = "/eliminar-item/"+id+"/"
        }
    })
}

function actualizarSubtotal(input) {
    const precio = parseFloat(input.getAttribute('data-precio'));
    const cantidad = parseInt(input.value);
    const subtotal = precio * cantidad;
    const cartItem = input.closest('.cart-item');
    const subtotalElement = cartItem.querySelector('.subtotal');
    subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
    actualizarTotal();
}

function actualizarTotal() {
    let total = 0;
    document.querySelectorAll('.subtotal').forEach(subtotalElement => {
        total += parseFloat(subtotalElement.textContent.replace('$', ''));
    });
    document.getElementById('total-price').textContent = `$${total.toFixed(2)}`;
}