export class ResLogin {
  constructor(
    public msg: string,
    public token: string) { }
}

export class ResLogout {
  constructor(
    public msg: string) { }
}

export class ResMsgOnly {
  constructor(
    public msg: string) { }
}

export class ResTimekeeper {
  constructor(
    public enabled: number,
    public lastUpdate: Date, //string,
    public state: string) { }
}

export class UserQEntry {
  constructor(
    public qnum: number,
    public cols: number,
    public rows: number,
    public blocknum: number,
    public linenum: number,
    public date: Date,
    public filename: string) { }
}

export class ResUserQList {
  constructor(
    public entries: UserQEntry[]) { }
}

export class QNumberList {
  constructor(
    public msg: string,
    public qnum_list: number[],
    public cols_list: number[],
    public rows_list: number[],
    public blocknum_list: number[],
    public linenum_list: number[]
  ) { }
}

export class ANumberList {
  constructor(
    public msg: string,
    public anum_list: number[],
  ) { }
}

export class QData {
  constructor(
    public author: string,
    public author_qnum: number,
    public author_filename: string,
    public author_date: Date,
    public qnum: number,
    public cols: number,
    public rows: number,
    public blocknum: number,
    public linenum: number,
    public text: string
  ) { }
}
