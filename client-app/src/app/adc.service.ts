import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { readFile } from './rx-file-reader';
import { CheckResults } from './checkresults';
import { ResLogin, ResLogout, ResMsgOnly, ResTimekeeper, UserQEntry, ResUserQList } from './apiresponse';

const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' })
};

@Injectable({
  providedIn: 'root'
})
export class AdcService {
  text1: string; // Q
  text2: string; // A
  filename1: string;
  filename2: string;

  // for ADC API
  username: string;
  access_token: string; // given from ADC server after login
  dummy_login_failed: boolean = false;

  //constructor(private messageService: MessageService) { }
  constructor(private http: HttpClient) { }

  readFile1(file: File): Observable<string> {
    this.filename1 = file.name;
    return readFile(file)
      .pipe(
	tap((txt: string) => {
	  this.text1 = txt;
	  //console.log('readFile1', txt);
	})
      );
    //return readFile(file).subscribe(txt => this.text1 = txt);
    //return readFile(file).subscribe((txt) => { this.txt = txt; console.log(txt); });
    /*
    return readFile(file)
      .subscribe((txt) => {
	this.text1 = txt;
	this.messageService.add(txt);
      });
    */
  }

  readFile2(file: File): Observable<string> {
    this.filename2 = file.name;
    //return readFile(file).subscribe(txt => this.text2 = txt);
    return readFile(file)
      .pipe(
	tap((txt: string) => {
	  this.text2 = txt;
	  //console.log('readFile2', txt);
	})
      );
  }

  clearText1() {
    this.filename1 = undefined;
    this.text1 = undefined;
  }

  clearText2() {
    this.filename2 = undefined;
    this.text2 = undefined;
  }

  /** checkFilesの後処理。テキストメッセージを整形する。 */
  formatResultText(res: Object): string {
    let txt = '';
    if ('error' in res) {
      txt += 'ERROR\n';
      let e: [string] = res['error']
      for (let i=0; i <e.length; i++) {
	txt += '[' + i + '] ' + e[i] + '\n';
      }
      txt += res['stack_trace'];
    } else {
      ['check_file', 'area', 'dim', 'line_corner', 'line_length', 'ban_data', 'corner', 'count'].forEach(key => {
	if (key in res) {
	  txt += key + '\n' + res[key] + '\n\n';
	}
      });
      if ('terminal' in res) {
	txt += 'terminal\n';
	let terminal: [[]] = res['terminal'];
	for (let i=0; i < terminal.length; i++) {
	  txt += i + ':';
	  for (let j=0; j < terminal[i].length; j++) {
	    txt += ' BLOCK ' + terminal[i][j]['block'];
	    txt += ' (' + terminal[i][j]['xy'][0] + ',' + terminal[i][j]['xy'][1] + ') ';
	  }
	  txt += '\n';
	}
      }
    }
    return txt;
  }

  /** POST */
  checkFiles(): Observable<Object> {
    let data = {Q: this.text1,
		A: this.text2};
    //console.log('data', data);
    //return this.http.post<Object>('http://127.0.0.1:4280/api/test_post', data, httpOptions).pipe( // !!CORS!!
    return this.http.post<Object>('/api/check_file', data, httpOptions)
      .pipe(
	map((res: Object) => {
	  //this.log(`checkFiles: res=${res}`);
	  //console.log('AdcService: checkFiles', res);
	  let txt = this.formatResultText(res);
	  return new CheckResults(txt, this.text1, this.text2);
	}),
	catchError(this.handleError<Object>('checkFiles'))
      );
  }

  /**
   * https://angular.jp/tutorial/toh-pt6
   *
   * 失敗したHttp操作を処理します。
   * アプリを持続させます。
   * @param operation - 失敗した操作の名前
   * @param result - observableな結果として返す任意の値
   */
  private handleError<T> (operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      // TODO: リモート上のロギング基盤にエラーを送信する
      //console.error(error); // かわりにconsoleに出力

      // TODO: ユーザーへの開示のためにエラーの変換処理を改善する
      //this.log(`${operation} failed: ${error.message}`);
      //console.log(`${operation} failed: ${error.message}`);
      //console.log(`${operation} failed: ${error['msg']}`);
      console.log('handleError: result=', result);
      result['msg'] = error.error.msg + '\n' + `${operation} failed: ${error.message}`;

      // 空の結果を返して、アプリを持続可能にする
      return of(result as T);
    };
  }

  /** Serviceのメッセージを記録 */
  private log(message: string) {
    //console.log(`AdcService: ${message}`);
    console.log('AdcService:', message);
  }

  getUsername(): string {
    if (this.username === void 0) {
      this.whoami()
	.subscribe((res: ResMsgOnly) => {
	  this.username = res.msg;
	});
    } // 非同期処理なので、おそらく１発めはundefinedのまま。ダメじゃん…
    return this.username;
  }

  async getUsernameAsync() {
    const response = await this.whoami().toPromise();
    console.log('getUsernameAsync: ', response);
    return response['msg'];
  }

  async getUsername2() {
    if (this.username) {
      return this.username;
    } else {
      return await this.getUsernameAsync();
    }
  }

  getAccessToken(): string {
    //console.log(this.access_token, this.dummy_login_failed == false);
    if (this.access_token === void 0 && this.dummy_login_failed == false) {
      // ダミーのloginを行い、もしもsessionによって認証されたら、tokenがもらえる
      let data = {'username': 'dummy',
		  'password': 'dummy'};
      this.http.post<Object>('/api/login', data, this.apiHttpOptions())
	.subscribe((res: Object) => {
	  this.access_token = res['token'];
	}, (err) => {
	  console.log('AdcService: getAccessToken ERROR', err);
	  this.dummy_login_failed = true;
	});
    } // 非同期処理なので、おそらく１発めはundefinedのまま。ダメじゃん…
    return this.access_token;
  }


  /** API呼び出し時に指定するHTTPヘッダー */
  private apiHttpOptions(): Object {
    let tmp = {'Content-Type': 'application/json'};
    if (this.username && this.access_token) {
      tmp['ADC-USER'] = this.username;
      tmp['ADC-TOKEN'] = this.access_token;
    }
    return {headers: new HttpHeaders(tmp)};
  }


  /** ADCサービスにログインしてトークンをもらう */
  loginADCservice(token:string, username:string, password:string): Observable<ResLogin> {
    this.username = username;
    this.access_token = token;
    let data = {'username': username,
		'password': password};
    return this.http.post<Object>('/api/login', data, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: loginADCservice', res);
	  let r = new ResLogin(res['msg'], res['token']);
	  this.access_token = r.token;
	  return r;
	}),
	catchError(this.handleError<ResLogin>('loginADCservice', new ResLogin('', 'ERROR')))
      );
  }

  /** ダミーのloginを行い、もしもsessionによって認証されたら、tokenがもらえる。 */
  getAccessTokenFromServer(): Observable<ResLogin> {
    let data = {'username': 'dummy',
		'password': 'dummy'};
    return this.http.post<Object>('/api/login', data, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: loginADCservice', res);
	  let r = new ResLogin(res['msg'], res['token']);
	  this.access_token = r.token;
	  return r;
	}),
	catchError(this.handleError<ResLogin>('getAccessTokenFromServer', new ResLogin('', 'ERROR')))
      );
  }

  /** ADCサービスからログアウトする */
  logoutADCservice(): Observable<ResLogout> {
    this.username = undefined;
    this.access_token = undefined;
    this.dummy_login_failed = false;
    let data = {}; // dummy
    return this.http.post<Object>('/api/logout', data, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: logoutADCservice', res);
	  let r = new ResLogout(res['msg']);
	  this.access_token = undefined;
	  return r;
	}),
	catchError(this.handleError<ResLogout>('logoutADCservice'))
      );
  }

  /** API, GET /api/whoamiを実行する */
  whoami(): Observable<ResMsgOnly> {
    return this.http.get<Object>('/api/whoami', this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: whoami', res);
	  this.username = res['msg'];
	  return new ResMsgOnly(res['msg']);
	}),
	catchError(this.handleError<ResMsgOnly>('whoami'))
      );
  }

  /** API, GET /admin/user/<usernm> を実行する。ユーザー情報を取得する。 */
  getUserInfo(): Observable<ResMsgOnly> {
    return this.http.get<Object>(`/api/admin/user/${this.username}`, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: getUserInfo', res);
	  return new ResMsgOnly(res['msg']);
	}),
	catchError(this.handleError<ResMsgOnly>('getUserInfo'))
      );
  }

  /**
   *  API, POST /user/<usernm>/password を実行する。パスワードを変更する。
   *
   *  @param passwd0  現在のパスワード。
   *  @param passwd1  新しいパスワード。
   *  @param usernm   ユーザー名。管理者は任意のユーザーのパスワードを変更可能なので、ユーザー名を引数で指定できる。
   */
  changePassword(usernm: string, passwd0: string, passwd1: string): Observable<ResMsgOnly> {
    let data = {'password_old': passwd0,
                'password_new': passwd1}
    return this.http.post<Object>(`/api/user/${usernm}/password`, data, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: changePassword', res);
	  return new ResMsgOnly(res['msg']);
	}),
	catchError(this.handleError<ResMsgOnly>('changePassword', new ResMsgOnly('')))
      );
  }

  /** timekeeperの値を取得する。 */
  getTimekeeper(): Observable<ResTimekeeper> {
    return this.http.get<Object>('/api/admin/timekeeper', this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: getTimekeeper', res);
	  return new ResTimekeeper(res['enabled'], new Date(res['lastUpdate']), res['state']);
	}),
	catchError(this.handleError<ResTimekeeper>('getTimekeeper'))
      );
  }


  getUserQList(usernm: string): Observable<ResUserQList> {
    return this.http.get<Object[]>(`/api/user/${usernm}/Q`, this.apiHttpOptions())
      .pipe(
	map((res: Object[]) => {
	  //console.log('AdcService: getUserQList', res);
	  let tmp: UserQEntry[] = []
	  for (let i=0; i<res.length; i++) {
	    let e = new UserQEntry(res[i]['qnum'],
				   res[i]['cols'],
				   res[i]['rows'],
				   res[i]['blocknum'],
				   res[i]['linenum'],
				   new Date(res[i]['date']/1000), // UTCを指定すべきところに、localtimeを指定してる
				   res[i]['filename']);
	    tmp.push(e);
	  }
	  return new ResUserQList(tmp);
	}),
	catchError(this.handleError<ResUserQList>('getUserQList'))
      );
  }


  /** ユーザがアップロード済みの問題データを取得する。 */
  getUserQ(usernm: string, qnum: number): Observable<string> {
    return this.http.get<Object>(`/api/user/${usernm}/Q/${qnum}`, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: getUserQ', res);
	  return res['text'];
	}),
	catchError((err) => {
	  console.log('AdcService: getUserQ ERROR', err);
	  return 'ERROR';
	})
      );
  }


  /** ユーザがアップロード済みの問題データを削除する。 */
  deleteUserQ(usernm: string, qnum: number): Observable<string> {
    return this.http.delete<Object>(`/api/user/${usernm}/Q/${qnum}`, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  console.log('AdcService: deleteUserQ', res);
	  return 'done';
	}),
	catchError((err) => {
	  console.log('AdcService: getUserQ ERROR', err);
	  return 'ERROR';
	})
      );
  }


  /** ユーザが問題データをアップロードする。 */
  postUserQ(usernm: string, qnum: number, qtext: string, qfilename: string): Observable<string> {
    let data = {'Q': qtext,
		'Q_filename': qfilename};
    return this.http.post<Object>(`/api/user/${usernm}/Q/${qnum}`, data, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: postUserQ', res);
	  return res['msg'];
	}),
	catchError((err) => {
	  //console.log('AdcService: postUserQ ERROR', err);
	  //return 'ERROR ' + err['error']['msg'];
	  throw new Error(err['error']['msg']);
	})
      );
  }


  /** ファイルをダウンロードさせる。 */
  downloadFile(data: any, type: string, download: string) {
    let blob = new Blob([data], { type: type});
    let url = window.URL.createObjectURL(blob);

    let a = document.createElement('a');
    document.body.appendChild(a);
    a.setAttribute('style', 'display: none');
    a.href = url;
    a.download = download;
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
}
