var canvas = document.getElementById("canvas");
if (canvas.getContext){
    var ctx = canvas.getContext('2d');
}

var boardOrigX = 10;
var boardOrigY = 10;
var boardW = 72;
var boardH = 72;
var gridSize = 20;
var bboxW = 0;
var bboxH = 0;

var board = [[]];
var blockMap = [[]];
var lineMap = [[]];

var blockNum = 2;
var blocks = [];
var blockLoc = [];
var blockColor = [];

var colors = [
    'gray',   // 0: monomino
    'cyan',   // 1: I
    'yellow', // 2: O
    'purple', // 3: T
    'blue',   // 4: J
    'orange', // 5: L
    'green',  // 6: S
    'red'     // 7: Z
];

function checkBlockShape() {
    for (var n = 0; n < blockNum; ++n) {
	var block = [];
	blocks[n].forEach(function(row) {
	    row.forEach(function(val) {
		block.push(val != 0 ? 1 : 0);
	    });
	    block.push(0);
	});
	
	switch(block.join('')) {
	case '1':
	    blockColor[n] = 0; // monomino
	    break;
	case '11110':
	case '10101010':
	    blockColor[n] = 1; // I
	    break;
	case '110110':
	    blockColor[n] = 2; // O
	    break;
	case '01001110':
	case '100110100':
	case '11100100':
	case '010110010':
	    blockColor[n] = 3; // T
	    break;
	case '010010110':
	case '10001110':
	case '110100100':
	case '11100010':
	    blockColor[n] = 4; // J
	    break;
	case '100100110':
	case '11101000':
	case '110010010':
	case '00101110':
	    blockColor[n] = 5; // L
	    break;
	case '01101100':
	case '100110010':
	    blockColor[n] = 6; // S
	    break;
	case '11000110':
	case '010110100':
	    blockColor[n] = 7; // Z
	    break;
	default:
	    console.log("block shape error!");
	}
    }
}

function initBoard() {
    for (var y = 0; y < boardH; ++y) {
	board[y] = [];
	blockMap[y] = [];
	for (var x = 0; x < boardW; ++x) {
	    board[y][x] = 0;
	    blockMap[y][x] = -1;
	}
    }
}

function placeBlock() {
    for (var n = 0; n < blockNum; ++n) {
	blocks[n].forEach(function(row,y) {
	    var yy = blockLoc[n][1] + y;
	    row.forEach(function(val,x) {
		var xx = blockLoc[n][0] + x;
		if (blocks[n][y][x] != 0) {
		    board[yy][xx] = val;
		    if (blockMap[yy][xx] < 0) {
			blockMap[yy][xx] = n;
		    }
		    else {
			console.log("block overlap error!");
		    }
		}
	    });
	});
    }
}

function placeLine() {
    for (var y = 0; y < boardH; ++y) {
	for (var x = 0; x < boardW; ++x) {
	    if (blockMap[y][x] < 0) {
		board[y][x] = lineMap[y][x];
	    }
	}
    }
}

function drawBoard() {
    initBoard();
    placeBlock();
    placeLine();
    
    // draw board
    ctx.strokeStyle = 'gray';
    ctx.fillStyle = 'white';
    ctx.lineWidth = 1;
    ctx.fillRect(boardOrigX, boardOrigY, boardW * gridSize, boardH * gridSize);
    ctx.strokeRect(boardOrigX, boardOrigY, boardW * gridSize, boardH * gridSize);
    
    // draw grid
    ctx.strokeStyle = 'gray';
    ctx.lineWidth = 1;
    for (var x = 1; x < boardW; ++x) {
	ctx.beginPath();
	ctx.moveTo(boardOrigX + x * gridSize, boardOrigY);
	ctx.lineTo(boardOrigX + x * gridSize, boardOrigY + boardH * gridSize);
	ctx.stroke();
    }
    for (var y = 1; y < boardH; ++y) {
	ctx.beginPath();
	ctx.moveTo(boardOrigX,                     boardOrigY + y * gridSize);
	ctx.lineTo(boardOrigX + boardW * gridSize, boardOrigY + y * gridSize);
	ctx.stroke();
    }

    // draw blocks
    for (var n = 0; n < blockNum; ++n) {
	ctx.strokeStyle = 'black';
	ctx.fillStyle = colors[blockColor[n]];
	ctx.lineWidth = 2;
	var blockX = boardOrigX + blockLoc[n][0] * gridSize;
	var blockY = boardOrigY + blockLoc[n][1] * gridSize
	blocks[n].forEach(function(row,y) {
	    row.forEach(function(val,x) {
		if (blocks[n][y][x] != 0) {
		    ctx.fillRect(blockX + x * gridSize, blockY + y * gridSize, gridSize, gridSize);
		    ctx.strokeRect(blockX + x * gridSize, blockY + y * gridSize, gridSize, gridSize);
		}
	    });
	});
    }

    // draw number
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.strokeStyle = 'white';
    ctx.fillStyle = 'black';
    for (var y = 0; y < boardH; ++y) {
	for (var x = 0; x < boardW; ++x) {
	    if (board[y][x] > 0) {
		var str = String(board[y][x]);
		var xx = boardOrigX + (x + 0.5) * gridSize;
		var yy = boardOrigY + (y + 0.5) * gridSize
		ctx.strokeText(str, xx, yy);
		ctx.fillText(str, xx, yy);
	    }
	}
    }

    // draw bbox
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.strokeRect(boardOrigX, boardOrigY, bboxW * gridSize, bboxH * gridSize);

}

function parseQFile(text) {
    var lines = text.split('\n');
    var m = null;
    var parseBlock = false;
    var n;
    lines.forEach(function(line) {
	if (parseBlock) {
	    if (/^\s*$/.exec(line)) {
		parseBlock = false;
	    }
	    else {
		blocks[n].push(line.replace(/\+/g, '-1').split(',').map(Number));
	    }
	}
	else if (m = /SIZE\s+(\d+)X(\d+)/.exec(line)) {
	    boardW = Number(m[1]);
	    boardH = Number(m[2]);
	}
	else if (m = /BLOCK_NUM\s+(\d+)/.exec(line)) {
	    blockNum = Number(m[1]);
	    blocks = new Array(blockNum);
	}
	else if (m = /BLOCK#(\d+)\s+(\d+)X(\d+)/.exec(line)) {
	    n = Number(m[1]) - 1;
	    var blockW = Number(m[2]);
	    var blockH = Number(m[3]);
	    blocks[n] = [];
	    parseBlock = true;
	}
    });
}

function parseAFile(text) {
    var lines = text.split('\n');
    var m = null;
    var parseMap = false;
    var lineCount = 0;
    var n;

    // reset lineMap
    for (var y = 0; y < boardH; ++y) {
	lineMap[y] = [];
	for (var x = 0; x < boardW; ++x) {
	    lineMap[y][x] = 0;
	}
    }
    
    lines.forEach(function(line) {
	if (parseMap) {
	    var mapLine = line.replace('+', '-1').split(',').map(Number);
	    for (var x = 0; x < bboxW; ++x) {
		if (mapLine[x] > 0) {
		    lineMap[lineCount][x] = mapLine[x];
		}
	    }
	    ++lineCount;
	    if (lineCount >= bboxH) {
		parseMap = false;
	    }
	}
	else if (m = /SIZE\s+(\d+)X(\d+)/.exec(line)) {
	    bboxW = Number(m[1]);
	    bboxH = Number(m[2]);
	    parseMap = true;
	    if (1) { // only draw within bbox
		boardW = bboxW;
		boardH = bboxH;
	    }
	}
	else if (m = /BLOCK#(\d+)\s+@\((\d+),(\d+)\)/.exec(line)) {
	    n = Number(m[1]) - 1;
	    blockLoc[n] = [Number(m[2]), Number(m[3])];
	}
    });
}

// file load
var qfile_load = false;
var afile_load = false;
var qform = document.forms.qform;
var aform = document.forms.aform;
qform.qfile.addEventListener('change', function(e) {
    var result = e.target.files[0];
    var reader = new FileReader();
    if (result) {
	reader.readAsText(result);
    }
    else {
	qfile_load = false;
    }
    reader.onload = function(ev) {
	parseQFile(reader.result);
	qfile_load = true;
	ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
});
aform.afile.addEventListener('change', function(e) {
    var result = e.target.files[0];
    var reader = new FileReader();
    if (result) {
	reader.readAsText(result);
    }
    else {
	afile_load = false;
    }
    reader.onload = function(ev) {
	parseAFile(reader.result);
	afile_load = true;
	if (qfile_load) {
	    checkBlockShape();
	    drawBoard();
	}
    }
});
