
const botonIncrementar = document.querySelectorAll('.incrementar');
const botonDisminuir = document.querySelectorAll('.disminuir');

botonIncrementar.forEach(boton => { 
    boton.addEventListener('click', () => { 
        const id = boton.getAttribute('data-id'); 
        const parrafo = document.getElementById(`contador-${id}`); 
        let contador = parseInt(parrafo.textContent);
         
        if(contador < 10 || contador > 0 && contador < 10){
            contador++;
            parrafo.textContent = contador;
            parrafo.removeAttribute('hidden');
        }
    }); 
});

botonDisminuir.forEach(boton => { 
    boton.addEventListener('click', () => { 
        const id = boton.getAttribute('data-id'); 
        const parrafo = document.getElementById(`contador-${id}`); 
        let contador = parseInt(parrafo.textContent); 
         
        if(contador > 0){
            contador--;
            parrafo.textContent = contador;

            if(contador == 0){
                parrafo.setAttribute('hidden', 'true');
            }
        }
    }); 
});
