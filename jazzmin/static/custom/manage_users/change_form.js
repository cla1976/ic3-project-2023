$('#userprofile_form').on('submit', function(e) {
    let seleccionTipoUsuario = $('#id_user_type').find('option:selected').text();
    console.log(seleccionTipoUsuario);
    if (seleccionTipoUsuario == 'Alumno') {
        let puertaProxima = $('#id_userprofilestudent-0-door_right').val();
        let puertaNumero = $('#id_userprofilestudent-0-doorNo').val();
        let confHorario = $('#id_userprofilestudent-0-time_type').val();

        if (!puertaProxima || !puertaNumero || !confHorario) {
            alert('Se deben completar los campos requeridos de la sección: Alumno');
            e.preventDefault();
        }

    }
    if (seleccionTipoUsuario == 'Mantenimiento') {
        let domingo = $('#id_userprofilemaintenance-0-sunday').val();
        let lunes = $('#id_userprofilemaintenance-0-monday').val();
        let martes = $('#id_userprofilemaintenance-0-tuesday').val();
        let miercoles = $('#id_userprofilemaintenance-0-wednesday').val();
        let jueves = $('#id_userprofilemaintenance-0-thursday').val();
        let viernes = $('#id_userprofilemaintenance-0-friday').val();
        let sabado = $('#id_userprofilemaintenance-0-saturday').val();
        const dias = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']; 

        if (!domingo || !lunes || !martes || !miercoles || !jueves || !viernes || !sabado) {
            alert('Se deben completar los campos requeridos de la sección: Personal de mantenimiento');
            e.preventDefault();
        }

        dias.forEach(function(dia) {
            if (dia == 'Sí') {
                let horaInicio = $(`id_userprofilemaintenance-0-${dias[dia]}_time_begin`);
                let horaFin = $(`id_userprofilemaintenance-0-${dias[dia]}_time_end`);
                if (!horaInicio || !horaFin) {
                    alert(`Se deben completar los campos de horario del día ${dias[dia]}`);
                    e.preventDefault(); 
                }
            }
        });
    }
});


let elementos = $('.card-default');
let seleccionHorariosValidez = $('#id_is_active').find('option:selected').text();
let seleccionTipoUsuario = $('#id_user_type').find('option:selected').text();

$('#alumnos-tab').parent('.card-default').hide();
$('#personal-de-mantenimientos-tab').parent('.card-default').hide();

if (seleccionTipoUsuario == 'Alumno') {
    $('#alumnos-tab').parent('.card-default').show();
    $('#personal-de-mantenimientos-tab').parent('.card-default').hide();
}
else if (seleccionTipoUsuario == 'Mantenimiento') {
    $('#alumnos-tab').parent('.card-default').hide();
    $('#personal-de-mantenimientos-tab').parent('.card-default').show();
}
else {
    $('#alumnos-tab').parent('.card-default').hide();
    $('#personal-de-mantenimientos-tab').parent('.card-default').hide();
}

if (seleccionHorariosValidez == 'Sí') {
    $('.field-begin_time').show();
    $('.field-end_time').show();    
}
else {
    $('.field-begin_time').hide();
    $('.field-end_time').hide();
}

$('#id_is_active').change(function() {
    seleccionHorariosValidez = $(this).find('option:selected').text();
    if (seleccionHorariosValidez == 'Sí'){
        $('.field-begin_time').css("display", "block");
        $('.field-end_time').css("display", "block");
    }
    else {
        $('.field-begin_time').css("display", "none");
        $('.field-end_time').css("display", "none");
    }
});

$("#id_user_type").change(function() {
    let seleccionTipoUsuario = $('#id_user_type').find('option:selected').text();
    if (seleccionTipoUsuario == 'Alumno') { 
        elementos.each(function() {
            if ($(this).find('#alumnos-tab').length) {
                $(this).css("display", "block");
            }
            else if ($(this).find('#personal-de-mantenimientos-tab').length) {
                $(this).css("display", "none");
            }
        });
    } 
    else if (seleccionTipoUsuario == 'Mantenimiento') { 
        elementos.each(function() {
            if ($(this).find('#alumnos-tab').length) {
                $(this).css("display", "none");
            }
            else if ($(this).find('#personal-de-mantenimientos-tab').length) {
                $(this).css("display", "block");
            }
        });
        $('.field-sunday_time_begin').hide();
        $('.field-sunday_time_end').hide();
        $('.field-monday_time_begin').hide();
        $('.field-monday_time_end').hide();
        $('.field-tuesday_time_begin').hide();
        $('.field-tuesday_time_end').hide();
        $('.field-wednesday_time_begin').hide();
        $('.field-wednesday_time_end').hide();
        $('.field-thursday_time_begin').hide();
        $('.field-thursday_time_end').hide();
        $('.field-friday_time_begin').hide();
        $('.field-friday_time_end').hide();
        $('.field-saturday_time_begin').hide();
        $('.field-saturday_time_end').hide();
        $("#id_userprofilemaintenance-0-sunday").change(function() {
            let textoDomingo = $(this).find('option:selected').text();
            if (textoDomingo == 'Sí') {
                $(".field-sunday_time_begin").css("display", "block");
                $(".field-sunday_time_end").css("display", "block");
            }
            else {
                $(".field-sunday_time_begin").css("display", "none");
                $(".field-sunday_time_end").css("display", "none");
            }
        });
        $("#id_userprofilemaintenance-0-monday").change(function() {
            let textolunes = $(this).find('option:selected').text();
            if (textolunes == 'Sí') {
                $(".field-monday_time_begin").css("display", "block");
                $(".field-monday_time_end").css("display", "block");
            }
            else {
                $(".field-monday_time_begin").css("display", "none");
                $(".field-monday_time_end").css("display", "none");
            }
        });
        $("#id_userprofilemaintenance-0-tuesday").change(function() {
            let textoMartes = $(this).find('option:selected').text();
            if (textoMartes == 'Sí') {
                $(".field-tuesday_time_begin").css("display", "block");
                $(".field-tuesday_time_end").css("display", "block");
            }
            else {
                $(".field-tuesday_time_begin").css("display", "none");
                $(".field-tuesday_time_end").css("display", "none");
            }
        });
        $("#id_userprofilemaintenance-0-wednesday").change(function() {
            let textoMiercoles = $(this).find('option:selected').text();
            if (textoMiercoles == 'Sí') {
                $(".field-wednesday_time_begin").css("display", "block");
                $(".field-wednesday_time_end").css("display", "block");
            }
            else {
                $(".field-wednesday_time_begin").css("display", "none");
                $(".field-wednesday_time_end").css("display", "none");
            }
        });
        $("#id_userprofilemaintenance-0-thursday").change(function() {
            let textoJueves = $(this).find('option:selected').text();
            if (textoJueves == 'Sí') {
                $(".field-thursday_time_begin").css("display", "block");
                $(".field-thursday_time_end").css("display", "block");
            }
            else {
                $(".field-thursday_time_begin").css("display", "none");
                $(".field-thursday_time_end").css("display", "none");
            }
        });
        $("#id_userprofilemaintenance-0-friday").change(function() {
            let textoViernes = $(this).find('option:selected').text();
            if (textoViernes == 'Sí') {
                $(".field-friday_time_begin").css("display", "block");
                $(".field-friday_time_end").css("display", "block");
            }
            else {
                $(".field-friday_time_begin").css("display", "none");
                $(".field-friday_time_end").css("display", "none");
            }
        });
        $("#id_userprofilemaintenance-0-saturday").change(function() {
            let textoSabado = $(this).find('option:selected').text();
            if (textoSabado == 'Sí') {
                $(".field-saturday_time_begin").css("display", "block");
                $(".field-saturday_time_end").css("display", "block");
            }
            else {
                $(".field-saturday_time_begin").css("display", "none");
                $(".field-saturday_time_end").css("display", "none");
            }
        });
    }
    else {
        elementos.each(function() {
            if ($(this).find('#personal-de-mantenimientos-tab').length || $(this).find('#alumnos-tab').length) {
                $(this).css("display", "none");
            }
        });
    }
});