const tg = window.Telegram.WebApp;
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

const canvasHistory = [];
const mouse = {x: 0, y: 0};
let draw = false;

const selectColor = document.getElementById("color");
const selectWidth = document.getElementById("width");
const undoButton = document.getElementById("undo");
const clearButton = document.getElementById("clear");

tg.expand();
tg.disableVerticalSwipes();
tg.lockOrientation();
tg.MainButton.setText("Send picture");
tg.MainButton.show();
tg.MainButton.enable();

context.beginPath();
context.rect(0, 0, 400, 400);
context.fillStyle = "white";
context.fill();
context.strokeStyle = "black";
context.lineCap = "round";
context.lineJoin = "round";

const startParams = tg.initDataUnsafe.start_param.split('__');
let startImg = null;
if (startParams.length > 1) {
    startImg = new Image();
    startImg.src = `/paint/picture/${startParams[1]}`;
    startImg.onload = () => {
        context.drawImage(startImg, 0, 0);
    };
}

Telegram.WebApp.onEvent('mainButtonClicked', function () {
    tg.MainButton.hide()
    tg.MainButton.disable()
    canvas.toBlob(async function (blob) {
        const data = new FormData();
        data.append('init_data', tg.initData);
        data.append('image', blob, 'image.png');
        await fetch('/paint/send', {method: 'POST', body: data});
        tg.close();
    }, 'image/png');
});


canvas.addEventListener("mousedown", function (e) {
    const ClientRect = this.getBoundingClientRect();
    mouse.x = e.clientX - ClientRect.left;
    mouse.y = e.clientY - ClientRect.top;
    draw = true;
    context.beginPath();
    context.moveTo(mouse.x, mouse.y);
    canvas.toBlob(function (blob) {
        canvasHistory.push(blob);
    }, 'image/png');
});

canvas.addEventListener("mousemove", function (e) {
    if (draw) {
        const ClientRect = this.getBoundingClientRect();
        mouse.x = e.clientX - ClientRect.left;
        mouse.y = e.clientY - ClientRect.top;
        context.lineTo(mouse.x, mouse.y);
        context.stroke();
    }
});

canvas.addEventListener("mouseup", function (e) {
    const ClientRect = this.getBoundingClientRect();
    mouse.x = e.clientX - ClientRect.left;
    mouse.y = e.clientY - ClientRect.top;
    context.lineTo(mouse.x, mouse.y);
    context.stroke();
    context.closePath();
    draw = false;
});

canvas.addEventListener("touchstart", function (e) {
    const ClientRect = this.getBoundingClientRect();
    mouse.x = e.changedTouches[0].clientX - ClientRect.left;
    mouse.y = e.changedTouches[0].clientY - ClientRect.top;
    draw = true;
    context.beginPath();
    context.moveTo(mouse.x, mouse.y);
    canvas.toBlob(function (blob) {
        canvasHistory.push(blob);
    }, 'image/png');
});

canvas.addEventListener("touchmove", function (e) {
    if (draw) {
        const ClientRect = this.getBoundingClientRect();
        mouse.x = e.changedTouches[0].clientX - ClientRect.left;
        mouse.y = e.changedTouches[0].clientY - ClientRect.top;
        context.lineTo(mouse.x, mouse.y);
        context.stroke();
    }
});

canvas.addEventListener("touchend", function (e) {
    const ClientRect = this.getBoundingClientRect();
    mouse.x = e.changedTouches[0].clientX - ClientRect.left;
    mouse.y = e.changedTouches[0].clientY - ClientRect.top;
    context.lineTo(mouse.x, mouse.y);
    context.stroke();
    context.closePath();
    draw = false;
});

selectColor.addEventListener("change", function () {
    context.strokeStyle = selectColor.value;
});


selectWidth.addEventListener("change", function () {
    context.lineWidth = selectWidth.value;
});


undoButton.addEventListener("click", function (e) {
    if (canvasHistory.length !== 0) {
        const oldCanvas = canvasHistory.pop();
        createImageBitmap(oldCanvas).then(function (img) {
            context.drawImage(img, 0, 0);
        });
    }
});

clearButton.addEventListener("click", function (e) {
    canvas.toBlob(function (blob) {
        canvasHistory.push(blob);
    }, 'image/png');
    if (startImg) {
        context.drawImage(startImg, 0, 0);
    } else {
        for (let i = 0; i < 3; i++) {
            context.rect(0, 0, 400, 400);
            context.fill();
        }
    }
});