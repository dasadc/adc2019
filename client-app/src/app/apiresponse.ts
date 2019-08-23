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
