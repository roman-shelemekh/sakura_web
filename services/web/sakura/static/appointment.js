const salon = document.getElementById('selectSalon')

salon.addEventListener('change', e => {
    const selectedOption = salon.options.selectedIndex
    window.location = e.target.value
})