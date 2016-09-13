var socket
var ship_pk
var client_pk = getCookie('client_pk')


control = {
  accelerator: 0,
  vector: 0,
  shot: 0,
  shot2: 0
}
has_correction_counter = 0

viewport = {x: 0, y: 0, time: new Date().getTime()}
before_viewport = {x: 0, y: 0, time: new Date().getTime()} 

names = Array()

function getDPI() {
  return document.getElementById("dpi").offsetHeight;
}

function copy_array(arr){
  var newArr = Array(arr.length)
  $.each(arr, function(idx, data){
    newArr[idx] = data.slice()
  })
  return newArr
}

function erase_client_pk(){
    deleteCookie('client_pk')
    client_pk = ''
    stop_draw_frame()
}

;(function() {
    var lastTime = 0;
    var vendors = ['ms', 'moz', 'webkit', 'o'];
    for(var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
        window.requestAnimationFrame = window[vendors[x]+'RequestAnimationFrame'];
        window.cancelAnimationFrame = window[vendors[x]+'CancelAnimationFrame'] 
                                   || window[vendors[x]+'CancelRequestAnimationFrame'];
    }
    if (!window.requestAnimationFrame)
        window.requestAnimationFrame = function(callback, element) {
            var currTime = new Date().getTime();
            var timeToCall = Math.max(0, 16 - (currTime - lastTime));
            var id = window.setTimeout(function() { callback(currTime + timeToCall); }, 
              timeToCall);
            lastTime = currTime + timeToCall;
            return id;
        };
    if (!window.cancelAnimationFrame)
        window.cancelAnimationFrame = function(id) {
            clearTimeout(id);
        };
}());


$(document).ready(function(){
    canvas=document.getElementById("draw");
    $canvas=$("#draw");
    $infopanel_health = $('.health')
    $infopanel_bullet1 = $('.bullet1')
    $infopanel_bullet2 = $('.bullet2')
    $infopanel_fuel = $('.fuel')
    $warning_ping = $('.warning_ping')
    $warning_ping_counter = $('.warning_ping .counter')

    $players = $('.players')
    $canvas_wrapper = $('.canvas_wrapper')
    WebGL2D.enable(canvas)
    ctx = canvas.getContext("webgl-2d"); 
    field = [1077, 662];
    ctx.fillStyle = '#000'
    ctx.fillRect(0, 0, field[0], field[1])
    preloader = getPreloader({
      "bckg": "/static/images/background.jpg",
      // "bckg": "/static/images/background_bot.png",
      "health": "/static/images/health_color.png",
      "fuel": "/static/images/fuel.png",
      "bullet1": "/static/images/bullet1.png",
      "bullet2": "/static/images/bullet2.png",
      "ship1": "/static/images/ship1_color.png",
      "ship2": "/static/images/ship2_color.png",
      "ship3": "/static/images/ship3_color.png",
      "ship_implode": "/static/images/implode.png",
      "immortal": "/static/images/immortal.png",

      "noname1": "/static/images/crop/footer.png",
      "noname2": "/static/images/crop/panel.png",
      "noname3": "/static/images/crop/radio_color0.png",
      "noname4": "/static/images/crop/radio_color1.png",
      "noname5": "/static/images/crop/radio_color2.png",
      "noname6": "/static/images/crop/radio_color3.png",
      "noname7": "/static/images/crop/radio_color4.png",
      "noname8": "/static/images/crop/radio_color5.png",
      "noname9": "/static/images/crop/radio_color6.png",
      "noname10": "/static/images/crop/radio_wearpon.png",
      "noname11": "/static/images/crop/settings.png",
      "noname12": "/static/images/crop/ships.png"
    }, start_fake_observer)
})

fake_observer_iteration = Math.random() * 2 * Math.PI
requestID_observer = undefined

observer_start = undefined
observer_x = 0
observer_y = 0
function start_fake_observer(){
    fake_observer_iteration+=0.004;
    observer_x = Math.sin(fake_observer_iteration)*field[0]*0.9 - field[0]
    observer_y = Math.cos(fake_observer_iteration)*field[1]*0.8 - field[1]
    if (!observer_start){
      observer_start = Date.now()
    }

    ctx.drawImage(preloader.images.bckg, observer_x, observer_y);

    requestID_observer = requestAnimationFrame(start_fake_observer)
}

function stop_fake_observer(callback){
    cancelAnimationFrame(requestID_observer)
    requestID_observer = undefined
    callback()
    // if (window.ga && observer_start){
        // ga('send', 'observer', 'run', 'sec', parseInt((Date.now() - observer_start)/1000), {nonInteraction: true});
    // }
    observer_start = undefined
}

requestID_game = undefined
function stop_draw_frame(){
    cancelAnimationFrame(requestID_game)
    requestID_game = undefined
}

function getPreloader(data, callback){
  var cnt = 0
  var obj = {
    images: {}
  }
  $.each(data, function(name, path){
      obj.images[name] = new Image()
      obj.images[name].onload = function(A){
        cnt -= 1
        if(cnt == 0){
           callback()
        }
      }
      obj.images[name].src = path
      cnt += 1
  })
  return obj
}

connecting_interval = null
function open_socket(callback){
   if (socket && socket.readyState==socket.OPEN){
      callback()
      return
   }
    $('.connecting').empty()

    var connecting_interval = setTimeout(function(){
        $('.connecting').show().text('Connecting... ')
    }, 100)

    socket = new WebSocket("ws://"+document.domain+"/ws/");
    socket.binaryType = 'arraybuffer';
    socket.onopen = function() {
      callback()
      clearInterval(connecting_interval)
      $('.connecting').hide()
      bindKeys()
    };
    socket.onmessage = function(event) {
      clearInterval(connecting_interval)
      parsing_data(event.data)
    }
    socket.onerror = function(event) {
      clearInterval(connecting_interval)
      var reason
      if (event.code == 1000){
          reason = "Normal closure, meaning that the purpose for which the connection was established has been fulfilled.";
      }else if(event.code == 1001){
          reason = "An endpoint is \"going away\", such as a server going down or a browser having navigated away from a page.";
      }else if(event.code == 1002){
          reason = "An endpoint is terminating the connection due to a protocol error";
      }else if(event.code == 1003){
          reason = "An endpoint is terminating the connection because it has received a type of data it cannot accept (e.g., an endpoint that understands only text data MAY send this if it receives a binary message).";
      }else if(event.code == 1004){
          reason = "Reserved. The specific meaning might be defined in the future.";
      }else if(event.code == 1005){
          reason = "No status code was actually present.";
      }else if(event.code == 1006){
          reason = "The connection was closed abnormally, e.g., without sending or receiving a Close control frame";
      }else if(event.code == 1007){
          reason = "An endpoint is terminating the connection because it has received data within a message that was not consistent with the type of the message (e.g., non-UTF-8 [http://tools.ietf.org/html/rfc3629] data within a text message).";
      }else if(event.code == 1008){
          reason = "An endpoint is terminating the connection because it has received a message that \"violates its policy\". This reason is given either if there is no other sutible reason, or if there is a need to hide specific details about the policy.";
      }else if(event.code == 1009){
          reason = "An endpoint is terminating the connection because it has received a message that is too big for it to process.";
      }else if(event.code == 1010){ // Note that this status code is not used by the server, because it can fail the WebSocket handshake instead
          reason = "An endpoint (client) is terminating the connection because it has expected the server to negotiate one or more extension, but the server didn't return them in the response message of the WebSocket handshake. <br /> Specifically, the extensions that are needed are: " + event.reason;
      }else if(event.code == 1011){
          reason = "A server is terminating the connection because it encountered an unexpected condition that prevented it from fulfilling the request.";
      }else if(event.code == 1015){
          reason = "The connection was closed due to a failure to perform a TLS handshake (e.g., the server certificate can't be verified).";
      }else{
          reason = "Unknown reason";
      }
      $('.connecting').html('Connecting error, Code: <b>' + event.code + '</b>. Reason: <b>' + reason + '</b>').show()
      stop_draw_frame()
    }
    socket.onclose = function(event) {
      if (!requestID_observer){
        start_fake_observer()
      }
      stop_draw_frame()
      show_dialog_and_fill_values()
    }
}

function set_color(obj, value, edge){
  obj.removeClass('little')
  obj.removeClass('middle')
  obj.removeClass('alot')
  obj.removeClass('no_one')

  if(value >= edge[1]){
    obj.addClass('alot')
  }else if(value >= edge[0]){
    obj.addClass('middle')
  }else if(value > 0){ 
    obj.addClass('little')
  }else {
    obj.addClass('no_one')
  }
  obj.html(value)
}


counter_frames = 0

function drawShip(data, has_correction){
  var count_frames = 19

  if (has_correction){
      diff_x_tmp = diff_y_tmp = 0
  }else{
      diff_x_tmp = diff_x
      diff_y_tmp = diff_y
  }

  var x = data[2] + diff_x_tmp
  var y = data[3] + diff_y_tmp

  if (data[5] > 0){
    var img = preloader.images.ship_implode
    var src_x = (data[5]-1) % 5
    var src_y = (data[5]-1 - src_x) / 5
    src_x = src_x * 50
    src_y = src_y * 50
    var size = [50, 50]
    var angle_rotate = 0
  }else{
    var angle_rotate = -(data[4]/100)
    if(data[6]<20){
      var size = [61, 65]
      var img = preloader.images.ship1
      src_y = 0
    }else if(data[6]<30){
      var size = [61, 108]
      var img = preloader.images.ship2
      var src_y = -3
    }else if(data[6]<40){
      var count_frames = 21
      var size = [61, 96]
      var img = preloader.images.ship3
      var src_y = 0
    }
    var src_x = size[0] * (data[6] % 10)
    src_y += size[1]*9 + data[1] * size[1]
  }
  ctx.save()
  ctx.translate(x, y)
  ctx.rotate(angle_rotate)

  if(data[8]){
    ctx.drawImage(
      preloader.images['immortal'], 
      0, 0,
      80, 80,
      -40, -40,
      80, 80
    )
  }

  ctx.drawImage(
    img,
    src_x, src_y,
    size[0], size[1],
    -size[0]/2,
    -size[1]/2,
    size[0], 
    size[1]
  )
  ctx.restore()
}


function drawBonus(bonus_data){
  var x = bonus_data[0] + diff_x
  var y = bonus_data[1] + diff_y 
  var type = bonus_data[2]

  var bonus_prop = {
      100: {count_frames: 16, size: [50, 59], img: 'fuel', offset: 0},
      200: {count_frames: 18, size: [45, 46], img: 'health', offset: 0},
      220: {count_frames: 18, size: [45, 46], img: 'health', offset: 1},
      250: {count_frames: 18, size: [45, 46], img: 'health', offset: 2},
      300: {count_frames: 18, size: [50, 54], img: 'bullet1', offset: 0},
      400: {count_frames: 18, size: [50, 54], img: 'bullet2', offset: 0}
  }
  var bonus = bonus_prop[type]
  var max_zoom = 1.2
  var new_size = 1 + 0.05 * Math.cos((counter_frames/3 % bonus.count_frames) / bonus.count_frames * 4 * Math.PI)
  var position = 3 * Math.cos((counter_frames/7 % bonus.count_frames) / bonus.count_frames * 4 * Math.PI) 

  ctx.drawImage(
    preloader.images[bonus.img], 
   (counter_frames % bonus.count_frames) * bonus.size[0], 
    bonus.size[1] * bonus.offset,
    bonus.size[0],
    bonus.size[1], 
    x - (bonus.size[0] * new_size)/2, 
    y - (bonus.size[1] * new_size)/2 + position,
    bonus.size[0] * new_size, 
    bonus.size[1] * new_size
  )
}


diff_x=0
diff_y=0
function draw_frame(){

    if (observer_x && observer_y){
        if( 
          Math.abs(observer_x - viewport.x) < 20 
          && Math.abs(observer_y - viewport.y) < 20
        ){
            var x=viewport.x
            var y=viewport.y
            diff_x_observer = diff_y_observer = 0
            observer_y = observer_x = undefined
        }else{
          var x = observer_x = observer_x + (viewport.x - observer_x) * 0.15
          var y = observer_y = observer_y + (viewport.y - observer_y) * 0.15
          diff_x_observer = observer_x - viewport.x
          diff_y_observer = observer_y - viewport.y
        }
    }

  counter_frames++;

  var has_correction = false
  if (diff_x_observer == 0){
    var now = new Date().getTime() 
    if (now - viewport.time > 20){
      var diff = viewport.time - before_viewport.time
      if (diff > 5){
        // console.info('=====')
        // console.info(before_viewport.x, viewport.x)
        // console.info(before_viewport.y, viewport.y)
        // console.info(diff)
        var x_speed = (viewport.x - before_viewport.x)/diff
        var y_speed = (viewport.y - before_viewport.y)/diff
        var diff = now - viewport.time
        diff_x = diff * x_speed
        diff_y = diff * y_speed
        has_correction |= true
      }else{
          diff_x = diff_y = 0
      }
    }else{
      diff_x = diff_y = 0
    }
  }else{
    diff_x = diff_x_observer
    diff_y = diff_y_observer
  }
  if(has_correction){
      has_correction_counter++;
  }

  var ships_gl_tmp = copy_array(ships_gl)

  if (diff_x_observer == 0){
    if (now - ships_gl_time > 20){
      if (before_ships_gl.length == ships_gl.length){
        var diff = ships_gl_time - before_ships_gl_time

        if (diff > 5){
          has_correction |= true
        // console.info("---")
        // console.info(before_ships_gl[0])
        // console.info(ships_gl[0])
          $.each(ships_gl, function(idx, ship){
            if (ship[0] == before_ships_gl[idx][0]){
              $.each(ship, function(idx_attr, val){
                var speed = (val - before_ships_gl[idx][idx_attr])/diff
                var current_diff = now - ships_gl_time 
                ships_gl_tmp[idx][idx_attr] = (ships_gl[idx][idx_attr] + current_diff * speed)
                if(idx_attr == 4 && ships_gl_tmp[idx][idx_attr] < 0){
                    ships_gl_tmp[idx][idx_attr] += 628 // 2 Pi * 100
                }
                if(idx_attr == 4 && ships_gl_tmp[idx][idx_attr] > 628){
                    ships_gl_tmp[idx][idx_attr] -= 628 // 2 Pi * 100
                }
              })
            }else{
              // console.info('ship_id not same')
            }
          })
        }
        // console.info(ships_gl_tmp[0])
      }else{
          // console.info('ship_id lenght not same')
      }
    }
  }

  if(has_correction){
    $warning_ping.show()
    $warning_ping_counter.html(has_correction_counter)
    setTimeout(function(){
      $warning_ping.hide()
    }, 500)
  }

  ctx.drawImage(preloader.images.bckg, viewport.x + diff_x, viewport.y +  diff_y);
  // $.each(polygons, function(id, polygon){
      // ctx.fillStyle = "rgba(255, 255, 255, 0.3)";
      // ctx.beginPath();
      // ctx.moveTo(polygon[0], polygon[1])
      // for(var i=0; i < polygon.length; i+=2){
        // ctx.lineTo(parseFloat(polygon[i]), parseFloat(polygon[i+1]))
      // }
      // ctx.closePath();
      // ctx.fill();
  // })

  $.each(bonuses_gl, function(id, bonus){
    drawBonus(bonus)
  })

  var counter = 0
  var fireColor = [ 
    '#520900', '#520900', 
    '#e24500', '#e24500', '#e24500',  '#e24500',  
    '#fe8d50', 
    '#ffee98', 
  ]
  $.each(bullets, function(id, bullet){
      if (bullet[2] == 0){
        ;++counter
        ctx.fillStyle = fireColor[counter % fireColor.length] 
        ctx.fillRect(bullet[0] + diff_x, bullet[1] + diff_y, 1.6, 1.6)
      } else {
        ctx.fillStyle = '#eee'
        ctx.fillRect(bullet[0] + diff_x, bullet[1] + diff_y, bullet[2]*0.2, bullet[2]*0.2)
      }
  })


  $.each(ships_gl_tmp, function(id, ship){

    if (has_correction){
        diff_x_tmp = diff_y_tmp = 0
    }else{
        diff_x_tmp = diff_x
        diff_y_tmp = diff_y
    }

    if (ship[5] == -1){
      var x = ship[2] + diff_x_tmp
      var y = ship[3] + diff_y_tmp
      var weight = ship[7]%100

      if(ship[7] < 30){
        var colors = ['#f00', '#700', '#300']
      } else if(ship[7] < 50){
        var colors = ['#ff0', '#770', '#330']
      } else {
        var colors = ['#0f0', '#070', '#030']
      }

      ctx.fillStyle = colors[0]
      ctx.fillRect(x-weight/2, y-36, weight, 1)
      ctx.fillStyle = colors[1] 
      ctx.fillRect(x-weight/2, y-35, weight, 1)
      ctx.fillStyle = colors[2] 
      ctx.fillRect(x-weight/2, y-34, weight, 1)

      var count_star = Math.floor(ship[7]/100)
      ctx.fillStyle = '#070'
      var first = (count_star * 3 + (count_star - 1)*3) /2
      while(count_star>0){
        ctx.fillRect(x+first-count_star*3-(count_star-1)*3, y+45, 3, 3)
        count_star--;
      }
    }
  })

  $.each(ships_gl_tmp, function(id, ship){
      drawShip(ship, has_correction)
  })

  requestID_game = requestAnimationFrame(draw_frame)
}

draw_objects = {}
ships_gl = []
ships_gl_time = new Date().getTime()
before_ships_gl = []
before_ships_gl_time = null
polygons = []
bullets = []
bonuses_gl = []
function parsing_plain(msg){

    if(msg.search('ship_infos') > -1){
      $players.empty()
      $('.name_title').remove()
      names = Array()
    }else{
      polygons = []
    }

    $.each(msg.split('|'), function(idx, data){
      data = data.split(':')
      var code = data[0]
      data = data[1]

      if(code == 'viewport'){
        var data = data.split('!')
        before_viewport.x = viewport.x
        before_viewport.y = viewport.y
        before_viewport.time = viewport.time

        viewport.x = parseFloat(data[0])
        viewport.y = parseFloat(data[1])
        viewport.time = new Date().getTime();


        $infopanel_health.text(data[2])
        $infopanel_fuel.text(data[3])
        $infopanel_bullet1.text(data[4])
        $infopanel_bullet2.text(data[5])

        set_color($infopanel_health,  data[2], [25, 50])
        set_color($infopanel_fuel,    data[3], [25, 50])
        set_color($infopanel_bullet1, data[4], [25, 50])
        set_color($infopanel_bullet2, data[5], [4, 8])
        
      }else if(code == 'ship_infos'){
        if (!data){
          return
        }
        ship_infos = data.split('!')
        var cls = ''
        if (ship_infos[0] == ship_pk){
          cls = "my"
        }
        
      if (ship_infos[2] > 1000){
        ship_infos[2]/=1000
        ship_infos[2] = parseInt(ship_infos[2])
        ship_infos[2] += 'k'
      }

      var short_name = ship_infos[1]
      if (ship_infos[1].length > 14){
        short_name = ship_infos[1].substr(0, 12) + '..'
      }

        $players.append(
            '<div class="' + cls + ' ship'+ship_pk+'">' 
            + '<div class="name">' + short_name + '</div>'
            + '<div class="stats">' + ship_infos[3] +'/' + ship_infos[2] 
            + '</div>'
            + '</div>'
        )

        if($.inArray(ship_infos[0], names) == -1){
          names.push(ship_infos[0])
          $canvas_wrapper.append(
            '<div class="name_title ship'+ship_infos[0]+'" style="display: none">' + ship_infos[1] + '</div>'
          )
        }
      }else if(code == 'polygon'){
          polygons.push(data.split('!'))
      }else{
          // console.info("Получены данные: " + asd)
      }
    })
}

function start_game(data){
  ship_pk = data.ship_pk
  client_pk = data.client_pk
  $('.startGameDialog').hide()
  $('.queueBox').hide()
  setCookie("client_pk", client_pk)
  stop_fake_observer(draw_frame)
}

function parsing_blob(msg){
  var i,j
  var type = msg[0] /* 10-bullets 20-bonuses 30-ship*/
  var viewport_x = msg[1]
  var viewport_y = msg[2]


  var tmp
  if (type == 10){

    bullets = []
    var chunk = 3
    for (i=3,j=msg.length; i<j; i+=chunk) {
        tmp = msg.slice(i, i+chunk)
        tmp[0] += viewport_x 
        tmp[1] += viewport_y 
        bullets.push(tmp)
    }             
  } else if (type == 20){ 
    bonuses_gl = []
    var chunk = 3
    for (i=3,j=msg.length; i<j; i+=chunk) {
        tmp = msg.slice(i, i+chunk)
        tmp[0] += viewport_x 
        tmp[1] += viewport_y 
        bonuses_gl.push(tmp)
    }             
  } else if (type == 30){ 

    before_ships_gl = copy_array(ships_gl)

    before_ships_gl_time = ships_gl_time
    ships_gl = []
    ships_gl_time = new Date().getTime()
    $('.name_title').hide()
    var chunk = 9
    for (i=3,j=msg.length; i<j; i+=chunk) {
        tmp = msg.slice(i, i+chunk)
        tmp[2] += viewport_x
        tmp[3] += viewport_y 
        tmp[7] /= 2
        ships_gl.push(tmp)

        var pk = 's_'+ tmp[0]
        var x = tmp[2] + diff_x
        var y = tmp[3] + diff_y
        var dead_step = tmp[5]

        if(dead_step == -1 && x > 50 && x < field[0]-50 && y > 50){
          $('.ship' + pk).css({
            left:  (x+90) + 'px ', 
            top: (y-40 )+ 'px'
          }).show()
        }
    }             
  } 
}


function parsing_data(msg){
  if (typeof(msg) == 'object'){
      parsing_blob(new Int16Array(msg))
      return
  }

  if(msg.substr(0,5) == 'plain'){
      return parsing_plain(msg.substr(5, 9999999999))
  }
  var obj = jQuery.parseJSON(msg);
  var command = obj.command
  var data = obj.data
  if (command == 'start_game'){
      start_game(data)
  }else if (command == 'waiting'){
    $('.queueBox').show()
    data.queue_position && $('.queue_position').text(data.queue_position)
    data.queue_size && $('.queue_size').text(data.queue_size)
    setCookie("client_pk", data.client_pk)
  }else if (command == 'socket_closed'){
    socket.close()
    erase_client_pk()

    // if (window.ga){
        // ga('send', 'game', 'dead', data.dead_reason, data.lifetime, {nonInteraction: true})
        // ga('send', 'game', 'dead_remain', 'health', parseInt($infopanel_health.text()), {nonInteraction: true})
        // ga('send', 'game', 'dead_remain', 'bullet1', parseInt($infopanel_bullet1.text()), {nonInteraction: true})
        // ga('send', 'game', 'dead_remain', 'bullet2', parseInt($infopanel_bullet2.text()), {nonInteraction: true})
        // ga('send', 'game', 'dead_remain', 'fuel', parseInt($infopanel_fuel.text()), {nonInteraction: true})
    // }
    show_dialog_and_fill_values()
  }else{
      console.info(command)
      console.info(data)
  }
}


function bindKeys(){
  $('body').keydown(function(x){

    if (x.keyCode == 69){ //e 
        control.shot = 1
    }else if (x.keyCode == 87){ //w 
        control.shot2 = 1
    }else if (x.keyCode == 73){  // Up
        control.accelerator = 1
    }else if (x.keyCode == 74){  // left
        control.vector = -1
    }else if (x.keyCode == 76){  // right
        control.vector = 1
    }

    if($.inArray(x.keyCode, [69, 87, 73, 74, 76]) > -1){
        sendCursorPosition()
    }else{
      // console.info(x.keyCode)
    }
  })
  $('body').keyup(function(x){
    if (x.keyCode == 69){ //e
        control.shot = 0
    }else if (x.keyCode == 87){ //w
        control.shot2 = 0
    }else if (x.keyCode == 73){  // Up
        control.accelerator = 0
    }else if (x.keyCode == 74){  // left
        control.vector = 0
    }else if (x.keyCode == 76){  // right
        control.vector = 0
    }
    if($.inArray(x.keyCode, [69, 87, 73, 74, 76]) > -1){
        sendCursorPosition()
    }else{
    }
  })
}

function sendCursorPosition(){
    if (client_pk && ship_pk){
      socket.send(
          client_pk + ':cursor_pos:' + ship_pk
          + '!' + control.accelerator
          + '!' + control.vector
          + '!' + control.shot2
          + '!' + control.shot
      )
    }
}

function GetURLParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) 
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) 
        {
            return sParameterName[1];
        }
    }
}
