function eliminar_producto(id){
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
            window.location.href = "/eliminar/"+id+"/"
        }
    })
}