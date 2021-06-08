const salon = document.getElementById('selectSalon')


salon.addEventListener('change', e => {
    selectedOption = salon.options.selectedIndex
    window.location = e.target.value
})


function allowDrop(event) {
    if (!event.target.matches('.drop-zone')) return;
    event.preventDefault()
    event.target.classList.add("drop-zone--over")
}

function drag(event) {
    event.dataTransfer.setData("text", event.target.id)
}

function leave(event) {
    event.target.classList.remove("drop-zone--over")
}

function drop(event) {
    event.preventDefault()
    const elementToDropId = event.dataTransfer.getData("text")
    const elementToDrop = document.getElementById(elementToDropId).cloneNode(true)
    elementToDrop.draggable = false
    elementToDrop.id = null
    elementToDrop.querySelector('.card-body').innerHTML += '<button type="button" class="btn-close float-end" aria-label="Close"></button>'
    event.target.appendChild(elementToDrop)
    event.target.classList.remove("drop-zone--over")
}

