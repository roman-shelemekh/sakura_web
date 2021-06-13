
const salon = document.getElementById('selectSalon')

salon.addEventListener('change', e => {
    const selectedOption = salon.options.selectedIndex
    window.location = e.target.value
})

function allowDrop(event) {
    if (!event.target.matches('.drop-zone')) return;
    event.preventDefault()
    event.target.parentElement.classList.add("table-light")
}

function drag(event) {
    event.dataTransfer.setData("text", event.target.id)
}

function leave(event) {
    event.target.parentElement.classList.remove("table-light")
}

function drop(event) {
    const [salon_id, hairdresser_id, date, elementToDrop] = dropPrep(event)
    const url = '/admin/schedule/add'
    postShift(salon_id, hairdresser_id, date, url)
        .then(json => {
            if (json.success){
                event.target.parentElement.querySelector('.drop-target').appendChild(elementToDrop)
            } else {
                var toastElList = [].slice.call(document.querySelectorAll('.toast'))
                var toastList = toastElList.map(function(toastEl) {
                  return new bootstrap.Toast(toastEl)
                })
                toastList.forEach(toast => {
                    toast.show()
                })
            }
        })
}

function adjacentDrop(event){
    const [salon_id, hairdresser_id, date, elementToDrop] = dropPrep(event)
    const url = '/admin/schedule/add'
    postShift(salon_id, hairdresser_id, date, url)
        .then(json => {
            if (json.success){
                event.target.parentElement.querySelector('.drop-target').appendChild(elementToDrop)
            } else {
                var toastElList = [].slice.call(document.querySelectorAll('.toast'))
                var toastList = toastElList.map(function(toastEl) {
                  return new bootstrap.Toast(toastEl)
                })
                toastList.forEach(toast => {
                    toast.show()
                })
            }
        })
}

function deleteHairdresser(event){
    const elementToDelete = event.target.parentElement.parentElement
    const salon_id = elementToDelete.getAttribute('data-salon')
    const hairdresser_id = elementToDelete.getAttribute('data-hairdresser')
    const date = elementToDelete.parentElement.parentElement.querySelector('b').innerText
    elementToDelete.remove()
    const url = '/admin/schedule/delete'
    postShift(salon_id, hairdresser_id, date,url)
}

function postShift(salon_id, hairdresser_id, date, url){
    const data = {
        salon_id: salon_id,
        hairdresser_id: hairdresser_id,
        date: date
    }
    return fetch(url, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-type': 'application/json; charset=UTF-8'
        }
    }).then(response => response.json())
}

function dropPrep(event){
    event.preventDefault()
    event.target.parentElement.classList.remove("table-light")
    const elementToDrop = document.getElementById(event.dataTransfer.getData("text")).cloneNode(true)
    elementToDrop.draggable = false
    elementToDrop.id = ''
    elementToDrop.querySelector('.card-body').innerHTML += '<button onclick="deleteHairdresser(event)" type="button" class="btn-close float-end" aria-label="Close"></button>'
    const salon_id = elementToDrop.getAttribute('data-salon')
    const hairdresser_id = elementToDrop.getAttribute('data-hairdresser')
    const date = event.target.parentElement.querySelector('b').innerText
    return [salon_id, hairdresser_id, date, elementToDrop]
}