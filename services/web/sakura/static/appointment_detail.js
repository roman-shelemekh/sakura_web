const date = document.getElementById('id_date')
checkbox_status(date.value)
const url = date.parentElement.getAttribute('data-url')
const salon_id = document.getElementById('id_salon')
const clients_list = document.getElementById('clients_list')
const hairdresser_select = document.getElementById('id_hairdresser')
const services_select = document.getElementById('services')

const send_data = {
    date: date.value,
    salon_id: salon_id.value,
    hairdresser_id: hairdresser_select.value
}
fetch_data(initial=true)

date.addEventListener('input', event =>{
    send_data['date'] = event.target.value
    console.log(send_data)
    fetch_data()
    checkbox_status(event.target.value)
})
salon_id.addEventListener('change', event =>{
    send_data['salon_id'] = event.target.value
    console.log(send_data)
    fetch_data()
})
hairdresser_select.addEventListener('change', event =>{
    send_data['hairdresser_id'] = event.target.value
    console.log(send_data)
    fetch_data()
})


function fetch_data(initial=false) {
    send_data['initial'] = initial
    fetch(url, {
        method: 'POST',
        body: JSON.stringify(send_data),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => response.json()).then(json => {
        console.log(json);
        for (const client of json.clients) {
            clients_list.innerHTML += '<option value="' + client + '">'
        }
        hairdresser_select.innerHTML = '<option value="">--выберите парикмахера--</option>'
        for (const hairdresser of json.hairdressers) {
            let option
            if (hairdresser.id === json.default_hairdresser) {
                option = '<option selected="selected" value="' + hairdresser.id + '">' + hairdresser.name + '</option>'
            } else {
                option = '<option value="' + hairdresser.id + '">' + hairdresser.name + '</option>'
            }
            hairdresser_select.innerHTML += option
        }
        services_select.innerHTML = ''
        for (const service of json.services){
            if (initial && json.default_services && json.default_services.includes(service.id)){
                services_select.innerHTML += '<option selected="selected" value="' + service.id + '">' + service.name + '</option>'
            } else {
                services_select.innerHTML += '<option value="' + service.id + '">' + service.name + '</option>'
            }
        }

    })
}

function checkbox_status(date){
    const parsed_date = Date.parse(date)
    const current_date = Date.now()
    const checkbox = document.getElementById('id_accomplished')
    if (parsed_date > current_date){
        checkbox.checked = false
        checkbox.setAttribute('disabled', "")
    } else {
        checkbox.removeAttribute('disabled')
    }
}