const date = document.getElementById('id_date')
checkbox_status(date.value)
const url = date.parentElement.getAttribute('data-url')
const salon_id = document.getElementById('id_salon')
const clients_list = document.getElementById('clients_list')
const clients_url = clients_list.getAttribute('data-url')
const client_data_url = clients_list.parentElement.getAttribute('data-url')
const add_client = document.getElementById('add_client')
const inicial_href = add_client.href
const hairdresser_select = document.getElementById('id_hairdresser')
const services_select = document.getElementById('services')
const client_input = document.getElementById('id_client')
const client_data = document.getElementById('client_data')

const send_data = {
    date: date.value,
    salon_id: salon_id.value,
    hairdresser_id: hairdresser_select.value
}

fetch_data()

date.addEventListener('input', event =>{
    send_data['date'] = event.target.value
    fetch_data()
    checkbox_status(event.target.value)
})
salon_id.addEventListener('change', event =>{
    send_data['salon_id'] = event.target.value
    fetch_data()
})
hairdresser_select.addEventListener('change', event =>{
    send_data['hairdresser_id'] = event.target.value
    fetch_data()
})
client_input.addEventListener('focus', event =>{
    fetch_clients()
    fetch_client_data(event.target.value)
})
client_input.addEventListener('change', event =>{
    fetch_client_data(event.target.value)
    add_client.href = inicial_href + '?phone_number=' + event.target.value
})


function fetch_data() {
    fetch(url, {
        method: 'POST',
        body: JSON.stringify(send_data),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => response.json()).then(json => {
        hairdresser_select.innerHTML = '<option value="">--выберите парикмахера--</option>'
        if (json.hairdressers){
            for (const hairdresser of json.hairdressers) {
                let option
                if (hairdresser.id === json.default_hairdresser) {
                    option = '<option selected="selected" value="' + hairdresser.id + '">' + hairdresser.name + '</option>'
                } else {
                    option = '<option value="' + hairdresser.id + '">' + hairdresser.name + '</option>'
                }
                hairdresser_select.innerHTML += option
            }
        }
        services_select.innerHTML = ''
        for (const service of json.services){
            services_select.innerHTML += '<option value="' + service.id + '">' + service.name + '</option>'
        }
    })
}

function fetch_clients(){
    fetch(clients_url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => response.json()).then(json => {
        clients_list.innerHTML = ''
        for (const client of json.clients) {
            clients_list.innerHTML += '<option value="' + client + '">'
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

function fetch_client_data(phone_number){
    fetch(client_data_url, {
        method: 'POST',
        body: JSON.stringify({phone_number: phone_number}),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => response.json()).then(json => {
        if (json.client){
            client_data.href = '/admin/client/' + json.client
            client_data.classList.remove('disabled')
            add_client.classList.add('disabled')
        } else {
            client_data.classList.add('disabled')
            add_client.classList.remove('disabled')
        }
    })
}