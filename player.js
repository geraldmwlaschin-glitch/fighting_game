<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>UFO Fighter Web</title>

<style>
body{
margin:0;
background:black;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
}

canvas{
background:#141432;
border:2px solid cyan;
}
</style>

</head>

<body>

<canvas id="game" width="800" height="500"></canvas>

<script>

const canvas = document.getElementById("game")
const ctx = canvas.getContext("2d")

/* -------- BULLET -------- */

class Bullet{

constructor(x,y,direction){
this.x=x
this.y=y
this.direction=direction
this.speed=8
this.width=8
this.height=4
}

update(){
this.x+=this.speed*this.direction
}

draw(){
ctx.fillStyle="yellow"
ctx.fillRect(this.x,this.y,this.width,this.height)
}

}


/* -------- PLAYER -------- */

class Player{

constructor(x,y){

this.width=32
this.height=48

this.x=x
this.y=y

this.start_x=x
this.start_y=y

this.vel_x=0
this.vel_y=0

this.on_ground=false

this.gravity=0.6
this.jump_power=-12

this.direction=1

this.has_shoot_power=false
this.shoot_cooldown=0

this.bullets=[]

this.shoot_power_count=0

this.invincible=false
this.invincible_end_time=0

this.INVINCIBLE_DURATION_MS=4000
}

/* movement */

move_left(){
this.vel_x=-5
this.direction=-1
}

move_right(){
this.vel_x=5
this.direction=1
}

/* jump */

jump(){
if(this.on_ground){
this.vel_y=this.jump_power
this.on_ground=false
}
}

/* shoot */

shoot(){

if(this.has_shoot_power && this.shoot_cooldown<=0){

let bullet=new Bullet(
this.x+this.width/2,
this.y+this.height/2,
this.direction
)

this.bullets.push(bullet)

this.shoot_cooldown=10
}
}

/* power up */

activate_power_up(type){

if(type==="shoot"){

this.shoot_power_count++
this.has_shoot_power=true

if(this.shoot_power_count>1){

let now=Date.now()

this.invincible_end_time=Math.max(this.invincible_end_time,now)+this.INVINCIBLE_DURATION_MS

this.invincible=true

this.shoot_power_count=0
}
}
}

/* reset */

reset(){

this.x=this.start_x
this.y=this.start_y

this.vel_y=0

this.has_shoot_power=false

this.bullets=[]

this.shoot_power_count=0
this.invincible=false
this.invincible_end_time=0
}

/* update */

update(platforms,enemies){

this.vel_y+=this.gravity

this.x+=this.vel_x
this.vel_x=0

this.y+=this.vel_y

if(this.shoot_cooldown>0){
this.shoot_cooldown--
}

/* invincibility update */

if(this.invincible){

if(Date.now()>=this.invincible_end_time){
this.invincible=false
}

}

this.on_ground=false

/* platform collision */

for(let platform of platforms){

if(this.x < platform.x + platform.w &&
this.x + this.width > platform.x &&
this.y < platform.y + platform.h &&
this.y + this.height > platform.y){

if(this.vel_y>0){

this.y=platform.y-this.height
this.vel_y=0
this.on_ground=true

}
else if(this.vel_y<0){

this.y=platform.y+platform.h
this.vel_y=0

}
}
}

/* enemy collision */

for(let enemy of enemies){

if(this.x < enemy.x + enemy.w &&
this.x + this.width > enemy.x &&
this.y < enemy.y + enemy.h &&
this.y + this.height > enemy.y){

if(!this.invincible){
this.reset()
}
else{
enemy.dead=true
}

}

}

/* update bullets */

for(let bullet of this.bullets){
bullet.update()
}

/* bullet collision */

for(let bullet of this.bullets){

for(let enemy of enemies){

if(bullet.x < enemy.x + enemy.w &&
bullet.x + bullet.width > enemy.x &&
bullet.y < enemy.y + enemy.h &&
bullet.y + bullet.height > enemy.y){

bullet.dead=true
enemy.dead=true

}

}

}

/* remove dead bullets */

this.bullets=this.bullets.filter(b=>!b.dead)

}

/* draw */

draw(){

ctx.fillStyle=this.invincible?"cyan":"red"

ctx.fillRect(this.x,this.y,this.width,this.height)

for(let bullet of this.bullets){
bullet.draw()
}

}

}


/* -------- TEST GAME -------- */

let player=new Player(100,100)

let platforms=[
{x:0,y:450,w:800,h:50}
]

let enemies=[
{x:500,y:410,w:30,h:40,dead:false}
]


/* input */

const keys={}

window.addEventListener("keydown",e=>{

keys[e.key]=true

if(e.key===" "){
player.jump()
}

if(e.key==="f"){
player.shoot()
}

})

window.addEventListener("keyup",e=>{
keys[e.key]=false
})


/* game loop */

function update(){

if(keys["a"]) player.move_left()
if(keys["d"]) player.move_right()

player.update(platforms,enemies)

enemies=enemies.filter(e=>!e.dead)

}

function draw(){

ctx.clearRect(0,0,800,500)

for(let p of platforms){

ctx.fillStyle="gray"
ctx.fillRect(p.x,p.y,p.w,p.h)

}

for(let e of enemies){

ctx.fillStyle="green"
ctx.fillRect(e.x,e.y,e.w,e.h)

}

player.draw()

}

function gameLoop(){

update()
draw()

requestAnimationFrame(gameLoop)

}

gameLoop()

</script>

</body>
</html>
