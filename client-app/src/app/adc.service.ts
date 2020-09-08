import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of, from } from 'rxjs';
import { catchError, map, tap, filter, flatMap } from 'rxjs/operators';

import { readFile } from './rx-file-reader';
import { CheckResults } from './checkresults';
import { ResLogin, ResLogout, ResMsgOnly, ResTimekeeper, UserQEntry, ResUserQList, QNumberList, QData, ANumberList, AdminQList, ResUserInfo } from './apiresponse';

const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' })
};

@Injectable({
  providedIn: 'root'
})
export class AdcService {
  text1: string; // Q
  text2: string; // A
  text3: string; // misc.
  filename1: string;
  filename2: string;
  filename3: string;

  // for ADC API
  username: string;
  access_token: string; // given from ADC server after login
  dummy_login_failed: boolean = false;
  not_login: number = 0;
  whoami_error_count: number = 0;
  view_score_mode: boolean = true;

  // BoardEditComponentのデータを保持する
  bec_keep = {
    board_size: {x: 72, y: 72},
    in_number: '',
    q_number: '777',
    num_mino: 0,
    num_line_cell: 0,
    blocks_on_board: [],
    working_mode_selected: 'construction',
    edit_modes_selected: [false, false, false],
  };


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

  readFile3(file: File): Observable<string> {
    this.filename3 = file.name;
    return readFile(file)
      .pipe(
	       tap((txt: string) => {
	          this.text3 = txt;
	          //console.log('readFile3', txt);
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

  clearText3() {
    this.filename3 = undefined;
    this.text3 = undefined;
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
      console.log(`handleError:  ${operation}, result=`, result);
      if (result !== void 0) {
	       //result['msg'] = error.error.msg + '\n' + `${operation} failed: ${error.message}`;
         result['error_msg'] = error.error.msg + '\n' + `${operation} failed: ${error.message}`;
      }

      // 空の結果を返して、アプリを持続可能にする
      return of(result as T);
    };
  }

  /** Serviceのメッセージを記録 */
  private log(message: string) {
    //console.log(`AdcService: ${message}`);
    console.log('AdcService:', message);
  }

  getUsernameCurrent(): string {
    return this.username;
  }

  getUsername(): string {
    if (this.username === void 0) {
      if (this.dummy_login_failed && 5 < this.not_login) {
	       console.log('Please login');
      }
      this.whoami()
      	.subscribe(
      	  (res: ResMsgOnly) => {
      	    this.username = res.msg;
      	  },
      	  (err) => {
      	    console.log('getUsername ERROR:', err['message']);
      	    //throw new Error('getUsername ERROR');
      	  }
      	);
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

  getAccessTokenCurrent(): string {
    return this.access_token;
  }

  getAccessToken(): string {
    //console.log('AdcService: getAccessToken', this.access_token, this.dummy_login_failed, this.not_login);
    if (this.dummy_login_failed && 5 < this.not_login) {
      return undefined;
    }
    this.not_login ++;
    if (this.access_token === void 0 && this.dummy_login_failed == false) {
      // ダミーのloginを行い、もしもsessionによって認証されたら、tokenがもらえる
      let data = {'username': 'dummy',
		  'password': 'dummy'};
      this.http.post<Object>('/api/login', data, this.apiHttpOptions())
      	.subscribe((res: Object) => {
      	  this.access_token = res['token'];
      	}, (err) => {
      	  console.log('AdcService: getAccessToken ERROR', err['message']);
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

  /** API, GET /api/versionを実行する */
  version(): Observable<number> {
    return this.http.get<Object>('/api/version', this.apiHttpOptions())
      .pipe(
      	map((res: Object) => {
      	  //console.log('AdcService: version', res);
      	  let v = res['version'] as number;
      	  return v;
      	}),
      	catchError(this.handleError<number>('version', -1))
      );
  }

  /** API, GET /api/whoamiを実行する */
  whoami(): Observable<ResMsgOnly> {
    //console.log('AdcService: whoami', this.whoami_error_count);
    return this.http.get<Object>('/api/whoami', this.apiHttpOptions())
      .pipe(
        map((res: Object) => {
          //console.log('AdcService: whoami', res);
          this.username = res['msg'];
          return new ResMsgOnly(res['msg']);
        }),
        catchError((err) => {
          //this.handleError<ResMsgOnly>('whoami', new ResMsgOnly('error'))
          console.log('Error whoami', err['message']);
          this.whoami_error_count ++;
          //throw new Error(err['error']['msg']);
          throw new Error('whoami error');
        })
      );
  }

  /** API, GET /admin/user/<usernm> を実行する。ユーザー情報を取得する。 */
  getUserInfo(username?: string): Observable<ResMsgOnly> {
    let user = this.username;
    if (username !== void 0) {
      user = username;
    }
    return this.http.get<Object>(`/api/admin/user/${user}`, this.apiHttpOptions())
      .pipe(
      	map((res: Object) => {
      	  //console.log('AdcService: getUserInfo', res);
      	  return new ResMsgOnly(res['msg']);
      	}),
        //catchError(this.handleError<ResMsgOnly>('getUserInfo', new ResMsgOnly('forbidden:?:?:?')))
        catchError(this.handleError<ResMsgOnly>('getUserInfo', new ResMsgOnly(undefined)))
        /*
        catchError((err) => {
          console.log('getUserInfo ERROR', err);
          //throw new Error(err['message']);
          return this.handleError<ResMsgOnly>('getUserInfo', new ResMsgOnly(''));
          //return new ResMsgOnly('');
        })
        */
      );
  }

  /** API, DELETE /admin/user/<usernm> を実行する。ユーザーを削除する。 */
  deleteUserInfo(user: string): Observable<ResMsgOnly> {
    return this.http.delete<Object>(`/api/admin/user/${user}`, this.apiHttpOptions())
      .pipe(
        map((res: Object) => {
          //console.log('delete user', res['msg']);
          return new ResMsgOnly(res['msg']);
        }),
        catchError(this.handleError<ResMsgOnly>('deleteUserInfo', new ResMsgOnly(undefined)))
      );
  }

  /**
   *  get user info of all users.
   *  for each user in getUserList(), call getUserInfo(user)
   *  どうも、結果(ResUserInfo)の順序は、一定ではないようだ。
   *  server APIをcallするのは、ソートされた順序通りらしいが、
   *  serverのレスポンスを受理完了するのが、順不同になってしまうためらしい
   */
  getAllUserInfo(): Observable<ResUserInfo> {
    return this.getUserList()
      .pipe(
        flatMap((users: string[]) => {
          //console.log('(flatMap) users=', users);
          return from(users);
        }),
        flatMap((username: string) => {
          //console.log('flatMap: username', username);
          return this.getUserInfo(username);
        }),
        filter((res: Object) => {
          return res['msg'] !== void 0;
        }),
        map((res: Object) => {
          //console.log('map', res['msg']);
          let tmp = res['msg'].split(':');
          return new ResUserInfo(tmp[0], tmp[1], tmp[2], tmp[3]);
        })
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
      	  return new ResTimekeeper(res['enabled'], res['state'], new Date(res['lastUpdate']));
      	})/*,
      	catchError(this.handleError<ResTimekeeper>('getTimekeeper'))*/
      );
  }

  /** timekeeperの値を変更する。lastUpdateは無視される。 */
  setTimekeeper(obj: ResTimekeeper): Observable<ResTimekeeper> {
    let dat: Object = {'enabled': obj.enabled,
		       'state': obj.state};
    return this.http.put<Object>('/api/admin/timekeeper', dat, this.apiHttpOptions())
      .pipe(
      	map((res: Object) => {
      	  //console.log('AdcService: setTimekeeper', res);
      	  return new ResTimekeeper(res['enabled'], res['state'], res['lastUpdate']);
      	})/*,
      	catchError(this.handleError<ResTimekeeper>('setTimekeeper'))*/
      );
  }

  /** TEST_MODEの値を取得する。 */
  getTestMode(): Observable<boolean> {
    return this.http.get<Object>('/api/admin/config/test_mode', this.apiHttpOptions())
      .pipe(
      	map((res: Object) => {
      	  //console.log('AdcService: getTestMode', res);
      	  return res['test_mode'];
      	})
      );
  }

  /** TEST_MODEの値を変更する。 */
  setTestMode(mode: boolean): Observable<boolean> {
    let dat: Object = {'test_mode': mode};
    return this.http.put<Object>('/api/admin/config/test_mode', dat, this.apiHttpOptions())
      .pipe(
      	map((res: Object) => {
      	  //console.log('AdcService: setTestMode', res);
      	  return res['test_mode'];
      	})
      );
  }


    /** VIEW_SCORE_MODEの値を取得する。 */
    getViewScoreMode(): Observable<boolean> {
      return this.http.get<Object>('/api/admin/config/view_score_mode', this.apiHttpOptions())
        .pipe(
          	map((res: Object) => {
          	  //console.log('AdcService: getViewScoreMode', res);
              this.view_score_mode = res['view_score_mode']
          	  return res['view_score_mode'];
          	})
        );
    }

    /** VIEW_SCORE_MODEの値を変更する。 */
    setViewScoreMode(mode: boolean): Observable<boolean> {
      let dat: Object = {'view_score_mode': mode};
      return this.http.put<Object>('/api/admin/config/view_score_mode', dat, this.apiHttpOptions())
        .pipe(
        	map((res: Object) => {
        	  //console.log('AdcService: setViewScoreMode', res);
        	  return res['view_score_mode'];
        	})
        );
    }



  getUserQList(usernm: string): Observable<ResUserQList> {
    return this.http.get<Object[]>(`/api/user/${usernm}/Q`, this.apiHttpOptions())
      .pipe(
      	map((res: Object[]) => {
      	  //console.log('AdcService: getUserQList', usernm, res);
      	  let tmp: UserQEntry[] = []
      	  if (res !== void 0) {
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

  /** 出題された問題データのリストを取得する。 */
  getQNumberList(): Observable<QNumberList> {
    return this.http.get<Object>('/api/Q', this.apiHttpOptions())
      .pipe(
      	map((res: Object[]) => {
      	  // console.log('AdcService: getQList', res);
      	  return new QNumberList(res['msg'],
      				 res['qnum_list'],
      				 res['cols_list'],
      				 res['rows_list'],
      				 res['blocknum_list'],
      				 res['linenum_list']);
      	})/*,
      	catchError(this.handleError<QNumberList>('getQList'))*/
      );
  }

  /** 出題された問題データを取得する。 */
  getQ(qnum: number): Observable<QData> {
    return this.http.get<Object>(`/api/Q/${qnum}`, this.apiHttpOptions())
      .pipe(
      	map((res: Object[]) => {
      	  //console.log('AdcService: getQ', res);
      	  return new QData(res['author'],
      			   res['qnum'],
      			   res['filename'],
      			   res['date'],
      			   qnum,
      			   res['cols'],
      			   res['rows'],
      			   res['blocknum'],
      			   res['linenum'],
      			   res['text']);
      	})/*,
      	catchError(this.handleError<QData>('getQ'))*/
      );
  }

  /** ユーザが回答データをアップロードする。 */
  putA(usernm: string, anum: number, atext: string, afilename: string): Observable<string> {
    let data = {'A': atext,
		'A_filename': afilename};
    return this.http.put<Object>(`/api/A/${usernm}/Q/${anum}`, data, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: putA', res);
	  return res['msg'];
	}),
	catchError((err) => {
	  console.log('AdcService: putA ERROR', err);
	  //return 'ERROR ' + err['error']['msg'];
	  throw new Error(err['error']['msg']);
	})
      );
  }

  /** 出題された問題データのリストを取得する。 */
  getANumberList(usernm: string): Observable<ANumberList> {
    return this.http.get<Object>(`/api/A/${usernm}`, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: getANumberList', res);
	  return new ANumberList(res['msg'],
				 res['anum_list']);
	})/*,
	catchError(this.handleError<ANumberList>('getANumberList'))*/
      );
  }


  getAdminQList(): Observable<AdminQList> {
    return this.http.get<Object[]>(`/api/admin/Q/list`, this.apiHttpOptions())
      .pipe(
	map((res: Object[]) => {
	  //console.log('AdcService: getAdminQList', res);
	  return new AdminQList(res['author_list'],
				res['author_qnum_list'],
				res['blocknum_list'],
				res['cols_list'],
				res['date'],
				res['linenum_list'],
				res['qnum_list'],
				res['rows_list'],
				res['text_admin'],
				res['text_user']);
	})/*,
	catchError(this.handleError<AdminQList>('getAdminQList',AdminQList.empty()))*/
      );
  }

  deleteAdminQList(): Observable<Object> {
    return this.http.delete<Object[]>(`/api/admin/Q/list`, this.apiHttpOptions())
      .pipe(
	map((res: Object[]) => {
	  //console.log('AdcService: deleteAdminQList', res);
	  return res;
	})/*,
	catchError(this.handleError<Object>('deleteAdminQList', AdminQList.empty()))*/
      );
  }

  putAdminQList(): Observable<Object> {
    //console.log('adc.service putAdminQList');
    let params = {'dummy': 0};
    return this.http.put<Object>(`/api/admin/Q/list`, params, this.apiHttpOptions())
      .pipe(
	map((res: Object) => {
	  //console.log('AdcService: putAdminQList', res);
	  return res;
	})/*,
	catchError(this.handleError<Object>('putAdminQList'))*/
      );
  }


  /** すべての問題データを取得する。 */
  getAdminQAll(): Observable<Object> {
    return this.http.get<Object>(`/api/admin/Q/all`, this.apiHttpOptions());
  }

  /** すべての回答データを消去する。 */
  deleteAdminQAll(): Observable<Object> {
    return this.http.delete<Object>(`/api/admin/Q/all`, this.apiHttpOptions());
  }


  /** すべての回答データを取得する。 */
  getAdminAAll(): Observable<Object> {
    return this.http.get<Object>(`/api/A`, this.apiHttpOptions());
  }

  /** すべての回答データを消去する。 */
  deleteAdminAAll(): Observable<Object> {
    return this.http.delete<Object>(`/api/A`, this.apiHttpOptions());
  }


  getScore(): Observable<Object> {
    return this.http.get<Object>(`/api/score`, this.apiHttpOptions());
  }

  /** 回答データを取得する。 see also getQ */
  getA(username: string, qnum: number): Observable<Object> {
    return this.http.get<Object>(`/api/A/${username}/Q/${qnum}`, this.apiHttpOptions())
      .pipe(
      	map((res: Object) => {
      	  //console.log('AdcService: getA', res);
      	  return res;
      	})
      );
  }

  /** ユーザーの一覧リストを取得する。 */
  getUserList(): Observable<string[]> {
    return this.http.get<Object>(`/api/admin/user`, this.apiHttpOptions())
      .pipe(
      	map((res: Object) => {
      	  //console.log('AdcService: getUserList', res);
      	  return res as string[];
      	})
      );
  }

  /** ユーザー登録 */
  createUser(data: Object): Observable<ResMsgOnly> {
    let username :string = data['username'];
    return this.http.post<Object>(`/api/admin/user/${username}`, data, this.apiHttpOptions())
      .pipe(
        map((res: Object) => {
          //console.log('createUser', res);
          return new ResMsgOnly(res['msg']);
        }),
        catchError(this.handleError<ResMsgOnly>('createUser', new ResMsgOnly(undefined)))
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
