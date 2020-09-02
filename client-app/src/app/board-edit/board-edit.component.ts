import { Component, OnInit, ElementRef, ViewEncapsulation, Input, SimpleChanges, OnChanges } from '@angular/core';

import * as d3 from 'd3';



@Component({
  selector: 'app-board-edit',
  encapsulation: ViewEncapsulation.None,  // コレで、CSSが効くようになる (原理不明)
  templateUrl: './board-edit.component.html',
  styleUrls: ['./board-edit.component.css']
})
export class BoardEditComponent implements OnInit, OnChanges {
  @Input() transitionTime = 1000;
  @Input() margin = {top: 10, right: 10, bottom: 10, left: 10};
  @Input() width0  = 1280;
  @Input() height0  = 1280;
  @Input() width = this.width0 - this.margin.left - this.margin.right;
  @Input() height = this.height0 - this.margin.top  - this.margin.bottom;
  @Input() block_size = {width: 16, height: 16};

  svg; // Top level SVG element
  g; // SVG Group element

  /*
  # blocksは、Pythonのadc2019.pyから作る。
  import adc2019
  key2name = {
    'a': 'I', # straight
    'b': 'O', # square
    'c': 'T',
    'd': 'L',
    'e': 'J',  # Lの鏡像反転
    'f': 'S',  # skew
    'g': 'Z',  # skewの鏡像反転
    'z': 'o'   # monomino
  }
  for k in sorted(adc2019.block.keys()):
    tmp = adc2019.block[k]
    tmp = [(line + '    ')[0:4] for line in adc2019.block[k]] + (['    ']*4)
    print("'%s':" % (key2name[k[0]]+str(k[1])), tmp[0:4], ',')
  */
  blocks = {
    'I0': ['X   ', 'X   ', 'X   ', 'X   '] ,
    'I1': ['XXXX', '    ', '    ', '    '] ,
    'I2': ['X   ', 'X   ', 'X   ', 'X   '] ,
    'I3': ['XXXX', '    ', '    ', '    '] ,
    'O0': ['XX  ', 'XX  ', '    ', '    '] ,
    'O1': ['XX  ', 'XX  ', '    ', '    '] ,
    'O2': ['XX  ', 'XX  ', '    ', '    '] ,
    'O3': ['XX  ', 'XX  ', '    ', '    '] ,
    'T0': [' X  ', 'XXX ', '    ', '    '] ,
    'T1': ['X   ', 'XX  ', 'X   ', '    '] ,
    'T2': ['XXX ', ' X  ', '    ', '    '] ,
    'T3': [' X  ', 'XX  ', ' X  ', '    '] ,
    'L0': ['X   ', 'X   ', 'XX  ', '    '] ,
    'L1': ['XXX ', 'X   ', '    ', '    '] ,
    'L2': ['XX  ', ' X  ', ' X  ', '    '] ,
    'L3': ['  X ', 'XXX ', '    ', '    '] ,
    'J0': [' X  ', ' X  ', 'XX  ', '    '] ,
    'J1': ['X   ', 'XXX ', '    ', '    '] ,
    'J2': ['XX  ', 'X   ', 'X   ', '    '] ,
    'J3': ['XXX ', '  X ', '    ', '    '] ,
    'S0': [' XX ', 'XX  ', '    ', '    '] ,
    'S1': ['X   ', 'XX  ', ' X  ', '    '] ,
    'S2': [' XX ', 'XX  ', '    ', '    '] ,
    'S3': ['X   ', 'XX  ', ' X  ', '    '] ,
    'Z0': ['XX  ', ' XX ', '    ', '    '] ,
    'Z1': [' X  ', 'XX  ', 'X   ', '    '] ,
    'Z2': ['XX  ', ' XX ', '    ', '    '] ,
    'Z3': [' X  ', 'XX  ', 'X   ', '    '] ,
    'o0': ['X   ', '    ', '    ', '    '] ,
    'o1': ['X   ', '    ', '    ', '    '] ,
    'o2': ['X   ', '    ', '    ', '    '] ,
    'o3': ['X   ', '    ', '    ', '    '] ,
  };

  parts_block = [
    'I0',  'I1',
    'O0',
    'T0',  'T1',
    'L0',  'L1',  'L2',  'L3',
    'J0',  'J1',  'J2',  'J3',
    'S0',  'S1',
    'Z0',  'Z1',
    'o0'
  ];

  type2class = {
    I: 'straight-tetromino',
    O: 'square-tetromino',
    T: 'T-tetromino',
    L: 'L-tetromino',
    J: 'J-tetromino',
    S: 'S-tetromino',
    Z: 'Z-tetromino',
    o: 'monomino'
  };

  /**
   *  block(blocksの要素1つ)の、bounding boxを求める。
   *
   > block_bounding_box(blocks['I0'])
   [ 0, 0, 0, 3 ]
   > block_bounding_box(blocks['I1'])
   [ 0, 0, 3, 0 ]
   > block_bounding_box(blocks['O0'])
   [ 0, 0, 1, 1 ]
   > block_bounding_box(blocks['T0'])
   [ 0, 0, 2, 1 ]
   */
  private block_bounding_box(block: Object): number[] {
    let xsum = [0, 0, 0, 0];
    let ysum = [0, 0, 0, 0];
    for (let y = 0; y < 4; y ++) {
      for (let x = 0; x < 4; x ++) {
        if (block[y][x] != ' ') {
          ysum[y] ++;
          xsum[x] ++;
        }
      }
    }
    let x0 = 0, y0 = 0, x1 = 3, y1 = 3;
    while (xsum[x0] == 0 && x0 < 4) { x0++; }
    while (ysum[y0] == 0 && y0 < 4) { y0++; }
    while (xsum[x1] == 0 && 0 < x1) { x1--; }
    while (ysum[y1] == 0 && 0 < y1) { y1--; }
    if ( x1 < x0 || y1 < y0 ) {
      throw "unexpected block";
    }
    return [x0, y0, x1, y1];
  }

  /**
  parts_block_data = [
    {block: 'I0', x: 0, y: 0},
    {block: 'I1', x: 2, y: 0},
    {block: 'O0', x: 7, y: 0},
    {block: 'T0', x: 10, y: 0},
    {block: 'T1', x: 14, y: 0},
    {block: 'L0', x: 17, y: 0},
    {block: 'L1', x: 20, y: 0},
    {block: 'L2', x: 24, y: 0},
    {block: 'L3', x: 27, y: 0},
    {block: 'J0', x: 31, y: 0},
    {block: 'J1', x: 34, y: 0},
    {block: 'J2', x: 38, y: 0},
    {block: 'J3', x: 41, y: 0},
    {block: 'S0', x: 45, y: 0},
    {block: 'S1', x: 49, y: 0},
    {block: 'Z0', x: 52, y: 0},
    {block: 'Z1', x: 56, y: 0},
    {block: 'o0', x: 59, y: 0},
  ];
  */
  private get_parts_block_data(): Object[] {
    let res = [];
    let x = 0;
    for (let pb of this.parts_block) {
      res.push({block: pb, x: x, y: 0});
      let bb: number[] = this.block_bounding_box(this.blocks[pb]);
      x += bb[2] - bb[0] + 1 + 1;
    }
    return res;
  }

  private all_block_data(): Object[] {
    let block_data = [];
    let y = 0
    for (let k of Object.keys(this.blocks)) {
      let t = k[0];
      let n = + k[1]; // integer型にする
      block_data.push({block: k, x: n*5, y: y});
      if (n==3) {
        y += 5;
      }
    }
    return block_data;
  }

  /**
   *  ブロックの形状とXY座標から、関数draw_mino()で描画時に使うデータを生成する。
   *
   *  Parameters
   *  ==========
   *  block_dat = {block: 'O0', x: 0, y: 0}
   *
   *  Returns
   *  ==========

   */
  private rect_data(block_dat: Object) {
    if (this.type2class[block_dat['block'][0]] === void 0) {
      throw 'unknown ' + block_dat['block'][0];
    }
    let res = [];
    let b = this.blocks[block_dat['block']];  // ['X   ', 'X   ', 'X   ', 'X   ']
    for (let y=0; y<b.length; y++) {
      //console.log('y', y, b[y]);
      for (let x=0; x<b[y].length; x++) {
        //console.log('x', x, b[y][x]);
        if (b[y][x] != ' ') {
          res.push({x: x, y: y});
        }
      }
    }
    return {
      rect: res,
      x: block_dat['x'],
      y: block_dat['y'],
      class: this.type2class[block_dat['block'][0]]
    };
  }

  private dragstarted(event, d) {
    //console.log('this.g', this.g);
    //console.log('dragstarted', 'event=', event, 'd=', d, 'd3.event=', d3.event);
    //this.g.attr("cursor", "grabbing");
    d3.select("#main_board")
      .attr("cursor", "grabbing");
	}

	private dragged(d, i, n) {
    // 第1引数はイベントではなくて、dataだった。dは常に0らしい
    //console.log('dragged', 'event=', event, 'd=', d, 'd3.event=', d3.event);
    //console.log('dragged', d, i, n, 'd3.event=', d3.event);
    //d3.select(this).attr("cx", d.x = event.x).attr("cy", d.y = event.y);
    d3.select(n[i])
      //.attr('x', d3.event.x)  // gのなので、x,yでは動かない
      //.attr('y', d3.event.y)
      .attr('transform',
            `translate(${d3.event.x}, ${d3.event.y})`);
    //console.log(d.x, d.y, event.x, event.y);
	}

	private dragended(event, d, n) {
		//console.log('dragended', 'event=', event, 'd=', d, 'd3.event=', d3.event);
    //this.g.attr("cursor", "grab");
    d3.select("#main_board")
      .attr("cursor", "grab");
	}

  private draw_mino(selection, block_dat: Object, id: string) {
    let dat = {
      block_dat: block_dat,
      dat: this.rect_data(block_dat)
    };
    //console.log(dat);
    let container = selection
      .selectAll('g #'+id)
      .data([dat])
      .enter()
      .append('g')
        .attr('id', id)
        .attr('class', (d, i) => d['dat']['class'])
        .attr("transform", (d, i) =>
              "translate(" + (d['dat']['x'] * this.block_size['width']) + "," + (d['dat']['y'] * this.block_size['height']) + ")")
        .call(d3.drag()
		      .on("start", this.dragstarted)
		      .on("drag", this.dragged)
		      .on("end", this.dragended));
    container
      .selectAll('rect')
      .data(dat['dat']['rect'])
      .enter()
      .append('rect')
        .attr('x', (d, i) => d['x'] * this.block_size['width'])
        .attr('y', (d, i) => d['y'] * this.block_size['width'])
        .attr('width',  this.block_size['width'])
        .attr('height', this.block_size['height'])
        .on('click', (data, index, elem) => { console.log('d=', data, 'i=', index, 'elem=', elem)});
    return container;
  }

  private draw_board(block_data: Object[]) {
    // append the svg object to the body of the page
    this.svg = d3.selectAll("#my_board")
      .append("svg")
        .attr("width",  this.width  + this.margin.left + this.margin.right)
        .attr("height", this.height + this.margin.top  + this.margin.bottom);
    this.g = this.svg
      .append("g")
        .attr("transform",
              "translate(" + this.margin.left + "," + this.margin.top + ")")
        .attr('id', 'main_board');
    //console.log(block_data);
    var selection = d3.selectAll("#main_board");
    for (let i=0; i<block_data.length; i++) {
      let bd = block_data[i];
      //console.log(selection, bd);
      //draw_mino(selection, bd);
      this.draw_mino(selection, bd, 'BLK'+i);
    }
    console.log('this.g', this.g);
  }


  constructor() { }

  ngOnInit(): void {
    let block_data = this.get_parts_block_data();
    //let block_data = this.all_block_data();

    this.draw_board(block_data);
  }

  ngOnChanges(changes: SimpleChanges) {
    console.log('ngOnChanges', changes)
  }
}
