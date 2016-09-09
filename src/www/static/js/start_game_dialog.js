$(document).ready(function(){

  show_dialog_and_fill_values()

  $go_button = $('.go')
  setInterval(limb_go_button(), 130)
  bind_go_button()
  bind_go_key()
  bind_leave_queue_key()

    $('.color_block .ship10').screwDefaultButtons({ 
      image: "url(/static/images/crop/radio_color0.png)", width:   26, height:  24
    });
    $('.color_block .ship20').screwDefaultButtons({ 
      image: "url(/static/images/crop/radio_color1.png)", width:   26, height:  24
    });
    $('.color_block .ship21').screwDefaultButtons({ 
      image: "url(/static/images/crop/radio_color2.png)", width:   26, height:  24
    });
    $('.color_block .ship22').screwDefaultButtons({ 
      image: "url(/static/images/crop/radio_color3.png)", width:   26, height:  24
    });
    $('.color_block .ship30').screwDefaultButtons({ 
      image: "url(/static/images/crop/radio_color4.png)", width:   26, height:  24
    });
    $('.color_block .ship31').screwDefaultButtons({ 
      image: "url(/static/images/crop/radio_color5.png)", width:   26, height:  24
    });
    $('.color_block .ship32').screwDefaultButtons({ 
      image: "url(/static/images/crop/radio_color6.png)", width:   26, height:  24
    });
    $('.weapon input:radio').screwDefaultButtons({ 
      image: "url(/static/images/crop/radio_wearpon.png)", width:   24, height:  24
    });
    $('.color_block input[type=radio]').on('change', function(){
      change_ship_log($(this).val())
    })

    bind_settings_link()
    bind_ship_tab()
})


function limb_go_button(){
  var height = 69
  var max_cnt = 10
  var new_y
  var direction = -1

  function wrapper(){
    if (!$('.startGameDialog').is(":visible")){
      return
    }
    var y = parseInt($go_button.css('background-position').split(' ')[1].replace('%', '').replace('px', ''))
    new_y = y + 69 * direction
    if (new_y < -max_cnt * height || new_y > 0){
      direction *= -1
    }
    new_y = y + 69 * direction
    $go_button.css("background-position",  '0 ' + new_y +'px')
  }
  return wrapper
}



function run_game(){

  $('.key_helper').hide()

  var weapon2, weapon1, ship_type

  $.each($('[name=ship_type]'), function(idx, obj){
    if(obj.checked){
      ship_type = obj.value
    }
  })

  var prefix = ship_type[0]
  $.each($('[name=sh' + prefix+ '_weapon1]'), function(idx, obj){
    if(obj.checked){
      weapon1 = obj.value
    }
  })

  $.each($('[name=sh' + prefix+ '_weapon2]'), function(idx, obj){
    if(obj.checked){
      weapon2 = obj.value
    }
  })

  var name = $('[name=name]')[0].value

  open_socket(function(){
      socket.send(
        ':join:'
        + getCookie('client_pk')
        + ':' + weapon1
        + ':' + weapon2
        + ':' + name
        + ':' + ship_type
      )
      setCookie('last_weapon1', weapon1, {expires: 3600*24*31})
      setCookie('last_weapon2', weapon2, {expires: 3600*24*31})
      setCookie('last_name', name, {expires: 3600*24*31})
      setCookie('last_ship_type', ship_type, {expires: 3600*24*31})
  }) 
}

function bind_leave_queue_key(){
  $('.leave_queue').on('click', function(){
    socket.close()
    erase_client_pk()
    $('.queueBox').hide()
    return false;
  })
}

function bind_go_button(){

  $('body').keydown(function(x){
    if (x.keyCode == 13 && $('.startGameDialog').is(":visible")){ //Enter
        pressGoButton()
        return false
    }
  })

  $('.go').on('click', function(){
    pressGoButton()
    return false
  })
}

function pressGoButton(){
  $('.startGameDialog').hide()
  show_keys_helper()
}

function show_keys_helper(){
  $('.key_helper').show()
  $('.go_key').trigger('focus')
}

function bind_go_key(){
  $('.go_key').on('click', function(){
      run_game()
      return false
  })
}


function change_ship_log(ship_idx){
  $('.ship_icon')
    .removeClass('ship10')
    .removeClass('ship20').removeClass('ship21').removeClass('ship22')
    .removeClass('ship30').removeClass('ship31').removeClass('ship32')
    .addClass('ship' + ship_idx)
}

function bind_ship_tab(){
  $('.ship_tab').on('click', function(){
    show_tab($(this).data('show_cls'))
  })
}

function show_tab(active_cls){
    if (!active_cls){
      return 
    }
    $('.ship_menu')
      .removeClass('ship1')
      .removeClass('ship2')
      .removeClass('ship3')
      .addClass(active_cls)
    $('.ship_block').hide()
    $('.ship_block.'+active_cls).show()
    $('.ship_block.'+active_cls+ ' .color_block input:first').screwDefaultButtons("check")
}

function bind_settings_link(){
  $('.settings').on('click', function(){
    $('.startGameDialog .middle').toggle(200)
    return false
  })
}

function show_dialog_and_fill_values(){

    $('.name_title').remove()
    if (client_pk){
        run_game()
        return
    }
    if ($('.startGameDialog').is(":visible")){
      return 
    }
    
    $('.startGameDialog').show()
    $('.key_helper').hide()

    var last_ship_type = getCookie('last_ship_type')
    if (last_ship_type){
      var active_cls = 'ship' + last_ship_type[0]
    }else{
      var active_cls = 'ship2'
      last_ship_type = '21'
    }
    show_tab(active_cls)
    console.info(last_ship_type)

    change_ship_log(last_ship_type)

    $('.color_block input:radio[value=' + last_ship_type + ']').screwDefaultButtons("check")
    $('.weapon input:radio[name=sh1_weapon1][value='+getCookie('last_weapon1')+']').screwDefaultButtons("check")
    $('.weapon input:radio[name=sh1_weapon2][value='+getCookie('last_weapon2')+']').screwDefaultButtons("check")
    $('.weapon input:radio[name=sh2_weapon1][value='+getCookie('last_weapon1')+']').screwDefaultButtons("check")
    $('.weapon input:radio[name=sh2_weapon2][value='+getCookie('last_weapon2')+']').screwDefaultButtons("check")
    $('.weapon input:radio[name=sh3_weapon1][value='+getCookie('last_weapon1')+']').screwDefaultButtons("check")
    $('.weapon input:radio[name=sh3_weapon2][value='+getCookie('last_weapon2')+']').screwDefaultButtons("check")
    if (getCookie('last_name')){
      $('[name=name]')[0].value = getCookie('last_name')
    }

}


