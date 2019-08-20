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
