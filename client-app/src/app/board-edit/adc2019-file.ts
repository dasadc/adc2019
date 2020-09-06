// based on adc2019.py

export class BlockType {
  type: string; // tetromino='a', 'b', 'c', 'd', 'e', 'f', 'g', monomino='z'
  index: number;
};

export class QData {

  size: number[] = [0, 0];
  block_num: number = 0;
  block_size: number[] = [];
  block_data: number[][][] = [];
  //block_type: BlockType[] = [];
  block_type: string[] = [];
  line_num: number = 0;

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
  static blocks = {
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
    'l0': ['X   ', '    ', '    ', '    '] ,
    'l1': ['X   ', '    ', '    ', '    '] ,
    'l2': ['X   ', '    ', '    ', '    '] ,
    'l3': ['X   ', '    ', '    ', '    '] ,
  };

  public parse(q_data: string) {
    //console.log(q_data);
    this.size = [0, 0];
    this.block_num = 0;
    this.line_num = 0;

    let input_line_cnt = 0
    let in_block = false;
    let block_size_x = 0;
    let block_size_y = 0;
    let dict_block_size = [];
    let dict_block_data = [];
    let block_tmp = [];
    let block_num_tmp = 0;
    let re_SIZE      = /SIZE\s+([0-9]+)X([0-9]+)/i;
    let re_BLOCK_NUM = /BLOCK_NUM\s+([0-9]+)/i;
    let re_BLOCK     = /BLOCK#([0-9]+)\s+([0-9]+)X([0-9]+)/i;
    q_data += '\n\n'  // for make possible to detect end of data
    let lines = q_data.split(/\r?\n/);

    let add_block = () => {
      //console.log('add_block');
      in_block = false;
      //    block_size[1] = (x,y) of "BLOCK#1 xXy"
      dict_block_size[block_num_tmp] = [block_size_x, block_size_y];
      //    block_data[1] = body data of "BLOCK#1 xXy"
      dict_block_data[block_num_tmp] = block_tmp; // ??????
      //console.log(`BLOCK ${block_num_tmp}, ${block_size_x} X ${block_size_y}`, block_tmp);
      this.block_type[block_num_tmp] = QData.match_block_shape(block_tmp);
      //console.log(this.block_type[block_num_tmp], block_tmp);

      if (block_tmp.length != block_size_y ||
          block_tmp[0].length != block_size_x) { // テキトー
        throw `check-Q3: inconsistent block size: BLOCK ${block_num_tmp}, ${block_size_x} X ${block_size_y}`;
      }
      block_num_tmp = 0;
      block_tmp = [];
    }

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
      input_line_cnt += 1;
      //console.log(input_line_cnt, line);
      line = line.trim();
      if (line == '') {
        if (in_block) {
          add_block();
        }
        continue;
      }
      let m = line.match(re_SIZE);
      if (m) {
        //console.log('m=', m);
        this.size[0] = + m[1];  // 文字列 --> 数値
        this.size[1] = + m[2];
        continue;
      }
      m = line.match(re_BLOCK_NUM);
      if (m) {
        //console.log('m=', m);
        this.block_num = + m[1];  // 文字列 --> 数値
        continue;
      }
      m = line.match(re_BLOCK);
      if (m) {
        //console.log('m=', m);
        if (in_block) {
          add_block();
        }
        in_block = true;
        block_num_tmp = + m[1];  // 文字列 --> 数値
        block_size_x = + m[2];
        block_size_y = + m[3]
        if (1 <= block_num_tmp && block_num_tmp <= this.block_num) {
          continue;
        } else {
          throw `invalid block number: ${block_num_tmp} <--- [1, ${this.block_num}]`;
        }
      }
      if (in_block) {
        let tmp: number[] = [];
        let r = 0;
        for (let c of line.split(',')) {
          c = c.trim();
          //console.log('c=', c);
          if (c == '+') {
            r = -1;  // block without number
          } else {
            r = + c; // 0 = not block, otherwise block with number
          }
          tmp.push(r);
          this.line_num = Math.max(this.line_num, r);
        }
        block_tmp.push(tmp);
        continue;
      }
      console.log('Warning: Unknown line: ${input_line_cnt}: ${line}');
    } // for
    if (! (dict_block_size.length == this.block_num + 1 &&
           dict_block_data.length == this.block_num + 1)) {
      console.log('block_size', dict_block_size);
      console.log('block_data', dict_block_data);
      throw `check-Q6: inconsistent block definition: ${this.block_num}, ${dict_block_size.length}`;
    }
    this.block_size = dict_block_size;
    this.block_data = dict_block_data;
  }

  private static match_block_shape(block_dat: number[][]): string {
    for (let k of Object.keys(QData.blocks)) {
      let ref = QData.blocks[k];
      //console.log('match_block_shape:', k, ref, block_dat);
      let match = true;
      for (let y=0; y<ref.length; y++) {
        for (let x=0; x<ref[y].length; x++) {
          let cell_is_empty: boolean = (block_dat[y] === void 0 || block_dat[y][x] == 0 || block_dat[y][x] === void 0);
          //let tmp = (block_dat[y] && block_dat[y][x]) ? block_dat[y][x] : '?';
          //console.log(`(${x}, ${y}) ${ref[y][x]} ${tmp} ${cell_is_empty}`);
          if (ref[y][x] == ' ') {  // 空き地
            if (cell_is_empty) {
              // 空き地である ---> OK
            } else {
              // NG
              match = false;
              continue;
            }
          } else {  // 空き地ではない
            if (cell_is_empty) {
              // 空き地である ---> NG
              match = false;
              continue;
            }
          }
        } // for x
        if (! match) continue;
      } // for y
      if (! match) continue;
      return k;
    }
    return '???';
  }

  constructor() {
    // https://stackoverflow.com/questions/1418050/string-strip-for-javascript
    if(typeof(String.prototype.trim) === "undefined")
    {
      String.prototype.trim = function()
      {
        return String(this).replace(/^\s+|\s+$/g, '');
      };
    }
  }
};
