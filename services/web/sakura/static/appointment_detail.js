const href = window.location.href.split('/')
const appointment_id = href[href.length - 1]
const clients_list = document.getElementById('clients_list')
const client_url = clients_list.getAttribute('data-url')
fetch(client_url, {
        method:'GET',
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(response => response.json())
    .then(json => {
        for(const client of json.clients){
            clients_list.innerHTML += '<option value="' + client + '">'
        }
    })


const date = document.getElementById('id_date')
checkbox_status(date.value)
const salon_id = document.getElementById('id_salon')
const send_data = {
    date: date.value,
    salon_id: salon_id.value,
    appointment_id: appointment_id
}
fetch_hairdressers(send_data)
date.addEventListener('input', event =>{
    send_data['date'] = event.target.value
    fetch_hairdressers(send_data)
    checkbox_status(event.target.value)
})
salon_id.addEventListener('change', event =>{
    send_data['salon_id'] = event.target.value
    fetch_hairdressers(send_data)
})


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


function fetch_hairdressers(send_data){
    const hairdresser_select = document.getElementById('id_hairdresser')
    const hairdresser_url = hairdresser_select.parentElement.getAttribute('data-url')
    fetch(hairdresser_url, {
            method: 'POST',
            body: JSON.stringify(send_data),
            headers: {
                'Content-type': 'application/json; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            }
    }).then(response => response.json()).then(json => {
        hairdresser_select.innerHTML = '<option value="">--выберите парикмахера--</option>'
        for(const hairdresser of json.hairdressers){
            let option
            if (hairdresser.id === json.default_hairdresser){
                option = '<option selected="selected" value="' + hairdresser.id + '">' + hairdresser.name + '</option>'
            } else {
                option = '<option value="' + hairdresser.id + '">' + hairdresser.name + '</option>'
            }
            hairdresser_select.innerHTML += option
        }
    })
}



