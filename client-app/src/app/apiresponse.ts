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
  public static enabledDescrTbl = {
    0: 'manual state transition',
    1: 'automatic state transition, depending on current time'
  };
  public static stateDescrTbl = {
    'init': 'initial',
    'im0': 'intermission (0)',
    'Qup': 'You can upload Q data.',
    'im1': 'intermission (1)',
    'Aup': 'You can upload A data.',
    'im2': 'intermission (2)',
  }

  constructor(
    public enabled: number,
    public state: string,
    public lastUpdate: Date) { }
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

export class AdminQList { // API: '/admin/Q/list', datastore kind: 'q_list_all'
  constructor(
    public author_list: number[],
    public author_qnum_list: number[],
    public blocknum_list: number[],
    public cols_list: number[],
    public date: Date,
    public linenum_list: number[],
    public qnum_list: number[],
    public rows_list: number[],
    public text_admin: string,
    public text_user: string
  ) { }

  public static empty(): AdminQList {
    return new AdminQList([], [], [], [], new Date(), [], [], [], '??', '?');
  }
}

