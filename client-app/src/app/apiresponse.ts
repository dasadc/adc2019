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
  public static roundDescrTbl = {
    1: 'round 1, preliminary contest (予選, 事前協議, 「長時間用の問題」に挑戦)',
    2: 'round 2, main contest (本戦, 本番競技, 「短時間用問題」と「参加者自作問題」に挑戦)',
    999: 'round 999, test (自動運営システムのシステムの動作テスト中)'
  };

  constructor(
    public enabled: number,
    public state: string,
    public round: number,
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

export class ResUserInfo {
  constructor(
    public username: string,
    public displayname: string,
    public uid: number,
    public gid: number
  ) { }
}
