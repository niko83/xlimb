var socket
var ws_id
$(document).ready(function(){
    socket = new WebSocket("ws://192.168.100.4:8080/game_rooms");
    socket.onopen = function() {
      window.onbeforeunload = function() {
        return
      }
    };
    socket.onmessage = function(event) {
      parsing_data(event.data)
    }
    socket.onerror = function(error) {console.info("Ошибка " + error.message)}
    socket.onclose = function(event) {
      if (event.wasClean) { 
        console.log('Соединение закрыто чисто')
      } else {
        console.log('Обрыв соединения')
      }
        console.log('Код: ' + event.code + ' причина: ' + event.reason);
    };
    bindCreateRoom()
})

function bindCreateRoom(){
  $('.create_game_room').on('click', function(){
    sendData('create_game_room', {'title': 'my_new_room'})
    return false
  })
}

function sendData(command, data){
  var json_str = JSON.stringify({
    'command': command,
    'data': data
  })
  socket.send(json_str)
  // console.log('sent:' + json_str)
}

function show_game_rooms(data){
    var container = $('.game_rooms .container')
    container.empty()
    $.each(data, function(idx, d){
      container.append('<strong>'+d.title+'</strong> <a href="/static/client.html?pk='+d.pk+'" class="join_to_game_room" data-pk="'+d.pk+'">join</a><br/>')
    })
}


function show_online(data){
  $('.online').html(data)
}

function parsing_data(msg){
  var obj = jQuery.parseJSON(msg);
  var command = obj.command
  var data = obj.data
  if (command == 'show_game_rooms'){
    show_game_rooms(data)
  }else if (command == 'show_online'){
    show_online(data)
  }else{
    console.info(command)
    console.info(data)
  }
}
