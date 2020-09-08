import { Component, OnInit, ElementRef, ViewEncapsulation, Input, SimpleChanges, OnChanges } from '@angular/core';

import * as d3 from 'd3';

import { AdcService } from '../adc.service';
import { QData, AData } from './adc2019-file';

/** XY座標 */
class Pos {
  constructor(public x:number,
              public y:number) {}
};

class Cell extends Pos {
  public static width: number;  // セルの幅
  public static height: number; // セルの高さ
  public value: string;

  constructor(x: number, y: number, value?: string) {
    super(x, y);
    this.value = value;
  }
}

/**
 * ブロックのデータ
 *  id : 'I0', 'I1', 'T0', ...
 *  pos : bb左上のXY座標(マス目単位)
 */
class BlockData {
  constructor(public id: string,
              public pos: Pos) {
  }

  dup(): BlockData {
    return BlockData.create(this.id, this.pos.x, this.pos.y);
  }

  static create(id: string, x: number, y: number): BlockData {
    return new BlockData(id, new Pos(x, y));
  }

  block_bounding_box(): number[] {
    return RectData.block_bounding_box(QData.blocks[this.id]);
  }

  block_size(): number[] {
    let bb: number[] = this.block_bounding_box();
    return this.block_size_bb(bb);
  }

  block_size_bb(bb: number[]): number[] {
    return [bb[2] - bb[0] + 1, bb[3] - bb[1] + 1];
  }
};

/**
 *  ブロックと、構成要素のマス
 *  rect 各マスのデータ。相対的なXY座標と値
 *  pos   ブロックの左上のXY座標
 *  cls   CSSで使うためのclass名
 *  lower_right 右下のXY座標
 *  //values  各マスに設定する値
 */
class RectData {
  public lower_right: Pos;
  //public values: string[] = [];

  constructor(public rect: Cell[],
              public pos: Pos,
              public cls: string) {
    let x = 0;
    let y = 0;
    for (let xy of rect) {
      x = Math.max(x, xy.x);
      y = Math.max(y, xy.y)
    }
    this.lower_right = new Pos(x+1, y+1);  // x,yは座標値なので+1して大きさにする
  }

  set_value(index: number, value: string): boolean {
    //this.values[index] = value;
    if (value === void 0 || value == '') {
      delete this.rect[index].value;
      return false;
    } else {
      this.rect[index].value = value;
      return true;
    }
  }

  /** Qファイル、QData.parse()で読み出したデータから、オブジェクトを作成する */
  static from_QData(q_b_type: string, q_b_size: number[], q_b_data: number[][], pos: Pos): RectData {
    let cls = BoardEditComponent.block_class(q_b_type);
    let rect: Cell[] = [];
    for (let y=0; y<q_b_size[1]; y++) {
      for (let x=0; x<q_b_size[0]; x++) {
        let v = q_b_data[y][x];
        let value: string;
        if (v == 0) {
          // 空白セル
          continue;
        } else if (v == -1) {
          value = '+';
        } else {
          value = '' + v;  // int --> string
        }
        rect.push(new Cell(x, y, value));
      } // x
    } // y
    return new RectData(rect, new Pos(pos.x, pos.y), cls);
  }

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
  static block_bounding_box(block: string[][]): number[] {
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
};

/** d3.js data()として使う、ブロックのデータ */
class BlockData_d3 {
  selected: boolean = false;
  dragstart_pos: Pos;
  temporally: boolean = false;
  delete_ok;
  block_num: number;  // Qデータで指定されている"BLOCK#番号"。Aデータ出力時に必要

  constructor(public block: BlockData,
              public rect: RectData,
              public pos: Pos,
              public id: string,
              public _component?: BoardEditComponent) {
  }

  /** Qファイル、QData.parse()で読み出したデータから、オブジェクトを作成する */
  static from_QData(q_b_type: string, q_b_size: number[], q_b_data: number[][],
                    pos: Pos, id:string, _component: BoardEditComponent): BlockData_d3 {
    let block = BlockData.create(q_b_type, pos.x, pos.y);
    let rect = RectData.from_QData(q_b_type, q_b_size, q_b_data, pos);
    let posxy = new Pos(pos.x * Cell.width, pos.y * Cell.height);
    return new BlockData_d3(block, rect, posxy, id, _component);
  }

  block_size(): number[] {
    return this.block.block_size();
  }

  /** ブロックを、セル座標(cx, cy)へ移動する */
  move_to(cx: number, cy: number, all: boolean = false) {
    this.block.pos.x = cx;
    this.block.pos.y = cy;
    this.rect.pos.x = cx;  // 同じデータが2箇所にある???重複
    this.rect.pos.y = cy;
    if (all) {
      this.pos.x = cx * Cell.width;
      this.pos.y = cy * Cell.height;
    }
  }

  /** ADC-Q形式のテキストを返す */
  block_text(): string {
    let tmp = [ ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'] ];
    let cell_width = 3;
    for (let cell of this.rect.rect) {
      let val = (cell.value === void 0) ? '+' : cell.value;
      tmp[cell.y][cell.x] = val;
      cell_width = Math.max(cell_width, val.length)
    }
    let size = this.block.block_size();  // bounding boxからブロックサイズを求める
    //console.log(this.rect.rect, tmp);
    let res = '';
    for (let y=0; y<size[1]; y++) {
      for (let x=0; x <size[0]; x++) {
        if (0 < x) res += ',';
        res += ('    ' + tmp[y][x]).slice(-cell_width);
      }
      res += '\n';
    }
    return res;
  }
};


@Component({
  selector: 'app-board-edit',
  encapsulation: ViewEncapsulation.None,  // コレで、CSSが効くようになる (原理不明)
  templateUrl: './board-edit.component.html',
  styleUrls: ['./board-edit.component.css']
})
export class BoardEditComponent implements OnInit, OnChanges {
  @Input() transitionTime = 1000;
  @Input() margin = {top: 10, right: 10, bottom: 10, left: 10};
  //@Input() width0  = 1280;
  //@Input() height0 = 1280;
  //@Input() width  = this.width0 - this.margin.left - this.margin.right;
  //@Input() height = this.height0 - this.margin.top  - this.margin.bottom;
  @Input() cell_width  = 16;
  @Input() cell_height = 16;
  @Input() max_block_num = {x: 72, y: 72};
  staging_area2_d = 100; // あとで計算しなおす
  svg_size = {a: 0, b: 0, c: 0, d: 0, e: 0, f: 0};  // 描画座標系での、各種サイズ
  board_size = {x: this.max_block_num['x'], y: this.max_block_num['y']};
  board_size_temp = {x: this.max_block_num['x'], y: this.max_block_num['y']}; // numberではなくてstringになっている!!
  in_number: string = "";
  q_number: string = "777";
  hover_number: string = "-";
  svg; // Top level SVG element, id = 'my_svg'
  g; // SVG Group element, id = 'main_board'
  d3_brush;
  //dragstart_pos: Pos;  // マス目の座標ではなく、gの座標
  dragstart_block_visible: boolean = false;
  num_mino = 0;
  num_line_cell = 0;
  blocks_on_board: BlockData_d3[] = [];
  working_mode_selected: string = 'construction';
  working_modes = [
    {title: 'Construction', value: 'construction'},
    {title: 'Solve', value: 'solve'},
  ];
  edit_modes = [
    /*0*/ {title: 'Set number', value: 'set_number', selected: false},
    //{title: 'Solve', value: 'solve', selected: false},
    /*1*/ {title: 'Draw line', value: 'draw_line', selected: false},
    /*2*/ {title: 'Select blocks', value: 'select_blocks', selected: false},
  ];
  edit_mode = {set_number: this.edit_modes[0]['selected'],
               draw_line: this.edit_modes[1]['selected']
  };

  qData;
  aData;
  do_readQFile = false;
  do_readAFile = false;
  do_config = false;

  /** 問題作成モードである */
  construction_mode(): boolean {
    return this.working_mode_selected == 'construction';
  }

  solve_mode(): boolean {
    return this.working_mode_selected == 'solve';
  }

  set_number_mode(): boolean {
    return this.edit_mode['set_number'];
  }

  draw_line_mode(): boolean {
    return this.edit_mode['draw_line'];
  }

  select_blocks_mode(): boolean {
    return this.edit_mode['select_blocks'];
  }

  /** チェックボックスの状態 */
  on_change_mode() {
    //console.log('show', 'working_mode_selected=', this.working_mode_selected, 'edit_modes=', this.edit_modes);
    for (let i of this.edit_modes) {
      this.edit_mode[i['value']] = i['selected'];
    }

    if (this.select_blocks_mode()) {
      this.enable_brush();
    }
  }

  /** 選択中のブロックのリストを返す */
  private selected_blocks(): BlockData_d3[] {
    let res = [];
    for (let bd of this.blocks_on_board) {
      if (bd.selected) {
        res.push(bd);
      }
    }
    return res;
  }

  /** staging areaにあるブロックのリストを返す。 */
  private blocks_on_staging_area(move: boolean = false) {
    let res: BlockData_d3[] = [];
    let on_board: BlockData_d3[] = [];
    for (let bd of this.blocks_on_board) {
      //console.log(bd.pos);
      if (this.svg_size.a <= bd.pos.x ||
          this.svg_size.c <= bd.pos.y) {
        res.push(bd);
      } else {
        on_board.push(bd);
      }
    }
    if (move) {
      this.blocks_on_board = on_board;
    }
    return res;
  }

  /** (x0, y0)-(x1, y1)の範囲内にあるブロックのリストを返す */
  private blocks_in_range(x0, y0, x1, y1): BlockData_d3[] {
    let res = [];
    for (let bd of this.blocks_on_board) {
      let size = bd.block_size();
      let bx0 = bd.pos.x;
      let by0 = bd.pos.y;
      let bx1 = bd.pos.x + size[0] * Cell.width;
      let by1 = bd.pos.y + size[1] * Cell.height;
      if (x0 <= bx0 && bx0 <= x1 && y0 <= by0 && by0 <= y1 &&
          x0 <= bx1 && bx1 <= x1 && y0 <= by1 && by1 <= y1) {
        res.push(bd);
      }
    }
    return res;
  }

  /** board areaにあるブロックのリストを返す。 */
  private get_blocks_on_board() {
    let res: BlockData_d3[] = [];
    let on_board: BlockData_d3[] = [];
    for (let bd of this.blocks_on_board) {
      //console.log(bd.pos);
      if (this.svg_size.a <= bd.pos.x ||
          this.svg_size.c <= bd.pos.y) {
        res.push(bd);
      } else {
        on_board.push(bd);
      }
    }
    return on_board;
  }

  /** block id*/
  private next_mino_id(): string {
    return 'BLK' + (this.num_mino ++);
  }

  private next_line_cell_id(): string {
    return 'L' + (this.num_line_cell ++);
  }

  /** cell id */
  private cell_id(block_id: string, index: number): string {
    return block_id + '-' + index;
  }

  /** cell label (マスの中の数字) id */
  private cell_label_id(block_id: string, index: number): string {
    return block_id + '-' + index + '-L';
  }

  // uniqueなブロック(回転した結果、既存ブロックと同じになっているものを除外)
  static parts_block = [
    'I0',  'I1',
    'O0',
    'T0',  'T1',  'T2',  'T3',
    'L0',  'L1',  'L2',  'L3',
    'J0',  'J1',  'J2',  'J3',
    'S0',  'S1',
    'Z0',  'Z1',
    'o0',
    //'l0',
  ];

  static type2class = {
    I: 'straight-tetromino',
    O: 'square-tetromino',
    T: 'T-tetromino',
    L: 'L-tetromino',
    J: 'J-tetromino',
    S: 'S-tetromino',
    Z: 'Z-tetromino',
    o: 'monomino',
    l: 'line-cell'
  };

  /** ブロックのID('I0', 'T0', ...)から、CSS用のclass名を求める */
  static block_class(id: string) {
    return BoardEditComponent.type2class[ id[0] ];  // 1文字目
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
  private get_parts_block_data(): BlockData[] {
    let res: BlockData[] = [];
    let x = 0; //this.max_block_num.x + 1;
    let y = 0;
    for (let pb of BoardEditComponent.parts_block) {
      res.push(BlockData.create(pb, x, y));
      //let bb = this.block_bounding_box(QData.blocks[pb]);
      ////x += bb[2] - bb[0] + 1 + 1;
      //y += bb[3] - bb[1] + 1 + 1;
    }
    return res;
  }

  private all_block_data(): BlockData[] {
    let block_data: BlockData[] = [];
    let x = 0;
    let y = 0
    for (let k of Object.keys(QData.blocks)) {
      let t = k[0];
      let n = + k[1]; // integer型にする
      //x = n * 5;
      block_data.push(BlockData.create(k, x, y));
      //if (n == 3) {
      //  y += 5;
      //}
    }
    return block_data;
  }

  /**
   * get_parts_block_data(), all_block_data()の返り値である、
   * BlockData[]から、
   * BlockData_d3[]を作る
  */
  private initial_blocks(blocks: BlockData[]): BlockData_d3[] {
    let res: BlockData_d3[] = [];
    for (let block_dat of blocks) {
      res.push(this.new_mino(block_dat));
    }
    return res;
  }

  /** ブロックblocksを、staging areaに再配置する */
  private put_blocks_on_staging_area(blocks: BlockData_d3[]) {
    let s1_width_c  = Math.floor(this.svg_size.b / this.cell_width);
    let s1_height_c = Math.floor(this.svg_size.c / this.cell_height);
    let s2_width_c  = this.board_size.x + s1_width_c;
    let s2_height_c = 99999;  // 十分大きな、仮の値
    //console.log('s1', s1_width_c, s1_height_c, 's2', s2_width_c, s2_height_c);
    let area = (4 <= s1_width_c) ? 1 : 2;  // staging area 1, 2
    let cx = (area == 1) ? this.board_size.x : 0; // 初期座標
    let cy = (area == 1) ? 0 : this.board_size.y;
    //console.log('svg_size=', this.svg_size);
    // pass 1
    for (let bd of blocks) {
      let bb: number[] =RectData.block_bounding_box(QData.blocks[bd.block.id]);
      //console.log(area, cx, cy, bd, bb);
      bd.rect.pos.x = cx;
      bd.rect.pos.y = cy;
      if (area == 1) {
        cx += bb[2] - bb[0] + 1 + 1;
        if (this.board_size.x + s1_width_c < cx + 4) { // 次に追加したら確実にはみ出す
          cx = this.board_size.x;
          cy += 4 + 1;
        }
        if (s1_height_c < cy) {
          area = 2;
          cx = 0;
          cy = this.board_size.y;
        }
      } else { // area == 2
        cx += bb[2] - bb[0] + 1 + 1;
        if (s2_width_c < cx) {
          cx = 0;
          cy += 4 + 1;
        }
      }
      //console.log('pass1', bd);
    }
    s2_height_c = cy + 4;
    this.staging_area2_d = s2_height_c * this.cell_height;
    this.draw_board();  // ボードのサイズを変更する
    // pass 2
    for (let bd of blocks) {
      bd.pos.x = bd.rect.pos.x * this.cell_width;
      bd.pos.y = bd.rect.pos.y * this.cell_height;
      this.put_mino(bd);
      //console.log('pass2', bd);
    }
    this.update_all_blocks();  // 再描画
  }

  /** staging areaにあるブロックを、並べ直す。 */
  private relayout_staging_area() {
    this.draw_board();  // サイズを計算し直し
    let blocks: BlockData_d3[] = this.blocks_on_staging_area(true); // 移動
    console.log('relayout', blocks);
    this.put_blocks_on_staging_area(blocks);
    this.update_all_blocks();
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
  private rect_data(block_dat: BlockData): RectData {
    let cls = BoardEditComponent.block_class(block_dat.id);
    if (cls === void 0) {
      throw 'unknown ' + block_dat.id;
    }
    let cells: Cell[] = [];
    let b = QData.blocks[block_dat.id];  // ['X   ', 'X   ', 'X   ', 'X   ']
    for (let y=0; y<b.length; y++) {
      for (let x=0; x<b[y].length; x++) {
        if (b[y][x] != ' ') {
          cells.push(new Cell(x, y));
        }
      }
    }
    return new RectData(cells, block_dat.pos, cls);
  }

  private new_BlockData_d3(block_dat: BlockData, id: string): BlockData_d3 {
    let rect_dat = this.rect_data(block_dat);
    return new BlockData_d3(block_dat, rect_dat,
                            new Pos(rect_dat.pos.x * this.cell_width,
                                     rect_dat.pos.y * this.cell_height),
                            id,
                            this);
  }

  /** ボードの情報を、数値の２次元配列にして返す */
  private get_board(): number[][] {
    let board: number[][] = [];
    let value: string[][] = [];
    for (let bd of this.blocks_on_board) {
      for (let cell of bd.rect.rect) {
        let x = bd.rect.pos.x + cell.x;
        let y = bd.rect.pos.y + cell.y;
        if (value[y] === void 0) {
          value[y] = [];
        }
        if (board[y] === void 0) {
          board[y] = [];
        }
        value[y][x] = cell.value;
        board[y][x] = (cell.value == '+') ? (-1) : (+ cell.value);
      }
    }
    console.log(board);
    return board;
  }

  /**
   * ブロックのドラッグを開始したときの、イベントハンドラ。
   *  プレスしたブロックが未選択のときは、どのブロックだけ移動する。選択中のブロックがあった場合、それらはすべて選択解除してから、ドラッグ開始する。
   *  プレスしたブロックが選択中のときは、選択中のブロックすべてを、ドラッグする。
   *  ドラッグされるブロックはすべて、選択中になる。
   *
   */
  private dragstarted(d: BlockData_d3, i: number, n) {
    //console.log('dragstarted: d=', d, 'i=', i, 'n=', n, 'd3.event=', d3.event);
    if (! d.selected) { // 未選択のブロックを、いきなりドラッグ開始
      d._component.select_block(d, false, true);
    }
    //d.dragstart_pos = new Pos(d.pos.x, d.pos.y);

    d3.selectAll('g .selected')
      .each((bd: BlockData_d3, j: number) => {
        bd.dragstart_pos = new Pos(bd.pos.x, bd.pos.y);
        if (! bd.selected) {
          bd._component.select_block(bd, true, false);
        }
      });
    d3.select("#main_board")
      .attr("cursor", "grabbing");
	}

	private dragged(d: BlockData_d3, i: number, n) {
    // 第1引数はイベントではなくて、dataだった。dは常に0らしい
    //console.log('dragged', 'event=', event, 'd=', d, 'd3.event=', d3.event);
    //console.log('dragged', d, i, n, 'd3.event=', d3.event);
    //d3.select(this).attr("cx", d.x = event.x).attr("cy", d.y = event.y);
    if (d3.event.sourceEvent.ctrlKey &&  // ctrl + drag
        d._component.construction_mode()) { // 問題作成モードである
      // 複製する
      //console.log('ctrl');
      // ドラッグ元の位置に、元のブロックを、テンポラリとして表示する
      if (! d._component.dragstart_block_visible) {
        let selection = d3.selectAll('#main_board')
        for (let bd of d._component.selected_blocks()) {
          //d._component.show_dragstart_block(bd);
          let temp_bd = d._component.duplicate_mino(bd, bd.id + '-temp_drag');
          temp_bd.temporally = true;
          temp_bd.selected = false;
          d._component.update_mino(selection, temp_bd, temp_bd.id);
        }
        d._component.dragstart_block_visible = true;
      }
    }
    //let blocks = (d.selected) ? d._component.selected_blocks() : [n[i]];
    //console.log('dragged: blocks=', blocks);
    d3.selectAll('g .selected')
      //.attr('x', d3.event.x)  // gなので、x,yでは移動しない
      //.attr('y', d3.event.y)
      .attr('transform', (bd: BlockData_d3, j) => {
        //console.log('d=', d);
        bd.pos.x += d3.event.dx;
        bd.pos.y += d3.event.dy;
        return `translate(${bd.pos.x}, ${bd.pos.y})`;
      });
	}

	//private dragended(event, d, n) {
  private dragended(d: BlockData_d3, i: number, n) {
    //console.log('dragended: d=', d, 'i=', i, 'n=', n, 'd3.event=', d3.event);
    //console.log(d3.event.sourceEvent);
    for (let bd of d._component.selected_blocks()) {
      bd._component.hide_dragstart_block();
      let node = d3.select('#my_svg').node() as any;
      let r = node.getBoundingClientRect();
      // 左・上方向ではみ出すのを防ぐ
      bd.pos.x = Math.max(0, Math.round((bd.pos.x) / Cell.width ) * Cell.width);
      bd.pos.y = Math.max(0, Math.round((bd.pos.y) / Cell.height) * Cell.height);
      // 右・下方向ではみ出すのを防ぐ
      if (r.width < bd.pos.x + (bd.rect.lower_right.x+1) * Cell.width) {
         bd.pos.x = r.width - ((bd.rect.lower_right.x+1) * Cell.width);
         //            marginの分だけ削られている???  ^^
      }
      if (r.height < bd.pos.y + (bd.rect.lower_right.y+1) * Cell.height) {
         bd.pos.y = r.height - ((bd.rect.lower_right.y+1) * Cell.height);
      }
      //bd.block.pos.x = Math.round(bd.pos.x / Cell.width);
      //bd.block.pos.y = Math.round(bd.pos.y / Cell.height);
      //bd.rect.pos.x = bd.block.pos.x;  // 同じデータが2箇所にある???重複
      //bd.rect.pos.y = bd.block.pos.y;
      bd.move_to(Math.round(bd.pos.x / Cell.width),
                 Math.round(bd.pos.y / Cell.height));
      // ctrl + dragのときは、ブロックを複製する
      if (d3.event.sourceEvent.ctrlKey &&  // ctrl + drag
          d._component.construction_mode()) { // 問題作成モードである
        // 複製する
        // ドラッグ先には、新しいブロック・オブジェクトが作られる
        let new_bd = bd._component.duplicate_mino(bd);
        // ドラッグ元は、以前のままブロックオブジェクトで、座標も元に戻す
        if (bd.dragstart_pos === void 0) {
          console.log('BUG', bd);
        }
        bd.pos.x = bd.dragstart_pos.x;
        bd.pos.y = bd.dragstart_pos.y;
        delete bd.dragstart_pos;
        bd.block.pos.x = Math.round(bd.pos.x / Cell.width);
        bd.block.pos.y = Math.round(bd.pos.y / Cell.height);
        bd._component.unselect_block(bd);
      }
    } // for
    d._component.update_all_blocks();
    //d3.select(n[i])
    d3.selectAll('g .selected')
      .transition()
      .ease(d3.easeCircleOut)
      .duration(this.transitionTime)
      .attr('transform', (d: BlockData_d3, i) => {
        return `translate(${d.pos.x}, ${d.pos.y})`;
      });
    d3.select("#main_board")
      .attr("cursor", "grab"); // https://developer.mozilla.org/ja/docs/Web/CSS/cursor
    //console.log('dragended DONE', d._component.blocks_on_board);
	}

  private mouseover(d, i, n) {
    //console.log('mouseover', d, i);
    d3.select("#main_board")
      .attr('cursor', 'grab');
  }

  private mouseout(d, i, n) {
    //console.log('mouseout');
    d3.select("#main_board")
      .attr('cursor', 'default');
  }

  private keydown(d, i, n) {
    //console.log('keydown');
    //console.log(d3.event);
    if (d3.event.key == 'Shift') {
      d3.select("#main_board")
        .attr('cursor', 'default');
    }
  }

  private keyup(d, i, n) {
    //console.log('keyup', d, i, n, d3.event);
    if (d3.event.key == 'Delete') {
      let _component: BoardEditComponent = undefined;
      d3.select('#my_base')
        .each((d2) => { _component = d2 as BoardEditComponent; });

      _component.delete_selected_mino();
    }
  }

/*
  //private show_dragstart_block(bd: BlockData) {
  private show_dragstart_block(bd: BlockData_d3) {
    if (!this.dragstart_block_visible) {
      this.dragstart_block_visible = true;
      //console.log('bd=', bd);
      //let bd_src = bd.dup();
      //let selection = d3.selectAll("#main_board");
      //this.draw_mino(selection, bd, 'temp_drag');
      let temp_bd = this.duplicate_mino(bd, bd.id + '-temp_drag');
      temp_bd.temporally = true;
    }
  }
*/
  private hide_dragstart_block() {
    if (this.dragstart_block_visible) {
      this.dragstart_block_visible = false;
      //d3.selectAll('#temp_drag')
      d3.selectAll('g .temporally')
        .each((d: BlockData_d3, i) => {
          let idx = this.blocks_on_board.indexOf(d);
          if (-1 < idx) {
            this.blocks_on_board.splice(idx, 1);
          }
          //console.log('hide', d, i, 'idx=', idx);
        })
        .remove();
    }
  }

  /**
   * ブロックのセルに文字列を設定する。
   *  index ブロック内のセルを指すインデックス値。
   */
  private set_cell_label(block_id: string, index: number, block_data: BlockData_d3) {
    //console.log('set_cell_label: block_id=', block_id, 'index=', index, 'block_data=', block_data);
    let have_value: boolean = block_data.rect.set_value(index, this.in_number);
    //let selection = d3.select('g #' + block_id);
    let selection = d3.select("#main_board");
    this.update_mino(selection, block_data, block_id);
  }

  /** add = 追加選択 */
  private select_block(block_data: BlockData_d3, add: boolean = false, update: boolean = true, always: boolean = false) {
    //console.log('select_block: block_id=', block_id, 'index=', index, 'block_data=', block_data, 'add=', add);
    let block_id: string = block_data.id;
    if (! add) {
      this.unselect_all_blocks([block_id]);
    }
    if (always) {
      block_data.selected = true; // 選択する
    } else if (block_data.dragstart_pos !== void 0) { // drag開始している
       /*
        1. drag開始イベント発生後は、ブロックは選択中になる
        2. ボタンをリリースすると、clickイベント発生。このselect_blockが呼ばれる
        3. drag終了イベントが発生していないなら、ただのclickである。
        4. drag終了イベントが発生したなら、clickイベントは発生しないはずである。
        */
        //delete block_data.dragstart_pos; // dragは中止である
        block_data.selected = true; // 選択する
    } else {
      // ここは実行されないはず？？？ そうでもない。未選択のセルをいきなりドラッグ開始したとき、ここにくる
      //console.log('select_block: BUG?')
      block_data.selected = ! block_data.selected;
    }
    //let selection = d3.select("#main_board");
    //this.update_mino(selection, block_data, block_id);
    if (update) {
      this.update_all_blocks();
    }
  }

  private unselect_block(block_data: BlockData_d3) {
    block_data.selected = false;
  }

  private unselect_all_blocks(excludes: string[] = []) {
    //console.log('unselect_all_blocks', this.blocks_on_board);
    let selection = d3.select("#main_board");
    for (let bd of this.blocks_on_board) {
      if (excludes.includes(bd.id)) {
        // 除外する
      } else {
        bd.selected = false;
      }
    }
  }

  /** すべてのブロックを再描画する */
  private update_all_blocks() {
    //console.log('update_all_blocks');
    let selection = d3.select("#main_board");
    for (let bd of this.blocks_on_board) {
      this.update_mino(selection, bd, bd.id);
    }
  }

  private on_click_cell_text(d: Cell, i: number, n): void {
    //console.log('on_click_cell_text: d=', d, 'i=', i, 'n=', n, 'd3.event=', d3.event);
    let _component: BoardEditComponent = undefined;
    d3.select('#my_base')
      .each((d) => { _component = d as BoardEditComponent; });
    _component.on_click_cell_main(d, i, n);
  }

  private on_click_cell(data: Cell, index: number, elem): void {
    //console.log('on_click_cell: d=', data, 'i=', index, 'elem=', elem, 'd3.event=', d3.event);
    let _component: BoardEditComponent = undefined;
    d3.select('#my_base')
      .each((d) => { _component = d as BoardEditComponent; });
    _component.on_click_cell_main(data, index, elem);
  }

  private on_click_cell_main(data: Cell, index: number, elem): void {
    let set_number: boolean = this.set_number_mode();
    let no_modifier_key: boolean = !d3.event.shiftKey && !d3.event.ctrlKey && !d3.event.metaKey && !d3.event.altKey;

    let block_id = elem[index].parentNode.id;
    d3.select('#' + block_id)
      .each((d: BlockData_d3, i) => {
        if (no_modifier_key && set_number) {
          // セルに文字列をセットする
          //console.log(d);
          this.unselect_block(d);
          this.set_cell_label(block_id, index, d);
        }
        if (! set_number) {
          let multi = (d3.event.shiftKey) ? true : false;
          // (追加で)選択する / 選択解除する
          //console.log(`select (add=${multi})`, d, i);
          this.select_block(d, multi);
          if (d.dragstart_pos !== void 0) {
            // ドラッグ中のはずが、clickイベント発生 >> ドラッグ中止
            delete d.dragstart_pos;
          }
        }
      });
  }

  private on_mouseover_cell(d: Cell, i: number, n): void {
    //console.log('on_mouseover_cell', d, i, n, d3.event);
    let cell_id = n[i].id;
    let cell_value = d.value;
    let value = (cell_value === void 0) ? '+' : cell_value;
    let x = d3.event.x;
    let y = d3.event.y;
    //console.log('on_mouseover_cell', x, y, value);
    /*
    let mb = d3.select('#main_board')
      .append('rect')
        .attr('x', x)
    */
    d3.select('#' + n[i].parentNode.id)
      .each((d: BlockData_d3, j)=>{
        let bx = d.rect.pos.x + d.rect.rect[i].x;
        let by = d.rect.pos.y + d.rect.rect[i].y;
        //console.log('cell mouseover', x, y, bx, by, value, i, d.rect.rect[i]);
        d._component.hover_number = `Board[${bx}, ${by}]=${value}`;

        let cursor = (d._component.set_number_mode()) ? 'default' : null/*'grab'*/;
        d3.select('#' + cell_id)
          .attr('cursor', cursor);
      });
  }

  private on_mouseover_cell_text(d: Cell, i: number, n): void {
    console.log('on_mouseover_cell_text', d, i, n, d3.event);
  }

  private on_click_my_base(d: BoardEditComponent, i, n) {
      // d は　BoardEditComponent
      //console.log('on_click_my_base: d=', d, 'i=', i, 'n=', n, 'd3.event=', d3.event, 'this=', this);
      if (d.draw_line_mode()) {
        let num = + d.in_number;  // string -> int
        if (0 < num) {
          //d.put_line_cell(d3.event.x, d3.event.y);  // どこが原点なのか不明
          //console.log('d3.mouse:', d3.mouse(n[i]));
          let xy = d3.mouse(n[i]);
          let cx = Math.floor((xy[0] - d.margin.left) / d.cell_width);
          let cy = Math.floor((xy[1] - d.margin.top ) / d.cell_height);
          //let cx = Math.round((xy[0] - d.margin.left) / d.cell_width);
          //let cy = Math.round((xy[1] - d.margin.top ) / d.cell_height);
          //let cx = Math.round(xy[0] / d.cell_width);
          //let cy = Math.round(xy[1] / d.cell_height);
          d.put_line_cell(cx, cy, num);
        }
      }
      //console.log(this.unselect_all_blocks);
      d.unselect_all_blocks();
      d.update_all_blocks();  // 再描画
  }

  private new_mino(bd: BlockData, block_id?: string): BlockData_d3 {
    if (block_id === void 0) {
      block_id = this.next_mino_id();
    }
    return this.new_BlockData_d3(bd, block_id);
  }

  private put_mino(bd: BlockData_d3) {
    this.blocks_on_board.push(bd);
  }

  private draw_mino(selection, block_dat: BlockData, block_id?: string) {
    let bd = this.new_mino(block_dat, block_id);
    this.put_mino(bd);
    //console.log('draw_mino', block_dat, block_id)

    this.update_mino(selection, bd, block_id);
  }

  private duplicate_mino(bd: BlockData_d3, block_id?: string): BlockData_d3 {
    if (block_id === void 0) {
      block_id = this.next_mino_id();
    }
    let new_block_data: BlockData = bd.block.dup();  // マスの中の数字はコピーされない
    let new_bd = this.new_BlockData_d3(new_block_data, block_id);
    new_bd.selected = bd.selected;
    new_bd._component = bd._component;
    //this.blocks_on_board.push(new_bd);
    this.put_mino(new_bd);
    return new_bd;
  }

  private delete_selected_mino() {
    //console.log('delete_selected_mino');
    d3.select('g#main_board')
      .selectAll('g .selected')
        .each((d: BlockData_d3) => {
          d.delete_ok = false;
          //console.log(d);
          if (this.solve_mode()) {
            // solve modeでは、線セルのみ、削除可能
            if (d.block.id == 'l0') {
              d.delete_ok = true;
            }
          } else {
            d.delete_ok = true;
          }
          if (d.delete_ok) {
            let idx = this.blocks_on_board.indexOf(d);
            if (-1 < idx) {
              //console.log(idx, this.blocks_on_board[idx]);
              this.blocks_on_board.splice(idx, 1);
            }
          }
        })
        .filter((d: BlockData_d3, i: number) => {
          //console.log('filter', d);
          if (! d.delete_ok) {
            console.log('cannot delete:', d);
          }
          return d.delete_ok;
        })
        .remove();
  }

  private delete_all_mino() {
    let main_board = d3.selectAll('g#main_board')
      .selectAll('g')
        .remove();
    //console.log('delete_all_mino', main_board);
    this.blocks_on_board = [];
  }

  private put_line_cell(cx: number, cy: number, num: number, update: boolean = true) {
    //console.log('put_line_cell:', cx, cy, num);
    let block_dat = BlockData.create('l0', cx, cy);
    let id = this.next_line_cell_id();
    let bd = this.new_BlockData_d3(block_dat, id);
    bd.rect.set_value(0, '' + num);  // int --> string
    //console.log('put_line_cell: bd=', bd);
    //this.line_cell_on_board.push(bd);
    this.put_mino(bd);
    let selection = d3.selectAll("#main_board");
    if (update) {
      this.update_mino(selection, bd, id);  // 描画
    }
  }

  /** ブロックを描画する／描画を更新する */
  private update_mino(selection, dat: BlockData_d3, block_id: string) {
    //console.log('update_mino', block_id, dat);
    // ブロック全体を囲むコンテナ(g)
    //console.log('update_mino', selection.selectAll('g #' + block_id));
    let container_id = 'g #' + block_id;
    let sel_data = selection
      .selectAll(container_id)
      .data([dat]);  // dataのセットまで済んでいるselection
    sel_data
      .exit()
      .remove();  // 余計な要素は削除する
    sel_data
      .enter()
      .append('g')
      .merge(sel_data)
        .attr('id', block_id)
        .attr('class', (d, i) => d.rect.cls)
        .attr("transform", (d, i) => `translate(${d.pos.x}, ${d.pos.y})`)
        .classed('selected', (d: BlockData_d3, i) => d.selected == true)
        .classed('temporally', (d: BlockData_d3, i) => d.temporally == true)
        .call(d3.drag()
          .filter(()=> !d3.event.button && !d3.event.shiftKey)
		      .on("start", this.dragstarted)
		      .on("drag", this.dragged)
		      .on("end", this.dragended))
        .on('mouseover', this.mouseover)
        .on('mouseout', this.mouseout);
    /*
    let container = selection.selectAll(container_id);
    console.log('selection=', selection);
    console.log('sel_data =', sel_data);
    console.log('container=', container);
    */
    // セル。ブロックの1マス(rect)
    //console.log('rect add: ', dat.rect.rect, container.selectAll('rect'));
    sel_data = selection
      .selectAll(container_id)
      .selectAll('rect')
      .data(dat.rect.rect);
    //console.log('sel_data =', sel_data);
    sel_data
      .exit()
      .remove();  // 余計な要素は削除する
    //console.log('sel_data =', sel_data);
    sel_data
      .enter()
      .append('rect')
      .merge(sel_data)
        .attr('id', (d, i) => this.cell_id(block_id, i))
        .attr('x', (d, i) => d.x * this.cell_width)
        .attr('y', (d, i) => d.y * this.cell_height)
        .attr('width',  this.cell_width)
        .attr('height', this.cell_height)
        .on('click', this.on_click_cell)
        .on('mouseover', this.on_mouseover_cell);
    // セルの中の数字
    /*
    console.log('text add 0: ', dat.rect.rect, container);
    console.log('text add 1: ', dat.rect.rect, selection.selectAll(container_id));
    console.log('text add 10: ', dat.rect.rect, container.selectAll('text'));
    console.log('text add 11: ', dat.rect.rect, selection.selectAll(container_id).selectAll('text'));
    */
    //let sel_data = container
    sel_data = selection
      .selectAll(container_id)
      .selectAll('text')
      .data(dat.rect.rect);
    //console.log('sel_data =', sel_data);
    sel_data
      .exit()
      .remove();  // 余分な要素は削除する
    //console.log('sel_data =', sel_data);
    sel_data
      .enter()
      /* filterすると、text要素の個数と、データ数がズレて、おかしくなるようだ
      .filter((d: Cell, i: number) => {
        console.log('filter', d, i);
        return (d.value !== void 0 && d.value != '');
      })
      */
      .append('text')
      .merge(sel_data)
        .attr('id', (d: Cell, i) => this.cell_label_id(block_id, i)) // BLK0-0-L
        .text((d: Cell, i: number) => {
          //console.log('text', d, i);
          return (d.value === void 0) ? null : d.value;
        })
        .attr('x', (d: Cell, i) => (d.x + 0.5) * Cell.width)  // セルの中心座標に
        .attr('y', (d: Cell, i) => (d.y + 0.5) * Cell.height)
        .classed('cell-label', true)
        .raise()
        .on('click', this.on_click_cell_text)
        .on('mouseover', this.on_mouseover_cell); // 同じイベントハンドラーで処理可能

    //return container;
  }

  /** d3.jsの挙動を調査するため */
  private update_mino_EX(selection, dat: BlockData_d3, block_id: string) {
    console.log('update_mino', block_id, dat);
    // ブロック全体を囲むコンテナ(g)
    //console.log('update_mino', selection.selectAll('g #' + block_id));
    let container_id = 'g #' + block_id;
    let tmp = selection
      .selectAll(container_id)
      .data([dat])
      .enter()
      .append('g')
        .attr('id', block_id)
        .attr('class', (d, i) => d.rect.cls)
        .attr("transform", (d, i) => `translate(${d.pos.x}, ${d.pos.y})`)
        .call(d3.drag()
          .filter(()=> !d3.event.button && !d3.event.shiftKey)
		      .on("start", this.dragstarted)
		      .on("drag", this.dragged)
		      .on("end", this.dragended))
        .on('mouseover', this.mouseover)
        .on('mouseout', this.mouseout);
    // うわ〜ん、d3.jsの挙動が、よくわからない
    let container = selection.selectAll(container_id);
    console.log('selection=',selection);
    console.log('tmp      =', tmp);  // append('g')したので、selectionより先に進んでる
    console.log('container=',container);
    // たぶん、この時点では、tmpとcontainerは、同じものを指している。
    // と思ったら、セルに文字をセットしたあとで、tmpが、何か変なものを指している
    console.log(tmp.nodes().length, container.nodes().length);
    if (tmp.nodes().length == container.nodes().length) {
      console.log('compare', tmp.nodes()[0].id, container.nodes()[0].id);
    }
    // セル。ブロックの1マス(rect)
    console.log('rect add: ', dat.rect.rect, container.selectAll('rect'));
    container
      .selectAll('rect')
      .data(dat.rect.rect)
      .enter()
      .append('rect')
        .attr('id', (d, i) => {this.cell_id(block_id, i); console.log('append rect', block_id, i);})
        .attr('x', (d, i) => d.x * this.cell_width)
        .attr('y', (d, i) => d.y * this.cell_height)
        .attr('width',  this.cell_width)
        .attr('height', this.cell_height)
        .on('click', this.on_click_cell)
        .on('mouseover', this.on_mouseover_cell);
    let contain2 = selection.selectAll(container_id);
    console.log('tmp      =', tmp);
    console.log('container=',container);
    console.log('contain2 =',contain2);
    console.log(tmp.nodes().length, container.nodes().length, contain2.nodes().length);
    if (tmp.nodes().length == container.nodes().length) {
      console.log('compare', tmp.nodes()[0].id, container.nodes()[0].id, contain2.nodes()[0].id);
    }
    // セルの中の数字
    console.log('text add 0: ', dat.rect.rect, container);
    console.log('text add 1: ', dat.rect.rect, selection.selectAll(container_id));
    console.log('text add 10: ', dat.rect.rect, container.selectAll('text'));
    console.log('text add 11: ', dat.rect.rect, selection.selectAll(container_id).selectAll('text'));
    //let sel_data = container
    let sel_data = selection
      .selectAll(container_id)
      .selectAll('text')
      .data(dat.rect.rect);
    console.log('sel_data', sel_data);
    sel_data
      .exit()
      .remove(); // 余分な要素は削除する
    console.log('sel_data', sel_data);
    sel_data
      .enter()
      .filter((d: Cell, i: number) => {
        console.log('filter', d, i);
        return (d.value !== void 0 && d.value != '');
      })
      .append('text')
      .merge(sel_data)
        .attr('id', (d: Cell, i) => this.cell_label_id(block_id, i)) // BLK0-0-L
        .text((d: Cell, i: number) => {
          console.log('text', d, i);
          return (d.value === void 0) ? null : d.value;
        })
        .attr('x', (d: Cell, i) => (d.x + 0.5) * Cell.width)  // セルの中心座標に
        .attr('y', (d: Cell, i) => (d.y + 0.5) * Cell.height)
        .classed('cell-label', true)
        .raise()
        .on('click', this.on_click_cell_text);

    return container;
  }

  private draw_board() {
    let a = this.cell_width * this.board_size.x;
    let c = this.cell_height * this.board_size.y;
    //console.log('width', screen.width, window.innerWidth, document.body.clientWidth );
    //console.log('height', screen.height, window.innerHeight, document.body.clientHeight );
    let d = this.staging_area2_d; // あとで計算しなおす
    let e = window.innerWidth - this.margin.left - this.margin.right; // ???
    let f = c + d + this.margin.top + this.margin.bottom; // あとで計算しなおす
    let b = Math.max(0, Math.floor((e - this.margin.left - this.margin.right - a) / this.cell_width)) * this.cell_width;
    //console.log('a=', a, 'b=', b, 'c=', c, 'd=', d, 'e=', e);
    // append the svg object to the body of the page
    d3.select("div#my_board")
      //.append("svg")
      .select("svg#my_svg")
        .remove();
    this.svg = d3.select("div#my_board")
        .append('svg')
          .attr('id', 'my_svg')
          .attr("width",  e)
          .attr("height", f);
    this.svg_size = {a: a, b: b, c: c, d: d, e: e, f: f};
    console.log(this.svg_size);
    this.svg
      .selectAll('rect#my_base')
      .data([this])
      .enter()
      .append('rect')
        .attr('id', 'my_base')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', e)
        .attr('height', f)
        .on('click', this.on_click_my_base)
    this.g = this.svg
      .append("g")
        .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`)
        .attr('id', 'main_board');
    // 横方向、10マス間隔で、目盛を描画
    for (let i=0; i<=this.board_size.x; i+=10) {
      this.svg
        .append('line')
          .attr('id', 'tick-x-' + i)
          .attr('x1', i * this.cell_width + this.margin.left)
          .attr('y1', 0)
          .attr('x2', i * this.cell_width + this.margin.left)
          .attr('y2', this.cell_height / 4)
          .classed('tick', true);
    }
    // 縦方向、10マス間隔で、目盛を描画
    for (let i=0; i<=this.board_size.y; i+=10) {
      this.svg
        .append('line')
          .attr('id', 'tick-y-' + i)
          .attr('x1', 0)
          .attr('y1', i * this.cell_height + this.margin.top)
          .attr('x2', this.cell_width / 4)
          .attr('y2', i * this.cell_height + this.margin.top)
          .classed('tick', true);
    }
    // 横方向の限界
    this.svg
      .append('line')
        .attr('id', 'border-line-right')
        .attr('x1', this.board_size.x * this.cell_width + this.margin.left)
        .attr('y1', 0)
        .attr('x2', this.board_size.x * this.cell_width + this.margin.left)
        .attr('y2', this.board_size.y * this.cell_height + this.margin.top)
        .classed('tick', true);
    // 縦方向の限界
    this.svg
      .append('line')
        .attr('id', 'border-line-bottom')
        .attr('x1', 0)
        .attr('y1', this.board_size.y * this.cell_height + this.margin.top)
        .attr('x2', this.board_size.x * this.cell_width + this.margin.left)
        .attr('y2', this.board_size.y * this.cell_height + this.margin.top)
        .classed('tick', true);
    //console.log(block_data);
    let selection = d3.select("#main_board");

    d3.select('body')
      .on('keydown', this.keydown)
      .on('keyup', this.keyup);
    this.d3_brush =
      d3.brush()
        .extent([[0, 0], [e, f]])
        /*
        .on('start', (d, i, n) => {
          console.log('brush start', d, i, n, d3.event.selection);
        })
        */
        .on('end', this.on_brush_end);
  }

  enable_brush() {
    this.svg
      .call(this.d3_brush);
  }

  disable_brush() {
    this.svg.on('.brush', null); // event listenerを消す？
    //bec.svg.attr('cursor', 'default');
    this.svg.selectAll('.overlay').remove();
    this.svg.selectAll('.selection').remove();
    this.svg.selectAll('.handle').remove();
    this.edit_mode['select_blocks'] = false;
    this.edit_modes[2].selected = false;  // [2]がわかりにくい
  }

  static get_component(): BoardEditComponent {
    let _component: BoardEditComponent = undefined;
    d3.select('#my_base')
      .each((d2) => { _component = d2 as BoardEditComponent; });
    return _component;
  }

  on_brush_end(d, i, n) {
    //console.log('brush end', d, i, n, d3.event.selection);
    if (d3.event.selection === null) {
      return;
    }
    let bec = BoardEditComponent.get_component();
    let x0 = d3.event.selection[0][0] - bec.margin.left;
    let y0 = d3.event.selection[0][1] - bec.margin.top;
    let x1 = d3.event.selection[1][0] - bec.margin.left;
    let y1 = d3.event.selection[1][1] - bec.margin.top;
    let blocks: BlockData_d3[] = bec.blocks_in_range(x0, y0, x1, y1);
    //console.log(blocks);
    bec.unselect_all_blocks();
    for (let bd of blocks) {
      bec.select_block(bd, true, false, true);
    }
    bec.svg.call(bec.d3_brush.move, null);
    bec.disable_brush();
    bec.update_all_blocks();  // 再描画
  }

  constructor(private adcService: AdcService) {
    Cell.width = this.cell_width;
    Cell.height = this.cell_height;
    this.qData = new QData();
    this.aData = new AData();
  }

  ngOnInit(): void {
    this.draw_board();

    let block_data: BlockData[] = this.get_parts_block_data();
    //let block_data = this.all_block_data();
    let data = this.initial_blocks(block_data);
    this.put_blocks_on_staging_area(data);
  }

  ngOnChanges(changes: SimpleChanges) {
    console.log('ngOnChanges', changes)
  }

  input_number(): void {
    console.log('input_number:', this.in_number);
  }

  onClick_config() {
    //console.log('readQ');
    this.do_config = true;
  }

  onClick_config_Cancel() {
    this.do_config = false;
    this.board_size_temp.x = this.board_size.x;
    this.board_size_temp.y = this.board_size.y;
  }

  onClick_config_OK() {
    this.do_config = false;
    if (this.construction_mode()) {
      this.board_size.x = + this.board_size_temp.x; // string --> int
      this.board_size.y = + this.board_size_temp.y;
      this.relayout_staging_area();
    }
    if (this.solve_mode()) {
      this.board_size_temp.x = this.board_size.x;
      this.board_size_temp.y = this.board_size.y;
    }
    //console.log(this.board_size, this.board_size_temp);
  }

  onClick_readQ() {
    //console.log('readQ');
    this.adcService.clearText1();
    this.do_readQFile = true;
  }

  onClick_readQ_OK() {
    //console.log('onClick_readQ_OK');
    this.do_readQFile = false;
    this.qData.parse(this.adcService.text1);
    //console.log(`Q　${this.qData.size} ${this.qData.block_num}`, this.qData.block_type, this.qData.block_size, this.qData.block_data);
    this.delete_all_mino();
    //this.update_all_blocks();  // 再描画
    //return;
    let q = this.qData;
    let pos = new Pos(0, 0);
    let blocks: BlockData_d3[] = [];
    for (let i=1; i<= q.block_num; i++) {
      let id = this.next_mino_id();
      let bd: BlockData_d3 = BlockData_d3.from_QData(q.block_type[i], q.block_size[i], q.block_data[i], pos, id, this);
      bd.block_num = i;
      blocks.push(bd);
      //console.log(pos, bd);
      //this.blocks_on_board.push(bd);  // ブロックを盤に追加
      //pos.x += q.block_size[i][0];
      //if (this.max_block_num.x < pos.x) {
      //  pos.x = 0;
      //  pos.y += 4;
      //}
    }
    this.put_blocks_on_staging_area(blocks);
    this.board_size.x = q.size[0];
    this.board_size.y = q.size[1];
    this.board_size_temp.x = q.size[0];
    this.board_size_temp.y = q.size[1];
    // 再描画
    this.draw_board();
    this.update_all_blocks();
  }

  onCleared_openQFile(c: boolean) {
    console.log('onCleared_readQ', c);
  }

  openQFile() {
    console.log('openQFile');
  }

  onClick_readA() {
    //console.log('readQ');
    this.adcService.clearText1();
    this.adcService.clearText2();
    this.do_readAFile = true;
  }

  onClick_readA_OK() {
    //console.log('onClick_readA_OK');
    if (this.do_readQFile && this.adcService.text1 !== void 0) {
      // Qデータも同時に読み込む
      this.onClick_readQ_OK();
    }
    this.do_readAFile = false;
    //console.log(this.adcService.text2);
    this.aData.parse(this.adcService.text2);
    console.log('aData', this.aData);
    // ブロックをA-dataで指定された座標へ移動する
    for (let bd of this.blocks_on_board) {
      if (bd.block_num !== void 0) { // BLOCK#番号 が指定されている
        let cxy: number[] = this.aData.get_block_pos(bd.block_num);
        //console.log(bd.block_num, cxy[0], cxy[1]);
        bd.move_to(cxy[0], cxy[1], true);
      }
    }
    let board = this.get_board();
    for (let y = 0; y < this.aData.size[1]; y ++) {
      for (let x = 0; x < this.aData.size[0]; x ++) {
        let a_n = this.aData.board[y][x];
        let b_n = board[y][x];
        if (b_n === void 0) {
          b_n = 0;
        }
        if (a_n != 0) {
          if (b_n == 0) {
            // 線セルを配置する
            this.put_line_cell(x, y, a_n, false);
          }
        }
      }  // for x
    }  // for y
    this.update_all_blocks();  // 再描画
  }


  onCleared_openAFile(c: boolean) {
    console.log('onCleared_readA', c);
  }


  onClick_refresh() {
    //console.log('refresh');
    this.relayout_staging_area();
  }

  onResize(event) {
    //console.log('onResize', event);
    this.relayout_staging_area();
  }

  onClick_writeA() {
    //console.log('onClick_writeA');
    let bd_on_board: BlockData_d3[] = this.get_blocks_on_board();
    //console.log(bd_on_board);
    let a_data: string = '';
    a_data += `A${this.q_number}\n`;
    a_data += `SIZE ${this.board_size.x}X${this.board_size.y}\n`;
    let board: string[][] = [];
    for (let y = 0; y < this.board_size.y; y ++) {
      let tmp: string[] = Array(this.board_size.x);
      for (let x = 0; x < this.board_size.x; x ++) {
        tmp[x] = '0';
      }
      board.push(tmp);
    }
    let a_data2 = '';
    let block_num = 1;
    let renumber = false;
    for (let bd of bd_on_board) {
      if (bd.block.id != 'l0') {  // ラインのセルではない
        if (bd.block_num === void 0) {
          // (BLOCK#番号の指定がない)Qデータ由来ではなく、Constructionモードで追加されたブロック
          renumber = true;
          break;
        }
      }
    }
    //console.log('renumber=', renumber);
    for (let bd of bd_on_board) {
      if (bd.block.id != 'l0') {  // ラインのセルではない
        let n: number = (renumber) ? (block_num++) : bd.block_num;
        a_data2 += `BLOCK#${n} @(${bd.rect.pos.x},${bd.rect.pos.y})\n`;
      }
      for (let cell of bd.rect.rect) {
        let value: string;
        if (cell.value === void 0 || cell.value == '+') {  // undefined
          value = '+';
        } else {
          value = '' + cell.value;
        }
        let x = bd.rect.pos.x + cell.x;
        let y = bd.rect.pos.y + cell.y;
        //console.log(x, y, value);
        board[y][x] = value;
      }
    }
    for (let y = 0; y < this.board_size.y; y ++) {
      for (let x = 0; x < this.board_size.x; x ++) {
        if (x != 0) {
          a_data += ',';
        }
        a_data += ('   ' + board[y][x]).slice(-3)
      }
      a_data += '\n';
    }
    a_data += a_data2;
    //console.log(board);
    //console.log(a_data);
    let filename = `A${this.q_number}.txt`;
    this.adcService.downloadFile(a_data, 'text/plain', filename);
  }

  onClick_writeQ() {
    //console.log('onClick_writeQ');
    let bd_on_board: BlockData_d3[] = this.get_blocks_on_board();
    //console.log(bd_on_board);
    let block_num = 1;
    let q_data2 = '';
    for (let bd of bd_on_board) {
      if (bd.block.id != 'l0') {  // ラインのセルではない
        q_data2 += '\n';
        let size: number[] = bd.block_size();
        q_data2 += `BLOCK#${block_num} ${size[0]}X${size[1]}\n`;
        block_num ++;
        q_data2 += bd.block_text();
      }
    }
    let q_data = `SIZE ${this.board_size.x}X${this.board_size.y}\n`;
    q_data += `BLOCK_NUM ${block_num - 1}\n`;
    q_data += q_data2;
    //console.log(q_data);
    let filename = `Q${this.q_number}.txt`;
    this.adcService.downloadFile(q_data, 'text/plain', filename);
  }
}
