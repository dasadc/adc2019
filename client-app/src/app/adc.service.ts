import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { readFile } from './rx-file-reader'
//import { MessageService } from './message.service'

const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' })
};

@Injectable({
  providedIn: 'root'
})
export class AdcService {
  public text1: string;
  public text2: string;
  public filename1: string;
  public filename2: string;
  public fileCheckResult: string;

  //constructor(private messageService: MessageService) { }
  constructor(private http: HttpClient) { }

  readFile1(file: File): Observable<string> {
    this.filename1 = file.name;
    return readFile(file).subscribe(txt => this.text1 = txt);
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
    return readFile(file).subscribe(txt => this.text2 = txt);
  }

  /** POST */
  checkFiles(): Observable<Object> {
    let data = {Q: this.text1,
		A: this.text2};
    //console.log('data', data);
    //return this.http.post<Object>('http://127.0.0.1:4280/api/test_post', data, httpOptions).pipe(
    return this.http.post<Object>('/api/test_post', data, httpOptions).pipe(
      tap((res: Object) => {
	//this.log(`checkFiles: res=${res}`);
	//console.log('AdcService: checkFiles', res);
	//this.fileCheckResult = JSON.stringify(res, null, 4);
	let txt = '';
	['check_file', 'area', 'dim', 'line_corner', 'line_length', 'ban_data', 'corner', 'count'].forEach(key => {
	  if (key in res) {
	    txt += '\n' + key + '\n' + res[key] + '\n';
	  }
	});
	if ('terminal' in res) {
	  txt += '\nterminal\n';
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
	this.fileCheckResult = txt;
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
    return (error: Object): Observable<T> => {

      // TODO: リモート上のロギング基盤にエラーを送信する
      console.error(error); // かわりにconsoleに出力

      // TODO: ユーザーへの開示のためにエラーの変換処理を改善する
      //this.log(`${operation} failed: ${error.message}`);

      // 空の結果を返して、アプリを持続可能にする
      return of(result as T);
    };
  }

  /** Serviceのメッセージを記録 */
  private log(message: string) {
    //console.log(`AdcService: ${message}`);
    console.log('AdcService:', message);
  }
}
